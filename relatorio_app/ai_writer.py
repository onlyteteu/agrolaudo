from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from .env import load_env_file
from .pattern_library import build_enrichment_prompt, build_writer_prompt, select_pattern_examples
from .report_engine import parse_report_data
from .report_schema import REPORT_JSON_SCHEMA, build_extraction_prompt, coerce_structured_data
from .technical_writer import TechnicalReportResult, generate_technical_report

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# Instrucao de sistema fixa (persona) aplicada SEMPRE antes de o Gemini gerar
# o laudo. Vai no campo systemInstruction do Gemini, separada dos dados, para
# firmar o papel e as regras inegociaveis com mais peso do que instrucoes
# diluidas no meio do prompt do usuario.
AGRONOMIST_SYSTEM_INSTRUCTION = (
    "Voce e um engenheiro agronomo senior, especializado em laudos de vistoria "
    "rural para analise de credito bancario. Escreve sempre em portugues do Brasil, "
    "em tom tecnico, formal, objetivo e conservador, no estilo de inventario de campo. "
    "Descreve com precisao o que existe na propriedade, preservando numeros, unidades "
    "e especificacoes informados (fios de arame, numero de pastos/piquetes, capacidade "
    "de reservatorio, tipo de curral, casas, galpoes etc.). "
    "Nunca inventa dados nao informados: quando faltar informacao, registra de forma "
    "neutra ('Nao informado') em vez de supor. "
    "Nao usa linguagem promocional, opinativa ou exagerada. "
    "Escreve as benfeitorias de cada propriedade em um unico bloco de texto corrido e "
    "denso, sem picotar a mesma propriedade em varias frases soltas, e evita conectores "
    "vazios como 'a infraestrutura de suporte ao rebanho inclui'. "
    "IMPORTANTE: 'denso' significa RICO EM CONTEUDO TECNICO, nunca curto ou economico. "
    "Desenvolve cada secao com profundidade e o maximo de detalhes verificaveis a partir "
    "dos dados informados; o laudo deve ser completo e extenso o suficiente para uma "
    "analise bancaria criteriosa, aproveitando cada dado da vistoria. "
    "Mantem exatamente as secoes que o sistema reconhece e entrega apenas o laudo final."
)


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


# Campos de PROSA que a IA enriquece. Todo o resto (cliente, cpf, areas,
# imoveis, equipamentos, insumos) vem do nosso motor deterministico e nunca e
# decidido pela IA — o que elimina numeros errados e celulas vazias.
PROSE_FIELDS = (
    "benfeitorias_descricao",
    "benfeitorias_observacoes",
    "investimentos_comentarios",
    "outros_comentarios",
    "conclusao",
    "insumos_comentarios",
)


def generate_technical_report_auto(raw_text: str) -> WriterRun:
    """Motor preenche, IA enriquece.

    1) O motor deterministico le as anotacoes e monta um rascunho correto (todas
       as secoes, numeros certos) -> ``base_structured`` alimenta a planilha.
    2) A IA (1 chamada) reescreve o rascunho em prosa rica, SEM mexer nos fatos.
    3) So os campos de PROSA da IA sao sobrepostos; os dados continuam do motor.

    Se a IA falhar (sem credito, timeout etc.), usa-se o rascunho do motor: o
    laudo sai completo do mesmo jeito, apenas com redacao mais simples."""
    load_env_file()
    local_result = generate_technical_report(raw_text)
    base_structured = parse_report_data(local_result.report_text)
    if isinstance(base_structured, dict):
        base_structured["_structured"] = True

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL

    if not api_key:
        return WriterRun(
            result=local_result,
            used_ai=False,
            provider="local",
            model="local-rules-v1",
            fallback_reason="GEMINI_API_KEY não configurada.",
            structured=base_structured,
            structured_source="motor",
        )

    try:
        prompt = build_enrichment_prompt(local_result.report_text, raw_text, max_examples=1)
        enriched_text = request_gemini_report(prompt, api_key=api_key, model=model)

        # Se a IA encurtou demais o rascunho, pede uma versao mais desenvolvida.
        if len(enriched_text.strip()) < len(local_result.report_text.strip()):
            retry_prompt = (
                prompt.rstrip()
                + "\n\nA versao anterior ficou curta demais. Reescreva desenvolvendo cada secao "
                "com mais profundidade tecnica, mantendo os mesmos numeros, fatos e titulos.\n"
            )
            retry_text = request_gemini_report(retry_prompt, api_key=api_key, model=model)
            if len(retry_text.strip()) > len(enriched_text.strip()):
                enriched_text = retry_text

        enriched_parsed = parse_report_data(enriched_text)
        structured = overlay_prose(base_structured, enriched_parsed)
        return WriterRun(
            result=TechnicalReportResult(report_text=enriched_text, notes=local_result.notes, source=f"gemini:{model}"),
            used_ai=True,
            provider="gemini",
            model=model,
            structured=structured,
            structured_source="motor+ia",
        )
    except Exception as exc:
        return WriterRun(
            result=local_result,
            used_ai=False,
            provider="local",
            model="local-rules-v1",
            fallback_reason=f"Gemini indisponível: {exc}",
            structured=base_structured,
            structured_source="motor",
        )


