from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .report_engine import clean_text_value, format_cpf_cnpj, normalize_key, parse_decimal_pt

ALQUEIRE_GOIANO_HA = 4.84

_MONTH_NAMES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


@dataclass
class PropertyNote:
    name: str
    area_ha: float | None = None
    status: str = ""
    lines: list[str] = field(default_factory=list)
    livestock: list[str] = field(default_factory=list)
    crops: list[str] = field(default_factory=list)
    crop_area_ha: float = 0.0
    livestock_area_ha: float = 0.0
    confinement_area_ha: float = 0.0
    pasture_area_ha: float = 0.0
    head_count: int = 0
    phases: list[str] = field(default_factory=list)
    pastures: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)
    future_projects: list[str] = field(default_factory=list)


@dataclass
class RawVisitNotes:
    client: str = ""
    cpf_cnpj: str = ""
    location: str = ""
    visit_date: str = ""
    access: str = ""
    mentions_alqueires: bool = False
    properties: list[PropertyNote] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)

    @property
    def total_head_count(self) -> int:
        return sum(prop.head_count for prop in self.properties)


@dataclass
class TechnicalReportResult:
    report_text: str
    notes: RawVisitNotes
    source: str = "local-rules-v1"

    def to_payload(self) -> dict[str, Any]:
        return {
            "report_text": self.report_text,
            "source": self.source,
            "summary": {
                "client": self.notes.client,
                "properties": len(self.notes.properties),
                "equipment": len(self.notes.equipment),
            },
        }


def generate_technical_report(raw_text: str) -> TechnicalReportResult:
    notes = parse_raw_visit_notes(raw_text)
    report_text = render_technical_report(notes)
    return TechnicalReportResult(report_text=report_text, notes=notes)


def parse_raw_visit_notes(raw_text: str) -> RawVisitNotes:
    notes = RawVisitNotes()
    current_property: PropertyNote | None = None
    in_equipment = False

    for raw_line in raw_text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue

        normalized = normalize_key(line)
        if _ALQUEIRE_HINT_RE.search(line):
            notes.mentions_alqueires = True

        if not notes.visit_date:
            visit_date = parse_visit_date_line(line)
            if visit_date:
                notes.visit_date = visit_date
                continue

        if not notes.access:
            access = parse_access_line(line)
            if access:
                notes.access = access
                if not notes.location:
                    city = extract_city_from_access(access)
                    if city:
                        notes.location = city
                continue

        if is_equipment_heading(normalized):
            in_equipment = True
            current_property = None
            continue

        if in_equipment:
            notes.equipment.append(normalize_equipment(line))
            continue

        # Captura maquinas/implementos MESMO sem um cabecalho "Maquinarios".
        # Antes, sem esse cabecalho, as linhas de maquina viravam comentario da
        # propriedade e se perdiam (secao 3 vinha "Nao informado").
        if is_machine_line(normalized):
            notes.equipment.append(normalize_equipment(line))
            continue

        # Cabecalho de propriedade tem prioridade sobre a regra de area
        # arrendada: "Fazenda Morro Grande - 30 alqueires (arrendada)" deve
        # manter o nome da fazenda (com o status), nao virar rotulo generico.
        header = parse_property_header(line)
        if header:
            current_property = PropertyNote(**header)
            notes.properties.append(current_property)
            continue

        rented = parse_rented_area_line(line)
        if rented:
            current_property = PropertyNote(**rented)
            notes.properties.append(current_property)
            continue

        simple_property_name = parse_property_name_line(line)
        if simple_property_name:
            current_property = PropertyNote(name=simple_property_name)
            notes.properties.append(current_property)
            continue

        if current_property:
            standalone_area = parse_standalone_area(line)
            if standalone_area is not None and current_property.area_ha is None:
                current_property.area_ha = standalone_area
                current_property.lines.append(line)
                continue
            current_property.lines.append(line)
            classify_property_line(current_property, line)
            continue

        if not notes.client and looks_like_client_line(line):
            notes.client = clean_text_value(line)
            continue

        if re.search(r"\b(?:CPF|CNPJ)\b", line, flags=re.IGNORECASE):
            notes.cpf_cnpj = format_cpf_cnpj(extract_labeled_value(line))
            continue

        if not notes.location and looks_like_location(line):
            notes.location = clean_text_value(line)

    return notes


def clean_line(value: str) -> str:
    line = str(value or "").strip()
    line = re.sub(r"\s+", " ", line)
    return line.strip(" -")


_ALQUEIRE_HINT_RE = re.compile(r"\b(?:alqueires?|aqueires?|alq\.?)\b", re.IGNORECASE)
_NUMERIC_DATE_RE = r"\d{1,2}[\/.-]\d{1,2}[\/.-]\d{2,4}"


def parse_visit_date_line(line: str) -> str | None:
    """Extrai a data da visita das anotacoes brutas.

    Aceita rotulos ('Data da visita: 05/07/2026', 'Visita em 05/07/2026'),
    linhas que sao apenas a data e datas por extenso ('5 de julho de 2026').
    """
    labeled = re.search(
        rf"(?:data\s+d[ae]\s+visita|visita(?:\s+(?:realizada|efetuada|feita))?\s+(?:em|dia|no\s+dia)|data)\s*[:\-]?\s*({_NUMERIC_DATE_RE})",
        line,
        flags=re.IGNORECASE,
    )
    if labeled:
        return labeled.group(1)

    if re.fullmatch(_NUMERIC_DATE_RE, line.strip()):
        return line.strip()

    textual = re.search(
        r"(?:data\s+d[ae]\s+visita|visita(?:\s+(?:realizada|efetuada|feita))?|data)\s*[:\-]?\s*(?:em\s+|no\s+dia\s+|dia\s+)?(\d{1,2})\s+de\s+([a-zçã]+)\s+de\s+(\d{4})",
        line,
        flags=re.IGNORECASE,
    )
    if textual:
        month = _MONTH_NAMES.get(normalize_key(textual.group(2)))
        if month:
            return f"{int(textual.group(1)):02d}/{month:02d}/{textual.group(3)}"
    return None


