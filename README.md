---
title: Template Final Assignment
emoji: 🕵🏻‍♂️
colorFrom: indigo
colorTo: indigo
sdk: gradio
sdk_version: 5.25.2
app_file: app.py
pinned: false
hf_oauth: true
# optional, default duration is 8 hours/480 minutes. Max duration is 30 days/43200 minutes.
hf_oauth_expiration_minutes: 480
---

## What this Space does

This Space fetches the Unit 4 challenge questions, runs a **LangGraph** agent against each question, and submits all answers to the scoring API.

It also emits traces to:
- **LangSmith** (LangChain tracing)
- **Langfuse** (callback-based tracing)
- **OpenTelemetry** (OTLP export, vendor-neutral)

## Repo structure

- `app.py`: Gradio UI + question fetch + submission
- `agent/`: LangGraph agent (entrypoint is `agent.run.answer()`)
- `observability/`: Langfuse + OpenTelemetry wiring (LangSmith via env)

## Required secrets / environment variables

### LLM provider (required to answer questions)

This repo defaults to OpenAI-compatible via `langchain-openai`:
- `OPENAI_API_KEY`: your API key
- `MODEL_NAME` (optional, default `gpt-4o-mini`)
- `MODEL_TEMPERATURE` (optional, default `0`)

### LangSmith (optional)

- `LANGCHAIN_TRACING_V2=true`
- `LANGCHAIN_API_KEY=...`
- `LANGCHAIN_PROJECT=hf-agents-unit4` (or any name you want)

### Langfuse (optional)

- `LANGFUSE_PUBLIC_KEY=...`
- `LANGFUSE_SECRET_KEY=...`
- `LANGFUSE_HOST` (optional; default is Langfuse Cloud)

### OpenTelemetry / OTLP (optional)

If set, the Space will export spans over OTLP/HTTP:
- `OTEL_EXPORTER_OTLP_ENDPOINT=https://<your-collector-host>:4318/v1/traces`
- `OTEL_EXPORTER_OTLP_HEADERS` (optional) e.g. `Authorization=Bearer <token>`
- `OTEL_SERVICE_NAME` (optional, default `hf-agents-unit4`)
- `OTEL_INSTRUMENT_REQUESTS` (optional, default `true`)

## How traces are emitted

- Each question run creates one OTel span: `agent.task` with attributes like `app.task_id`, `app.username`, `app.model`.
- LangSmith will show the full LangChain/LangGraph run (LLM + tool calls) when enabled.
- Langfuse will show the same run via the callback handler when configured.

## Notes

- If you don’t set `OPENAI_API_KEY`, the agent will error during execution (you’ll see `AGENT ERROR` rows in the results table).
- Keep answers concise: the agent is instructed to return only the final answer.