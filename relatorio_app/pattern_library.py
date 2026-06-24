from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .report_engine import normalize_key
from .technical_writer import parse_raw_visit_notes

ROOT_DIR = Path(__file__).resolve().parents[1]
PATTERN_DIR = ROOT_DIR / "patterns" / "relatorio_credito"
EXAMPLES_DIR = PATTERN_DIR / "examples"
STYLE_GUIDE = PATTERN_DIR / "style_guide.md"


@dataclass(frozen=True)
class PatternExample:
    id: str
    title: str
    tags: tuple[str, ...]
    approved: bool
    notes: str = ""
    raw_text: str = ""
    expected_text: str = ""
    final_workbook: str = ""

    @property
    def has_expected(self) -> bool:
        return bool(self.expected_text.strip())


@dataclass(frozen=True)
class PatternSelection:
    tags: tuple[str, ...]
    examples: tuple[PatternExample, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "tags": list(self.tags),
            "selected": [
                {
                    "id": example.id,
                    "title": example.title,
                    "approved": example.approved,
                    "tags": list(example.tags),
                    "has_expected": example.has_expected,
                }
                for example in self.examples
            ],
        }


def classify_case_tags(raw_text: str) -> tuple[str, ...]:
    notes = parse_raw_visit_notes(raw_text)
    tags: set[str] = set()

    property_mentions = count_property_mentions(raw_text)
    if len(notes.properties) > 1 or property_mentions > 1:
        tags.add("multi_propriedades")
    elif len(notes.properties) == 1:
        tags.add("propriedade_unica")

    if notes.equipment:
        tags.add("maquinarios")

    normalized_text = normalize_key(raw_text)
    if "arrendada" in normalized_text or "arrendado" in normalized_text:
        tags.add("arrendada")
    if "espolio" in normalized_text:
        tags.add("espolio")
    if "turismo" in normalized_text:
        tags.add("turismo_rural")
    if "confinamento" in normalized_text:
        tags.add("confinamento")
    if "seca" in normalized_text and "confinamento" in normalized_text:
        tags.add("confinamento_seca")
    if "cria" in normalized_text:
        tags.add("cria")
    if "recria" in normalized_text:
        tags.add("recria")
    if "engorda" in normalized_text:
        tags.add("engorda")
    if "cria_recria_engorda" in normalized_text or ("cria" in normalized_text and "recria" in normalized_text and "engorda" in normalized_text):
        tags.add("ciclo_completo")
    if "solar" in normalized_text or "placa" in normalized_text:
        tags.add("energia_solar")
    if "andropogon" in normalized_text:
        tags.add("andropogon")
    if "quicuia" in normalized_text:
        tags.add("quicuia")
    if "brachiarao" in normalized_text or "braquiarao" in normalized_text or "brach" in normalized_text:
        tags.add("braquiarao")
    if any(term in normalized_text for term in ("2600", "2200", "1600", "6400", "grande_escala")):
        tags.add("grande_escala")
    if any(term in normalized_text for term in ("peixe", "piscicultura", "tambaqui", "caranha", "piau", "tanque")):
        tags.add("piscicultura")
    if "tanque" in normalized_text:
        tags.add("tanques")
    if "aluguel" in normalized_text or "alugada" in normalized_text or "alugado" in normalized_text:
        tags.add("area_alugada")
        tags.add("arrendada")
    if "piquete" in normalized_text:
        tags.add("piquetes")
    if "cocho" in normalized_text:
        tags.add("cochos_cobertos" if "coberto" in normalized_text else "cochos")
    if "bebedouro" in normalized_text:
        tags.add("bebedouros")
    if "poco_artesiano" in normalized_text or "poço_artesiano" in normalized_text:
        tags.add("poco_artesiano")
        tags.add("recursos_hidricos")
    if "corrego" in normalized_text or "córrego" in normalized_text or "agua" in normalized_text or "água" in normalized_text:
        tags.add("recursos_hidricos")
    if "rotacionado" in normalized_text:
        tags.add("rotacionado")
    if "casa_funcionarios" in normalized_text or "casas_funcionarios" in normalized_text:
        tags.add("casas_funcionarios")
    if "casa_propria" in normalized_text or "casa_sede" in normalized_text:
        tags.add("casa_sede")
    if "futuros_projetos" in normalized_text or "projetos_futuros" in normalized_text:
        tags.add("projetos_futuros")
    if "reforma_de_pastagem" in normalized_text or "reforma_pastagem" in normalized_text:
        tags.add("reforma_pastagem")
    if "aquisicao_de_gado" in normalized_text or "aquisição_de_gado" in normalized_text or "aquisicao_animais" in normalized_text:
        tags.add("aquisicao_animais")
    if len(raw_text.strip()) < 700:
        tags.add("baixo_detalhamento")

    crop_terms = {
        "milho": "milho",
        "mandioca": "mandioca",
        "soja": "soja",
        "sorgo": "sorgo",
    }
    for term, tag in crop_terms.items():
        if term in normalized_text:
            tags.add(tag)
            tags.add("lavoura")

    cattle_terms = ("gado", "nelore", "novilha", "novilhas", "vaca", "vacas", "cabeca", "cabecas")
    if any(term in normalized_text for term in cattle_terms):
        tags.add("pecuaria_corte")
    if "leite" in normalized_text or "lactacao" in normalized_text:
        tags.add("leite")
        tags.add("pecuaria_mista")
    if "pastagem" in normalized_text or "patagem" in normalized_text or "brachiarao" in normalized_text or "braquiarao" in normalized_text:
        tags.add("pastagens")
    if "brachiaria" in normalized_text or "brachiara" in normalized_text:
        tags.add("brachiaria")
    if "mombaca" in normalized_text:
        tags.add("mombaca")

    return tuple(sorted(tags))


