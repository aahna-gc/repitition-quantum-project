# ConiQ-QEC
reference paper link: https://arxiv.org/abs/2508.05779
 # timeline
 Mon Aug 17
+ Aahna: Read ConiQ §II-B (QEC basics,  code, Table I logical operators) and §V (AHA scheme) closely. Write out by hand: the  code’s stabilizers, its 4 logical operators, and the automorphism-based SWAP/CNOT from Fig. 6a-b. This is your ground truth for correctness checks later.
+ Chloe: Read ConiQ §II-A (physical instruction set) and §VI-A (VAIR definition) closely. Start the physical-layer simulator: a Python class representing the state tuple (I, J, A, S) from §II-A, with Trans_a_to_s, Trans_s_to_a, Mov, 1Qgate, ParallelCZ as methods, enforcing the order-preserving and row-column constraints.
+ Hyunmin: Pull 2-3 magic-state distillation protocols (15-to-1, small-angle) with concrete input-copy counts and output-infidelity formulas. Set up the repo skeleton (folders: physical/, gadgets/, vair/, simulator/, benchmarks/) so everyone commits into a shared structure from day one.
