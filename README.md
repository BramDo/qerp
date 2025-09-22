# Quantum-Enhanced Reaction Pathway Analysis (QERP)

Reproduceerbare workflow voor DMET-embedding + measurement-efficiënte (S)KQD/ADAPT-VQE
op aromatische ringen. Doelen: MVP-notebook (Aer+GPU), benzothiofeen-pad met hardware-validatie,
en een korte technische notitie.

## Structuur
- `src/neb/`  DFT/NEB pipeline en parsers (ASE + externe DFT)
- `src/dmet/` DMET-wrapper en actieve-ruimte diagnostiek
- `src/ham/`  Tweede-kwantisatie → qubits (mapping, tapering)
- `src/solvers/`  SKQD, ADAPT-VQE en hulpfuncties
- `src/mitigation/`  Readout-correctie, ZNE, symmetrie-filters
- `src/post/`  Postprocessing, figuren, tabellen
- `src/utils/`  IO, logging, configuratie
- `notebooks/`  A: toy fragment (MVP); B: benzothiofeen-pad
- `reports/`  2-pagina technische notitie (LaTeX)
- `data/`  Voorbeeldgeometrieën en tussenresultaten

## Snelle start (MVP - Aer GPU)
1. Installeer vereisten: `pip install -r requirements.txt`
2. Open `notebooks/A_toy_fragment_SKQD.ipynb`
3. Run alle cellen → energieschattingen + simpele plots

## Licentie
MIT
