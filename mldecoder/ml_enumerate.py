from collections import defaultdict
from itertools import product


def enumerate_ml_table(mechanisms, verbose=False):

    k = len(mechanisms)
    if k > 24:
        raise ValueError(
            f"{k} mechanisms -> 2^{k} subsets is not brute-forceable here. "
            "This decoder is only intended for small testbeds (e.g. the "
            "9-mechanism Shor-code bit-flip sector)."
        )

    # (syndrome, logical_class) -> accumulated probability mass
    coset_mass = defaultdict(lambda: defaultdict(float))

    for bits in product((0, 1), repeat=k):
        prob = 1.0
        detector_acc = frozenset()
        logical_acc = frozenset()

        for on, (p, dets, obs) in zip(bits, mechanisms):
            if on:
                prob *= p
                # XOR: symmetric difference toggles which detectors/
                # observables are currently flipped as mechanisms combine
                detector_acc = detector_acc.symmetric_difference(dets)
                logical_acc = logical_acc.symmetric_difference(obs)
            else:
                prob *= (1.0 - p)

        coset_mass[detector_acc][logical_acc] += prob

    # argmax over logical classes, per syndrome
    ml_table = {}
    for syndrome, classes in coset_mass.items():
        best_class = max(classes.items(), key=lambda kv: kv[1])[0]
        ml_table[syndrome] = best_class
        if verbose:
            print(f"syndrome={sorted(syndrome)}: "
                  f"{ {tuple(sorted(c)): round(m, 6) for c, m in classes.items()} } "
                  f"-> predicted {sorted(best_class)}")

    return ml_table


def decode(observed_detectors, ml_table, default=frozenset()):
    syndrome = frozenset(observed_detectors)
    return ml_table.get(syndrome, default)


if __name__ == "__main__":
    # Smoke test using the ACTUAL 9 mechanisms captured from
    # decoder.py run against the distance-3 repetition-code circuit
    # (detectors: 4, observables: 1). this is reusing real output rather than
    # re-deriving synthetic numbers, so this exercises the real DEM shape
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
