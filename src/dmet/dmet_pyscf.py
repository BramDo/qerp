"""PySCF-backed helpers for building DMET fragments.

This module contains a light-weight wrapper around PySCF and Qiskit Nature
that produces the minimal data structures required by the rest of QERP.  The
helpers deliberately stay close to the chemistry literature: they first
construct a mean-field solution, then return the active-space Hamiltonian in
qubit form together with a few diagnostics that are typically inspected during
DMET studies.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from pyscf import gto, scf
from qiskit.quantum_info import SparsePauliOp
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper, ParityMapper
from qiskit_nature.second_q.operators import FermionicOp
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
from qiskit_nature.units import DistanceUnit


@dataclass
class DMETConfig:
    """Configuration options for building a DMET fragment."""

    basis: str = "sto-3g"
    charge: int = 0
    spin: int = 0
    distance_unit: DistanceUnit = DistanceUnit.ANGSTROM
    active_electrons: int | None = None
    active_orbitals: int | None = None
    fragment_orbitals: Sequence[int] | None = None
    mapper: str = "parity"
    two_qubit_reduction: bool = True


@dataclass
class DMETFragment:
    """Container for data returned by the DMET wrapper."""

    geometry: Sequence[Tuple[str, Tuple[float, float, float]]]
    basis: str
    active_electrons: int
    active_orbitals: int
    fragment_orbitals: Sequence[int]
    hartree_fock_energy: float
    fermionic_hamiltonian: FermionicOp
    qubit_hamiltonian: SparsePauliOp


def build_fragment_from_xyz(xyz_path: str | Path, cfg: DMETConfig | None = None) -> DMETFragment:
    """Create a DMET fragment from a simple XYZ geometry file."""

    cfg = cfg or DMETConfig()
    geometry = _parse_xyz(xyz_path)
    return build_fragment_from_geometry(geometry, cfg)


def build_fragment_from_geometry(
    geometry: Sequence[Tuple[str, Iterable[float]]],
    cfg: DMETConfig | None = None,
) -> DMETFragment:
    """Create a DMET fragment from an in-memory geometry."""

    cfg = cfg or DMETConfig()
    geometry = _normalise_geometry(geometry)

    mol = _build_pyscf_molecule(geometry, cfg)
    hf_energy = _run_restricted_hf(mol)

    driver = PySCFDriver(
        atom=_format_geometry_for_pyscf(geometry),
        basis=cfg.basis,
        unit=cfg.distance_unit,
        charge=cfg.charge,
        spin=cfg.spin,
    )
    problem = driver.run()

    electrons = cfg.active_electrons or sum(problem.num_particles)
    orbitals = cfg.active_orbitals or _infer_spatial_orbitals(problem)

    transformer = ActiveSpaceTransformer(
        num_electrons=electrons,
        num_spatial_orbitals=orbitals,
    )
    problem_active = transformer.transform(problem)

    fragment_orbitals = tuple(cfg.fragment_orbitals or range(orbitals))

    fermionic_op = problem_active.hamiltonian.second_q_op()
    mapper = _build_mapper(
        cfg.mapper,
        num_particles=problem_active.num_particles,
        two_qubit_reduction=cfg.two_qubit_reduction,
    )
    qubit_op = mapper.map(
        fermionic_op,
        register_length=problem_active.num_spatial_orbitals * 2,
    )

    return DMETFragment(
        geometry=geometry,
        basis=cfg.basis,
        active_electrons=electrons,
        active_orbitals=orbitals,
        fragment_orbitals=fragment_orbitals,
        hartree_fock_energy=hf_energy,
        fermionic_hamiltonian=fermionic_op,
        qubit_hamiltonian=qubit_op,
    )


def build_h2_fragment(
    bond_length: float = 0.735,
    cfg: DMETConfig | None = None,
) -> DMETFragment:
    """Construct a minimal DMET fragment for a gas-phase H₂ molecule."""

    cfg = cfg or DMETConfig()

    h2_geometry = (
        ("H", (0.0, 0.0, -bond_length / 2.0)),
        ("H", (0.0, 0.0, bond_length / 2.0)),
    )

    if cfg.active_electrons is None:
        cfg = replace(cfg, active_electrons=2)
    if cfg.active_orbitals is None:
        cfg = replace(cfg, active_orbitals=2)
    if cfg.fragment_orbitals is None:
        cfg = replace(cfg, fragment_orbitals=(0, 1))

    return build_fragment_from_geometry(h2_geometry, cfg)


def _parse_xyz(xyz_path: str | Path) -> Sequence[Tuple[str, Tuple[float, float, float]]]:
    path = Path(xyz_path)
    raw_lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(raw_lines) < 2:
        msg = f"XYZ file '{path}' is too short to contain geometry information."
        raise ValueError(msg)

    try:
        expected_atoms = int(raw_lines[0])
    except ValueError as exc:
        raise ValueError(f"First line of '{path}' must contain the atom count.") from exc

    atom_lines = raw_lines[2 : 2 + expected_atoms]
    geometry: List[Tuple[str, Tuple[float, float, float]]] = []
    for line in atom_lines:
        parts = line.split()
        if len(parts) < 4:
            msg = f"Failed to parse coordinates from line '{line}'."
            raise ValueError(msg)
        symbol = parts[0]
        coords = tuple(float(value) for value in parts[1:4])
        geometry.append((symbol, coords))

    if len(geometry) != expected_atoms:
        msg = (
            f"XYZ file '{path}' declares {expected_atoms} atoms but contains "
            f"{len(geometry)} coordinate lines."
        )
        raise ValueError(msg)

    return tuple(geometry)


def _normalise_geometry(
    geometry: Sequence[Tuple[str, Iterable[float]]],
) -> Sequence[Tuple[str, Tuple[float, float, float]]]:
    normalised: List[Tuple[str, Tuple[float, float, float]]] = []
    for symbol, coords in geometry:
        coord_tuple = tuple(float(value) for value in coords)
        if len(coord_tuple) != 3:
            msg = f"Coordinate for atom '{symbol}' must have three components."
            raise ValueError(msg)
        normalised.append((symbol, coord_tuple))
    return tuple(normalised)


def _build_pyscf_molecule(
    geometry: Sequence[Tuple[str, Tuple[float, float, float]]],
    cfg: DMETConfig,
) -> gto.Mole:
    mol = gto.Mole()
    mol.unit = cfg.distance_unit.value
    mol.atom = _format_geometry_for_pyscf(geometry)
    mol.basis = cfg.basis
    mol.charge = cfg.charge
    mol.spin = cfg.spin
    mol.build()
    return mol


def _format_geometry_for_pyscf(
    geometry: Sequence[Tuple[str, Tuple[float, float, float]]],
) -> str:
    lines = [f"{symbol} {x} {y} {z}" for symbol, (x, y, z) in geometry]
    return "\n".join(lines)


def _run_restricted_hf(mol: gto.Mole) -> float:
    mf = scf.RHF(mol)
    return float(mf.kernel())


def _build_mapper(
    name: str,
    *,
    num_particles: tuple[int, int] | None,
    two_qubit_reduction: bool,
):
    lowered = name.lower()
    if lowered == "parity":
        if two_qubit_reduction:
            if num_particles is None:
                msg = "Two-qubit reduction requires particle counts."
                raise ValueError(msg)
            return ParityMapper(num_particles=num_particles)
        return ParityMapper()
    if lowered in {"jw", "jordan-wigner", "jordan_wigner"}:
        return JordanWignerMapper()
    msg = f"Unsupported mapper '{name}'."
    raise ValueError(msg)


def _infer_spatial_orbitals(problem) -> int:
    integrals = problem.hamiltonian.electronic_integrals
    alpha = integrals.alpha
    if hasattr(alpha, "dimension"):
        return alpha.dimension
    return alpha.get_matrix().shape[0]


__all__ = [
    "DMETConfig",
    "DMETFragment",
    "build_fragment_from_geometry",
    "build_fragment_from_xyz",
    "build_h2_fragment",
]