def overlay_prose(base: dict, enriched: dict | None) -> dict:
    """Mantem TODOS os dados do motor (``base``) e sobrepoe apenas os campos de
    prosa vindos do texto enriquecido pela IA, quando presentes."""
    if not isinstance(base, dict):
        return base
    merged = dict(base)
    if isinstance(enriched, dict):
        for field in PROSE_FIELDS:
            value = enriched.get(field)
            if value not in (None, ""):
                merged[field] = value
    merged["_structured"] = True
    return merged


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


def merge_structured_with_text(structured: dict | None, text_parsed: dict | None) -> dict | None:
    """Completa a extracao estruturada com os campos lidos do texto do laudo.

    Usa ``structured`` (fatos da IA) como base e preenche SOMENTE os campos
    vazios/ausentes com ``text_parsed`` (regex sobre o laudo). Nao sobrescreve
    dado bom. Reduz drasticamente celulas em branco (conclusao, comentarios,
    areas por propriedade) quando o JSON da IA vem incompleto."""
    if not isinstance(structured, dict):
        return text_parsed if isinstance(text_parsed, dict) else structured
    if not isinstance(text_parsed, dict):
        return structured

    merged = dict(structured)
    for key, value in text_parsed.items():
        if key == "imoveis" or value in (None, ""):
            continue
        if merged.get(key) in (None, ""):
            merged[key] = value

    _merge_imoveis(merged, text_parsed.get("imoveis"))
    merged["_structured"] = True
    return merged


def _merge_imoveis(merged: dict, text_imoveis: object) -> None:
    """Preenche campos vazios de cada imovel (areas, atividade, culturas) a
    partir da lista lida do texto, casando por posicao."""
    if not isinstance(text_imoveis, list) or not text_imoveis:
        return
    base_imoveis = merged.get("imoveis")
    if not isinstance(base_imoveis, list) or not base_imoveis:
        merged["imoveis"] = text_imoveis
        return
    for index, item in enumerate(base_imoveis):
        if not isinstance(item, dict) or index >= len(text_imoveis):
            continue
        source = text_imoveis[index]
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if value in (None, ""):
                continue
            if item.get(key) in (None, ""):
                item[key] = value


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


def request_gemini_report(
    prompt: str,
    *,
    api_key: str,
    model: str,
    system_instruction: str = AGRONOMIST_SYSTEM_INSTRUCTION,
) -> str:
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
            # gemini-2.5-flash e um modelo "thinking": os tokens de raciocinio
            # contam dentro de maxOutputTokens. Com 8192, o pensamento consumia
            # boa parte do orcamento e sobrava pouco para o laudo (texto curto).
            # Ampliamos o teto para caber raciocinio + laudo completo e denso.
            "maxOutputTokens": 32768,
            "responseMimeType": "text/plain",
        },
    }
    if system_instruction and system_instruction.strip():
        payload["systemInstruction"] = {"parts": [{"text": system_instruction.strip()}]}
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
            # Teto ampliado: o raciocinio do modelo 2.5 conta no orcamento; um
            # JSON truncado quebraria a extracao estruturada e cairia no regex.
            "maxOutputTokens": 32768,
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
