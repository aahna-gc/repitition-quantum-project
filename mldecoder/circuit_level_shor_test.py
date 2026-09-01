
# ________________________
# HI PLEASE READ
# DO NOT MISS THIS
# PLS READ THIS
# !!!!!!!!!!!!!!!!!!!!
# **TO RUN THIS: put the following in terminal after environment has been activated etc:**
# cd .. 
# cd repitition-quantum-project
# python -m pytest mldecoder/circuit_level_shor_test.py -v
# ****RUN EACH LINE SEPERATELY TO RUN THE TESTS,
# this is just because the shor circuit is in a different folder than this test.
# !!!!!!!!!!!
# __________________________


# ---------------------------------------------------------------------
# Group 1 pipeline compatibility and hand-derivable structure
# ---------------------------------------------------------------------


import pytest
from shor_code.circuit_level_code import circuit_level_shor
from decoder import get_dem, parse_dem
from ml_enumerate import enumerate_ml_table


def test_zero_noise_has_no_error_mechanisms():
    circuit = circuit_level_shor(p_gate=0.0, p_idle=0.0, p_measure=0.0, rounds=1)
    dem = get_dem(circuit, decompose_errors=False)
    mechanisms = parse_dem(dem)
    assert mechanisms == [], (
        f"expected no error mechanisms at zero noise, got {len(mechanisms)}"
    )
 
 
@pytest.mark.parametrize("rounds,expected_detectors", [(1, 8), (2, 16), (3, 24)])
def test_detector_count_matches_stabilizer_count(rounds, expected_detectors):
    circuit = circuit_level_shor(p_gate=0.01, p_idle=0.005, p_measure=0.01,
                                  rounds=rounds)
    dem = get_dem(circuit, decompose_errors=False)
    n_det, n_obs = dem.num_detectors, dem.num_observables
    assert n_det == expected_detectors, (
        f"rounds={rounds}: expected {expected_detectors} detectors "
        f"(8 per round), got {n_det}"
    )
 
 
def test_dem_extraction_runs_on_real_circuit():
    circuit = circuit_level_shor(p_gate=0.01, p_idle=0.005, p_measure=0.01,
                                  rounds=1)
    dem = get_dem(circuit, decompose_errors=False)
    mechanisms = parse_dem(dem)
    assert len(mechanisms) > 0, "expected nonzero error mechanisms at p>0"
 
 
def test_ml_table_builds_without_crashing_on_real_circuit():
   
    circuit = circuit_level_shor(p_gate=0.01, p_idle=0.005, p_measure=0.01,
                                  rounds=1)
    dem = get_dem(circuit, decompose_errors=False)
    mechanisms = parse_dem(dem)
    print(f"\nk = {len(mechanisms)} error mechanisms for rounds=1")
    ml_table = enumerate_ml_table(mechanisms)
    assert len(ml_table) > 0
 
 
# ---------------------------------------------------------------------
# Group 2: PLACEHOLDER !!!!
# ---------------------------------------------------------------------
 
@pytest.mark.skip(
    reason=(
        "BLOCKED: circuit_level_shor has no OBSERVABLE_INCLUDE, so "
        "detector_error_model() reports 0 logical observables. Cannot "
        "validate ML decoder predictions against known Shor-code error "
        "patterns (e.g. 'a single-qubit error should never flip the "
        "logical value') until Chloe adds a final logical measurement + "
        "OBSERVABLE_INCLUDE to the circuit. Raise with Chloe/team before "
        "un-skipping this."
    )
)
def test_known_single_qubit_error_does_not_flip_logical():
    """NOTE NOTE NOTE READ THIS: Once a logical observable exists: inject a single data-qubit error
    (e.g. via an explicit X on qubit 0 before the first round, or by
    checking mechanisms with weight-1 support) and confirm the ML
    decoder's predicted logical class matches 'no logical flip'"""
    pytest.skip("see BLOCKED reason above")
