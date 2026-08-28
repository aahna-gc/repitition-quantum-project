import stim

def circuit_round(circuit, p_gate, p_idle, p_measure, first_round=False):
    # Z-stabilizers (bit-flip errors)
    z_stabilizers = [
        (0, 1), (1, 2),
        (3, 4), (4, 5),
        (6, 7), (7, 8)
    ]

    for control1, control2 in z_stabilizers:
        # First CX layer
        circuit.append("CX", [control1, 9])
        circuit.append("DEPOLARIZE2", [control1, 9], p_gate)
        idle = [q for q in range(10) if q not in {control1, 9}]
        circuit.append("DEPOLARIZE1", idle, p_idle)
        circuit.append("TICK")

        # Second CX layer
        circuit.append("CX", [control2, 9])
        circuit.append("DEPOLARIZE2", [control2, 9], p_gate)
        idle = [q for q in range(10) if q not in {control2, 9}]
        circuit.append("DEPOLARIZE1", idle, p_idle)
        circuit.append("TICK")

        # Measurement
        circuit.append("X_ERROR", [9], p_measure)
        circuit.append("MR", [9])
        circuit.append("DEPOLARIZE1", range(9), p_idle)

        # Measure parity for multi-round implementation
        if first_round:
            # No previous measurement to compare to.
            circuit.append("DETECTOR", [stim.target_rec(-1)])
        else:
            # Compare to same stabilizer from the previous round.
            circuit.append("DETECTOR", [stim.target_rec(-1), stim.target_rec(-9)])
        circuit.append("TICK")

    # X-stabilizers (phase-flip errors)
    x_stabilizers = [
        (0, 1, 2, 3, 4, 5),
        (3, 4, 5, 6, 7, 8)
    ]

    for stabilizer in x_stabilizers:
        # First Hadamard layer
        circuit.append("H", stabilizer)
        circuit.append("DEPOLARIZE1", stabilizer, p_gate)
        idle = [q for q in range(10) if q not in stabilizer]
        circuit.append("DEPOLARIZE1", idle, p_idle)
        circuit.append("TICK")

        # CX gates
        for control in stabilizer:
            circuit.append("CX", [control, 9])
            circuit.append("DEPOLARIZE2", [control, 9], p_gate)
            idle = [q for q in range(10) if q not in {control, 9}]
            circuit.append("DEPOLARIZE1", idle, p_idle)
            circuit.append("TICK")

        # Second Hadamard layer
        circuit.append("H", stabilizer)
        circuit.append("DEPOLARIZE1", stabilizer, p_gate)
        idle = [q for q in range(10) if q not in stabilizer]
        circuit.append("DEPOLARIZE1", idle, p_idle)
        circuit.append("TICK")

        # Measurement
        circuit.append("X_ERROR", [9], p_measure)
        circuit.append("MR", [9])
        circuit.append("DEPOLARIZE1", range(9), p_idle)

        # Measure parity for multi-round implementation
        if first_round:
            # No previous measurement to compare to.
            circuit.append("DETECTOR", [stim.target_rec(-1)])
        else:
            # Compare to same stabilizer from the previous round.
            circuit.append("DETECTOR", [stim.target_rec(-1), stim.target_rec(-9)])
        circuit.append("TICK")



def circuit_level_shor(p_gate, p_idle, p_measure, rounds):
    circuit = stim.Circuit()

    # Initialize all data qubits (0-8) and the ancilla qubit (9)
    circuit.append("R", range(10))

    # Encode a state as 3 qubits (layer 1)
    circuit.append("CX", [0, 3])
    circuit.append("DEPOLARIZE2", [0, 3], p_gate)
    circuit.append("DEPOLARIZE1", [1, 2, 4, 5, 6, 7, 8, 9], p_idle)
    circuit.append("TICK")

    circuit.append("CX", [0, 6])
    circuit.append("DEPOLARIZE2", [0, 6], p_gate)
    circuit.append("DEPOLARIZE1", [1, 2, 3, 4, 5, 7, 8, 9], p_idle)
    circuit.append("TICK")

    circuit.append("H", [0, 3, 6])
    circuit.append("DEPOLARIZE1", [0, 3, 6], p_gate)
    circuit.append("DEPOLARIZE1", [1, 2, 4, 5, 7, 8, 9], p_idle)
    circuit.append("TICK")

    # Concatenation (layer 2)
    blocks = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]

    ## First CX layer (to ensure parallelness)
    for control, target1, target2 in blocks:
        circuit.append("CX", [control, target1])
        circuit.append("DEPOLARIZE2", [control, target1], p_gate)
    circuit.append("DEPOLARIZE1", [2, 5, 8, 9], p_idle)
    circuit.append("TICK")

    ## Second CX layer
    for control, target1, target2 in blocks:
        circuit.append("CX", [control, target2])
        circuit.append("DEPOLARIZE2", [control, target2], p_gate)
    circuit.append("DEPOLARIZE1", [1, 4, 7, 9], p_idle)
    circuit.append("TICK")

    # Run multiple QEC rounds
    for runs in range(rounds):
        circuit_round(circuit, p_gate, p_idle, p_measure, first_round=(runs==0))
    return circuit