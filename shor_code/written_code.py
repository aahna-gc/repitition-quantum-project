import stim

# Has circuit-level errors, not phenomenological noise.
# Do not use this version for tests; this purely exists for understanding.

def written_shor(p_gate, p_idle, p_measure):
    circuit = stim.Circuit(f'''
    # -- Initialize all data qubits (0-8) and the ancilla qubit (9) --

    R 0 1 2 3 4 5 6 7 8 9

    # -- Layer 1 --
    CX 0 3
    DEPOLARIZE2({p_gate}) 0 3
    DEPOLARIZE1({p_idle}) 1 2 4 5 6 7 8 9
    TICK

    CX 0 6
    DEPOLARIZE2({p_gate}) 0 6
    DEPOLARIZE1({p_idle}) 1 2 3 4 5 7 8 9
    TICK

    H 0 3 6
    DEPOLARIZE1({p_gate}) 0 3 6
    DEPOLARIZE1({p_idle}) 1 2 4 5 7 8 9
    TICK

    # -- Layer 2 --

    CX 0 1
    DEPOLARIZE2({p_gate}) 0 1
    CX 3 4
    DEPOLARIZE2({p_gate}) 3 4
    CX 6 7
    DEPOLARIZE2({p_gate}) 6 7
    DEPOLARIZE1({p_idle}) 2 5 8 9
    TICK

    CX 0 2
    DEPOLARIZE2({p_gate}) 0 2
    CX 3 5
    DEPOLARIZE2({p_gate}) 3 5
    CX 6 8
    DEPOLARIZE2({p_gate}) 6 8
    DEPOLARIZE1({p_idle}) 1 4 7 9
    TICK

    # -- Bit flip stabilizers --

    # Z0Z1
    ## Layer 1
    CX 0 9
    DEPOLARIZE2({p_gate}) 0 9
    DEPOLARIZE1({p_idle}) 1 2 3 4 5 6 7 8
    TICK

    ## Layer 2
    CX 1 9
    DEPOLARIZE2({p_gate}) 1 9
    DEPOLARIZE1({p_idle}) 0 2 3 4 5 6 7 8
    TICK

    ## Measurement
    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # Z1Z2
    ## Layer 1
    CX 1 9
    DEPOLARIZE2({p_gate}) 1 9
    DEPOLARIZE1({p_idle}) 0 2 3 4 5 6 7 8
    TICK

    ## Layer 2
    CX 2 9
    DEPOLARIZE2({p_gate}) 2 9
    DEPOLARIZE1({p_idle}) 0 1 3 4 5 6 7 8
    TICK

    ## Measurement
    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # Z3Z4
    ## Layer 1
    CX 3 9
    DEPOLARIZE2({p_gate}) 3 9
    DEPOLARIZE1({p_idle}) 0 1 2 4 5 6 7 8
    TICK

    ## Layer 2
    CX 4 9
    DEPOLARIZE2({p_gate}) 4 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 5 6 7 8
    TICK

    ## Measurement
    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # Z4Z5
    ## Layer 1
    CX 4 9
    DEPOLARIZE2({p_gate}) 4 9
    DEPOLARIZE1({p_idle}) 0 1 2 3  5 6 7 8
    TICK

    ## Layer 2
    CX 5 9
    DEPOLARIZE2({p_gate}) 5 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 6 7 8
    TICK

    ## Measurement
    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # Z6Z7
    ## Layer 1
    CX 6 9
    DEPOLARIZE2({p_gate}) 6 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 7 8
    TICK

    ## Layer 2
    CX 7 9
    DEPOLARIZE2({p_gate}) 7 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 6 8
    TICK

    ## Measurement
    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # Z7Z8
    ## Layer 1
    CX 7 9
    DEPOLARIZE2({p_gate}) 7 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 6 8
    TICK

    ## Layer 2
    CX 8 9
    DEPOLARIZE2({p_gate}) 8 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 6 7
    TICK

    ## Measurement
    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # -- Phase flip stabilizers --

    # X0X1X2X3X4X5
    H 0 1 2 3 4 5
    DEPOLARIZE1({p_gate}) 0 1 2 3 4 5
    DEPOLARIZE1({p_idle}) 6 7 8 9
    TICK

    CX 0 9
    DEPOLARIZE2({p_gate}) 0 9
    DEPOLARIZE1({p_idle}) 1 2 3 4 5 6 7 8
    TICK

    CX 1 9
    DEPOLARIZE2({p_gate}) 1 9
    DEPOLARIZE1({p_idle}) 0 2 3 4 5 6 7 8
    TICK

    CX 2 9
    DEPOLARIZE2({p_gate}) 2 9
    DEPOLARIZE1({p_idle}) 0 1 3 4 5 6 7 8
    TICK

    CX 3 9
    DEPOLARIZE2({p_gate}) 3 9
    DEPOLARIZE1({p_idle}) 0 1 2 4 5 6 7 8
    TICK

    CX 4 9
    DEPOLARIZE2({p_gate}) 4 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 5 6 7 8
    TICK

    CX 5 9
    DEPOLARIZE2({p_gate}) 5 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 6 7 8
    TICK

    H 0 1 2 3 4 5
    DEPOLARIZE1({p_gate}) 0 1 2 3 4 5
    DEPOLARIZE1({p_idle}) 6 7 8 9
    TICK

    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK

    # X3X4X5X6X7X8
    H 3 4 5 6 7 8
    DEPOLARIZE1({p_gate}) 3 4 5 6 7 8
    DEPOLARIZE1({p_idle}) 0 1 2 9
    TICK

    CX 3 9
    DEPOLARIZE2({p_gate}) 3 9
    DEPOLARIZE1({p_idle}) 0 1 2 4 5 6 7 8
    TICK

    CX 4 9
    DEPOLARIZE2({p_gate}) 4 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 5 6 7 8
    TICK

    CX 5 9
    DEPOLARIZE2({p_gate}) 5 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 6 7 8
    TICK

    CX 6 9
    DEPOLARIZE2({p_gate}) 6 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 7 8
    TICK

    CX 7 9
    DEPOLARIZE2({p_gate}) 7 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 6 8
    TICK

    CX 8 9
    DEPOLARIZE2({p_gate}) 8 9
    DEPOLARIZE1({p_idle}) 0 1 2 3 4 5 6 7
    TICK

    H 3 4 5 6 7 8
    DEPOLARIZE1({p_gate}) 3 4 5 6 7 8
    DEPOLARIZE1({p_idle}) 0 1 2 9
    TICK

    X_ERROR({p_measure}) 9
    MR 9
    DETECTOR rec[-1]
    TICK
    '''
    )