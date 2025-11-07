# Milestone 01 – LLM Fundamentals

## Objective
Establish a repeatable workflow for running open-source language models locally and documenting the insights you gain while experimenting with prompting and sampling controls.

## Preparation checklist
- [ ] Install a lightweight inference runtime such as [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/).
- [ ] Pull at least one instruction-tuned model that runs well on your hardware (e.g., `phi3:mini` or `mistral:7b`).
- [ ] Create a notebook in `notebooks/` for tracking prompts, responses, and observations.

## Key experiments
1. **Hello world completion** – Use the CLI provided by your runtime to generate a short response and record latency, token counts, and subjective quality.
2. **Prompt variants** – Compare system prompts and role-play instructions; capture how tone and specificity shift the output.
3. **Sampling sweep** – Hold the prompt constant while varying temperature, top-k, and top-p. Note when outputs become repetitive or incoherent.
4. **Token inspection** – Export token probabilities (if supported) or run the model with verbose logging to understand how text is chunked.

## Deliverables
- Updated learning journal entry summarizing experiments, surprises, and open questions.
- Saved prompt/response transcripts in the new notebook or as markdown snippets in `docs/`.
- A short checklist of model/runtime commands you found most useful (consider adding a cheatsheet in `docs/`).

## Stretch goals
- Evaluate a second model and document trade-offs in speed vs. quality.
- Script a tiny CLI wrapper in `src/` that streams completions from your runtime for reuse in later phases.
- Investigate GPU vs. CPU execution if you have access to both and measure the difference.
