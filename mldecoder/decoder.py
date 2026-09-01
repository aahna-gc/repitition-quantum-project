import stim
from ml_enumerate import enumerate_ml_table, decode
 #hi lol 
 
def get_dem(circuit: "stim.Circuit", decompose_errors: bool = True):

    return circuit.detector_error_model(decompose_errors=decompose_errors)
 
 
def parse_dem(dem: "stim.DetectorErrorModel"):

    mechanisms = []
 
    for instruction in dem.flattened():
        # .flattened() expands repeat blocks and resolves shift_detectors
        # offsets, so we can iterate a flat instruction list
        if instruction.type != "error":
            continue
 
        probability = instruction.args_copy()[0]
        detector_indices = set()
        observable_indices = set()
 
        for target in instruction.targets_copy():
            if target.is_relative_detector_id():
                detector_indices.add(target.val)
            elif target.is_logical_observable_id():
                observable_indices.add(target.val)
            # separator targets (for decomposed multi-part errors) are
            # skipped here
 
        mechanisms.append(
            (probability, frozenset(detector_indices), frozenset(observable_indices))
        )
 
    return mechanisms
 
 
def num_detectors_and_observables(dem: "stim.DetectorErrorModel"):
    return dem.num_detectors, dem.num_observables
 
 
if __name__ == "__main__":
    # Smoke-test target: a small repetition-code circuit first (the
    # bare-repetition-code control from shor_decoder_gap.py), since it's
    # the simplest circuit Stim can generate directly. Swap in the actual
    # Shor-code circuit later.
    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=1,
        distance=3,
        after_clifford_depolarization=0.05,
    )
 
    dem = get_dem(circuit, decompose_errors=False)
    mechanisms = parse_dem(dem)

    ml_table = enumerate_ml_table(mechanisms)
    print(f"\nbuilt table over {len(ml_table)} distinct syndromes")
 
    n_det, n_obs = num_detectors_and_observables(dem)
    print(f"detectors: {n_det}, observables: {n_obs}")
    print(f"parsed {len(mechanisms)} error mechanisms")
    for p, dets, obs in mechanisms[:10]:
        print(f"  p={p:.5f}  detectors={sorted(dets)}  observables={sorted(obs)}")
