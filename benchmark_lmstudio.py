"""
benchmark_lmstudio.py

Benchmarks models loaded in LM Studio's Local Server (OpenAI-compatible API)
on tokens/sec (wall-clock based) and peak VRAM usage, across a fixed set of
prompts. Writes results to results_lmstudio.csv.

IMPORTANT: LM Studio only serves whichever model is currently loaded in the
Local Server tab. This script benchmarks ONE model per run — load the model
in LM Studio first, then run this script, then repeat for the next model.

Requirements:
    pip install requests pynvml

Usage:
    1. Open LM Studio -> Local Server tab -> load a model -> Start Server
       (default: http://localhost:1234)
    2. Edit CURRENT_MODEL_LABEL below to match whatever you just loaded
       (just a label for your results.csv - doesn't need to match exactly)
    3. python benchmark_lmstudio.py
    4. Repeat for each model you want to test - results append to the same CSV.
"""

import csv
import os
import time
import requests
from statistics import mean

try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
    GPU_HANDLE = pynvml.nvmlDeviceGetHandleByIndex(0)
except Exception:
    GPU_AVAILABLE = False
    print("Warning: pynvml not available or no NVIDIA GPU detected. "
          "VRAM stats will be skipped.")

LMSTUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Label for whichever model you have loaded in LM Studio right now.
# Edit this before each run - it's just for the CSV, doesn't need to be exact.
CURRENT_MODEL_LABEL = "openai/gpt-oss-20b"

PROMPTS = {
    "short_qa": "What is the capital of France, and what is it known for? Answer in 2-3 sentences.",
    "code_gen": "Write a Python function that returns the nth Fibonacci number using memoisation.",
    "summarisation": (
        "Summarise the following in 2 sentences: Local large language models "
        "run entirely on a user's own hardware rather than a remote server. "
        "This means no data leaves the machine, there are no per-query costs, "
        "and performance is bounded by the user's own GPU and RAM rather than "
        "a shared cloud service. The trade-off is that consumer hardware "
        "typically cannot match the largest cloud-hosted models on raw capability."
    ),
    "reasoning": (
        "A farmer has 17 sheep. All but 9 die. How many sheep does the farmer "
        "have left? Explain your reasoning briefly."
    ),
}

RUNS_PER_PROMPT = 3
RESULTS_FILE = "results_lmstudio.csv"


def get_vram_used_mb():
    if not GPU_AVAILABLE:
        return None
    info = pynvml.nvmlDeviceGetMemoryInfo(GPU_HANDLE)
    return info.used / (1024 ** 2)


def run_single_generation(prompt):
    """Sends one chat completion request to LM Studio and times it."""
    payload = {
        "model": CURRENT_MODEL_LABEL,  # LM Studio ignores this if only one model is loaded
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "stream": False,
    }

    vram_before = get_vram_used_mb()
    start = time.perf_counter()
    response = requests.post(LMSTUDIO_URL, json=payload, timeout=300)
    end = time.perf_counter()
    vram_after = get_vram_used_mb()

    response.raise_for_status()
    data = response.json()

    usage = data.get("usage", {})
    completion_tokens = usage.get("completion_tokens", 0)
    wall_clock_s = end - start

    # LM Studio doesn't give a generation-only duration like Ollama does,
    # so tokens/sec here is based on total wall-clock time (includes any
    # prompt processing / network overhead - slightly conservative).
    tokens_per_sec = completion_tokens / wall_clock_s if wall_clock_s > 0 else 0

    return {
        "tokens_per_sec": tokens_per_sec,
        "wall_clock_s": wall_clock_s,
        "completion_tokens": completion_tokens,
        "vram_before_mb": vram_before,
        "vram_after_mb": vram_after,
    }


def benchmark_current_model():
    print(f"\n=== Benchmarking {CURRENT_MODEL_LABEL} (via LM Studio) ===")
    model_results = []

    for prompt_name, prompt_text in PROMPTS.items():
        run_metrics = []
        for run_num in range(1, RUNS_PER_PROMPT + 1):
            print(f"  [{prompt_name}] run {run_num}/{RUNS_PER_PROMPT}...", end=" ")
            try:
                metrics = run_single_generation(prompt_text)
                run_metrics.append(metrics)
                print(f"{metrics['tokens_per_sec']:.1f} tok/s")
            except Exception as e:
                print(f"FAILED ({e})")

        if run_metrics:
            avg_tps = mean(m["tokens_per_sec"] for m in run_metrics)
            avg_vram = mean(
                m["vram_after_mb"] for m in run_metrics if m["vram_after_mb"] is not None
            ) if GPU_AVAILABLE else None

            model_results.append({
                "model": CURRENT_MODEL_LABEL,
                "prompt": prompt_name,
                "avg_tokens_per_sec": round(avg_tps, 2),
                "avg_vram_mb": round(avg_vram, 1) if avg_vram is not None else "N/A",
                "runs": len(run_metrics),
            })

    return model_results


def main():
    results = benchmark_current_model()

    file_exists = os.path.isfile(RESULTS_FILE)
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["model", "prompt", "avg_tokens_per_sec", "avg_vram_mb", "runs"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Results appended to {RESULTS_FILE}")
    print("Load the next model in LM Studio, update CURRENT_MODEL_LABEL, and re-run.")


if __name__ == "__main__":
    main()
