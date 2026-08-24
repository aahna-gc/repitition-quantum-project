# repitition-quantum-project
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
