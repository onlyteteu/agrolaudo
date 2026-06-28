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
from .report_schema import REPORT_JSON_SCHEMA, build_extraction_prompt, coerce_structured_data
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
    # Dados estruturados que alimentam a planilha. Vem da IA (com marca
    # "_structured") quando possivel, ou da releitura por regex como fallback.
    structured: dict | None = None
    structured_source: str = "regex"

    def to_payload(self) -> dict:
        payload = self.result.to_payload()
        payload["writer"] = {
            "used_ai": self.used_ai,
            "provider": self.provider,
            "model": self.model,
            "fallback_reason": self.fallback_reason,
            "structured_source": self.structured_source,
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
            structured=parse_report_data(local_result.report_text),
            structured_source="regex",
        )

    try:
        prompt = build_writer_prompt(raw_text, local_result.report_text, max_examples=3)
        report_text = request_gemini_report(prompt, api_key=api_key, model=model)
        quality_issues = assess_report_quality(report_text)
        if quality_issues:
            retry_prompt = build_quality_retry_prompt(prompt, report_text, quality_issues)
            improved_text = request_gemini_report(retry_prompt, api_key=api_key, model=model)
            if len(improved_text.strip()) >= len(report_text.strip()):
                report_text = improved_text
        parsed = parse_report_data(report_text)
        if not parsed.get("cliente") or not parsed.get("imovel_nome"):
            raise GeminiWriterError("A resposta da IA não trouxe campos mínimos reconhecíveis.")

        # Extracao estruturada: a IA devolve os campos diretamente (fonte da
        # verdade). Se falhar, caimos para a releitura por regex acima.
        structured, structured_source = resolve_structured_data(
            raw_text, report_text, parsed, api_key=api_key, model=model
        )
        return WriterRun(
            result=TechnicalReportResult(report_text=report_text, notes=local_result.notes, source=f"gemini:{model}"),
            used_ai=True,
            provider="gemini",
            model=model,
            structured=structured,
            structured_source=structured_source,
        )
    except Exception as exc:
        return WriterRun(
            result=local_result,
            used_ai=False,
            provider="local",
            model="local-rules-v1",
            fallback_reason=f"Gemini indisponível: {exc}",
            structured=parse_report_data(local_result.report_text),
            structured_source="regex",
        )


def resolve_structured_data(
    raw_text: str,
    report_text: str,
    regex_parsed: dict,
    *,
    api_key: str,
    model: str,
) -> tuple[dict, str]:
    """Tenta a extracao estruturada via IA; cai para regex se nao for confiavel."""
    try:
        structured = extract_structured_report(raw_text, report_text, api_key=api_key, model=model)
        if structured_is_sane(structured):
            return structured, "gemini-json"
    except Exception:
        pass
    return regex_parsed, "regex"


def structured_is_sane(structured: dict) -> bool:
    """Guardrail contra extracoes ruins da IA (areas zeradas, culturas com lixo).

    A IA e nao-deterministica: se a saida nao passar nestes checks basicos,
    descartamos e usamos o parser deterministico (regex sobre o texto tecnico).
    """
    if not structured.get("cliente") or not structured.get("imovel_nome"):
        return False
    imoveis = structured.get("imoveis") or []
    if not imoveis:
        return False
    for item in imoveis:
        if not isinstance(item, dict):
            return False
        total = item.get("area_total_ha")
        if not isinstance(total, (int, float)) or total <= 0:
            return False
        pasture = item.get("area_pastagens_ha") or 0
        crop = item.get("area_cultivo_ha") or 0
        if isinstance(pasture, (int, float)) and isinstance(crop, (int, float)):
            if pasture + crop > total * 1.1 + 1:
                return False
        cultures = str(item.get("principais_culturas") or "")
        if "hectare" in cultures.lower() or len(cultures) > 90:
            return False
    return True


class GeminiWriterError(RuntimeError):
    pass


def assess_report_quality(report_text: str) -> list[str]:
    text = report_text.strip()
    issues: list[str] = []
    upper = text.upper()
    required_sections = [
        "1. DISCRIM",
        "2. TIPO",
        "3. DESCRI",
        "OUTROS COMENT",
        "CONCLUS",
        "FRASES DIRETAS",
    ]
    for section in required_sections:
        if section not in upper:
            issues.append(f"secao obrigatoria ausente ou mal identificada: {section}")

    if len(text) < 2400:
        issues.append("texto final curto demais para laudo de credito rural")

    improvements = extract_between_markers(upper, "2. TIPO", "3. DESCRI")
    if len(improvements) < 700:
        issues.append("secao 2. TIPO pouco desenvolvida")

    conclusion = extract_between_markers(upper, "CONCLUS", "FRASES DIRETAS")
    if len(conclusion) < 300:
        issues.append("conclusao muito curta")

    sentence_count = text.count(".")
    if sentence_count < 12:
        issues.append("poucas frases tecnicas desenvolvidas")

    return issues


def extract_between_markers(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    end = text.find(end_marker, start + len(start_marker))
    if end == -1:
        return text[start:]
    return text[start:end]


def build_quality_retry_prompt(original_prompt: str, first_report: str, issues: list[str]) -> str:
    return "\n".join(
        [
            original_prompt.strip(),
            "",
            "A PRIMEIRA RESPOSTA FICOU ABAIXO DO PADRAO DE QUALIDADE.",
            "PROBLEMAS DETECTADOS:",
            *[f"- {issue}" for issue in issues],
            "",
            "PRIMEIRA RESPOSTA:",
            first_report.strip(),
            "",
            "TAREFA DE REESCRITA:",
            "Reescreva o relatorio completo, mantendo apenas os dados informados e sem inventar informacoes.",
            "Aumente a profundidade tecnica, principalmente na secao 2. TIPO, em paragrafos completos.",
            "Mantenha a estrutura obrigatoria e entregue apenas o relatorio final.",
        ]
    ).strip() + "\n"


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


def extract_structured_report(raw_text: str, report_text: str, *, api_key: str, model: str) -> dict:
    """Extrai os campos estruturados via Gemini (responseSchema) e os normaliza."""
    prompt = build_extraction_prompt(raw_text, report_text)
    ai_data = request_gemini_json(prompt, REPORT_JSON_SCHEMA, api_key=api_key, model=model)
    return coerce_structured_data(ai_data)


def request_gemini_json(prompt: str, schema: dict, *, api_key: str, model: str) -> dict:
    """Chama o Gemini forcando saida JSON conforme o schema e devolve o dict."""
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
            "temperature": 0.0,
            "topP": 0.9,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
            "responseSchema": schema,
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
        raise GeminiWriterError(extract_http_error_message(exc)) from exc
    except urllib.error.URLError as exc:
        raise GeminiWriterError(str(exc.reason)) from exc

    text = extract_text_from_gemini_response(response_payload)
    if not text.strip():
        raise GeminiWriterError("resposta estruturada vazia do Gemini.")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(strip_json_fences(text))


def strip_json_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


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
