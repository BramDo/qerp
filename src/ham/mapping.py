from __future__ import annotations
from qiskit_nature.second_q.mappers import ParityMapper, QubitConverter
from qiskit.quantum_info import SparsePauliOp

def map_to_qubits(second_q_op, num_particles) -> SparsePauliOp:
    conv = QubitConverter(ParityMapper(), two_qubit_reduction=True)
    return conv.convert(second_q_op, num_particles=num_particles)
