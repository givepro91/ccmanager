#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-LLM Client for External AI Consultation

Provides a unified interface for calling Gemini and OpenAI APIs with
hardcoded model names to prevent agent modifications.

Usage:
    python llm_client.py --provider gemini --phase consultation --prompt "..."
    python llm_client.py --provider openai --phase review --prompt-file task.md

Origin: TeamSPWK/BluePrintCheck
Version: 1.0.0
"""

import argparse
import json
import os
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

# =============================================================================
# SSL Context (macOS Python needs certifi for HTTPS)
# =============================================================================

def _get_ssl_context():
    """Get SSL context with proper certificate bundle."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
        ctx.load_default_certs()
        return ctx

SSL_CONTEXT = _get_ssl_context()

# =============================================================================
# HARDCODED MODEL CONFIGURATION - DO NOT MODIFY
# =============================================================================

MODELS = {
    "gemini": {
        "consultation": "gemini-3-flash-preview",     # Fast, cost-effective
        "review": "gemini-3-pro-preview",             # High quality, thorough
    },
    "openai": {
        "consultation": "gpt-5.2",                     # Fast consultation
        "review": "gpt-5.2",                           # High reasoning effort
    },
}

TIMEOUTS = {
    "consultation": 180,  # 3 minutes
    "review": 600,        # 10 minutes
}

MAX_TOKENS = {
    "consultation": 8192,
    "review": 16384,
}

# =============================================================================
# Environment Setup
# =============================================================================

def load_env():
    """Load .env file from workspace root."""
    env_paths = [
        Path(__file__).parent.parent.parent.parent / ".env",
        Path.cwd() / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        os.environ.setdefault(key.strip(), value)
            return True
    return False


def check_api_keys() -> Dict[str, bool]:
    """Check which API keys are available."""
    return {
        "gemini": bool(os.environ.get("GEMINI_API_KEY")),
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
    }


# =============================================================================
# Gemini Client
# =============================================================================

class GeminiClient:
    """Google Gemini API client."""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 16384,
        temperature: float = 0.7,
        timeout: int = 180,
    ) -> Dict[str, Any]:
        """Generate response from Gemini API."""
        import urllib.request
        import urllib.error

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
                result = json.loads(response.read().decode("utf-8"))
                elapsed = time.time() - start_time

                text = ""
                tokens = {"prompt": 0, "completion": 0, "total": 0}

                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        text = "".join(p.get("text", "") for p in parts)

                if "usageMetadata" in result:
                    usage = result["usageMetadata"]
                    tokens = {
                        "prompt": usage.get("promptTokenCount", 0),
                        "completion": usage.get("candidatesTokenCount", 0),
                        "total": usage.get("totalTokenCount", 0),
                    }

                return {
                    "success": True,
                    "response": text,
                    "tokens": tokens,
                    "elapsed_seconds": round(elapsed, 2),
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(e))
            except json.JSONDecodeError:
                error_msg = error_body or str(e)

            return {
                "success": False,
                "error": error_msg,
                "error_type": "HTTPError",
                "status_code": e.code,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": str(e.reason),
                "error_type": "URLError",
            }
        except TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "error_type": "TimeoutError",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }


# =============================================================================
# OpenAI Client
# =============================================================================

