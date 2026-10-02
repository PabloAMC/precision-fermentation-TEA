"""Black-box stoichiometry and thermodynamics of microbial growth.

Method: Humbird (2021) SI sheet A.1, which follows Heijnen & van Dijken (1992) for the
Gibbs energy dissipated per unit of biomass made, and Tijhuis et al. (1993) for maintenance.

1. Species are written with an elemental formula. For biomass it is per C-mole. The degree
   of reduction uses NH3, CO2 and H2O as the zero reference:
       gamma = 4 C + H - 2 O - 3 N
2. Biomass formation properties come from empirical elemental correlations (A.1 row 3):
       dHf = 19.7 C M_C/10 - 278.2 H M_H/10 - 108 O M_O/10 + 29 N M_N/10        [kJ/C-mol]
       dSf = -0.813 (5.74 C + 65.342 H + 102.569 O + 95.805 N)                  [J/C-mol/K]
       dGf = dHf - 298.15 dSf / 1000                                            [kJ/C-mol]
3. Anabolic reaction: carbon source + NH3 -> 1 C-mol biomass + CO2 + H2O. Its coefficients
   solve the C, H, O and N element balances (4 equations, 4 unknowns).
4. Catabolic reaction: 1 carbon source + O2 -> CO2 + H2O (C, H, O balances).
5. Gibbs energy dissipated per C-mol biomass, carbon source with c carbons and degree of
   reduction gamma_s (Heijnen & van Dijken 1992):
       D = 200 + 18 (6 - c)^1.8 + exp( ((3.8 - gamma_s/c)^2)^0.16 (3.6 + 0.4 c) )   [kJ/C-mol]
6. Growth reaction = anabolic + lam * catabolic, where lam = -(D + dG_anab) / dG_cat. The
   catabolic extent supplies exactly the Gibbs energy that growth dissipates.
7. Maintenance Gibbs energy (Tijhuis et al. 1993; T in deg C):
       m_G = 4.5 exp(-69000/8.314 (1/(T + 273) - 1/298))                       [kJ/(C-mol h)]
   Maintenance is m_G / (-dG_cat) moles of the catabolic reaction per C-mol biomass per hour.
8. Herbert-Pirt: the specific rate of species i is q_i = y_i mu + m_i (mol per C-mol biomass
   per h), with y_i the growth-reaction coefficient and m_i the maintenance coefficient.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
# Atomic masses as used in Humbird's Phys sheet (row 4).
ATOM = {"C": 12.011, "H": 1.0079, "O": 15.9994, "N": 14.0067, "S": 32.065}
R_GAS = 8.314  # J/mol/K
ELEMENTS = ("C", "H", "O", "N")


@dataclass(frozen=True)
class Species:
    name: str
    C: float = 0.0
    H: float = 0.0
    O: float = 0.0
    N: float = 0.0
    S: float = 0.0
    gamma: float = 0.0
    dHf: float = 0.0  # kJ/mol (per C-mol for biomass)
    dGf: float = 0.0  # kJ/mol
    mw: float = 0.0   # g/mol (per C-mol for biomass)

    def element(self, e: str) -> float:
        return getattr(self, e)


@lru_cache(maxsize=None)
def compounds() -> dict[str, Species]:
    raw = yaml.safe_load((ROOT / "data/thermo/compounds.yaml").read_text())
    out = {}
    for name, r in raw.items():
        out[name] = Species(name, r["C"], r["H"], r["O"], r["N"], r["S"], r["gamma"],
                            r["dHf_kJ_mol"], r["dGf_kJ_mol"], r["mw"])
    return out


def get(name: str) -> Species:
    return compounds()[name]


def biomass(C: float = 1.0, H: float = 1.703, O: float = 0.459, N: float = 0.171,
            name: str = "DCW") -> Species:
    """Biomass per C-mole with correlation-based thermodynamic properties (A.1 row 3)."""
    mw = C * ATOM["C"] + H * ATOM["H"] + O * ATOM["O"] + N * ATOM["N"]
    gamma = 4 * C + H - 2 * O - 3 * N
    dHf = (19.7 * C * 12.011 / 10 - 278.2 * H * 1.00794 / 10 - 108 * O * 15.9994 / 10
           + 29 * N * 14.00674 / 10)
    dSf = -0.813 * (C * 5.74 + H * 65.342 + O * 102.569 + N * 95.805)
    dGf = dHf - 298.15 * dSf / 1000
    return Species(name, C, H, O, N, 0.0, gamma, dHf, dGf, mw)


@dataclass
class Reaction:
    """Stoichiometric coefficients (negative = consumed) keyed by species."""
    coef: dict[Species, float] = field(default_factory=dict)

    def __add__(self, other: "Reaction") -> "Reaction":
        out = dict(self.coef)
        for s, v in other.coef.items():
            out[s] = out.get(s, 0.0) + v
        return Reaction(out)

    def scaled(self, k: float) -> "Reaction":
        return Reaction({s: k * v for s, v in self.coef.items()})

    def of(self, name: str) -> float:
        return sum(v for s, v in self.coef.items() if s.name == name)

    def residual(self, e: str) -> float:
        return sum(v * s.element(e) for s, v in self.coef.items())

    @property
    def dG(self) -> float:
        return sum(v * s.dGf for s, v in self.coef.items())

    @property
    def dH(self) -> float:
        return sum(v * s.dHf for s, v in self.coef.items())


def _solve(fixed: dict[Species, float], unknown: list[Species],
           elements: tuple[str, ...]) -> Reaction:
    """Find coefficients of `unknown` species that close the element balances."""
    A = np.array([[s.element(e) for s in unknown] for e in elements], dtype=float)
    b = -np.array([sum(v * s.element(e) for s, v in fixed.items()) for e in elements])
    x = np.linalg.solve(A, b)
    coef = dict(fixed)
    coef.update({s: float(v) for s, v in zip(unknown, x)})
    return Reaction(coef)


def anabolic(bio: Species, csource: Species, nsource: Species | None = None) -> Reaction:
    """csource + NH3 -> 1 C-mol biomass + CO2 + H2O (element balanced).

    A C-source less reduced than the biomass (glucose: gamma 4 per C against ~4.1) supplies the
    missing electrons by oxidising some of itself, so CO2 is released. A C-source more reduced than
    the biomass (methanol: gamma 6) would balance only by fixing CO2, which methylotrophic yeasts do
    not do; there every biomass carbon comes from the C-source and the surplus electrons go to the
    electron acceptor, O2 (Heijnen & van Dijken 1992; Kleerebezem & van Loosdrecht 2010)."""
    nsource = nsource or get("NH3 (aq)")
    r = _solve({bio: 1.0}, [csource, nsource, get("CO2 (aq)"), get("H2O (l)")], ELEMENTS)
    if r.of("CO2 (aq)") < -1e-12:
        r = _solve({bio: 1.0, csource: -bio.C / csource.C}, [nsource, get("O2 (aq)"), get("H2O (l)")],
                   tuple(e for e in ELEMENTS if e != "C"))
    return r


def catabolic(csource: Species) -> Reaction:
    """1 csource + O2 -> CO2 + H2O (element balanced)."""
    return _solve({csource: -1.0}, [get("O2 (aq)"), get("CO2 (aq)"), get("H2O (l)")],
                  ("C", "H", "O"))


def heijnen_dissipation(csource: Species) -> float:
    """Gibbs energy dissipated per C-mol biomass [kJ/C-mol], Heijnen & van Dijken (1992).

    c = carbon atoms per molecule of the C-source; gamma/c = its degree of reduction per C-mol.
    The correlation is defined for 1 <= c <= 6 (for c > 6, (6 - c)^1.8 is not real).
    """
    c, g = csource.C, csource.gamma
    if not 1 <= c <= 6:
        raise ValueError(f"Heijnen correlation needs 1 <= c <= 6 carbon atoms, got {c}")
    return 200 + 18 * (6 - c) ** 1.8 + np.exp(((3.8 - g / c) ** 2) ** 0.16 * (3.6 + 0.4 * c))


def maintenance_gibbs(T_C: float) -> float:
    """Maintenance Gibbs energy [kJ/(C-mol h)], Tijhuis et al. (1993)."""
    return 4.5 * np.exp(-69000 / R_GAS * (1 / (273 + T_C) - 1 / 298))


@dataclass
class GrowthModel:
    """Growth and maintenance stoichiometry for one organism on one carbon source."""
    bio: Species
    csource: Species
    T_C: float = 30.0

    def __post_init__(self):
        self.anab = anabolic(self.bio, self.csource)
        self.cat = catabolic(self.csource)
        self.dissipation = heijnen_dissipation(self.csource)
        self.lam = -(self.dissipation + self.anab.dG) / self.cat.dG
        self.growth = self.anab + self.cat.scaled(self.lam)
        self.m_G = maintenance_gibbs(self.T_C)
        self.maint_extent = -self.m_G / self.cat.dG          # mol catabolism / (C-mol h)
        self.maint = self.cat.scaled(self.maint_extent)

    def q(self, name: str, mu: float) -> float:
        """Specific rate of `name` in mol per C-mol biomass per hour (Herbert-Pirt)."""
        return self.growth.of(name) * mu + self.maint.of(name)

    @property
    def max_yield(self) -> float:
        """Biomass yield without maintenance, g DCW / g carbon source."""
        return self.bio.mw / (-self.growth.of(self.csource.name) * self.csource.mw)
