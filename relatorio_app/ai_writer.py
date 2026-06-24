from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .env import load_env_file
from .pattern_library import build_writer_prompt, select_pattern_examples
from .report_engine import parse_report_data
from .technical_writer import TechnicalReportResult, generate_technical_report

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


@dataclass(frozen=True)
class WriterRun:
    result: TechnicalReportResult
    used_ai: bool
    provider: str
    model: str
    fallback_reason: str = ""

    def to_payload(self) -> dict:
        payload = self.result.to_payload()
        payload["writer"] = {
            "used_ai": self.used_ai,
            "provider": self.provider,
            "model": self.model,
            "fallback_reason": self.fallback_reason,
        }
        return payload


def generate_technical_report_auto(raw_text: str) -> WriterRun:
    load_env_file()
    local_result = generate_technical_report(raw_text)
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL

    if not api_key:
        return WriterRun(
            result=local_result,
            used_ai=False,
            provider="local",
            model="local-rules-v1",
            fallback_reason="GEMINI_API_KEY não configurada.",
        )

    try:
        prompt = build_writer_prompt(raw_text, local_result.report_text, max_examples=3)
        report_text = request_gemini_report(prompt, api_key=api_key, model=model)
        parsed = parse_report_data(report_text)
        if not parsed.get("cliente") or not parsed.get("imovel_nome"):
            raise GeminiWriterError("A resposta da IA não trouxe campos mínimos reconhecíveis.")
        return WriterRun(
            result=TechnicalReportResult(report_text=report_text, notes=local_result.notes, source=f"gemini:{model}"),
            used_ai=True,
            provider="gemini",
            model=model,
        )
    except Exception as exc:
        return WriterRun(
            result=local_result,
            used_ai=False,
            provider="local",
            model="local-rules-v1",
            fallback_reason=f"Gemini indisponível: {exc}",
        )


class GeminiWriterError(RuntimeError):
    pass


def request_gemini_report(prompt: str, *, api_key: str, model: str) -> str:
    timeout = parse_timeout(os.environ.get("GEMINI_TIMEOUT_SECONDS"))
    endpoint = (
        f"{GEMINI_API_BASE_URL}/models/"
        f"{urllib.parse.quote(model, safe='')}:generateContent"
        f"?key={urllib.parse.quote(api_key, safe='')}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.25,
            "topP": 0.9,
            "maxOutputTokens": 8192,
            "responseMimeType": "text/plain",
        },
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = extract_http_error_message(exc)
        raise GeminiWriterError(message) from exc
    except urllib.error.URLError as exc:
        raise GeminiWriterError(str(exc.reason)) from exc

    text = extract_text_from_gemini_response(response_payload)
    if not text.strip():
        raise GeminiWriterError("resposta vazia do Gemini.")
    return sanitize_report_text(text)


def parse_timeout(value: str | None) -> int:
    try:
        timeout = int(str(value or "").strip())
    except ValueError:
        return 45
    return max(10, min(timeout, 120))


def extract_http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return f"HTTP {exc.code}"
    message = payload.get("error", {}).get("message")
    return f"HTTP {exc.code}: {message}" if message else f"HTTP {exc.code}"


def extract_text_from_gemini_response(payload: dict) -> str:
    candidates = payload.get("candidates") or []
    parts = []
    for candidate in candidates:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            if isinstance(part, dict) and part.get("text"):
                parts.append(str(part["text"]))
    if parts:
        return "\n".join(parts)

    prompt_feedback = payload.get("promptFeedback") or {}
    block_reason = prompt_feedback.get("blockReason")
    if block_reason:
        raise GeminiWriterError(f"prompt bloqueado pelo Gemini: {block_reason}")
    return ""


def sanitize_report_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()
        if cleaned.lower().startswith("text"):
            cleaned = cleaned[4:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned + "\n"
