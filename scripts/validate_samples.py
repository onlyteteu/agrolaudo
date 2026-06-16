from __future__ import annotations

import json
from pathlib import Path
import sys

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from relatorio_app.report_engine import generate_report, parse_decimal_pt, parse_report_data
from server import parse_review_data

OUTPUT_DIR = ROOT / "outputs" / "validation"


CASES = [
    {
        "name": "wesley",
        "source": ROOT / "sample_gemini_text.txt",
        "output": OUTPUT_DIR / "wesley.xlsx",
        "fields": {
            "cliente": "Wesley Paulo",
            "cidade_uf": "Cromínia-GO",
            "imovel_nome": "Sítio Pedro Rosa (Fazenda Santa Bárbara)",
            "area_total_ha": 53.24,
            "area_pastagens_ha": 37.27,
            "area_cultivo_ha": 15.97,
            "atividade_principal": "Pecuária mista (Leite e Corte)",
            "principais_culturas": "Pastagens forrageiras destinadas ao pastejo do rebanho leiteiro e de corte",
        },
        "cells": {
            "A18": "Sítio Pedro Rosa (Fazenda Santa Bárbara)",
            "D18": 53.24,
            "E18": 37.27,
            "F18": 15.97,
            "F27": "X",
            "A51": "Não informado",
            "G40": None,
            "F30": None,
            "I30": None,
        },
    },
    {
        "name": "mandioca",
        "source": ROOT / "sample_mandioca_text.txt",
        "output": OUTPUT_DIR / "mandioca.xlsx",
        "fields": {
            "cliente": "Lúcio Mauro",
            "imovel_nome": "Fazenda Água Branca",
            "area_total_ha": 29.04,
            "area_pastagens_ha": 0.0,
            "area_cultivo_ha": 29.04,
            "atividade_principal": "Cultivo comercial de Mandioca (Manihot esculenta)",
            "principais_culturas": "Mandioca",
        },
        "cells": {
            "A18": "Fazenda Água Branca",
            "D18": 29.04,
            "E18": 0,
            "F18": 29.04,
            "F27": "X",
            "A51": "Não informado",
            "G40": None,
            "F30": None,
            "I30": None,
        },
    },
]


MULTIPLE_PROPERTY_TEXT = """
1. DISCRIMINACAO
Nomes das propriedades: Fazenda Boa Vista; Fazenda Santa Luzia
Area Total (ha): 120,50 ha
Area de Pastagens (ha): 80,00 ha
Area de Cultivo (ha): 40,50 ha
Atividade principal desenvolvida: Pecuaria de corte
Principais culturas: Pastagens
2. TIPO (Benfeitorias e Infraestrutura)
O produtor possui as fazendas Fazenda Boa Vista e Fazenda Santa Luzia localizadas no mesmo municipio.
OUTROS COMENTARIOS
As areas sao conduzidas de forma integrada.
CONCLUSAO
Atividade regular.
"""


def assert_equal(actual, expected, label: str) -> None:
    if isinstance(expected, float):
        if round(float(actual), 2) != round(expected, 2):
            raise AssertionError(f"{label}: esperado {expected!r}, veio {actual!r}")
        return
    if actual != expected:
        raise AssertionError(f"{label}: esperado {expected!r}, veio {actual!r}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for raw, expected in {"29,04 ha": 29.04, "29.04": 29.04, "1.234,56": 1234.56}.items():
        assert_equal(parse_decimal_pt(raw), expected, f"conversão numérica {raw}")

    multiple = parse_report_data(MULTIPLE_PROPERTY_TEXT)
    expected_properties = [{"nome": "Fazenda Boa Vista"}, {"nome": "Fazenda Santa Luzia"}]
    assert_equal(multiple.get("imovel_nome"), "Fazenda Boa Vista; Fazenda Santa Luzia", "multiplas propriedades campo imovel")
    assert_equal(multiple.get("imoveis"), expected_properties, "multiplas propriedades lista")

    multiple_output = generate_report(MULTIPLE_PROPERTY_TEXT, output_path=OUTPUT_DIR / "multiplas-propriedades.xlsx")
    multiple_worksheet = load_workbook(multiple_output).active
    assert_equal(multiple_worksheet["A18"].value, "Fazenda Boa Vista; Fazenda Santa Luzia", "multiplas propriedades celula A18")

    phrase = parse_report_data("O produtor explora as fazendas Fazenda Primavera e Fazenda Santa Clara localizadas em Morrinhos-GO.")
    assert_equal(phrase.get("imoveis"), [{"nome": "Fazenda Primavera"}, {"nome": "Fazenda Santa Clara"}], "multiplas propriedades em frase")

    from_json = parse_report_data({"imoveis": [{"nome": "Fazenda Modelo"}, {"nome": "Sitio Dois Irmaos"}]})
    assert_equal(from_json.get("imovel_nome"), "Fazenda Modelo; Sitio Dois Irmaos", "multiplas propriedades em JSON")

    photo_output = generate_report(
        CASES[0]["source"].read_text(encoding="utf-8"),
        sorted((ROOT / "sample_photos").glob("*.jpg")),
        OUTPUT_DIR / "fotos-com-moldura.xlsx",
    )
    photo_worksheet = load_workbook(photo_output).active
    report_photo_rows = [
        int(image.anchor._from.row) + 1
        for image in photo_worksheet._images
        if getattr(getattr(image, "anchor", None), "_from", None) is not None and int(image.anchor._from.row) + 1 >= 200
    ]
    assert_equal(report_photo_rows, [210, 229, 248], "posicao das fotos inseridas")
    assert_equal(photo_worksheet["D209"].value, "Foto 01", "legenda primeira foto")
    assert_equal(photo_worksheet["D228"].value, "Foto 02", "legenda segunda foto")
    assert_equal(photo_worksheet["D209"].border.top.style, "medium", "borda superior primeira foto")
    assert_equal(photo_worksheet["D209"].border.left.style, "medium", "borda esquerda primeira foto")
    assert_equal(photo_worksheet["J226"].border.right.style, "medium", "borda direita primeira foto")
    assert_equal(photo_worksheet["J226"].border.bottom.style, "medium", "borda inferior primeira foto")

    for case in CASES:
        text = case["source"].read_text(encoding="utf-8")
        parsed = parse_report_data(text)
        for field, expected in case["fields"].items():
            assert_equal(parsed.get(field), expected, f"{case['name']} campo {field}")

        output = generate_report(text, output_path=case["output"])
        worksheet = load_workbook(output).active
        for cell, expected in case["cells"].items():
            assert_equal(worksheet[cell].value, expected, f"{case['name']} célula {cell}")

        reviewed_fields = {field: str(parsed[field]) for field in case["fields"] if field.startswith("area_")}
        reviewed = parse_review_data(
            json.dumps({"parsed": parsed, "fields": reviewed_fields}, ensure_ascii=False),
            text,
        )
        reviewed_output = generate_report(reviewed, output_path=OUTPUT_DIR / f"{case['name']}-revisado.xlsx")
        reviewed_worksheet = load_workbook(reviewed_output).active
        for cell in ("D18", "E18", "F18"):
            assert_equal(reviewed_worksheet[cell].value, case["cells"][cell], f"{case['name']} revisão célula {cell}")

    print("OK: validações de extração e preenchimento concluídas.")


if __name__ == "__main__":
    main()
