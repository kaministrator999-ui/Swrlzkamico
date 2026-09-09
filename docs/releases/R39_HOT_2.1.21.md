# Hot R39 2.1.21

Server 2.2.3 fixed native fp16 subnormal scaling, bringing native vocabulary logits into float-noise agreement with the Python reference. Hot 2.1.21 keeps live reference validation but reduces per-token rerank work from 48 candidates to the top 6 selection frontier, preserving diagnostics while trimming decode overhead. Prefill diagnostics now label intentionally skipped logits as skipped rather than NaN-looking output.
