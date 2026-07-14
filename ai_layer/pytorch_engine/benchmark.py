import os
import time
import json
import torch
import numpy as np
from ai_layer.config import settings
from ai_layer.pytorch_engine.inference import get_triage_model

def run_benchmark(domain: str, runs: int = 100):
    print(f"\n==========================================")
    print(f"  BENCHMARKING PYTORCH ENGINE - DOMAIN: {domain.upper()}")
    print(f"==========================================\n")
    
    model = get_triage_model(domain)
    
    if not model:
        print("[Benchmark] Model not found. Train the model first.")
        return
        
    model.eval()
    
    # Inputs
    dummy_tab = torch.randn(1, 10, dtype=torch.float32)
    dummy_text = torch.randn(1, 384, dtype=torch.float32)
    
    # Warmup
    for _ in range(10):
        _ = model(dummy_tab, dummy_text)
        
    # Standard Latency Benchmark
    latencies = []
    for _ in range(runs):
        start = time.perf_counter()
        with torch.no_grad():
            _ = model(dummy_tab, dummy_text)
        latencies.append((time.perf_counter() - start) * 1000) # ms
        
    avg_latency = np.mean(latencies)
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    throughput = 1000.0 / avg_latency if avg_latency > 0 else 0
    
    # Try torch.compile optimization benchmark if torch>=2.0.0 is used and supported
    compiled_avg_latency = None
    try:
        if hasattr(torch, "compile"):
            print("[Benchmark] Compiling model with torch.compile...")
            compiled_model = torch.compile(model)
            # Warmup compilation
            _ = compiled_model(dummy_tab, dummy_text)
            
            compiled_latencies = []
            for _ in range(runs):
                start = time.perf_counter()
                with torch.no_grad():
                    _ = compiled_model(dummy_tab, dummy_text)
                compiled_latencies.append((time.perf_counter() - start) * 1000)
            compiled_avg_latency = np.mean(compiled_latencies)
            print(f"[Benchmark] Compiled Avg Latency: {compiled_avg_latency:.4f} ms")
    except Exception as e:
        print(f"[Benchmark] torch.compile not supported or failed: {e}")
        
    benchmark_results = {
        "domain": domain,
        "runs": runs,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "avg_latency_ms": round(avg_latency, 4),
        "p50_latency_ms": round(p50, 4),
        "p95_latency_ms": round(p95, 4),
        "p99_latency_ms": round(p99, 4),
        "throughput_fps": round(throughput, 2),
        "torch_compile_latency_ms": round(compiled_avg_latency, 4) if compiled_avg_latency else None
    }
    
    print("------------------------------------------")
    print(f"Benchmark Results:")
    for k, v in benchmark_results.items():
        print(f"  - {k}: {v}")
    print("------------------------------------------")
    
    # Save results
    save_path = settings.data_path(domain) / "benchmark.json"
    with open(save_path, "w") as f:
        json.dump(benchmark_results, f, indent=2)
    print(f"[Benchmark] Saved results to: {save_path}")
    
    return benchmark_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark triage model.")
    parser.add_argument("--domain", type=str, default="sme", choices=["sme", "education", "agriculture"])
    parser.add_argument("--runs", type=int, default=100)
    args = parser.parse_args()
    
    run_benchmark(args.domain, args.runs)
