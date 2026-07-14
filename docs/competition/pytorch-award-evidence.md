# PyTorch award evidence

`ImpactTriageNet` emits non-evidence decision signals: risk, priority, review requirement, confidence, model version, and latency. Final award evidence should compare it against heuristic and LLM-only baselines using macro-F1, high-risk recall, calibration, p95 CPU latency, throughput, model size, ONNX parity, and workflow decisions changed.
