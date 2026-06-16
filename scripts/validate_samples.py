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
