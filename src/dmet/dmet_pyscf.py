from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class DMETConfig:
    basis: str = "def2-svp"
    charge: int = 0
    spin: int = 0

def build_fragment(mol_xyz: str, cfg: DMETConfig) -> dict[str, Any]:
    # TODO: PySCF DMET; return dict with MO info, active space, integrals
    return {"active_orbitals": (8, 8), "integrals": None}
