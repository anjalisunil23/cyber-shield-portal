"""Optional LLM wrapper with graceful local fallback.

The LLM is assistive only. It must never decide guilt, admissibility, or enforcement action.
Missing keys or network failures never crash the application.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger("cybershield.ai.llm")

DISCLAIMER = (
    "Cyber Shield is an investigation support and decision-assistance platform. "
    "AI-generated findings are recommendations only and must be independently verified "
    "by authorized investigators."
)


class LLMService:
    @classmethod
    def availability(cls) -> dict[str, Any]:
        settings = get_settings()
        provider = (settings.ai_provider or "local").strip().lower()
        has_key = bool((settings.ai_api_key or "").strip())
        configured = provider not in {"", "local", "none", "off"} and has_key
        return {
            "provider": provider if configured else "local",
            "model": settings.ai_model_name if configured else "rule-based",
            "available": configured,
            "mode": "configured" if configured else "fallback",
            "disclaimer": DISCLAIMER,
        }

    @classmethod
    def interpret(cls, task: str, grounded_text: str, fallback: str) -> str:
        """Optionally polish grounded text. Never invent facts beyond fallback/grounded_text."""
        settings = get_settings()
        provider = (settings.ai_provider or "local").strip().lower()
        api_key = (settings.ai_api_key or "").strip()
        if provider in {"", "local", "none", "off"} or not api_key:
            return fallback

        try:
            if provider in {"openai", "azure-openai", "azure"}:
                return cls._openai_complete(task, grounded_text, fallback, api_key, settings.ai_model_name)
        except Exception as exc:
            logger.warning("AI service unavailable (%s); using local fallback.", exc)
        return fallback

    @staticmethod
    def _openai_complete(task: str, grounded_text: str, fallback: str, api_key: str, model: str) -> str:
        import json
        import urllib.error
        import urllib.request

        payload = {
            "model": model or "gpt-4o-mini",
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Cyber Shield, an investigator decision-support assistant. "
                        "Use only the provided evidence excerpts. Do not decide guilt, crime, "
                        "or legal admissibility. If information is missing, say so. "
                        "Return concise investigator-facing prose."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Task: {task}\n\nGrounded evidence:\n{grounded_text[:8000]}\n\nFallback draft:\n{fallback}",
                },
            ],
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        text = (
            body.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        return text or fallback