def parse_access_line(line: str) -> str | None:
    match = re.match(
        r"^(?:vias?\s+de\s+acesso|acesso|como\s+chegar|rota|trajeto)\s*[:\-]\s*(.+)$",
        line,
        flags=re.IGNORECASE,
    )
    return clean_text_value(match.group(1)) if match else None


def extract_city_from_access(access: str) -> str | None:
    match = re.search(
        r"(?:saindo|partindo|a\s+partir)\s+de\s+([A-ZÀ-Ú][A-Za-zÀ-ÿ'\s]*?\s*-\s*[A-Z]{2})\b",
        access,
    )
    return clean_text_value(match.group(1)) if match else None


def is_equipment_heading(normalized: str) -> bool:
    return normalized in {
        "maquinarios",
        "maquinario",
        "maquinas",
        "maquinas_e_equipamentos",
        "equipamentos",
        "implementos",
    }


# Tipos de maquina/implemento reconheciveis mesmo sem cabecalho. Sao termos
# especificos (nao inclui "maquinario"/"galpao", para nao confundir com
# benfeitorias como "galpao de armazenagem de maquinarios").
_MACHINE_TERMS = {
    "trator", "tratores", "microtrator", "colheitadeira", "colhedora",
    "plantadeira", "semeadeira", "adubadeira", "pulverizador", "pulverizadora",
    "grade", "aradora", "niveladora", "arado", "subsolador", "sulcador",
    "escarificador", "caminhao", "caminhoneta", "caminhonete", "caminhonete",
    "moto", "motocicleta", "carreta", "reboque", "ensiladeira", "forrageira",
    "rocadeira", "rocadeiras", "guincho", "distribuidor", "distribuidora",
    "esparramador", "esparramadora", "esparramadeira", "vagao", "comboio",
    "retroescavadeira", "escavadeira", "empilhadeira", "enfardadeira",
    "ordenhadeira", "motoniveladora", "plataforma", "triturador", "batedeira",
    "carregadeira", "colhedeira",
}


def is_machine_line(normalized: str) -> bool:
    tokens = set(normalized.split("_"))
    return any(term in tokens for term in _MACHINE_TERMS)


