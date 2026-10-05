# LLM_Token_Check
**What's the real capability-per-pound of consumer hardware running open-source
language models?**

This repo benchmarks a handful of open-source LLMs running locally via
[LM Studio](https://lmstudio.ai) on consumer-grade hardware (RTX 5060 Ti,
16GB VRAM) and reports what they can actually do - tokens/sec and VRAM usage
- as a cost-free alternative to commercial AI APIs for everyday tasks.

## Why

Sophisticated AI tooling is often assumed to require cloud infrastructure and
recurring subscription costs. This project tests that assumption directly: how
much genuinely useful capability is already sitting on hardware people own or
can buy secondhand for a few hundred pounds?

## Hardware

| Component | Spec |
|---|---|
| GPU | RTX 5060 Ti, 16GB VRAM |
| CPU | Ryzen 5 5600 |
| RAM | 32GB DDR4 |
| Approx. cost | £1000 (built/upgraded incrementally) |

## Models tested

| Model | Params | Use case |
|---|---|---|
| Qwen2.5-Coder 7B Instruct | 7B | Code generation |
| Gemma 4 e4b | ~4B (effective) | General / lightweight tasks |
| Qwen 3.5 9B | 9B | General reasoning |
| DeepSeek R1 Distill Qwen 14B | 14B | Reasoning |
| GPT-OSS 20B | 20B | Heavier tasks |

## Methodology

All models run locally via **LM Studio's Local Server** (OpenAI-compatible
  API at `http://localhost:1234`) - no cloud calls, no data leaving the
  machine.
**Note:** LM Studio serves one loaded model at a time, so each model was
  loaded manually in the LM Studio app before running the benchmark script,
  then swapped for the next.
- Each model given the same fixed set of 4 prompts: short Q&A, code
  generation, summarisation, and reasoning.
- Measured: tokens/sec (wall-clock based — LM Studio's API doesn't expose a
  generation-only timing figure the way some other local-inference tools do,
  so this includes minor request overhead) and peak VRAM usage.
  Each prompt run 3x, results averaged to reduce noise.
  Benchmark script: [`benchmark_lmstudio.py`](./benchmark_lmstudio.py).

## Results

| Model | Avg tokens/sec | Peak VRAM |
|---|---|---|
| Qwen2.5-Coder 7B Instruct | 26.9 | 12.8GB |
| Gemma 4 e4b | 56.1 | 7.8GB |
| Qwen 3.5 9B | 57.8 | 11.0GB |
| DeepSeek R1 Distill Qwen 14B | 34.0 | 11.1GB |
| GPT-OSS 20B | 42.0 | 15.4GB |

*(Figures are averages across all 4 prompt types, 3 runs each. Full per-prompt
breakdown in `results_lmstudio.csv`.)*

## Cost comparison

| Approach | Upfront cost | Estimated Ongoing cost | Data privacy |
|---|---|---|---|
| Local (this setup) | £1000 | £0/query | Fully local |
| OpenAI Budget tier (GPT-5.6 Luna)| £0 | £1.20/1M tokens | Sent to provider |
| Anthropic Budget (Haiku 4.5) | £0 | £4.00/1M tokens | 
| Google Budget (Gemini 3.5 Flash-Lite) | £0 | £2.00/1M tokens |

N.B. OpenAI's flagship is the most expensive at output ($30/M), while its budget tier (Luna) undercuts everyone at $0.20 input after a price cut that dropped OpenAI's flagship GPT-5.6 ladder to run from Luna at $0.20 per million input tokens to Sol at $5.00 per million input tokens.

Anthropic sits in the middle on flagship pricing and is currently the cheapest of the three on its mid-tier model - Sonnet 5 is priced at $2.00 input and $10.00 output per million tokens, described as the best price-to-performance ratio in the Claude lineup. Worth flagging: that's a temporary launch rate - it was originally due to rise to $3/$15 on 1 September 2026, though Anthropic has since confirmed the $2/$10 rate is now standard rather than a promo. 

Google's Gemini undercuts both on the budget tier - Gemini 3.5 Flash-Lite comes in at $0.30 input and $2.50 output per million tokens, and its mid-tier Flash model is priced below both OpenAI's and Anthropic's mid-tiers on output

## Reproducing this

1. Install [LM Studio](https://lmstudio.ai).
2. Load a model, then go to the **Local Server** tab and hit **Start Server**
   (default: `http://localhost:1234`).
3. Install Python deps: `pip install requests pynvml`
4. Edit `CURRENT_MODEL_LABEL` in `benchmark_lmstudio.py` to match the model
   you've loaded.
5. Run: `python benchmark_lmstudio.py`
6. Results append to `results_lmstudio.csv`. Load the next model in LM
   Studio, update the label, and re-run — repeat for each model tested.

## Takeaways

**Smaller isn't automatically slower.** Gemma 4 e4b, the smallest model
  tested at ~4B effective parameters, posted the best VRAM efficiency (7.8GB)
  and was competitive on speed with models more than double its size.
**Qwen 3.5 9B was the fastest overall** (~57.8 tok/s average), suggesting
  the sweet spot on this hardware sits closer to 7–9B than to 14–20B for
  everyday responsiveness.
**GPT-OSS 20B ran, but right at the card's limit** — ~15.4GB of the
  available 16GB. It's usable, but there's very little headroom left for
  longer context windows or running anything else alongside it.
  Overall: a 16GB consumer GPU comfortably runs the 7–14B range with room to
  spare, and can stretch to 20B models at the cost of most of the available
  VRAM headroom.

## About

Built as part of an ongoing interest in local AI deployment and reducing the
cost barrier to useful AI tooling.
