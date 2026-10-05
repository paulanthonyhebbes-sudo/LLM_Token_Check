# LLM_Token_Check

**How fast do open-source language models run on consumer hardware, how much GPU memory do they need, and how does running them locally compare with paying for a commercial API?**

This repo benchmarks five open-source LLMs running locally through [LM Studio](https://lmstudio.ai) on a consumer PC with an RTX 5060 Ti (16 GB VRAM). It measures generation speed (tokens per second) and peak VRAM use, then sets the hardware cost against current API pricing.

It measures speed and memory, not answer quality. The results show what this hardware can run comfortably, not how good each model's answers are.

---

## Why

Useful AI tooling is often assumed to need cloud infrastructure and ongoing subscription costs. This project tests that assumption: what can hardware that people already own, or can buy second-hand, run locally at a usable speed?

---

## Hardware

| Component | Spec |
|---|---|
| GPU | RTX 5060 Ti, 16 GB VRAM |
| CPU | Ryzen 7 7800X3D |
| RAM | 64 GB DDR4 |
| Approximate cost | £1,800 (built and upgraded over time) |

---

## Models tested

| Model | Parameters | Use case |
|---|---|---|
| Qwen2.5-Coder 7B Instruct | 7B | Code generation |
| Gemma 4 E4B | ~4.5B effective | General and lightweight tasks |
| Qwen 3.5 9B | 9B | General reasoning |
| DeepSeek R1 Distill Qwen 14B | 14B | Reasoning |
| GPT-OSS 20B | 21B total, 3.6B active (mixture-of-experts) | Heavier tasks |

A mixture-of-experts model holds all its parameters in memory but uses only a subset of them for each token. This is why GPT-OSS 20B needs a lot of VRAM but can still generate text quickly.

---

## Methodology

- All models ran locally through LM Studio's local server (OpenAI-compatible API at `http://localhost:1234`). No cloud calls were made and no data left the machine.
- LM Studio serves one model at a time. Each model was loaded manually in the LM Studio app before running the benchmark script, then swapped for the next.
- Every model received the same four prompts: short Q&A, code generation, summarisation and reasoning.
- Each prompt was run three times and the results averaged to reduce noise. The one exception is the reasoning prompt for Qwen 3.5 9B, which was run once.
- **Tokens per second** is measured by wall-clock time. LM Studio's API does not expose a generation-only timing figure, so the result includes some request overhead.
- **Peak VRAM** is the highest GPU memory use recorded during the runs.
- Benchmark script: [`benchmark_lmstudio.py`](./benchmark_lmstudio.py)

---

## Results

| Model | Avg tokens/sec | Peak VRAM |
|---|---|---|
| Qwen2.5-Coder 7B Instruct | 26.9 | 12.8 GB |
| Gemma 4 E4B | 56.1 | 7.8 GB |
| Qwen 3.5 9B | 56.4 | 11.0 GB |
| DeepSeek R1 Distill Qwen 14B | 34.0 | 11.1 GB |
| GPT-OSS 20B | 42.0 | 15.4 GB |

Tokens per second is the average across the four prompt types. Peak VRAM is the highest value across all runs, converted from MB with 1 GB = 1,024 MB. The full per-prompt breakdown is in [`results_lmstudio.csv`](./results_lmstudio.csv).

---

## Cost comparison

Standard API prices per million tokens, checked on 5 October 2026. Providers publish and bill in US dollars, so these figures are converted to pounds at the mid-market rate on that date ($1 = £0.755) and rounded to the nearest penny.

| Option | Upfront cost | Input (£/1M tokens) | Output (£/1M tokens) | Where prompts are processed |
|---|---|---|---|---|
| Local (this setup) | £1,800 hardware | None | None | On this PC |
| [OpenAI GPT-5.6 Luna](https://openai.com/api/pricing/) | None | £0.15 | £0.91 | Provider's servers |
| [Anthropic Claude Haiku 4.5](https://platform.claude.com/docs/en/about-claude/pricing) | None | £0.76 | £3.78 | Provider's servers |
| [Google Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/pricing) | None | £0.23 | £1.89 | Provider's servers |

Points to keep in mind when reading this table:

- **The local models and the API models are not equivalent.** This table compares cost and privacy, not answer quality.
- **Local running is not free.** The local row excludes electricity. The hardware cost also covers a PC used for other purposes, not only LLMs.
- **API prices change often.** Check the linked pricing pages for current rates. Batch processing and prompt caching can lower API costs further.
- **The pound figures move with the exchange rate.** What you actually pay also depends on your card or bank's conversion fees.

---

## Takeaways

- **Model size alone did not predict speed.** The 7B coding model was the slowest tested (26.9 tokens/sec). Qwen 3.5 9B (56.4) and Gemma 4 E4B (56.1) were effectively tied for fastest. Architecture, quantisation and the type of prompt all affect the result.
- **Smaller models can match larger ones on speed.** Gemma 4 E4B used the least VRAM (7.8 GB) while matching Qwen 3.5 9B on speed.
- **Prompt type changed speed more than expected.** Code generation was the fastest prompt for four of the five models. GPT-OSS 20B reached 75.5 tokens/sec on code generation but 28 to 35 on the other prompts. Longer outputs likely spread the fixed request overhead across more tokens, which raises the wall-clock figure.
- **Mixture-of-experts models trade memory for speed.** GPT-OSS 20B ran faster than the dense 14B model because it uses only 3.6B parameters per token. It still needed 15.4 GB of the 16 GB available, leaving little room for longer context windows or other applications.
- **A 16 GB card covers the 7B to 14B range comfortably** and can stretch to a 20B mixture-of-experts model at the cost of most of its VRAM headroom.

---

## Limitations

- Speed and memory only. Answer quality was not scored.
- Quantisation level and context length for each model are not shown in this table. Both affect speed and VRAM use.
- Peak VRAM is GPU memory in use during the run and may include memory used by other applications.
- Wall-clock timing includes some request overhead, which affects short responses most.
- Results come from one machine and one GPU.

---

## Reproducing this

1. Install [LM Studio](https://lmstudio.ai).
2. Load a model, open the **Local Server** tab and click **Start Server** (default: `http://localhost:1234`).
3. Install the Python dependencies:

   ```bash
   pip install requests pynvml
   ```

4. Edit `CURRENT_MODEL_LABEL` in `benchmark_lmstudio.py` to match the model you have loaded.
5. Run the benchmark:

   ```bash
   python benchmark_lmstudio.py
   ```

6. Results are appended to `results_lmstudio.csv`. Load the next model in LM Studio, update the label and run again for each model.

---

## About

Built as part of an ongoing interest in local AI deployment and in lowering the cost barrier to useful AI tools.
