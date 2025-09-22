from __future__ import annotations
from dataclasses import dataclass
from typing import List
# Placeholders for NEB orchestration (ASE hooks)
@dataclass
class NEBImage:
    xyz: str  # path to xyz
    energy: float | None = None

def run_neb(images: List[NEBImage]) -> List[NEBImage]:
    # TODO: plug in ASE + chosen DFT backend
    return images
