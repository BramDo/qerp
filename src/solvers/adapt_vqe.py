from __future__ import annotations
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import SLSQP
from qiskit_nature.second_q.circuit.library import UCCSD

def adapt_vqe_factory(problem, mapper, estimator):
    ansatz = UCCSD(problem.num_spatial_orbitals, problem.num_particles, mapper=mapper)
    return VQE(estimator, ansatz, SLSQP(maxiter=200))