class OpenAIClient:
    """OpenAI API client."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 16384,
        temperature: float = 0.7,
        timeout: int = 180,
        high_effort: bool = False,
    ) -> Dict[str, Any]:
        """Generate response from OpenAI API."""
        import urllib.request
        import urllib.error

        url = "https://api.openai.com/v1/chat/completions"

        if high_effort:
            system_content = (
                "You are a senior software architect conducting a thorough technical review. "
                "Provide detailed, comprehensive feedback. Be specific about issues, "
                "reference exact sections/files, and explain your reasoning thoroughly. "
                "Prioritize critical issues over minor improvements."
            )
        else:
            system_content = (
                "You are a senior software architect providing technical consultation. "
                "Be specific, actionable, and prioritize your suggestions."
            )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
                result = json.loads(response.read().decode("utf-8"))
                elapsed = time.time() - start_time

                text = ""
                tokens = {"prompt": 0, "completion": 0, "total": 0}

                if "choices" in result and result["choices"]:
                    choice = result["choices"][0]
                    if "message" in choice:
                        text = choice["message"].get("content", "")

                if "usage" in result:
                    usage = result["usage"]
                    tokens = {
                        "prompt": usage.get("prompt_tokens", 0),
                        "completion": usage.get("completion_tokens", 0),
                        "total": usage.get("total_tokens", 0),
                    }

                return {
                    "success": True,
                    "response": text,
                    "tokens": tokens,
                    "elapsed_seconds": round(elapsed, 2),
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(e))
            except json.JSONDecodeError:
                error_msg = error_body or str(e)

            return {
                "success": False,
                "error": error_msg,
                "error_type": "HTTPError",
                "status_code": e.code,
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": str(e.reason),
                "error_type": "URLError",
            }
        except TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "error_type": "TimeoutError",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }


# =============================================================================
# Main Interface
# =============================================================================

def call_llm(
    provider: str,
    phase: str,
    prompt: str,
    timeout: Optional[int] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Call LLM with specified provider and phase.

    Args:
        provider: "gemini" or "openai"
        phase: "consultation" or "review"
        prompt: The prompt to send
        timeout: Optional timeout override
        verbose: Print debug info

    Returns:
        Dict with response or error
    """
    if provider not in MODELS:
        return {
            "success": False,
            "error": f"Invalid provider: {provider}. Use 'gemini' or 'openai'",
            "error_type": "ValidationError",
        }

    if phase not in MODELS[provider]:
        return {
            "success": False,
            "error": f"Invalid phase: {phase}. Use 'consultation' or 'review'",
            "error_type": "ValidationError",
        }

    model = MODELS[provider][phase]
    max_tokens = MAX_TOKENS[phase]
    timeout = timeout or TIMEOUTS[phase]

    if verbose:
        print(f"[DEBUG] Provider: {provider}", file=sys.stderr)
        print(f"[DEBUG] Phase: {phase}", file=sys.stderr)
        print(f"[DEBUG] Model: {model}", file=sys.stderr)
        print(f"[DEBUG] Max tokens: {max_tokens}", file=sys.stderr)
        print(f"[DEBUG] Timeout: {timeout}s", file=sys.stderr)
        print(f"[DEBUG] Prompt length: {len(prompt)} chars", file=sys.stderr)

    try:
        if provider == "gemini":
            client = GeminiClient()
            result = client.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        else:
            client = OpenAIClient()
            result = client.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                timeout=timeout,
                high_effort=(phase == "review"),
            )

        result["provider"] = provider
        result["model"] = model
        result["phase"] = phase
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

        return result

    except ValueError as e:
        return {
            "success": False,
            "provider": provider,
            "model": model,
            "phase": phase,
            "error": str(e),
            "error_type": "ConfigurationError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "model": model,
            "phase": phase,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Multi-LLM Client for External AI Consultation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Gemini consultation
  python llm_client.py --provider gemini --phase consultation --prompt "Analyze..."

  # OpenAI review from file
  python llm_client.py --provider openai --phase review --prompt-file task.md

  # Check API keys
  python llm_client.py --check-keys

  # List models
  python llm_client.py --list-models
""")

    parser.add_argument("--provider", choices=["gemini", "openai"], help="LLM provider to use")
    parser.add_argument("--phase", choices=["consultation", "review"], help="Phase determines model selection")
    parser.add_argument("--prompt", help="Prompt text to send")
    parser.add_argument("--prompt-file", help="Read prompt from file")
    parser.add_argument("--output", help="Write response to file (default: stdout)")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")
    parser.add_argument("--verbose", action="store_true", help="Print debug info")
    parser.add_argument("--check-keys", action="store_true", help="Check API key availability")
    parser.add_argument("--list-models", action="store_true", help="List hardcoded models")

    args = parser.parse_args()

    load_env()

    if args.check_keys:
        keys = check_api_keys()
        result = {
            "gemini": "available" if keys["gemini"] else "not set",
            "openai": "available" if keys["openai"] else "not set",
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if any(keys.values()) else 1)

    if args.list_models:
        print(json.dumps(MODELS, indent=2))
        sys.exit(0)

    if not args.provider:
        parser.error("--provider is required")
    if not args.phase:
        parser.error("--phase is required")
    if not args.prompt and not args.prompt_file:
        parser.error("--prompt or --prompt-file is required")

    if args.prompt_file:
        try:
            with open(args.prompt_file, "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            result = {
                "success": False,
                "error": f"Failed to read prompt file: {e}",
                "error_type": "FileError",
            }
            print(json.dumps(result, indent=2))
            sys.exit(1)
    else:
        prompt = args.prompt

    result = call_llm(
        provider=args.provider,
        phase=args.phase,
        prompt=prompt,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            if args.verbose:
                print(f"[DEBUG] Response written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to write output: {e}", file=sys.stderr)
            print(output_json)
            sys.exit(1)
    else:
        print(output_json)

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
