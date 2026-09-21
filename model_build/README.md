# R39 canonical model builder

This directory owns the build-time path that will turn accepted temporary LALM behavior into a new canonical .§wyrlzx artifact.

`r39_model_builder.py` is the first gate: it reads the actual SWRLZX structure through the production R39 reader, inventories tensor/quantization topology and the consolidation corpus, and refuses to call anything a candidate until tensor bytes have genuinely changed and the artifact can be repacked with new integrity metadata.

This is intentionally separate from runtime-hot. Runtime-hot tests behavior; this builder promotes accepted behavior into the next model.

Current implementation status: **inspection/build-plan gate only**. Optimizer, requantization, SWRLZX writer/repacker, and equivalence gate remain to be implemented. Production is unchanged.