def parse_property_header(line: str) -> dict[str, Any] | None:
    match = re.match(
        r"^(?P<name>(?:Fazenda|S[ií]tio|Sitio|Ch[aá]cara|Chacara|Est[aâ]ncia|Estancia|Rancho|Gleba|Granja|Retiro|Lote|Im[oó]vel|Propriedade)\b.+?)"
        r"\s*(?:[-–—,(]|\bcom\b|\bde\b)\s*"
        r"(?P<area>\d+(?:[,.]\d+)?)\s*(?P<unit>alqueires?|aqueires?|alq\.?|hectares?|ha)\b\)?(?P<tail>.*)$",
        line,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    raw_name = title_case_agro(clean_text_value(match.group("name")))
    area = _to_hectares(match.group("area"), match.group("unit"))
    tail = clean_text_value(match.group("tail") or "")
    status = extract_status(tail)
    name = raw_name
    if status and status.lower() not in normalize_key(raw_name).replace("_", " "):
        name = f"{raw_name} ({status})"

    return {"name": name, "area_ha": float(area) if area is not None else None, "status": status}


def parse_property_name_line(line: str) -> str | None:
    if not re.match(
        r"^(?:Fazenda|S[ií]tio|Sitio|Ch[aá]cara|Chacara|Est[aâ]ncia|Estancia|Rancho|Gleba|Granja|Retiro)\b",
        line,
        flags=re.IGNORECASE,
    ):
        return None
    if re.search(r"\d+(?:[,.]\d+)?\s*(?:alqueires?|aqueires?|hectares?|ha)\b", line, flags=re.IGNORECASE):
        return None
    return title_case_agro(clean_text_value(line))


def parse_standalone_area(line: str) -> float | None:
    match = re.match(
        r"^(?:aprox(?:imadamente)?\.?\s*|area\s+(?:total\s+)?(?:de\s+)?)?(\d+(?:[,.]\d+)?)\s*(alqueires?|aqueires?|alq\.?|hectares?|ha)$",
        line,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return _to_hectares(match.group(1), match.group(2))


def parse_rented_area_line(line: str) -> dict[str, Any] | None:
    normalized = normalize_key(line)
    if not any(term in normalized for term in ("aluguel", "alugada", "alugado", "arrendada", "arrendado")):
        return None
    area = extract_area_ha(line)
    if area is None:
        return None
    label = "Propriedade Área Alugada" if "alug" in normalized else "Propriedade Área Arrendada"
    return {"name": label, "area_ha": area, "status": "arrendada"}


def extract_status(value: str) -> str:
    match = re.search(r"\(([^)]+)\)", value or "")
    if not match:
        return ""
    status = clean_text_value(match.group(1))
    normalized = normalize_key(status)
    if "arrendada" in normalized or "arrendado" in normalized:
        return "arrendada"
    if "espolio" in normalized:
        return "Espólio"
    return status


def looks_like_client_line(line: str) -> bool:
    normalized = normalize_key(line)
    if len(line) > 90 or ":" in line:
        return False
    rejected = {"fazenda", "sitio", "chacara", "alqueire", "cabeca", "lavoura", "maquinario"}
    return not any(term in normalized for term in rejected)


def looks_like_location(line: str) -> bool:
    return bool(re.search(r"\b[A-Z]{2}\b", line)) or bool(re.search(r"\s-\s*[A-Z]{2}$", line))


def extract_labeled_value(line: str) -> str:
    match = re.match(r"^[^:]+:\s*(.+)$", line)
    return clean_text_value(match.group(1) if match else line)


def classify_property_line(property_note: PropertyNote, line: str) -> None:
    normalized = normalize_key(line)
    area = extract_area_ha(line)

    if "futuros_projetos" in normalized or "projetos_futuros" in normalized:
        return

    if is_future_project_line(normalized):
        property_note.future_projects.append(normalize_future_project(line))
        return

    if normalized.startswith("confinamento"):
        add_unique(property_note.phases, "Confinamento")
        if area:
            property_note.confinement_area_ha += area
        property_note.livestock.append(line)
        property_note.head_count += extract_head_count(line)
        return

    if is_livestock_line(normalized):
        property_note.livestock.append(line)
        property_note.head_count += extract_head_count(line)
        phase = extract_phase_from_line(line)
        if phase:
            add_unique(property_note.phases, phase)
        if area:
            property_note.livestock_area_ha += area
        return

    if is_crop_line(normalized):
        property_note.crops.append(line)
        if area:
            property_note.crop_area_ha += area
        return

    if normalized in {"cria", "recria", "engorda", "terminacao"}:
        add_unique(property_note.phases, title_case_agro(line))
        return

    if is_pasture_line(normalized):
        # "55 hectares de pastagem" -> area de pastagem (nao entra como cultura).
        if area:
            property_note.pasture_area_ha += area
        label = pasture_grass_label(line)
        if label:
            add_unique(property_note.pastures, label)
        return

    # Linhas longas sao narrativa (comentario), nao item de infraestrutura,
    # mesmo citando "casa"/"tanque" etc.
    if len(line) <= 90 and is_improvement_line(normalized):
        property_note.improvements.append(normalize_improvement(line))
        return

    if is_fish_line(normalized):
        property_note.comments.append(normalize_fish_line(line))
        return

    property_note.comments.append(line)


_AREA_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(alqueires?|aqueires?|alq\.?|hectares?|ha)\b", re.IGNORECASE)


def _to_hectares(value_text: str, unit: str) -> float | None:
    """Converte um valor + unidade para hectares. Alqueire goiano = 4,84 ha."""
    value = parse_decimal_pt(value_text)
    if not isinstance(value, (float, int)):
        return None
    unit = unit.lower()
    if unit.startswith("alq") or unit.startswith("aqu"):
        return round(float(value) * ALQUEIRE_GOIANO_HA, 2)
    return float(value)


def extract_area_ha(line: str) -> float | None:
    """Extrai a primeira area do texto, ja em hectares (aceita ha e alqueires)."""
    match = _AREA_RE.search(line)
    if not match:
        return None
    return _to_hectares(match.group(1), match.group(2))


def extract_phase_from_line(line: str) -> str:
    normalized = normalize_key(line)
    if "recria" in normalized:
        return "Recria"
    if "cria" in normalized:
        return "Cria"
    if "terminacao" in normalized or "engorda" in normalized:
        return "Terminação"
    return ""


_LIVESTOCK_TERMS = {
    "cabeca", "cabecas", "gado", "nelore", "angus", "brangus", "senepol",
    "tabapua", "guzera", "girolando", "res", "reis", "reses", "rebanho",
    "plantel", "garrote", "garrotes", "novilha", "novilhas", "novilho",
    "novilhos", "vaca", "vacas", "bezerro", "bezerros", "bezerra", "bezerras",
    "boi", "bois", "touro", "touros", "matriz", "matrizes", "bovino",
    "bovinos", "bufalo", "bufalos", "ovelha", "ovelhas", "ovino", "ovinos",
    "caprino", "caprinos", "cabra", "cabras", "suino", "suinos", "porco",
    "porcos", "leitao", "leitoes", "frango", "frangos", "galinha", "galinhas",
    "aves", "equino", "equinos", "cavalo", "cavalos",
}

_HEAD_COUNT_RE = re.compile(
    r"(\d+)_(?:cabecas?|cab|vacas?|bois?|boi|novilhas?|novilhos?|garrotes?|"
    r"bezerr\w+|touros?|matrizes|matriz|reses|animais|bovin\w+|bufal\w+|"
    r"ovelhas?|ovinos?|caprinos?|cabras?|suinos?|porcos?|leit(?:ao|oes)|"
    r"frangos?|galinhas?|aves|vitel\w+)(?:_|$)"
)

_MEASURE_UNIT_RE = re.compile(r"(?:^|_)(?:alqueires?|aqueires?|alq|hectares?|ha|litros?|metros?|kg|quilos?|arrobas?|toneladas?|sacas?|caixas?)(?:_|$)")


def is_livestock_line(normalized: str) -> bool:
    return any(term in normalized.split("_") for term in _LIVESTOCK_TERMS)


def extract_head_count(line: str) -> int:
    """Soma as cabecas declaradas na linha ('49 vacas e 2 bois' -> 51).

    Sem substantivo de rebanho apos o numero, aceita um numero solto no fim da
    linha ('Gado de corte nelore - 130' -> 130), desde que nao seja medida."""
    normalized = normalize_key(line)
    total = sum(int(value) for value in _HEAD_COUNT_RE.findall(normalized))
    if total:
        return total
    tail = re.search(r"_(\d{1,6})$", normalized)
    if tail and not _MEASURE_UNIT_RE.search(normalized):
        return int(tail.group(1))
    return 0


_DAIRY_TERMS = {"leite", "leiteira", "leiteiro", "lactacao", "ordenha", "girolando", "holandes", "holandesa", "jersey"}
_BEEF_TERMS = {"corte", "nelore", "angus", "brangus", "senepol", "tabapua", "guzera", "confinamento", "engorda", "terminacao"}


def property_livestock_profile(prop: PropertyNote) -> tuple[bool, bool]:
    """Devolve (leite, corte) conforme os termos declarados na propriedade."""
    tokens: set[str] = set()
    for line in prop.lines + prop.livestock + prop.comments:
        tokens.update(normalize_key(line).split("_"))
    dairy = bool(tokens & _DAIRY_TERMS)
    beef = bool(tokens & _BEEF_TERMS)
    return dairy, beef


def is_fish_line(normalized: str) -> bool:
    return any(term in normalized for term in ("peixe", "piscicultura", "tambaqui", "caranha", "piau"))


def is_future_project_line(normalized: str) -> bool:
    if any(term in normalized for term in ("reforma_de_pastagem", "reforma_pastagem", "reforma_de_cerca", "reforma_cerca", "correcao_de_solo")):
        return True
    return normalized.startswith(("aquisicao", "compra_de", "construcao_de", "ampliacao_de"))


def is_pasture_line(normalized: str) -> bool:
    if any(term in normalized for term in (
        "pastagem", "patagem", "pasto_", "andropogon", "quicuia", "brachiarao",
        "braquiarao", "brach", "braqui", "mombaca", "marandu", "panicum",
        "tifton", "humidicola", "decumbens", "capim",
    )):
        return True
    return "pasto" in normalized.split("_")


# Culturas reconhecidas por token (singular/plural), na ordem de exibicao.
_CROP_LABELS: list[tuple[tuple[str, ...], str]] = [
    (("milho",), "Milho"),
    (("mandioca",), "Mandioca"),
    (("soja",), "Soja"),
    (("sorgo",), "Sorgo"),
    (("feijao",), "Feijão"),
    (("cana",), "Cana-de-açúcar"),
    (("cafe",), "Café"),
    (("arroz",), "Arroz"),
    (("algodao",), "Algodão"),
    (("girassol",), "Girassol"),
    (("amendoim",), "Amendoim"),
    (("trigo",), "Trigo"),
    (("aveia",), "Aveia"),
    (("milheto",), "Milheto"),
    (("banana", "bananal"), "Banana"),
    (("laranja", "citros", "citrus"), "Citros"),
    (("eucalipto",), "Eucalipto"),
    (("seringueira",), "Seringueira"),
    (("tomate",), "Tomate"),
    (("batata",), "Batata"),
    (("abobora",), "Abóbora"),
    (("melancia",), "Melancia"),
    (("maracuja",), "Maracujá"),
    (("alho",), "Alho"),
    (("cebola",), "Cebola"),
    (("abacaxi",), "Abacaxi"),
    (("mamao",), "Mamão"),
    (("manga",), "Manga"),
    (("uva",), "Uva"),
    (("hortalica", "hortalicas", "horta"), "Hortaliças"),
]

_CROP_CONTEXT_TOKENS = {"lavoura", "lavouras", "cultivo", "cultura", "culturas", "plantio", "plantacao", "safra", "roca"}
_CROP_TOKENS = {token for tokens, _ in _CROP_LABELS for token in tokens} | {f"{token}s" for tokens, _ in _CROP_LABELS for token in tokens}


def is_crop_line(normalized: str) -> bool:
    tokens = set(normalized.split("_"))
    return bool(tokens & (_CROP_CONTEXT_TOKENS | _CROP_TOKENS))


# Termos de benfeitoria: casados por substring (compostos/derivados) ou por
# token exato (palavras curtas que gerariam falso positivo por substring).
_IMPROVEMENT_SUBSTRINGS = (
    "placa", "solar", "fotovolta", "fabrica", "racao", "trincheira", "silo",
    "curral", "galpao", "armazem", "armazenagem", "barracao", "casa",
    "energia", "poco", "artesiano", "represa", "tanque", "piquete", "cocho",
    "bebedouro", "corrego", "cerca", "mangueira", "estabulo", "ordenha",
    "aprisco", "pocilga", "chiqueiro", "aviario", "estufa", "irrigacao",
    "alojamento", "esterqueira", "biodigestor", "embarcadouro", "embarcador",
    "resfriador", "cisterna", "escritorio", "refeitorio", "balanca",
    "nascente", "acude", "reservatorio", "caixa_d",
)
_IMPROVEMENT_TOKENS = {"brete", "tronco", "sede", "pivo", "rio", "barraco"}


def is_improvement_line(normalized: str) -> bool:
    # "cerca de 30 ..." e aproximacao numerica, nao benfeitoria.
    if re.match(r"^cerca_de_\d", normalized):
        return False
    if any(term in normalized for term in _IMPROVEMENT_SUBSTRINGS):
        return True
    return bool(set(normalized.split("_")) & _IMPROVEMENT_TOKENS)


def add_unique(values: list[str], value: str) -> None:
    key = normalize_key(value)
    if key and key not in {normalize_key(item) for item in values}:
        values.append(value)


def pasture_grass_label(line: str) -> str:
    """Devolve 'Pastagens de <capins>' quando a linha cita um capim; caso
    contrario devolve '' (ex.: '55 hectares de pastagem' nao vira 'cultura')."""
    normalized = normalize_key(line)
    grasses: list[str] = []
    if "andropogon" in normalized:
        grasses.append("Andropogon")
    if "quicuia" in normalized or "kikuyu" in normalized:
        grasses.append("Quicuia")
    if "mombaca" in normalized:
        grasses.append("Mombaça")
    if "panicum" in normalized:
        grasses.append("Panicum")
    if "marandu" in normalized:
        grasses.append("Marandu")
    if "tifton" in normalized:
        grasses.append("Tifton")
    if "humidicola" in normalized:
        grasses.append("Humidícola")
    if "decumbens" in normalized:
        grasses.append("Decumbens")
    if "brach" in normalized or "bracg" in normalized or "braqui" in normalized or "brizanth" in normalized:
        grasses.append("Braquiária")
    seen: set[str] = set()
    unique = [g for g in grasses if not (g in seen or seen.add(g))]
    return "Pastagens de " + ", ".join(unique) if unique else ""


def normalize_improvement(line: str) -> str:
    replacements = {
        "fabrica de raçao": "fábrica de ração",
        "fabrica de racao": "fábrica de ração",
        "trincheira para armazenar silo": "trincheiras para armazenagem de silo",
        "galpão armazenagem maquinario": "galpão para armazenagem de maquinário",
        "galpao armazenagem maquinario": "galpão para armazenagem de maquinário",
        "placas solar": "placas solares",
    }
    normalized = normalize_key(line)
    text = line
    for source, target in replacements.items():
        if normalize_key(source) in normalized:
            text = re.sub(source, target, text, flags=re.IGNORECASE)
    return text


def normalize_fish_line(line: str) -> str:
    return re.sub(r"\bpeixe\b", "piscicultura", line, flags=re.IGNORECASE)


def normalize_future_project(line: str) -> str:
    normalized = normalize_key(line)
    if "reforma" in normalized and "pastagem" in normalized:
        return "reforma de pastagens"
    if "reforma" in normalized and "cerca" in normalized:
        return "reforma de cercas"
    if "correcao" in normalized and "solo" in normalized:
        return "correção de solos"
    animal_terms = ("gado", "animais", "matriz", "matrizes", "bezerro", "bezerros", "novilha", "novilhas", "vacas")
    if ("aquisicao" in normalized or "compra" in normalized) and any(term in normalized for term in animal_terms):
        return "aquisição de animais"
    machine_terms = ("maquina", "maquinas", "trator", "equipamento", "equipamentos", "implemento", "implementos", "caminhao")
    if ("aquisicao" in normalized or "compra" in normalized) and any(term in normalized for term in machine_terms):
        return "aquisição de máquinas e equipamentos"
    return lower_first(line)


def normalize_equipment(line: str) -> str:
    corrections = {
        "baldran": "Baldan",
        "new holand": "New Holland",
        "hoster": "Hoster",
        "frigorifio": "frigorífico",
        "vagao": "Vagão",
        "caminhao": "Caminhão",
        "bau": "baú",
        "calcario": "calcário",
    }
    text = line
    for source, target in corrections.items():
        text = re.sub(source, target, text, flags=re.IGNORECASE)
    return title_case_equipment(text)


def title_case_equipment(value: str) -> str:
    keep_lower = {"de", "da", "do", "para", "com", "e"}
    keep_upper = {"JF", "IVECO", "VOLVO"}
    words = []
    for word in value.split():
        clean = word.strip()
        upper = clean.upper()
        lower = clean.lower()
        if upper in keep_upper:
            words.append(upper)
        elif lower in keep_lower:
            words.append(lower)
        elif clean.isdigit():
            words.append(clean)
        else:
            words.append(clean[:1].upper() + clean[1:].lower())
    return " ".join(words)


def title_case_agro(value: str) -> str:
    keep_lower = {"de", "da", "do", "das", "dos", "e", "em", "para"}
    words = []
    for word in value.split():
        lower = word.lower()
        if lower in keep_lower:
            words.append(lower)
        else:
            words.append(word[:1].upper() + word[1:].lower())
    return " ".join(words)


def render_technical_report(notes: RawVisitNotes) -> str:
    properties = notes.properties
    property_names = "; ".join(prop.name for prop in properties) or "Não informado"
    activities = summarize_activities(properties)
    cultures = summarize_cultures(properties)

    sections = [
        "1. DISCRIMINAÇÃO",
        f"Cliente: {notes.client or 'Não informado'}",
    ]
    if notes.cpf_cnpj:
        sections.append(f"CPF/CNPJ: {notes.cpf_cnpj}")
    if notes.location:
        sections.append(f"Município/UF: {notes.location}")
    if notes.visit_date:
        sections.append(f"Data da visita: {notes.visit_date}")
    if notes.access:
        sections.append(f"Vias de acesso: {notes.access}")
    sections.extend(
        [
            f"Nome da propriedade: {property_names}",
            f"Tipo de exploração: {summarize_ownership(properties)}",
            f"Atividades desenvolvidas: {activities}",
            "Situação produtiva: Ativa e em exploração agropecuária",
            f"Atividade principal desenvolvida: {activities}",
            f"Principais culturas: {cultures}",
            "",
            "Dados de Área e Exploração por Propriedade:",
            "",
        ]
    )

    for prop in properties:
        sections.extend(render_property_discrimination(prop))

    sections.extend(
        [
            "2. TIPO (Benfeitorias e Infraestrutura)",
            render_improvements_section(notes),
            "3. DESCRIÇÃO (Máquinas, Equipamentos e Implementos)",
            render_equipment_section(notes.equipment),
            "INVESTIMENTOS EM ANDAMENTO (Comentários)",
            render_investments_section(notes),
            "OUTROS COMENTÁRIOS",
            render_other_comments(notes, activities, cultures),
            "CONCLUSÃO",
            render_conclusion(notes, activities),
            "FRASES DIRETAS (PADRÃO DE MATRÍCULA/VISUALIZAÇÃO)",
            render_direct_phrase(notes, activities),
        ]
    )
    return "\n".join(part for part in sections if part is not None).strip() + "\n"


def render_property_discrimination(prop: PropertyNote) -> list[str]:
    total_ha = float(prop.area_ha or 0.0)
    pasture_ha = resolve_pasture_ha(prop)
    crop_ha = resolve_crop_ha(prop)
    return [
        prop.name,
        f"Área Total (ha): {format_pt_number(total_ha)} ha",
        f"Área de Pastagens (ha): {format_pt_number(pasture_ha)} ha",
        f"Área de Cultivo (ha): {format_pt_number(crop_ha)} ha",
        f"Atividade principal desenvolvida: {property_activity(prop)}",
        f"Principais culturas: {property_cultures(prop)}",
        "",
    ]


def resolve_pasture_ha(prop: PropertyNote) -> float:
    # 1) Pastagem informada explicitamente ("55 hectares de pastagem").
    if prop.pasture_area_ha:
        return prop.pasture_area_ha
    if prop.livestock_area_ha:
        return prop.livestock_area_ha
    # 2) Sem valor explicito: pastagem = area total menos lavoura/confinamento.
    #    Sem lavoura declarada, toda a area vira pastagem (nao inventa cultivo).
    if (prop.pastures or prop.livestock) and prop.area_ha is not None:
        remaining = prop.area_ha - prop.crop_area_ha - prop.confinement_area_ha
        return round(max(remaining, 0.0), 2)
    return 0.0


def resolve_crop_ha(prop: PropertyNote) -> float:
    # Cultivo so existe quando ha lavoura ou confinamento informados. Caso
    # contrario fica 0 (nunca uma fracao inventada da area total).
    return round(prop.crop_area_ha + prop.confinement_area_ha, 2)


def property_activity(prop: PropertyNote) -> str:
    parts: list[str] = []
    if prop.livestock:
        dairy, beef = property_livestock_profile(prop)
        if dairy and beef:
            parts.append("Pecuária mista (Leite e Corte)")
        elif dairy:
            parts.append("Pecuária leiteira")
        elif "Confinamento" in prop.phases:
            parts.append("Pecuária de corte em confinamento")
        elif prop.phases:
            parts.append(f"Pecuária de corte ({', '.join(prop.phases)})")
        else:
            parts.append("Pecuária de corte")
    if prop.crops:
        parts.append(f"Lavoura de {', '.join(extract_crop_names(prop.crops))}")
    if any(is_fish_line(normalize_key(comment)) for comment in prop.comments):
        parts.append("Piscicultura")
    if any("turismo" in normalize_key(comment) for comment in prop.comments):
        parts.append("Turismo rural")
    return join_human(parts) or "Exploração agropecuária"


def property_cultures(prop: PropertyNote) -> str:
    values = extract_crop_names(prop.crops)
    for pasture in prop.pastures:
        add_unique(values, pasture)
    if prop.livestock and not values:
        values.append("Pastagens e suporte alimentar ao rebanho")
    if any(is_fish_line(normalize_key(comment)) for comment in prop.comments):
        add_unique(values, "Lâmina d'água para piscicultura")
    return ", ".join(values) if values else "Não informado"


def extract_crop_names(lines: list[str]) -> list[str]:
    crops: list[str] = []
    for line in lines:
        tokens = set(normalize_key(line).split("_"))
        for crop_tokens, label in _CROP_LABELS:
            candidates = set(crop_tokens) | {f"{token}s" for token in crop_tokens}
            if tokens & candidates:
                add_unique(crops, label)
    return crops


def summarize_ownership(properties: list[PropertyNote]) -> str:
    statuses = {normalize_key(prop.status): prop.status for prop in properties if prop.status}
    if not statuses:
        return "Própria"
    labels = ["Própria"]
    if "arrendada" in statuses:
        labels.append("arrendada")
    if "espolio" in statuses:
        labels.append("Espólio")
    return join_human(labels) + ", conforme informado"


def summarize_activities(properties: list[PropertyNote]) -> str:
    values: list[str] = []
    for prop in properties:
        for item in property_activity(prop).split(" e "):
            add_unique(values, item)
    return join_human(values) or "Exploração agropecuária"


def summarize_cultures(properties: list[PropertyNote]) -> str:
    values: list[str] = []
    for prop in properties:
        for item in property_cultures(prop).split(", "):
            add_unique(values, item)
    return ", ".join(values) if values else "Não informado"


def property_block_opener(name: str) -> str:
    """Prefixo 'Na/No <propriedade>' com a preposicao correta pelo tipo."""
    masculine = re.match(r"\s*(S[ií]tio|Sitio|Rancho|Retiro|Lote|Im[oó]vel)\b", name, flags=re.IGNORECASE)
    return f"No {name}" if masculine else f"Na {name}"


def lower_first(value: str) -> str:
    text = clean_text_value(value)
    if not text or text[0].isdigit():
        return text
    return text[0].lower() + text[1:]


def render_improvements_section(notes: RawVisitNotes) -> str:
    paragraphs: list[str] = []
    for prop in notes.properties:
        sentences: list[str] = []

        if prop.improvements:
            items = join_human([lower_first(item) for item in prop.improvements])
            sentences.append(f"a infraestrutura declarada compreende {items}")

        if prop.livestock:
            livestock_text = summarize_livestock(prop)
            details: list[str] = []
            if "Confinamento" in prop.phases:
                confinement = "manejo em regime de confinamento"
                if prop.confinement_area_ha:
                    confinement += f" em área de {format_pt_number(prop.confinement_area_ha)} ha"
                details.append(confinement)
            other_phases = [phase for phase in prop.phases if phase != "Confinamento"]
            if other_phases:
                details.append(f"condução nas fases de {join_human(other_phases).lower()}")
            lines_with_heads = sum(1 for line in prop.livestock if extract_head_count(line) > 0)
            if prop.head_count and lines_with_heads > 1:
                details.append(f"plantel declarado de {format_pt_int(prop.head_count)} cabeças")
            sentence = f"a atividade pecuária informada compreende {lower_first(livestock_text)}"
            if details:
                sentence += f", com {join_human(details)}"
            if livestock_text:
                sentences.append(sentence)
            elif details:
                sentences.append(f"a atividade pecuária declarada tem {join_human(details)}")

        if prop.crops:
            crops = ", ".join(extract_crop_names(prop.crops)).lower()
            sentence = f"a área agrícola destina-se à lavoura de {crops}"
            if prop.crop_area_ha:
                sentence += f", em {format_pt_number(prop.crop_area_ha)} ha declarados"
            sentences.append(sentence)

        if prop.pastures:
            grasses = join_human([pasture.removeprefix("Pastagens de ") for pasture in prop.pastures])
            sentence = f"as pastagens declaradas são formadas por {grasses}"
            if prop.pasture_area_ha:
                sentence += f", em {format_pt_number(prop.pasture_area_ha)} ha informados"
            sentences.append(sentence)

        if prop.comments:
            sentences.append(f"registra-se ainda: {join_human([lower_first(comment) for comment in prop.comments])}")

        if not sentences:
            continue

        opener = property_block_opener(prop.name)
        first, *rest = sentences
        block = f"{opener}, {first}."
        if rest:
            block += " " + " ".join(f"{sentence[0].upper()}{sentence[1:]}." for sentence in rest)
        paragraphs.append(block)

    if not paragraphs:
        return "Conforme as informações coletadas, não foram detalhadas benfeitorias específicas nas unidades produtivas."
    return "\n\n".join(paragraphs)


def summarize_livestock(prop: PropertyNote) -> str:
    normalized_lines = []
    for line in prop.livestock:
        # Linhas de confinamento sao descritas a parte (fase + area).
        if normalize_key(line).startswith("confinamento"):
            continue
        text = re.sub(r"\s*-\s*\d+(?:[,.]\d+)?\s*(?:alqueires?|aqueires?|alq\.?|hectares?|ha)\b", "", line, flags=re.IGNORECASE)
        text = re.sub(r"\s*-\s*(?:cria|recria|engorda|termina[cç][aã]o|confinamento)\s*$", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*-\s*(\d{1,6})\s*$", r", totalizando \1 cabeças", text)
        normalized_lines.append(text)
    return join_human(normalized_lines)


def render_equipment_section(equipment: list[str]) -> str:
    if not equipment:
        return "Não informado"
    return "; ".join(equipment)


def render_investments_section(notes: RawVisitNotes) -> str:
    client = notes.client or "O produtor"
    future_projects = [project for prop in notes.properties for project in prop.future_projects]
    if future_projects:
        return (
            f"A atividade conduzida por {client} apresenta projetos futuros declarados de "
            f"{join_human(future_projects)}, com objetivo de melhorar a capacidade produtiva e ampliar a escala operacional."
        )
    if not notes.properties:
        return f"Não foram informados investimentos em andamento para {client}."
    return (
        f"As informações da visita indicam operação agropecuária conduzida por {client}, "
        f"com {len(notes.properties)} unidade(s) produtiva(s) e estrutura compatível com as atividades descritas. "
        "Não foram informados investimentos futuros específicos além das benfeitorias, lavouras, rebanho e maquinários declarados."
    )


# Evidencias de insumos declaradas nas anotacoes (rotulo humano -> termos).
_INPUT_EVIDENCE = (
    ("água", ("represa", "bebedouro", "poco", "artesiano", "corrego", "nascente", "acude", "cisterna", "reservatorio", "caixa_d", "tanque")),
    ("energia elétrica", ("placa", "solar", "fotovolta", "energia", "gerador", "trifasic", "rede_eletrica")),
    ("mão de obra", ("funcionario", "caseiro", "vaqueiro", "colaborador", "trabalhador", "peao", "peoes")),
    ("estrutura de armazenagem", ("galpao", "silo", "armazem", "barracao", "paiol", "tulha", "trincheira", "deposito")),
    ("estrutura de transporte", ("caminhao", "caminhoes", "caminhonete", "carreta", "frota")),
)


def detect_input_evidence(notes: RawVisitNotes) -> list[str]:
    parts: list[str] = list(notes.equipment)
    for prop in notes.properties:
        parts.extend(prop.improvements)
        parts.extend(prop.comments)
    blob = normalize_key(" ".join(parts))
    return [label for label, terms in _INPUT_EVIDENCE if any(term in blob for term in terms)]


def render_other_comments(notes: RawVisitNotes, activities: str, cultures: str) -> str:
    total_area = sum(float(prop.area_ha or 0.0) for prop in notes.properties)
    location = f" em {notes.location}" if notes.location else ""
    diversified = " e " in activities or "," in activities
    profile = "perfil diversificado, com atuação em" if diversified else "perfil voltado a"
    comments = [f"A exploração rural{location} apresenta {profile} {activities.lower()}."]

    area_sentence = f"A área total informada corresponde a {format_pt_number(total_area)} hectares"
    if notes.mentions_alqueires:
        area_sentence += f", considerando o fator técnico de {format_pt_number(ALQUEIRE_GOIANO_HA)} hectares por alqueire"
    comments.append(area_sentence + ".")

    total_heads = notes.total_head_count
    if total_heads:
        comments.append(f"O plantel total informado é de {format_pt_int(total_heads)} cabeças.")

    if notes.equipment:
        comments.append(
            f"O suporte de mecanização declarado reúne {len(notes.equipment)} "
            f"{'itens' if len(notes.equipment) > 1 else 'item'} entre máquinas, veículos e implementos."
        )

    evidence = detect_input_evidence(notes)
    if evidence:
        comments.append(f"As anotações evidenciam disponibilidade de {join_human(evidence)}.")

    if cultures != "Não informado":
        comments.append(f"As principais culturas e suportes produtivos identificados foram: {cultures}.")

    statuses = {normalize_key(prop.status) for prop in notes.properties if prop.status}
    if "arrendada" in statuses:
        comments.append("Parte das áreas declaradas é conduzida sob arrendamento.")
    if "espolio" in statuses:
        comments.append("Há área em condição de espólio, conforme informado.")

    tourism = [comment for prop in notes.properties for comment in prop.comments if "turismo" in normalize_key(comment)]
    if tourism:
        comments.append("Foi relatada exploração complementar de turismo rural em uma das propriedades, associada à disponibilidade hídrica e ao uso da casa para locação de finais de semana.")
    future_projects = [project for prop in notes.properties for project in prop.future_projects]
    if future_projects:
        comments.append(f"Foram informados projetos futuros de {join_human(future_projects)}, indicando planejamento de intensificação produtiva.")
    return " ".join(comments)


def render_conclusion(notes: RawVisitNotes, activities: str) -> str:
    client = notes.client or "O produtor"
    total_area = sum(float(prop.area_ha or 0.0) for prop in notes.properties)
    base = (
        f"Conclui-se que {client} desenvolve atividade rural ativa, com base produtiva formada por "
        f"{len(notes.properties)} unidade(s), área total informada de {format_pt_number(total_area)} hectares"
    )
    total_heads = notes.total_head_count
    if total_heads:
        base += f" e plantel declarado de {format_pt_int(total_heads)} cabeças"
    base += f", com exploração voltada a {activities.lower()}."
    support: list[str] = []
    if notes.equipment:
        support.append("suporte de mecanização próprio")
    if any(prop.improvements for prop in notes.properties):
        support.append("benfeitorias compatíveis com a atividade")
    if support:
        base += f" A estrutura declarada conta com {join_human(support)}."
    return (
        base
        + " As informações apresentadas demonstram estrutura operacional compatível com a escala declarada, "
        "recomendando-se a continuidade da análise de crédito rural após conferência documental, cadastral e patrimonial."
    )


def render_direct_phrase(notes: RawVisitNotes, activities: str) -> str:
    total_area = sum(float(prop.area_ha or 0.0) for prop in notes.properties)
    plantel = f", PLANTEL INFORMADO DE {format_pt_int(notes.total_head_count)} CABEÇAS" if notes.total_head_count else ""
    return (
        f"OPERAÇÃO AGROPECUÁRIA COM {len(notes.properties)} UNIDADE(S) PRODUTIVA(S), "
        f"ÁREA TOTAL INFORMADA DE {format_pt_number(total_area)} HECTARES{plantel} "
        f"E ATUAÇÃO EM {activities.upper()}."
    )


def join_human(values: list[str]) -> str:
    cleaned = [clean_text_value(value).strip(" .") for value in values if clean_text_value(value).strip(" .")]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    return ", ".join(cleaned[:-1]) + " e " + cleaned[-1]


def format_pt_number(value: float | int | None) -> str:
    number = 0.0 if value is None else float(value)
    text = f"{number:,.2f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_pt_int(value: float | int | None) -> str:
    number = 0 if value is None else int(round(float(value)))
    return f"{number:,}".replace(",", ".")
