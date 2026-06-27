from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .report_engine import clean_text_value, normalize_key, parse_decimal_pt

ALQUEIRE_GOIANO_HA = 4.84


@dataclass
class PropertyNote:
    name: str
    area_alqueires: float | None = None
    status: str = ""
    lines: list[str] = field(default_factory=list)
    livestock: list[str] = field(default_factory=list)
    crops: list[str] = field(default_factory=list)
    crop_area_alqueires: float = 0.0
    livestock_area_alqueires: float = 0.0
    confinement_area_alqueires: float = 0.0
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
    properties: list[PropertyNote] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)


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
        if is_equipment_heading(normalized):
            in_equipment = True
            current_property = None
            continue

        if in_equipment:
            notes.equipment.append(normalize_equipment(line))
            continue

        rented = parse_rented_area_line(line)
        if rented:
            current_property = PropertyNote(**rented)
            notes.properties.append(current_property)
            continue

        header = parse_property_header(line)
        if header:
            current_property = PropertyNote(**header)
            notes.properties.append(current_property)
            continue

        simple_property_name = parse_property_name_line(line)
        if simple_property_name:
            current_property = PropertyNote(name=simple_property_name)
            notes.properties.append(current_property)
            continue

        if current_property:
            standalone_area = parse_standalone_alqueire_area(line)
            if standalone_area is not None and current_property.area_alqueires is None:
                current_property.area_alqueires = standalone_area
                current_property.lines.append(line)
                continue
            current_property.lines.append(line)
            classify_property_line(current_property, line)
            continue

        if not notes.client and looks_like_client_line(line):
            notes.client = clean_text_value(line)
            continue

        if re.search(r"\b(?:CPF|CNPJ)\b", line, flags=re.IGNORECASE):
            notes.cpf_cnpj = extract_labeled_value(line)
            continue

        if not notes.location and looks_like_location(line):
            notes.location = clean_text_value(line)

    return notes


def clean_line(value: str) -> str:
    line = str(value or "").strip()
    line = re.sub(r"\s+", " ", line)
    return line.strip(" -")


def is_equipment_heading(normalized: str) -> bool:
    return normalized in {
        "maquinarios",
        "maquinario",
        "maquinas",
        "maquinas_e_equipamentos",
        "equipamentos",
        "implementos",
    }


