"""Fermentation mass balance and sizing.

Inputs: annual output of pure protein (t/yr), titer (g/L), overall DSP
recovery, batch and turnaround times, fermenter working volume.
Outputs: broth volume per year, number of fermenters, sugar demand.

Equations
  protein_in_broth [kg/yr] = output / recovery
  broth [m3/yr]            = protein_in_broth / titer          (g/L == kg/m3)
  batches/yr per vessel    = operating_hours / (batch_time + turnaround)
  n_fermenters             = ceil(broth / (working_volume * batches_per_vessel))
  sugar [kg/yr]            = protein_in_broth / yield
"""
import math
from dataclasses import dataclass


@dataclass
class UpstreamResult:
    protein_in_broth_kg: float
    broth_m3: float
    batches_per_vessel: float
    n_fermenters: int
    total_working_volume_m3: float
    sugar_kg: float


def run(p: dict, overall_recovery: float) -> UpstreamResult:
    plant, strain, ferm = p["plant"], p["strain"], p["fermenter"]
    output_kg = plant["annual_output_t"] * 1000 * plant["purity_target"]
    protein_in_broth = output_kg / overall_recovery
    broth = protein_in_broth / strain["titer_g_per_L"]
    batches = plant["operating_hours"] / (strain["batch_time_h"] + strain["turnaround_h"])
    n = math.ceil(broth / (ferm["working_volume_m3"] * batches))
    sugar = protein_in_broth / strain["yield_g_per_g_sugar"]
    return UpstreamResult(protein_in_broth, broth, batches, n,
                          n * ferm["working_volume_m3"], sugar)
