from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
import uuid
from copy import copy
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, TwoCellAnchor
from openpyxl.worksheet.worksheet import Worksheet
from PIL import Image, ImageOps

from .field_mapping import (
    DATE_FIELDS,
    EQUIPMENT_COLUMNS,
    EQUIPMENT_END_ROW,
    EQUIPMENT_START_ROW,
    FIELD_ALIASES,
    FIELD_TO_CELL,
    INSUMO_ROWS,
    PERSPECTIVA_ROWS,
    PHOTO_ANCHORS,
    PHOTO_MAX_SIZE,
    SHEET_NAME,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT_DIR / "templates" / "relatorio-modelo.xlsx"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "outputs"


def normalize_key(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", str(value))
    without_accents = "".join(ch for ch in without_accents if not unicodedata.combining(ch))
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", without_accents.lower()).strip("_")
    return normalized


def parse_report_data(raw: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, dict):
        return normalize_data(raw)

    text = (raw or "").strip()
    if not text:
        return {}

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return normalize_data(parsed)
    except json.JSONDecodeError:
        pass

    data: dict[str, Any] = {}
    current_key: str | None = None
    loose_lines: list[str] = []

    for original_line in text.splitlines():
        line = original_line.strip()
        if not line:
            if current_key:
                data[current_key] = f"{data[current_key]}\n"
            continue

        match = re.match(r"^([^:=-]{2,80})\s*[:=-]\s*(.+)$", line)
        if match:
            key = FIELD_ALIASES.get(normalize_key(match.group(1)), normalize_key(match.group(1)))
            data[key] = clean_text_value(match.group(2))
            current_key = key
        elif current_key:
            data[current_key] = f"{data[current_key]}\n{line}".strip()
        else:
            loose_lines.append(line)

    if loose_lines:
        data["raw_text"] = "\n".join(loose_lines)

    data.update(parse_narrative_report(text))

    return normalize_data(data)


def parse_narrative_report(text: str) -> dict[str, Any]:
    compact = normalize_spaces(text)
    data: dict[str, Any] = {}

    labeled_fields = {
        "cliente": r"Cliente|Produtor|Mutuário|Mutuario",
        "data_visita": r"Data da visita|Data de visita|Data",
        "cpf_cnpj": r"CPF/CNPJ|CNPJ/CPF|CPF|CNPJ",
        "cidade_uf": r"Município/UF|Municipio/UF|Município|Municipio|Cidade/UF|Cidade",
        "localizacao_1": r"Localização|Localizacao|Endereço/localização|Endereco/localizacao",
        "imovel_nome": r"Nome da propriedade",
        "tipo_exploracao": r"Tipo de exploração|Tipo de exploracao",
        "atividades_desenvolvidas": r"Atividades desenvolvidas",
        "situacao_produtiva": r"Situação produtiva|Situacao produtiva",
        "area_total_ha": r"Área Total \(ha\)|Area Total \(ha\)",
        "area_pastagens_ha": r"Área de Pastagens \(ha\)|Area de Pastagens \(ha\)",
        "area_cultivo_ha": r"Área de Cultivo \(ha\)|Area de Cultivo \(ha\)",
        "atividade_principal": r"Atividade principal desenvolvida",
        "principais_culturas": r"Principais culturas",
    }
    label_patterns = list(labeled_fields.values())
    section_patterns = [
        r"\d+\.\s*TIPO",
        r"\d+\.\s*DESCRIÇÃO|DESCRICAO",
        r"INVESTIMENTOS EM ANDAMENTO",
        r"OUTROS COMENTÁRIOS|OUTROS COMENTARIOS",
        r"CONCLUSÃO|CONCLUSAO",
        r"FRASES DIRETAS",
    ]
    stop_pattern = "|".join([rf"(?:{pattern})\s*:" for pattern in label_patterns] + section_patterns)

    for field, label_pattern in labeled_fields.items():
        value = extract_after_label(compact, label_pattern, stop_pattern)
        if value:
            data[field] = value

    for area_field in ("area_total_ha", "area_pastagens_ha", "area_cultivo_ha"):
        if data.get(area_field):
            data[area_field] = parse_decimal_pt(data[area_field])

    if data.get("area_total_ha") not in (None, "") and data.get("area_pastagens_ha") not in (None, "") and not data.get("area_cultivo_ha"):
        data["area_cultivo_ha"] = round(float(data["area_total_ha"]) - float(data["area_pastagens_ha"]), 2)

    if not data.get("atividade_principal") and data.get("atividades_desenvolvidas"):
        data["atividade_principal"] = data["atividades_desenvolvidas"]

    benfeitorias = extract_section(
        compact,
        r"\d+\.\s*TIPO\s*\(Benfeitorias e Infraestrutura\)",
        [r"\d+\.\s*DESCRIÇÃO", r"\d+\.\s*DESCRICAO", r"INVESTIMENTOS EM ANDAMENTO"],
    )
    if benfeitorias:
        data["benfeitorias_descricao"] = benfeitorias
        data.setdefault("benfeitorias_conservacao", "BOM")
        data.setdefault(
            "benfeitorias_observacoes",
            "Estrutura compativel com a escala produtiva informada.",
        )

    equipamentos = extract_section(
        compact,
        r"\d+\.\s*DESCRIÇÃO\s*\(Máquinas, Equipamentos e Implementos\)|\d+\.\s*DESCRICAO\s*\(Maquinas, Equipamentos e Implementos\)",
        [r"INVESTIMENTOS EM ANDAMENTO"],
    )
    if equipamentos:
        data["equipamentos"] = parse_equipment_section(equipamentos)

    investimentos = extract_section(
        compact,
        r"INVESTIMENTOS EM ANDAMENTO\s*\(Comentários\)|INVESTIMENTOS EM ANDAMENTO\s*\(Comentarios\)",
        [r"OUTROS COMENTÁRIOS", r"OUTROS COMENTARIOS", r"CONCLUSÃO", r"CONCLUSAO"],
    )
    if investimentos:
        data["investimentos_comentarios"] = investimentos

    outros = extract_section(
        compact,
        r"OUTROS COMENTÁRIOS|OUTROS COMENTARIOS",
        [r"CONCLUSÃO", r"CONCLUSAO", r"FRASES DIRETAS"],
    )
    if outros:
        data["outros_comentarios"] = outros

    conclusao = extract_section(
        compact,
        r"CONCLUSÃO|CONCLUSAO",
        [r"FRASES DIRETAS"],
    )
    if conclusao:
        data["conclusao"] = conclusao

    frase_direta = extract_section(
        compact,
        r"FRASES? DIRETAS?\s*(?:\(PADRÃO DE MATRÍCULA/VISUALIZAÇÃO\)|\(PADRAO DE MATRICULA/VISUALIZACAO\))?",
        [],
    )
    if frase_direta:
        data["insumos_comentarios"] = frase_direta

    city = extract_city(compact)
    if city:
        data.setdefault("cidade_uf", city)
        data.setdefault("localizacao_1", city)

    area_alqueires = extract_area_alqueires(compact)
    if area_alqueires:
        data["area_alqueires"] = area_alqueires

    client = extract_client_name(compact)
    if client:
        data["cliente"] = client

    rebanho = extract_rebanho(compact)
    if rebanho:
        data["rebanho"] = rebanho

    return data


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_text_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return value.strip().strip('"').strip("'").strip()


def extract_after_label(text: str, label_pattern: str, stop_pattern: str) -> str | None:
    match = re.search(
        rf"(?:{label_pattern})\s*:\s*(.*?)(?=\s*(?:{stop_pattern})|$)",
        text,
        flags=re.IGNORECASE,
    )
    return clean_text_value(match.group(1)) if match else None


def extract_section(text: str, start_pattern: str, end_patterns: list[str]) -> str | None:
    end_pattern = "|".join(end_patterns)
    lookahead = rf"(?=\s*(?:{end_pattern})|$)" if end_pattern else r"(?=$)"
    match = re.search(
        rf"(?:{start_pattern})\s*(.*?){lookahead}",
        text,
        flags=re.IGNORECASE,
    )
    return clean_text_value(match.group(1)) if match else None


def parse_decimal_pt(value: Any) -> float | Any:
    if isinstance(value, (int, float)):
        return value

    match = re.search(r"\d[\d.,]*", str(value))
    if not match:
        return value

    number = match.group(0)
    if "," in number and "." in number:
        decimal_separator = "," if number.rfind(",") > number.rfind(".") else "."
        thousand_separator = "." if decimal_separator == "," else ","
        number = number.replace(thousand_separator, "").replace(decimal_separator, ".")
    elif "," in number:
        number = number.replace(".", "").replace(",", ".")
    elif number.count(".") > 1:
        parts = number.split(".")
        number = "".join(parts[:-1]) + "." + parts[-1]
    elif "." in number:
        integer, decimal = number.split(".", 1)
        if len(decimal) == 3 and len(integer) <= 3:
            number = integer + decimal

    return float(number)


def extract_city(text: str) -> str | None:
    patterns = [
        r"município de\s+([A-ZÀ-ÚA-Za-zà-úÇçãõíóéâêôü\s]+-[A-Z]{2})",
        r"municipio de\s+([A-ZÀ-ÚA-Za-zà-úÇçãõíóéâêôü\s]+-[A-Z]{2})",
        r"localizad[oa]\s+em\s+([A-ZÀ-ÚA-Za-zà-úÇçãõíóéâêôü\s]+-[A-Z]{2})",
        r"\bem\s+([A-ZÀ-ÚA-Za-zà-úÇçãõíóéâêôü\s]+-[A-Z]{2})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return normalize_spaces(match.group(1))
    return None


def extract_area_alqueires(text: str) -> str | None:
    match = re.search(r"\((\d+(?:[.,]\d+)?)\s*alqueires?\)", text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def extract_client_name(text: str) -> str | None:
    match = re.search(
        r"produtor(?:a)?\s+(.+?)(?=\s+(?:está|esta|desenvolve|conduz|localizad[oa]|mantém|mantem)\b)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return clean_text_value(match.group(1))


def extract_rebanho(text: str) -> str | None:
    patterns = [
        r"plantel total informado\s+(?:é\s+de|e\s+de|de)\s+(.+?)(?=\.|$)",
        r"rebanho consolidado de\s+(.+?)(?=\.|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_text_value(match.group(1))
    return None


def parse_equipment_section(section: str) -> list[dict[str, Any]]:
    if re.search(
        r"não dispõe|nao dispoe|não informado|nao informado|não detalhou|nao detalhou",
        section,
        flags=re.IGNORECASE,
    ):
        return [
            {
                "descricao": "Não informado",
                "fabricante": "-",
                "modelo": "-",
                "estado": "BOM",
                "financiado_bb": "NÃO",
                "financiado_outros": "NÃO",
                "segurado": "NÃO",
                "gravame": "NÃO",
                "outras_informacoes": "Não há frota mecanizada própria ou sistema de irrigação declarado.",
            }
        ]
    description = extract_after_label(section, r"Descrição|Descricao", r"(?:Fabricante|Modelo)\s*:|$")
    manufacturer = extract_after_label(section, r"Fabricante", r"(?:Modelo|Estado)\s*:|$")
    model = extract_after_label(section, r"Modelo", r"(?:Estado|Conservação|Conservacao)\s*:|$")
    if description:
        return [
            {
                "descricao": description,
                "fabricante": manufacturer or "-",
                "modelo": model or "-",
                "estado": "BOM",
                "financiado_bb": "NÃO",
                "financiado_outros": "NÃO",
                "segurado": "NÃO",
                "gravame": "NÃO",
                "outras_informacoes": "",
            }
        ]
    return []


def normalize_data(data: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}

    for key, value in data.items():
        normalized_key = FIELD_ALIASES.get(normalize_key(key), normalize_key(key))

        if isinstance(value, dict):
            normalized[normalized_key] = normalize_nested_dict(value)
        elif isinstance(value, list):
            normalized[normalized_key] = value
        else:
            normalized[normalized_key] = value

    return normalized


def normalize_nested_dict(value: dict[str, Any]) -> dict[str, Any]:
    return {normalize_key(k): v for k, v in value.items()}


def generate_report(
    data_source: str | dict[str, Any],
    photo_paths: list[str | Path] | None = None,
    output_path: str | Path | None = None,
    template_path: str | Path = DEFAULT_TEMPLATE,
) -> Path:
    data = parse_report_data(data_source)
    template = Path(template_path)

    if not template.exists():
        raise FileNotFoundError(f"Modelo nao encontrado: {template}")

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    output = Path(output_path) if output_path else DEFAULT_OUTPUT_DIR / f"relatorio-gerado-{run_id}.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)

    workbook = load_workbook(template)
    worksheet = workbook[SHEET_NAME] if SHEET_NAME in workbook.sheetnames else workbook.active

    clear_variable_model_values(worksheet)
    apply_fields(worksheet, data)
    apply_equipment(worksheet, data.get("equipamentos", []))
    apply_insumos(worksheet, data.get("insumos", {}))
    apply_perspectivas(worksheet, data.get("perspectivas", {}))
    polish_written_ranges(worksheet)
    adjust_dynamic_row_heights(worksheet)
    apply_photos(worksheet, photo_paths or [], output.parent / f"{output.stem}-images")

    workbook.save(output)
    return output


def clear_variable_model_values(worksheet: Worksheet) -> None:
    for cell in ["B4", *FIELD_TO_CELL.values(), *(cell for cell, _ in DATE_FIELDS.values())]:
        set_cell(worksheet, cell, None)

    for cell in ["A27", "F27", "G27", "H27", "I27", "F30", "G30", "H30", "I30", "F32", "G32", "H32", "I32"]:
        set_cell(worksheet, cell, None)

    clear_equipment_rows(worksheet)
    clear_yes_no_area(worksheet, INSUMO_ROWS.values(), "E", "F", "G")
    clear_yes_no_area(worksheet, PERSPECTIVA_ROWS.values(), "F", "G", "H")
    clear_legacy_option_marks(worksheet)


def apply_fields(worksheet: Worksheet, data: dict[str, Any]) -> None:
    client_block = build_client_block(data)
    if client_block:
        set_cell(worksheet, "B4", client_block)

    if not data.get("finalidade_vistoria"):
        data["finalidade_vistoria"] = "VERIFICAÇÃO IN-LOCO DE REAIS CONDIÇÕES DE PRODUTIVIDADE DO CLIENTE EM QUESTÃO;"

    for field, cell in FIELD_TO_CELL.items():
        value = data.get(field)
        if value not in (None, ""):
            set_cell(worksheet, cell, value)

    for field, (cell, pattern) in DATE_FIELDS.items():
        value = data.get(field)
        if value not in (None, ""):
            set_cell(worksheet, cell, pattern.format(value))

    conservacao = normalize_key(str(data.get("benfeitorias_conservacao", "")))
    if conservacao:
        set_mark(worksheet, "F27", conservacao.startswith("bom"))
        set_mark(worksheet, "G27", conservacao.startswith("regular"))
        set_mark(worksheet, "H27", conservacao.startswith("ruim"))

    if data.get("raw_text") and not data.get("outros_comentarios"):
        set_cell(worksheet, "B181", data["raw_text"])


def build_client_block(data: dict[str, Any]) -> str | None:
    if data.get("resumo_cliente"):
        return str(data["resumo_cliente"])

    lines: list[str] = []
    for field in ("cliente", "cidade_uf"):
        if data.get(field):
            lines.append(str(data[field]))

    property_line = build_property_line(data)
    if property_line:
        lines.extend(["", property_line])

    activity_bits = []
    if data.get("atividade_principal"):
        activity_bits.append(str(data["atividade_principal"]))
    if data.get("rebanho"):
        activity_bits.append(str(data["rebanho"]))
    if data.get("fase"):
        activity_bits.append(str(data["fase"]))
    if activity_bits:
        lines.extend(["", " - ".join(activity_bits)])

    projects = data.get("futuros_projetos")
    if projects:
        lines.extend(["", "Futuros projetos"])
        if isinstance(projects, list):
            lines.extend(str(item) for item in projects if str(item).strip())
        else:
            lines.append(str(projects))

    return "\n".join(lines).strip() or None


def build_property_line(data: dict[str, Any]) -> str | None:
    name = data.get("imovel_nome")
    if not name:
        return None

    area_parts = []
    if data.get("area_alqueires"):
        area_parts.append(f"{data['area_alqueires']} alqueires")
    if data.get("area_total_ha"):
        area_parts.append(f"{data['area_total_ha']} ha")

    if area_parts:
        return f"{name} - {' / '.join(area_parts)}"
    return str(name)


def apply_equipment(worksheet: Worksheet, equipment: Any) -> None:
    clear_equipment_rows(worksheet)
    if not isinstance(equipment, list):
        return

    for index, item in enumerate(equipment[: EQUIPMENT_END_ROW - EQUIPMENT_START_ROW + 1]):
        if not isinstance(item, dict):
            continue
        row = EQUIPMENT_START_ROW + index
        normalized_item = normalize_nested_dict(item)
        for field, col in EQUIPMENT_COLUMNS.items():
            value = normalized_item.get(field)
            if value not in (None, ""):
                set_cell(worksheet, f"{col}{row}", value)


def apply_insumos(worksheet: Worksheet, insumos: Any) -> None:
    clear_yes_no_area(worksheet, INSUMO_ROWS.values(), "E", "F", "G")
    if not isinstance(insumos, dict):
        return

    for key, row in INSUMO_ROWS.items():
        item = insumos.get(key)
        if item is None:
            continue
        apply_yes_no_observation(worksheet, row, "E", "F", "G", item)


def apply_perspectivas(worksheet: Worksheet, perspectivas: Any) -> None:
    clear_yes_no_area(worksheet, PERSPECTIVA_ROWS.values(), "F", "G", "H")
    if not isinstance(perspectivas, dict):
        return

    normalized = normalize_nested_dict(perspectivas)
    for key, row in PERSPECTIVA_ROWS.items():
        item = normalized.get(key)
        if item is None:
            continue
        apply_yes_no_observation(worksheet, row, "F", "G", "H", item)


def apply_yes_no_observation(
    worksheet: Worksheet,
    row: int,
    yes_col: str,
    no_col: str,
    observation_col: str,
    item: Any,
) -> None:
    value = item
    observation = None

    if isinstance(item, dict):
        normalized_item = normalize_nested_dict(item)
        value = normalized_item.get("sim", normalized_item.get("valor", normalized_item.get("status")))
        observation = normalized_item.get("observacao", normalized_item.get("observacoes"))

    truthy = parse_bool(value)
    set_mark(worksheet, f"{yes_col}{row}", truthy is True)
    set_mark(worksheet, f"{no_col}{row}", truthy is False)
    if observation not in (None, ""):
        set_cell(worksheet, f"{observation_col}{row}", observation)


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    normalized = normalize_key(str(value))
    if normalized in {"sim", "s", "true", "x", "1", "yes"}:
        return True
    if normalized in {"nao", "n", "false", "0", "no"}:
        return False
    return None


def set_cell(worksheet: Worksheet, coordinate: str, value: Any) -> None:
    target = top_left_for_merged_cell(worksheet, coordinate)
    worksheet[target] = value


def set_mark(worksheet: Worksheet, coordinate: str, enabled: bool) -> None:
    target = top_left_for_merged_cell(worksheet, coordinate)
    cell = worksheet[target]
    cell.value = "X" if enabled else None
    cell.alignment = copy(cell.alignment)
    cell.alignment = Alignment(
        horizontal="center",
        vertical=cell.alignment.vertical or "center",
        wrap_text=cell.alignment.wrap_text,
    )
    cell.font = copy(cell.font)
    cell.font = Font(
        name=cell.font.name,
        size=cell.font.sz,
        bold=True,
        italic=cell.font.italic,
        color=cell.font.color,
        underline=cell.font.underline,
    )


def top_left_for_merged_cell(worksheet: Worksheet, coordinate: str) -> str:
    for merged_range in worksheet.merged_cells.ranges:
        if coordinate in merged_range:
            return merged_range.start_cell.coordinate
    return coordinate


def clear_equipment_rows(worksheet: Worksheet) -> None:
    rows = [40, *range(EQUIPMENT_START_ROW, EQUIPMENT_END_ROW + 2)]
    for row in rows:
        for col in EQUIPMENT_COLUMNS.values():
            set_cell(worksheet, f"{col}{row}", None)


def clear_yes_no_area(worksheet: Worksheet, rows: Any, yes_col: str, no_col: str, observation_col: str) -> None:
    for row in rows:
        for col in (yes_col, no_col, observation_col):
            set_cell(worksheet, f"{col}{row}", None)


def clear_legacy_option_marks(worksheet: Worksheet) -> None:
    option_cells = [
        "A150",
        "D150",
        "H150",
        "A151",
        "D151",
        "H151",
        *[f"B{row}" for row in range(154, 159)],
        *[f"B{row}" for row in range(161, 164)],
        *[f"B{row}" for row in range(166, 169)],
        "B171",
        "B172",
        "B175",
        "B176",
    ]
    for coordinate in option_cells:
        target = top_left_for_merged_cell(worksheet, coordinate)
        value = worksheet[target].value
        if isinstance(value, str):
            worksheet[target].value = re.sub(r"\(\s*[xX]\s*\)", "(   )", value)

    for coordinate in ["B172", "B176"]:
        target = top_left_for_merged_cell(worksheet, coordinate)
        value = worksheet[target].value
        if isinstance(value, str) and ":" in value:
            prefix = value.split(":", 1)[0].rstrip()
            worksheet[target].value = f"{prefix}: "


def polish_written_ranges(worksheet: Worksheet) -> None:
    wrap_cells = [
        "B4",
        "C8",
        "A12",
        "A18",
        "I18",
        "K18",
        "A27",
        "I27",
        "D93",
        "D105",
        "D129",
        "B144",
        "B181",
        "B190",
    ]
    for coordinate in wrap_cells:
        target = top_left_for_merged_cell(worksheet, coordinate)
        cell = worksheet[target]
        cell.alignment = copy(cell.alignment)
        cell.alignment = Alignment(
            horizontal=cell.alignment.horizontal,
            vertical=cell.alignment.vertical or "center",
            wrap_text=True,
        )

    for coordinate in ["D18", "E18", "F18", "G18", "H18"]:
        target = top_left_for_merged_cell(worksheet, coordinate)
        worksheet[target].number_format = "0.00"


def adjust_dynamic_row_heights(worksheet: Worksheet) -> None:
    header_value = worksheet[top_left_for_merged_cell(worksheet, "B4")].value
    if isinstance(header_value, str) and header_value.strip():
        line_count = header_value.count("\n") + 1
        worksheet.row_dimensions[4].height = max(96, min(210, line_count * 18 + 18))


def apply_photos(worksheet: Worksheet, photo_paths: list[str | Path], image_output_dir: Path) -> None:
    valid_photos = [Path(path) for path in photo_paths if Path(path).exists()]
    if not valid_photos:
        remove_old_report_photos(worksheet)
        return

    image_output_dir.mkdir(parents=True, exist_ok=True)
    remove_old_report_photos(worksheet)

    for index, photo_path in enumerate(valid_photos[: len(PHOTO_ANCHORS)]):
        prepared_path = prepare_photo(photo_path, image_output_dir, index + 1)
        image = ExcelImage(str(prepared_path))
        from_row, from_col, to_row, to_col = PHOTO_ANCHORS[index]
        image.anchor = TwoCellAnchor(
            editAs="twoCell",
            _from=AnchorMarker(row=from_row, col=from_col),
            to=AnchorMarker(row=to_row, col=to_col),
        )
        worksheet.add_image(image)


def remove_old_report_photos(worksheet: Worksheet) -> None:
    kept_images = []
    for image in getattr(worksheet, "_images", []):
        row = image_anchor_row(image)
        if row is None or row < 200:
            kept_images.append(image)
    worksheet._images = kept_images


def image_anchor_row(image: ExcelImage) -> int | None:
    anchor = getattr(image, "anchor", None)
    marker = getattr(anchor, "_from", None)
    if marker is None:
        return None
    return int(marker.row) + 1


def prepare_photo(photo_path: Path, output_dir: Path, index: int) -> Path:
    output_path = output_dir / f"foto-{index:02d}.jpg"
    with Image.open(photo_path) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail(PHOTO_MAX_SIZE, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", PHOTO_MAX_SIZE, "white")
        x = (PHOTO_MAX_SIZE[0] - image.width) // 2
        y = (PHOTO_MAX_SIZE[1] - image.height) // 2
        canvas.paste(image, (x, y))
        canvas.save(output_path, quality=88, optimize=True)
    return output_path


def collect_photos(photo_dir: str | Path | None) -> list[Path]:
    if not photo_dir:
        return []
    root = Path(photo_dir)
    if not root.exists():
        return []
    allowed = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    return sorted(path for path in root.iterdir() if path.suffix.lower() in allowed)


def load_data_argument(data_arg: str | None, data_file: str | None) -> str:
    if data_file:
        return Path(data_file).read_text(encoding="utf-8")
    return data_arg or ""


def copy_template_to_workspace(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera relatorio agronomico em Excel.")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="Caminho do modelo .xlsx")
    parser.add_argument("--data", default=None, help="JSON ou texto com campos no formato campo: valor")
    parser.add_argument("--data-file", default=None, help="Arquivo .json/.txt com os dados")
    parser.add_argument("--photos", default=None, help="Pasta com fotos")
    parser.add_argument("--out", default=None, help="Caminho do .xlsx gerado")
    args = parser.parse_args()

    data_text = load_data_argument(args.data, args.data_file)
    photos = collect_photos(args.photos)
    output = generate_report(data_text, photos, args.out, args.template)
    print(output)


if __name__ == "__main__":
    main()
