"""
1. 	     phenomenological vs. circuit-level noise
             Builds the *same* repetition-code memory experiment under both
             noise models and shows how the resulting circuits/detector
             error models differ. This matters for us because our final
             Shor-code benchmark (Chloe's Aug 25 circuit) needs to declare
             up front which noise model it uses -- the project spec calls
             for a "code-capacity noise model", which is the simplest
             cousin of the phenomenological model (single-shot noise on
             data qubits only, perfect measurement/syndrome extraction).

2.          pymatching as a reference decoder
             pymatching implements minimum-weight perfect matching (MWPM)
             decoding against a detector error model. It's NOT the
             brute-force ML decoder our project needs (MWPM approximates
             ML and only works cleanly for graphlike, e.g. repetition/
             surface-code-like, error models) -- but it's a fast, trusted,
             well-tested reference point for "what does a good decoder's
             logical error rate look like" while Aahna builds the exact
             brute-force ML decoder.

"""

import stim
import pymatching
import numpy as np


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# part 1. noise models

def code_capacity_circuit(distance: int, p: float) -> stim.Circuit:
    """The simplest noise model: one shot of iid noise on each data qubit,
    then a SINGLE, PERFECT round of syndrome extraction. No measurement
    error, no multi-round repetition. This is the model our Shor-code
    benchmark project actually uses, so it's the one to get comfortable
    with first."""
    circuit = stim.Circuit()
    data = list(range(distance))
    ancilla = list(range(distance, 2 * distance - 1))

    circuit.append("R", data + ancilla)
    circuit.append("X_ERROR", data, p)  # <-- the only noise in the whole circuit
    for i, a in enumerate(ancilla):
        circuit.append("CNOT", [data[i], a, data[i + 1], a])
    circuit.append("M", ancilla)
    for i in range(len(ancilla)):
        circuit.append("DETECTOR", [stim.target_rec(-(len(ancilla) - i))])
    circuit.append("M", data)
    obs_targets = [stim.target_rec(-(distance - i)) for i in range(distance)]
    circuit.append("OBSERVABLE_INCLUDE", obs_targets, 0)
    return circuit


def phenomenological_circuit(distance: int, rounds: int, p: float) -> stim.Circuit:
    """Phenomenological model: noise on data qubits AND noisy syndrome
    measurements, repeated over multiple rounds. Closer to a real device,
    strictly more complex than code-capacity. We build it here purely so
    we can see, side by side, what "more realistic" costs you in circuit
    complexity and detector count."""
    circuit = stim.Circuit()
    data = list(range(distance))
    ancilla = list(range(distance, 2 * distance - 1))

    circuit.append("R", data + ancilla)
    for r in range(rounds):
        circuit.append("X_ERROR", data, p)          # data-qubit noise, each round
        circuit.append("X_ERROR", ancilla, p)        # measurement-adjacent noise
        for i, a in enumerate(ancilla):
            circuit.append("CNOT", [data[i], a, data[i + 1], a])
        circuit.append("M", ancilla)
        if r == 0:
            for i in range(len(ancilla)):
                circuit.append("DETECTOR", [stim.target_rec(-(len(ancilla) - i))])
        else:
            # compare this round's ancilla parity to the previous round's
            for i in range(len(ancilla)):
                off = len(ancilla) - i
                circuit.append(
                    "DETECTOR",
                    [stim.target_rec(-off), stim.target_rec(-off - len(ancilla))],
                )
        circuit.append("TICK")

    circuit.append("M", data)
    obs_targets = [stim.target_rec(-(distance - i)) for i in range(distance)]
    circuit.append("OBSERVABLE_INCLUDE", obs_targets, 0)
    return circuit


def part_a_compare_noise_models() -> None:
    section("PART A: code-capacity vs. phenomenological noise models")

    d, p = 3, 0.1
    cc = code_capacity_circuit(d, p)
    ph = phenomenological_circuit(d, rounds=3, p=p)

    cc_dem = cc.detector_error_model()
    ph_dem = ph.detector_error_model()

    print(f"Code-capacity circuit  : {cc.num_detectors} detectors, "
          f"{len(cc)} instructions, {cc_dem.num_errors} distinct error mechanisms")
    print(f"Phenomenological circuit: {ph.num_detectors} detectors, "
          f"{len(ph)} instructions, {ph_dem.num_errors} distinct error mechanisms")
    print(
        "\nInterpretation: code-capacity has exactly one noisy step "
        "(perfect syndrome extraction), so its detector error model is "
        "small and static -- it's the right minimal setting for isolating "
        "decoder-vs-ML gaps, which is our project's actual goal. "
        "Phenomenological noise adds a temporal dimension (measurement "
        "errors + multiple rounds), which is more realistic but conflates "
        "decoder quality with syndrome-extraction noise -- not what we "
        "want for this experiment."
    )

#part 2. 

def part_b_pymatching_reference(trials: int = 20_000) -> None:
    section("PART B: pymatching (MWPM) as a reference decoder")

    d, p = 3, 0.1
    circuit = code_capacity_circuit(d, p)
    dem = circuit.detector_error_model()

    matcher = pymatching.Matching.from_detector_error_model(dem)

    sampler = circuit.compile_detector_sampler()
    detectors, observables = sampler.sample(
        shots=trials, separate_observables=True
    )

    predictions = matcher.decode_batch(detectors)
    predicted_obs = predictions.astype(bool).flatten()
    actual_obs = observables.astype(bool).flatten()

    logical_error_rate = np.mean(predicted_obs != actual_obs)
    print(f"Repetition code (d={d}, p={p}), {trials} trials")
    print(f"pymatching (MWPM) logical error rate: {logical_error_rate:.5f}")
    print(
        "\nNotes for the team:\n"
        "  - MWPM is exact/optimal for a single repetition or surface code "
        "(graphlike detector error model) but does NOT generalize cleanly "
        "to the concatenated 9-qubit Shor code's two-level structure -- "
        "that's exactly why our project needs a purpose-built brute-force "
        "ML decoder (Aahna) instead of just calling pymatching.\n"
        "  - We keep this script as a *sanity-check reference*: any decoder "
        "we build for a bare repetition code should track pymatching's "
        "logical error rate closely, since majority-vote is provably "
        "optimal there too (this is our project's 'zero-gap control')."
    )


def main() -> None:
    print(f"Stim version: {stim.__version__}, pymatching version: {pymatching.__version__}")
    part_a_compare_noise_models()
    part_b_pymatching_reference()


if __name__ == "__main__":
    main()