def count_property_mentions(raw_text: str) -> int:
    import re

    return len(
        re.findall(
            r"\b(?:Fazenda|S[ií]tio|Sitio|Ch[aá]cara|Chacara|Est[aâ]ncia|Estancia|Rancho|Gleba|Granja|Retiro)\b",
            raw_text,
            flags=re.IGNORECASE,
        )
    )


def load_style_guide() -> str:
    if not STYLE_GUIDE.exists():
        return ""
    return STYLE_GUIDE.read_text(encoding="utf-8")


def load_pattern_examples() -> list[PatternExample]:
    if not EXAMPLES_DIR.exists():
        return []

    examples: list[PatternExample] = []
    for metadata_path in sorted(EXAMPLES_DIR.glob("*/metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        example_dir = metadata_path.parent
        example_id = str(metadata.get("id") or example_dir.name)
        raw_text = read_example_text(example_dir, metadata, "raw_path", "raw.txt")
        expected_text = read_example_text(example_dir, metadata, "output_path", "expected.txt")
        tags = tuple(sorted(normalize_key(tag) for tag in metadata.get("tags", []) if str(tag).strip()))
        examples.append(
            PatternExample(
                id=example_id,
                title=str(metadata.get("title") or example_id),
                tags=tags,
                approved=bool(metadata.get("approved", False)),
                notes=str(metadata.get("notes") or ""),
                raw_text=raw_text,
                expected_text=expected_text,
                final_workbook=str(resolve_example_path(example_dir, str(metadata.get("final_workbook_path")))) if metadata.get("final_workbook_path") else "",
            )
        )

    return examples


def read_example_text(example_dir: Path, metadata: dict[str, Any], metadata_key: str, default_file: str) -> str:
    combined = read_combined_example(example_dir, metadata)
    if combined:
        if metadata_key == "raw_path":
            return combined[0]
        if metadata_key == "output_path":
            return combined[1]

    path_value = metadata.get(metadata_key)
    candidate = resolve_example_path(example_dir, str(path_value)) if path_value else example_dir / default_file
    if not candidate.exists():
        return ""
    return candidate.read_text(encoding="utf-8")


def read_combined_example(example_dir: Path, metadata: dict[str, Any]) -> tuple[str, str] | None:
    combined_path = metadata.get("combined_path")
    if not combined_path:
        return None
    path = resolve_example_path(example_dir, str(combined_path))
    if not path.exists():
        return None
    return split_combined_example(path.read_text(encoding="utf-8"))


def split_combined_example(content: str) -> tuple[str, str]:
    raw_match = re_split_section(content, r"DADOS?\s+BRUTOS?|DADO\s+BRUTO")
    if not raw_match:
        response_only = re_split_section(content, r"RESPOSTA\s+GEMINI|RESPOSTA\s+APROVADA|RELAT[ÓO]RIO\s+APROVADO")
        if response_only:
            return response_only[0].strip(), response_only[1].strip()
        return content.strip(), ""

    after_raw = raw_match[1]
    response_match = re_split_section(after_raw, r"RESPOSTA\s+GEMINI|RESPOSTA\s+APROVADA|RELAT[ÓO]RIO\s+APROVADO")
    if not response_match:
        return after_raw.strip(), ""
    return response_match[0].strip(), response_match[1].strip()


def re_split_section(content: str, label_pattern: str) -> tuple[str, str] | None:
    import re

    match = re.search(rf"(?im)^\s*(?:#\s*)?{label_pattern}\s*:?\s*$", content)
    if not match:
        compact_match = re.search(rf"(?i){label_pattern}\s*:", content)
        if not compact_match:
            return None
        return content[: compact_match.start()], content[compact_match.end() :]
    return content[: match.start()], content[match.end() :]


def resolve_example_path(example_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    candidate = (example_dir / path).resolve()
    if candidate.exists():
        return candidate
    return (ROOT_DIR / path).resolve()


def select_pattern_examples(raw_text: str, limit: int = 3) -> PatternSelection:
    tags = classify_case_tags(raw_text)
    tag_set = set(tags)
    scored: list[tuple[float, PatternExample]] = []

    for example in load_pattern_examples():
        example_tags = set(example.tags)
        overlap = tag_set & example_tags
        score = float(len(overlap) * 10)
        if example.approved:
            score += 2
        if example.has_expected:
            score += 3
        if "multi_propriedades" in tag_set and "multi_propriedades" in example_tags:
            score += 4
        if "propriedade_unica" in tag_set and "propriedade_unica" in example_tags:
            score += 2
        if score > 0:
            scored.append((score, example))

    scored.sort(key=lambda item: (-item[0], item[1].id))
    return PatternSelection(tags=tags, examples=tuple(example for _, example in scored[:limit]))


def build_writer_prompt(raw_text: str, local_draft: str = "", max_examples: int = 3) -> str:
    selection = select_pattern_examples(raw_text, limit=max_examples)
    style_guide = load_style_guide().strip()
    parts = [
        "Você é um agrônomo responsável por redigir relatório técnico para análise de crédito rural.",
        "Siga rigorosamente o guia de estilo e a estrutura do relatório.",
    ]
    if style_guide:
        parts.extend(["", "GUIA DE ESTILO:", style_guide])

    approved_examples = [example for example in selection.examples if example.has_expected]
    if approved_examples:
        parts.extend(["", "EXEMPLOS APROVADOS PARA IMITAR O PADRÃO:"])
        for index, example in enumerate(approved_examples, start=1):
            parts.extend(
                [
                    "",
                    f"EXEMPLO {index}: {example.title}",
                    f"TAGS: {', '.join(example.tags)}",
                    "SAÍDA APROVADA:",
                    clip_text(example.expected_text, 3600),
                ]
            )

    if local_draft.strip():
        parts.extend(
            [
                "",
                "RASCUNHO LOCAL ESTRUTURADO:",
                "Use como apoio de campos e cálculos, mas melhore a redação técnica quando necessário.",
                clip_text(local_draft, 4200),
            ]
        )

    parts.extend(
        [
            "",
            "DADOS BRUTOS DA VISITA:",
            raw_text.strip(),
            "",
            "TAREFA:",
            "Gere apenas o relatório técnico final, sem explicações adicionais, mantendo as seções obrigatórias.",
        ]
    )
    return "\n".join(parts).strip() + "\n"


def clip_text(value: str, max_chars: int) -> str:
    text = value.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[trecho reduzido]"
