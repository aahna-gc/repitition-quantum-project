# repitition-quantum-project

# tentative timeline
At a glance: \
Concatenated quantum error-correcting codes are conventionally decoded using fast, local hard-decision (majority-vote) rules applied level-by-level — a practical choice used throughout the concatenated-code literature, including recent high-rate constructions, precisely because exact maximum-likelihood (ML) decoding scales exponentially with qubit count. This practicality-driven choice comes at a known but rarely quantified cost: hard-decision decoding discards probabilistic information at each level that an optimal decoder would retain. We isolate and measure this decoder-induced gap directly on the canonical example of code concatenation: the 9-qubit Shor code, itself a phase-flip repetition code concatenated with a bit-flip repetition code. Using a code-capacity noise model, we compare three decoders: majority-vote decoding of a bare 3-qubit repetition code (a zero-gap control, since majority vote is provably optimal for a single repetition code), standard hard-decision level-by-level decoding of the full Shor code, and an exact brute-force ML decoder enumerating all possible error patterns. By holding the code and noise model fixed and varying only the decoder, we attribute the resulting difference in logical error rate entirely to decoder suboptimality rather than code structure — providing, on the most pedagogically standard concatenated code, a concrete answer to how much of concatenated codes' apparent disadvantage relative to more heavily-optimized decoders (e.g., surface-code matching) is a decoder limitation rather than an inherent property of concatenation itself.

# tentative timeline
checkmark for completion: ✓ \
timeline: \
Tue, Aug 18
+ Aahna: Install Stim; work through the official Stim getting-started tutorial (circuits, detectors, observables) + install requirements.txt ✓
+ Chloe: Install Stim; work through the official Stim getting-started tutorial (circuits, detectors, observables) + install requirements.txt ✓
+ Hyunmin: Install Stim; work through the official Stim getting-started tutorial (circuits, detectors, observables) + install requirements.txt ✓

Sun, Aug 23:
+ Aahna: Read up on Maximum Likelihood decoding theory for stabilizer codes — logical cosets, partition functions, degenerate error classes. ✓ Also: schedule emails to Deutsch and Shantanu
+ Chloe: Study the Shor [[9,1,3]] code in depth: stabilizer generators, encoding circuit, X/Z error correction structure. ✓
+ Hyunmin: Read Stim docs on phenomenological vs. circuit-level noise models; survey how Stim's built-in decoders (pymatching) work as a reference point.

Mon, Aug 24:
+ Aahna: Sketch pseudocode for a brute-force ML decoder: enumerate all logical cosets, sum error probabilities exactly from the detector error model. ✓
+ Chloe: Prototype a minimal (unencoded) Stim circuit for the Shor code to get comfortable with circuit syntax before fault-tolerant version.
+ Hyunmin: Investigate literature on local hard-decision majority-vote decoders for concatenated codes; note what “information loss” means at each layer.

Tues, Aug 25:
+ Aahna: Begin ML decoder skeleton: pull detector error model out of a Stim circuit via circuit.detector_error_model(). (make sure to let others know what filenames correlate to what)
+ Chloe: Build the fault-tolerant Shor code memory circuit under a phenomenological noise model in Stim. (make sure to let others know what filenames correlate to what)
+ Hyunmin: Build benchmarking harness scaffolding: experiment config schema, result logging (CSV/JSON), directory conventions. (make sure to let others know what filenames correlate to what)
