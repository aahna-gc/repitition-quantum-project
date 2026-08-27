import stim

def pheno_noise_shor(p_pheno):
    circuit = stim.Circuit()

    # Initialize all data qubits (0-8) and the ancilla qubit (9)
    circuit.append("R", range(10))

    # Encode a state as 3 qubits (layer 1)
    for q in [3, 6]:
        circuit.append("CX", [0, q])
        circuit.append("TICK")
    circuit.append("H", [0, 3, 6])
    circuit.append("TICK")

    # Concatenation (layer 2)
    blocks = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]

    ## First CX layer (to ensure parallelness)
    for control, target1, target2 in blocks:
        circuit.append("CX", [control, target1])
    circuit.append("TICK")

    ## Second CX layer
    for control, target1, target2 in blocks:
        circuit.append("CX", [control, target2])
    circuit.append("TICK")

    # Phenomenological noise
    circuit.append("DEPOLARIZE1", range(9), p_pheno)
    circuit.append("TICK")

    # Bit-flip (Z) stabilizers
    z_stabilizers = [
        (0, 1), (1, 2),
        (3, 4), (4, 5),
        (6, 7), (7, 8)
    ]

    for control1, control2 in z_stabilizers:
        # First CX layer
        circuit.append("CX", [control1, 9])
        circuit.append("TICK")

        # Second CX layer
        circuit.append("CX", [control2, 9])
        circuit.append("TICK")

        # Measurement
        circuit.append("MR", [9])
        circuit.append("DETECTOR", [stim.target_rec(-1)])
        circuit.append("TICK")

    # Phase-flip (X) stabilizers
    x_stabilizers = [
        (0, 1, 2, 3, 4, 5),
        (3, 4, 5, 6, 7, 8)
    ]

    for stabilizer in x_stabilizers:
        # First Hadamard layer
        circuit.append("H", stabilizer)
        circuit.append("TICK")

        # CX gates
        for control in stabilizer:
            circuit.append("CX", [control, 9])
            circuit.append("TICK")

        # Second Hadamard layer
        circuit.append("H", stabilizer)
        circuit.append("TICK")

        # Measurement
        circuit.append("MR", [9])
        circuit.append("DETECTOR", [stim.target_rec(-1)])
        circuit.append("TICK")

        return circuit