# ----------
# if you are not sure what folder you're in:
# run this command!
# cd ~/Documents/GitHub/repitition-quantum-project/mldecoder && python ml_enumerate.py
# you're welcome
# ___________


from collections import defaultdict
import numpy as np


def enumerate_ml_table(mechanisms, verbose=False):
    k = len(mechanisms)
    if k > 24:
        raise ValueError(
            f"{k} mechanisms -> 2^{k} subsets is not brute-forceable here. "
            "This decoder is only intended for small testbeds (e.g. the "
            "9-mechanism Shor-code bit-flip sector)."
        )

    # bit-pack each mechanism's detector/observable pattern into an
    # integer mask so the enumeration can run as numpy array ops
    det_masks = np.array(
        [sum(1 << d for d in dets) for _, dets, _ in mechanisms], dtype=np.uint64
    )
    obs_masks = np.array(
        [sum(1 << o for o in obs) for _, _, obs in mechanisms], dtype=np.uint64
    )
    probs = np.array([p for p, _, _ in mechanisms], dtype=np.float64)

    # doubling construction ---> grow the off and on branches for each
    # mechanism in turn, vectorized across all subsets built so far,
    # instead of recomputing every subset from scratch in a loop (bc that would suck)
    syndromes = np.zeros(1, dtype=np.uint64)
    logicals = np.zeros(1, dtype=np.uint64)
    weights = np.ones(1, dtype=np.float64)

    for i in range(k):
        p = probs[i]
        weights_off = weights * (1.0 - p)
        weights_on = weights * p
        syndromes_on = syndromes ^ det_masks[i]
        logicals_on = logicals ^ obs_masks[i]

        syndromes = np.concatenate([syndromes, syndromes_on])
        logicals = np.concatenate([logicals, logicals_on])
        weights = np.concatenate([weights_off, weights_on])

    # group by (syndrome, logical) pair and sum probability mass
    # combined integer key + np.unique/np.bincount instead of a Python
    # dict-of-dicts accumulator
    logical_bits = max(int(logicals.max()).bit_length() if logicals.size else 0, 1)
    combined = (syndromes << np.uint64(logical_bits)) | logicals

    unique_keys, inverse = np.unique(combined, return_inverse=True)
    mass = np.bincount(inverse, weights=weights)

    unique_logicals = (unique_keys & np.uint64((1 << logical_bits) - 1)).astype(np.int64)
    unique_syndromes = (unique_keys >> np.uint64(logical_bits)).astype(np.int64)

    # argmax logical class per syndrome
    order = np.argsort(unique_syndromes, kind="stable")
    sorted_syn = unique_syndromes[order]
    sorted_log = unique_logicals[order]
    sorted_mass = mass[order]

    def mask_to_frozenset(mask):
        return frozenset(i for i in range(mask.bit_length()) if mask & (1 << i))

    # collect all (logical, mass) pairs per syndrome for verbose printing,
    # matching the original's per-syndrome debug output
    per_syndrome_classes = defaultdict(dict) if verbose else None

    ml_table = {}
    i, n = 0, len(sorted_syn)
    while i < n:
        j = i
        best_mass, best_logical = -1.0, 0
        cur_syn = int(sorted_syn[i])
        while j < n and sorted_syn[j] == cur_syn:
            logical_val = int(sorted_log[j])
            mass_val = float(sorted_mass[j])
            if verbose:
                per_syndrome_classes[cur_syn][logical_val] = mass_val
            if mass_val > best_mass:
                best_mass, best_logical = mass_val, logical_val
            j += 1
        syndrome_fs = mask_to_frozenset(cur_syn)
        best_class_fs = mask_to_frozenset(best_logical)
        ml_table[syndrome_fs] = best_class_fs
        if verbose:
            classes_display = {
                tuple(sorted(mask_to_frozenset(lg))): round(m, 6)
                for lg, m in per_syndrome_classes[cur_syn].items()
            }
            print(f"syndrome={sorted(syndrome_fs)}: {classes_display} "
                  f"-> predicted {sorted(best_class_fs)}")
        i = j

    return ml_table


def decode(observed_detectors, ml_table, default=frozenset()):
    syndrome = frozenset(observed_detectors)
    return ml_table.get(syndrome, default)


if __name__ == "__main__":
    # Smoke test using the actual 9 mechanisms captured from
    # decoder.py run against the distance-3 repetition-code circuit
    # (detectors: 4, observables: 1).
    # this is reusing real output rather than
    # re-deriving synthetic numbers --> real DEM shape
    mechanisms = [
        (0.01352, frozenset({0}),    frozenset()),
        (0.01352, frozenset({0, 1}), frozenset()),
        (0.02667, frozenset({0, 2}), frozenset()),
        (0.02667, frozenset({0, 3}), frozenset()),
        (0.02667, frozenset({1, 3}), frozenset()),
        (0.01352, frozenset({1}),    frozenset({0})),
        (0.01352, frozenset({2}),    frozenset()),
        (0.01352, frozenset({2, 3}), frozenset()),
        (0.01352, frozenset({3}),    frozenset({0})),
    ]

    ml_table = enumerate_ml_table(mechanisms, verbose=True)

    print(f"\nbuilt table over {len(ml_table)} distinct syndromes "
          f"(out of {2**len(mechanisms)} subsets enumerated)")

    # sanity check: no detectors fired -> should predict no logical flip
    assert decode([], ml_table) == frozenset(), \
        "empty syndrome should decode to no logical flip"
    print("sanity check passed: empty syndrome -> no logical flip")
