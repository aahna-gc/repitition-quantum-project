from shor_code.circuit_level_code import circuit_level_shor
from shor_decoder.hard_decision_decoder import hard_decision_decode


def hard_decision_logical_error_rate(p_gate, p_idle, p_measure, rounds, shots):
    # Construct Chloe's circuit
    circuit = circuit_level_shor(p_gate, p_idle, p_measure, rounds)

    # Sample detectors and true logical observable values from Stim
    sampler = circuit.compile_detector_sampler()
    detector_bits, observable_bits = sampler.sample(
        shots=shots, separate_observables=True
    )

    # Run hard-decision majority-vote decoding over all sampled shots
    predicted_flips = hard_decision_decode(detector_bits)

    # Count mismatches between prediction and true observable
    fails = 0
    for shot in range(shots):
        predicted_flip = predicted_flips[shot, 0]
        true_flip = int(observable_bits[shot][0])
        if predicted_flip != true_flip:
            fails += 1

    return fails / shots


if __name__ == "__main__":
    SHOTS = 2000  # Matched to your ML sweep shot count
    ROUNDS = 1    # Matched to your ML sweep rounds

    noise_levels = [0.05, 0.02, 0.01, 0.005, 0.002, 0.001]

    print(f"{'p_gate':>8} | {'HD fail rate':>13}")
    print("-" * 27)
    for p in noise_levels:
        rate = hard_decision_logical_error_rate(
            p_gate=p, p_idle=p / 2, p_measure=p, rounds=ROUNDS, shots=SHOTS
        )
        print(f"{p:8.4f} | {rate:13.5f}")