def parse_property_header(line: str) -> dict[str, Any] | None:
    match = re.match(
        r"^(?P<name>(?:Fazenda|S[ií]tio|Sitio|Ch[aá]cara|Chacara|Est[aâ]ncia|Estancia|Rancho|Gleba|Granja|Retiro|Lote|Im[oó]vel|Propriedade)\b.+?)\s*[-–]\s*(?P<area>\d+(?:[,.]\d+)?)\s*(?:alqueires?|aqueires?)(?P<tail>.*)$",
        line,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    raw_name = title_case_agro(clean_text_value(match.group("name")))
    area = parse_decimal_pt(match.group("area"))
    tail = clean_text_value(match.group("tail") or "")
    status = extract_status(tail)
    name = raw_name
    if status and status.lower() not in normalize_key(raw_name).replace("_", " "):
        name = f"{raw_name} ({status})"

    return {"name": name, "area_alqueires": float(area), "status": status}


def parse_property_name_line(line: str) -> str | None:
    if not re.match(
        r"^(?:Fazenda|S[ií]tio|Sitio|Ch[aá]cara|Chacara|Est[aâ]ncia|Estancia|Rancho|Gleba|Granja|Retiro)\b",
        line,
        flags=re.IGNORECASE,
    ):
        return None
    if re.search(r"\d+(?:[,.]\d+)?\s*(?:alqueires?|aqueires?)", line, flags=re.IGNORECASE):
        return None
    return title_case_agro(clean_text_value(line))


def parse_standalone_alqueire_area(line: str) -> float | None:
    match = re.match(r"^(?:aprox(?:imadamente)?\s*)?(\d+(?:[,.]\d+)?)\s*(?:alqueires?|aqueires?)$", line, flags=re.IGNORECASE)
    if not match:
        return None
    value = parse_decimal_pt(match.group(1))
    return float(value) if isinstance(value, (float, int)) else None


def parse_rented_area_line(line: str) -> dict[str, Any] | None:
    normalized = normalize_key(line)
    if not any(term in normalized for term in ("aluguel", "alugada", "alugado", "arrendada", "arrendado")):
        return None
    area = extract_alqueire_value(line)
    if area is None:
        return None
    label = "Propriedade Área Alugada" if "alug" in normalized else "Propriedade Área Arrendada"
    return {"name": label, "area_alqueires": area, "status": "arrendada"}


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
    area = extract_alqueire_value(line)

    if "futuros_projetos" in normalized or "projetos_futuros" in normalized:
        return

    if is_future_project_line(normalized):
        property_note.future_projects.append(normalize_future_project(line))
        return

    if normalized.startswith("confinamento"):
        add_unique(property_note.phases, "Confinamento")
        if area:
            property_note.confinement_area_alqueires += area
        property_note.livestock.append(line)
        return

    if is_livestock_line(normalized):
        property_note.livestock.append(line)
        phase = extract_phase_from_line(line)
        if phase:
            add_unique(property_note.phases, phase)
        if area:
            property_note.livestock_area_alqueires += area
        return

    if is_crop_line(normalized):
        property_note.crops.append(line)
        if area:
            property_note.crop_area_alqueires += area
        return

    if normalized in {"cria", "recria", "engorda", "terminacao"}:
        add_unique(property_note.phases, title_case_agro(line))
        return

    if is_pasture_line(normalized):
        add_unique(property_note.pastures, normalize_pasture(line))
        return

    if is_improvement_line(normalized):
        property_note.improvements.append(normalize_improvement(line))
        return

    if is_fish_line(normalized):
        property_note.comments.append(normalize_fish_line(line))
        return

    property_note.comments.append(line)


def extract_alqueire_value(line: str) -> float | None:
    match = re.search(r"(\d+(?:[,.]\d+)?)\s*(?:alqueires?|aqueires?)", line, flags=re.IGNORECASE)
    if not match:
        return None
    value = parse_decimal_pt(match.group(1))
    return float(value) if isinstance(value, (float, int)) else None


def extract_phase_from_line(line: str) -> str:
    normalized = normalize_key(line)
    if "recria" in normalized:
        return "Recria"
    if "cria" in normalized:
        return "Cria"
    if "terminacao" in normalized or "engorda" in normalized:
        return "Terminação"
    return ""


def is_livestock_line(normalized: str) -> bool:
    livestock_terms = {
        "cabeca",
        "cabecas",
        "gado",
        "nelore",
        "res",
        "reis",
        "reses",
        "garrote",
        "garrotes",
        "novilha",
        "novilhas",
        "vaca",
        "vacas",
        "bezerro",
        "bezerros",
        "boi",
        "bois",
    }
    return any(term in normalized.split("_") for term in livestock_terms)


def is_fish_line(normalized: str) -> bool:
    return any(term in normalized for term in ("peixe", "piscicultura", "tambaqui", "caranha", "piau"))


def is_future_project_line(normalized: str) -> bool:
    return any(term in normalized for term in ("reforma_de_pastagem", "reforma_pastagem", "aquisicao_de_gado", "aquisicao_animais"))


def is_pasture_line(normalized: str) -> bool:
    return any(term in normalized for term in ("pastagem", "patagem", "andropogon", "quicuia", "brachiarao", "braquiarao", "brach"))


def is_crop_line(normalized: str) -> bool:
    return any(term in normalized for term in ("lavoura", "cultivo", "milho", "soja", "mandioca", "sorgo"))


def is_improvement_line(normalized: str) -> bool:
    terms = (
        "placa",
        "solar",
        "fabrica",
        "racao",
        "trincheira",
        "silo",
        "curral",
        "galpao",
        "armazem",
        "armazenagem",
        "barracao",
        "casa",
        "energia",
        "poco",
        "artesiano",
        "represa",
        "tanque",
        "piquete",
        "cocho",
        "bebedouro",
        "corrego",
    )
    return any(term in normalized for term in terms)


def add_unique(values: list[str], value: str) -> None:
    key = normalize_key(value)
    if key and key not in {normalize_key(item) for item in values}:
        values.append(value)


def normalize_pasture(line: str) -> str:
    normalized = normalize_key(line)
    grasses: list[str] = []
    if "andropogon" in normalized:
        grasses.append("Andropogon")
    if "quicuia" in normalized:
        grasses.append("Quicuia")
    if "brach" in normalized or "bracg" in normalized or "braqui" in normalized:
        grasses.append("Braquiarão")
    if grasses:
        return "Pastagens de " + ", ".join(grasses)
    return title_case_agro(line.replace("Patagem", "Pastagem"))


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
    if "aquisicao" in normalized and ("gado" in normalized or "animais" in normalized):
        return "aquisição de animais"
    return line


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
    total_ha = alqueires_to_hectares(prop.area_alqueires)
    pasture_ha = alqueires_to_hectares(resolve_pasture_alqueires(prop))
    crop_ha = alqueires_to_hectares(resolve_crop_alqueires(prop))
    return [
        prop.name,
        f"Área Total (ha): {format_pt_number(total_ha)} ha",
        f"Área de Pastagens (ha): {format_pt_number(pasture_ha)} ha",
        f"Área de Cultivo (ha): {format_pt_number(crop_ha)} ha",
        f"Atividade principal desenvolvida: {property_activity(prop)}",
        f"Principais culturas: {property_cultures(prop)}",
        "",
    ]


def resolve_pasture_alqueires(prop: PropertyNote) -> float:
    if prop.livestock_area_alqueires:
        return prop.livestock_area_alqueires
    if (prop.pastures or prop.livestock) and prop.area_alqueires is not None:
        # Pastagem = area total menos o que for lavoura/confinamento declarado.
        # Sem lavoura declarada, toda a area vira pastagem (segue os modelos
        # reais; nao inventa divisao de cultivo).
        remaining = prop.area_alqueires - prop.crop_area_alqueires - prop.confinement_area_alqueires
        return max(remaining, 0.0)
    return 0.0


def resolve_crop_alqueires(prop: PropertyNote) -> float:
    # Cultivo so existe quando ha lavoura ou confinamento informados. Caso
    # contrario fica 0 (nunca uma fracao inventada da area total).
    return prop.crop_area_alqueires + prop.confinement_area_alqueires


def alqueires_to_hectares(value: float | None) -> float:
    if not value:
        return 0.0
    return round(float(value) * ALQUEIRE_GOIANO_HA, 2)


def property_activity(prop: PropertyNote) -> str:
    parts: list[str] = []
    if prop.livestock:
        if "Confinamento" in prop.phases:
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
        normalized = normalize_key(line)
        if "milho" in normalized:
            add_unique(crops, "Milho")
        elif "mandioca" in normalized:
            add_unique(crops, "Mandioca")
        elif "soja" in normalized:
            add_unique(crops, "Soja")
        elif "sorgo" in normalized:
            add_unique(crops, "Sorgo")
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


def render_improvements_section(notes: RawVisitNotes) -> str:
    paragraphs: list[str] = []
    for prop in notes.properties:
        details = []
        if prop.improvements:
            details.append(join_human(prop.improvements))
        if prop.livestock:
            details.append(f"atividade pecuária informada com {summarize_livestock(prop)}")
        if prop.crops:
            details.append(f"área agrícola destinada a {', '.join(extract_crop_names(prop.crops)).lower()}")
        if prop.pastures:
            details.append(", ".join(prop.pastures).lower())
        if prop.comments:
            details.append(join_human(prop.comments))
        if prop.future_projects:
            details.append("projetos futuros de " + join_human(prop.future_projects))
        if details:
            paragraphs.append(f"Na {prop.name}, foi informado {join_human(details)}.")
    if not paragraphs:
        return "Conforme as informações coletadas, não foram detalhadas benfeitorias específicas nas unidades produtivas."
    return "\n\n".join(paragraphs)


def summarize_livestock(prop: PropertyNote) -> str:
    normalized_lines = []
    for line in prop.livestock:
        text = re.sub(r"\s*-\s*\d+(?:[,.]\d+)?\s*alqueires?", "", line, flags=re.IGNORECASE)
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


def render_other_comments(notes: RawVisitNotes, activities: str, cultures: str) -> str:
    total_area = sum(alqueires_to_hectares(prop.area_alqueires) for prop in notes.properties)
    location = f" em {notes.location}" if notes.location else ""
    comments = [
        f"A exploração rural{location} apresenta perfil diversificado, com atuação em {activities.lower()}.",
        f"A área total informada corresponde a {format_pt_number(total_area)} hectares, considerando o fator técnico de {format_pt_number(ALQUEIRE_GOIANO_HA)} hectares por alqueire.",
    ]
    if cultures != "Não informado":
        comments.append(f"As principais culturas e suportes produtivos identificados foram: {cultures}.")
    tourism = [comment for prop in notes.properties for comment in prop.comments if "turismo" in normalize_key(comment)]
    if tourism:
        comments.append("Foi relatada exploração complementar de turismo rural em uma das propriedades, associada à disponibilidade hídrica e ao uso da casa para locação de finais de semana.")
    future_projects = [project for prop in notes.properties for project in prop.future_projects]
    if future_projects:
        comments.append(f"Foram informados projetos futuros de {join_human(future_projects)}, indicando planejamento de intensificação produtiva.")
    return " ".join(comments)


def render_conclusion(notes: RawVisitNotes, activities: str) -> str:
    client = notes.client or "O produtor"
    return (
        f"Conclui-se que {client} desenvolve atividade rural ativa, com base produtiva formada por {len(notes.properties)} unidade(s) "
        f"e exploração voltada a {activities.lower()}. As informações apresentadas demonstram estrutura operacional compatível com a escala declarada, "
        "recomendando-se a continuidade da análise de crédito rural após conferência documental, cadastral e patrimonial."
    )


def render_direct_phrase(notes: RawVisitNotes, activities: str) -> str:
    total_area = sum(alqueires_to_hectares(prop.area_alqueires) for prop in notes.properties)
    return (
        f"OPERAÇÃO AGROPECUÁRIA COM {len(notes.properties)} UNIDADE(S) PRODUTIVA(S), "
        f"ÁREA TOTAL INFORMADA DE {format_pt_number(total_area)} HECTARES E ATUAÇÃO EM {activities.upper()}."
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
