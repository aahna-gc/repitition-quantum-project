from shor_code.circuit_level_code import circuit_level_shor
from decoder import get_dem, parse_dem
from ml_enumerate import enumerate_ml_table, decode
 
 
def ml_logical_error_rate(p_gate, p_idle, p_measure, rounds, shots):
    circuit = circuit_level_shor(p_gate, p_idle, p_measure, rounds)
 
    dem = get_dem(circuit, decompose_errors=False)
    mechanisms = parse_dem(dem)
    print(f"  (k = {len(mechanisms)} error mechanisms at p_gate={p_gate})")
    ml_table = enumerate_ml_table(mechanisms)
 
    sampler = circuit.compile_detector_sampler()
    detector_bits, observable_bits = sampler.sample(
        shots=shots, separate_observables=True
    )
 
    fails = 0
    for shot in range(shots):
        fired_detectors = [i for i, bit in enumerate(detector_bits[shot]) if bit]
        predicted = decode(fired_detectors, ml_table)
        predicted_flip = 1 if 0 in predicted else 0
        true_flip = int(observable_bits[shot][0])
        if predicted_flip != true_flip:
            fails += 1
 
    return fails / shots
 
 
if __name__ == "__main__":
    SHOTS = 2000  # start small: raise once you know a p-value runs
    ROUNDS = 1    # start with 1 round: keeps k as small as possible
 
    noise_levels = [0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
 
    print(f"{'p_gate':>8} | {'ML fail rate':>13}")
    print("-" * 27)
    for p in noise_levels:
        rate = ml_logical_error_rate(
            p_gate=p, p_idle=p / 2, p_measure=p, rounds=ROUNDS, shots=SHOTS
        )
        print(f"{p:8.4f} | {rate:13.5f}")
