---
name: llm-review
description: |
  Multi-LLM consultation wrapper for external AI reviews.
  Supports Gemini and GPT with hardcoded model names to prevent agent modifications.
allowed-tools: Bash, Read, Write
---

# LLM Review - Multi-AI Consultation Skill

Provides a reliable interface for calling external LLMs (Gemini, GPT) with fixed model configurations.

## Purpose

1. **Prevent model name changes** by agents (hardcoded in Python)
2. **Standardize API protocols** (different APIs handled internally)
3. **Provide consistent JSON output** for easy parsing

---

## Usage

```bash
python3 .claude/skills/llm-review/llm_client.py \
  --provider [gemini|openai] \
  --phase [consultation|review] \
  --prompt "Your prompt" \
  --output /tmp/result.json
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--provider` | Yes | `gemini` or `openai` |
| `--phase` | Yes | `consultation` (fast) or `review` (thorough) |
| `--prompt` | Yes* | Prompt text |
| `--prompt-file` | Yes* | Read prompt from file |
| `--output` | No | Output file (default: stdout) |
| `--timeout` | No | Timeout seconds |

---

## Models (HARDCODED - DO NOT CHANGE)

| Phase | Gemini | OpenAI |
|-------|--------|--------|
| consultation | `gemini-3-flash-preview` | `gpt-5.2` |
| review | `gemini-3-pro-preview` | `gpt-5.2` |

---

## Output Format

```json
{
  "success": true,
  "provider": "gemini",
  "model": "gemini-3-flash-preview",
  "response": "LLM response text...",
  "tokens": {"prompt": 1234, "completion": 567, "total": 1801},
  "elapsed_seconds": 3.2
}
```

Error: `"success": false, "error": "...", "error_type": "..."`

---

## Environment

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google AI Studio API key |
| `OPENAI_API_KEY` | OpenAI API key |

Auto-loads from `.env` in workspace root.

**Check keys:** `python3 .claude/skills/llm-review/llm_client.py --check-keys`

---

## Error Handling

| Error | Behavior |
|-------|----------|
| API key missing | Returns error JSON |
| Timeout | Returns partial if available |
| Rate limit | Retries 3x with backoff |
