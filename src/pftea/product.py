"""The secreted protein: elemental formula from sequence, and its formation stoichiometry.

1. Elemental formula. The mature sequence is summed over free amino acids (formulas from
   the compound table), minus one H2O per peptide bond and 2 H per disulfide. The result
   is normalised to one C-mole. Glycans and phosphates are ignored (<2% of mass).
2. Thermodynamic properties per C-mole use the same elemental correlation as biomass
   (thermo.biomass). This is an analogy (grade D); it only enters the heat balance, which
   Cooney's rule cross-checks.
3. Formation reaction. Anabolic: glucose + NH3 -> 1 C-mol protein + CO2 + H2O, with C, H,
   O and N balanced and sulfur ignored (<1% of atoms). Energy comes from lam moles of
   glucose catabolism (glucose + 6 O2 -> 6 CO2 + 6 H2O) per C-mol protein:
       product reaction = anabolic + lam * catabolic
   Given a product yield Y_ps (g protein per g glucose through the product reaction):
       lam = M_p / (Y_ps M_glc) + nu_glc,anab       (nu_glc,anab < 0)
   so lam >= 0 requires Y_ps <= Y_anab = M_p / (-nu_glc,anab M_glc), the electron ceiling.
4. Energetic ceiling. Protein synthesis costs n_ATP per residue (plant.atp_per_residue): the
   peptide bond (4), the net cost of making the amino acid from glucose and NH4+ (Stouthamer,
   ~0.3) and sulfate assimilation for the protein's sulfur. Respiring one glucose yields Y_ATP
   ATP. Then
       lam_min = n_ATP (residues per C-mol) / Y_ATP,    Y_ps,max = M_p / ((lam_min - nu) M_glc)
   Transport, secretion, folding and turnover are not counted, so Y_ps,max is an upper bound;
   real processes run below it. The scenarios set Y_ps directly and report Y_ps / Y_ps,max.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from . import thermo as th

ROOT = Path(__file__).resolve().parents[2]
AA = {"A": "Alanine", "R": "Arginine", "N": "Asparagine", "D": "Aspartic acid", "C": "Cysteine",
      "Q": "Glutamine", "E": "Glutamic acid", "G": "Glycine", "H": "Histidine", "I": "Isoleucine",
      "L": "Leucine", "K": "Lysine", "M": "Methionine", "F": "Phenylalanine", "P": "Proline",
      "S": "Serine", "T": "Threonine", "W": "Tryptophan", "Y": "Tyrosine", "V": "Valine"}


@lru_cache(maxsize=None)
def load(key: str) -> dict:
    return yaml.safe_load((ROOT / f"data/products/{key}.yaml").read_text())


def formula_from_sequence(seq: str, disulfides: int = 0) -> dict[str, float]:
    tot = {"C": 0.0, "H": 0.0, "O": 0.0, "N": 0.0, "S": 0.0}
    comp = th.compounds()
    for ch in seq.replace(" ", ""):
        aa = comp[AA[ch]]
        for e in tot:
            tot[e] += aa.element(e)
    n = len(seq.replace(" ", ""))
    tot["H"] -= 2 * (n - 1) + 2 * disulfides
    tot["O"] -= (n - 1)
    return tot


@dataclass(frozen=True)
class Protein:
    key: str
    name: str
    residues: int
    formula: dict           # per molecule
    species: th.Species     # per C-mole
    mw_molecule: float      # g/mol

    @property
    def residues_per_cmol(self) -> float:
        return self.residues / self.formula["C"]


@lru_cache(maxsize=None)
def protein(key: str) -> Protein:
    d = load(key)
    if "formula_cmol" in d:                        # formula-only product (e.g. NREL cellulase)
        fc = d["formula_cmol"]
        n_res = 1000                               # nominal; only residues_per_cmol matters
        f = {e: fc.get(e, 0.0) * n_res / d["residues_per_cmol"] for e in ("C", "H", "O", "N", "S")}
        sp = th.biomass(1.0, fc["H"], fc["O"], fc["N"], name=d["name"])
        mw_mol = sum(f[e] * th.ATOM[e] for e in f)
        sp = th.Species(sp.name, 1.0, sp.H, sp.O, sp.N, fc.get("S", 0.0), sp.gamma, sp.dHf, sp.dGf, mw_mol / f["C"])
        return Protein(key, d["name"], n_res, f, sp, mw_mol)
    seq = d["mature_sequence"].replace(" ", "")
    f = formula_from_sequence(seq, d.get("disulfides", 0))
    c = f["C"]
    sp = th.biomass(1.0, f["H"] / c, f["O"] / c, f["N"] / c, name=d["name"])
    mw_mol = sum(f[e] * th.ATOM[e] for e in f)
    # per C-mole species keeps S out of the element balance but in the molar mass
    sp = th.Species(sp.name, 1.0, sp.H, sp.O, sp.N, f["S"] / c, sp.gamma, sp.dHf, sp.dGf,
                    mw_mol / c)
    return Protein(key, d["name"], len(seq), f, sp, mw_mol)


def anabolic(p: Protein, csource: th.Species) -> th.Reaction:
    return th.anabolic(p.species, csource)


def product_reaction(p: Protein, csource: th.Species, Y_ps: float) -> th.Reaction:
    """Formation of 1 C-mol protein at product yield Y_ps (g/g) through this reaction."""
    an = anabolic(p, csource)
    nu = an.of(csource.name)                          # negative
    lam = p.species.mw / (Y_ps * csource.mw) + nu
    if lam < -1e-12:
        raise ValueError(f"Y_ps={Y_ps:.3f} exceeds the electron ceiling {electron_ceiling(p, csource):.3f}")
    return an + th.catabolic(csource).scaled(max(lam, 0.0))


def electron_ceiling(p: Protein, csource: th.Species) -> float:
    nu = anabolic(p, csource).of(csource.name)
    return p.species.mw / (-nu * csource.mw)


def energetic_ceiling(p: Protein, csource: th.Species, atp_per_residue: float,
                      atp_per_glucose: float) -> float:
    """Maximum product yield (g/g) once the ATP cost of synthesis is paid by respiration."""
    nu = anabolic(p, csource).of(csource.name)
    lam = atp_per_residue * p.residues_per_cmol / atp_per_glucose
    return p.species.mw / ((lam - nu) * csource.mw)


def o2_per_kg(p: Protein, csource: th.Species, Y_ps: float) -> float:
    """mol O2 consumed per kg protein made through the product reaction."""
    r = product_reaction(p, csource, Y_ps)
    return -r.of("O2 (aq)") / p.species.mw * 1000
