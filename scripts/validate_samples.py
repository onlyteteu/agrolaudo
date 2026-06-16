from __future__ import annotations

import json
from pathlib import Path
import sys

from openpyxl import load_workbook
from PIL import Image

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


SANDRO_STYLE_TEXT = """
1. DISCRIMINACAO
Nome da propriedade: Complexo Agropecuario Teste (Fazendas: Boa Sorte, Sao Judas, Santa Camila, Sao Jose dos Anjicos e Santa Carolina)

Dados de Area e Exploracao por Propriedade:

Fazenda Boa Sorte
Area Total (ha): 3.388,00 ha
Area de Pastagens (ha): 2.371,60 ha
Area de Cultivo (ha): 1.016,40 ha
Atividade principal desenvolvida: Pecuaria de corte (Recria)
Principais culturas: Pastagens de Andropogon, Quicuia e Braquiarao

Fazenda Sao Judas
Area Total (ha): 2.429,68 ha
Area de Pastagens (ha): 1.700,78 ha
Area de Cultivo (ha): 728,90 ha
Atividade principal desenvolvida: Pecuaria de corte (Cria)
Principais culturas: Pastagens de Andropogon

Fazenda Santa Camila
Area Total (ha): 1.863,40 ha
Area de Pastagens (ha): 1.304,38 ha
Area de Cultivo (ha): 559,02 ha
Atividade principal desenvolvida: Pecuaria de corte (Cria)
Principais culturas: Pastagens de Quicuia

Fazenda Sao Jose dos Anjicos
Area Total (ha): 731,00 ha
Area de Pastagens (ha): 511,70 ha
Area de Cultivo (ha): 219,30 ha
Atividade principal desenvolvida: Pecuaria de corte (Recria estruturada)
Principais culturas: Pastagens de Andropogon

Fazenda Santa Carolina
Area Total (ha): 821,00 ha
Area de Pastagens (ha): 574,70 ha
Area de Cultivo (ha): 246,30 ha
Atividade principal desenvolvida: Pecuaria de corte (Terminacao)
Principais culturas: Pastagens de Andropogon

2. TIPO (Benfeitorias e Infraestrutura)
O complexo pecuario apresenta infraestrutura integrada e alto padrao tecnico.

INVESTIMENTOS EM ANDAMENTO (Comentarios)
Projeto com cinco unidades produtivas e manejo integrado.

OUTROS COMENTARIOS
Operacao conduzida em grande escala com controles mensais.

CONCLUSAO
Atividade regular e tecnicamente recomendada.

FRASES DIRETAS
COMPLEXO PECUARIO COM CINCO UNIDADES PRODUTIVAS INTEGRADAS.
"""


COLLAPSED_PROPERTY_TEXT = (
    "1. DISCRIMINACAONome da propriedade: Fazenda Beira Rio e Fazenda Val da Onca"
    "Tipo de exploracao: Propria"
    "Dados de Area e Exploracao por Propriedade:"
    "Fazenda Beira Rio"
    "Area Total (ha): 580,80 ha"
    "Area de Pastagens (ha): 406,56 ha"
    "Area de Cultivo (ha): 174,24 ha"
    "Atividade principal desenvolvida: Pecuaria mista"
    "Principais culturas: Pastagens forrageiras"
    "Fazenda Val da Onca"
    "Area Total (ha): 580,80 ha"
    "Area de Pastagens (ha): 406,56 ha"
    "Area de Cultivo (ha): 174,24 ha"
    "Atividade principal desenvolvida: Pecuaria mista"
    "Principais culturas: Pastagens forrageiras"
    "2. TIPO (Benfeitorias e Infraestrutura)"
    "O projeto agropecuario fica em duas unidades produtivas."
    "INVESTIMENTOS EM ANDAMENTO (Comentarios)"
    "Investimentos integrados."
    "OUTROS COMENTARIOS"
    "Comentarios tecnicos."
    "CONCLUSAO"
    "Atividade regular."
    "FRASES DIRETAS"
    "OPERACAO INTEGRADA EM DUAS FAZENDAS."
)


COLLAPSED_GROUP_TEXT = (
    "1. DISCRIMINACAONome da propriedade: Grupo Pedra (Unidades: Buriti e Aroeira)"
    "Dados de Area e Exploracao por Propriedade:"
    "Grupo Pedra - Unidade Buriti (Ituverava-SP)"
    "Area Total (ha): 1.432,35 ha"
    "Area de Pastagens (ha): 0,00 ha"
    "Area de Cultivo (ha): 1.432,35 ha"
    "Atividade principal desenvolvida: Cultivo comercial de Cana-de-Acucar"
    "Principais culturas: Cana-de-Acucar"
    "Grupo Pedra - Unidade Aroeira (Tupaciguara-MG)"
    "Area Total (ha): 1.800,00 ha"
    "Area de Pastagens (ha): 0,00 ha"
    "Area de Cultivo (ha): 1.800,00 ha"
    "Atividade principal desenvolvida: Cultivo comercial de Cana-de-Acucar e graos"
    "Principais culturas: Cana-de-Acucar, Soja e Amendoim"
    "2. TIPO (Benfeitorias e Infraestrutura)"
    "O complexo agricola apresenta estrutura operacional robusta."
)


DETAIL_PROPERTY_TEXT = (
    "1. DISCRIMINACAONome da propriedade: Fazenda Sao Jose e Fazenda Santo Antonio"
    "Dados de Area e Exploracao:"
    "Area Total (ha): 329,32 ha"
    "Area de Pastagens (ha): 230,52 ha"
    "Area de Cultivo (ha): 98,80 ha"
    "Atividade principal desenvolvida: Pecuaria de corte"
    "Principais culturas: Pastagens"
    "Detalhamento por Unidade (ha):"
    "Fazenda Sao Jose (Jaupaci-GO - 50,04 alqueires): 242,19 ha brutos / 169,53 ha de pastagens liquidas"
    "Fazenda Santo Antonio (Palmeiras-GO - 18,00 alqueires): 87,12 ha brutos / 60,99 ha de pastagens liquidas"
    "2. TIPO (Benfeitorias e Infraestrutura)"
    "As unidades possuem infraestrutura produtiva."
)


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
    assert_equal(multiple_worksheet["A18"].value, "Fazenda Boa Vista", "primeira propriedade celula A18")
    assert_equal(multiple_worksheet["A19"].value, "Fazenda Santa Luzia", "segunda propriedade celula A19")

    phrase = parse_report_data("O produtor explora as fazendas Fazenda Primavera e Fazenda Santa Clara localizadas em Morrinhos-GO.")
    assert_equal(phrase.get("imoveis"), [{"nome": "Fazenda Primavera"}, {"nome": "Fazenda Santa Clara"}], "multiplas propriedades em frase")

    from_json = parse_report_data({"imoveis": [{"nome": "Fazenda Modelo"}, {"nome": "Sitio Dois Irmaos"}]})
    assert_equal(from_json.get("imovel_nome"), "Fazenda Modelo; Sitio Dois Irmaos", "multiplas propriedades em JSON")

    sandro_style = parse_report_data(SANDRO_STYLE_TEXT)
    assert_equal(len(sandro_style.get("imoveis", [])), 5, "sandro quantidade de propriedades")
    assert_equal(sandro_style["imoveis"][0]["area_total_ha"], 3388.0, "sandro area primeira propriedade")
    assert_equal(sandro_style.get("area_total_ha"), 9233.08, "sandro area total consolidada")

    sandro_output = generate_report(SANDRO_STYLE_TEXT, output_path=OUTPUT_DIR / "sandro-multiplas-propriedades.xlsx")
    sandro_worksheet = load_workbook(sandro_output).active
    assert_equal(sandro_worksheet["A18"].value, "Fazenda Boa Sorte", "sandro propriedade linha 18")
    assert_equal(sandro_worksheet["A19"].value, "Fazenda Sao Judas", "sandro propriedade linha 19")
    assert_equal(sandro_worksheet["A20"].value, "Fazenda Santa Camila", "sandro propriedade linha 20")
    assert_equal(sandro_worksheet["A21"].value, "Fazenda Sao Jose dos Anjicos", "sandro propriedade linha 21")
    assert_equal(sandro_worksheet["A22"].value, "Fazenda Santa Carolina", "sandro propriedade linha 22")
    assert_equal(sandro_worksheet["D22"].value, 821.0, "sandro area quinta propriedade")
    assert_equal(sandro_worksheet["A24"].value, "3        BENFEITORIAS", "sandro secao benfeitorias deslocada")
    assert_equal(sandro_worksheet["A28"].value, "O complexo pecuario apresenta infraestrutura integrada e alto padrao tecnico.", "sandro texto benfeitorias deslocado")
    assert_equal(sandro_worksheet["D94"].value, "Projeto com cinco unidades produtivas e manejo integrado.", "sandro investimentos deslocado")
    assert_equal(sandro_worksheet["D106"].value, "COMPLEXO PECUARIO COM CINCO UNIDADES PRODUTIVAS INTEGRADAS.", "sandro frase direta deslocada")

    collapsed = parse_report_data(COLLAPSED_PROPERTY_TEXT)
    assert_equal(collapsed.get("imovel_nome"), "Fazenda Beira Rio; Fazenda Val da Onca", "texto colado nomes limpos")
    assert_equal(collapsed["imoveis"][0]["principais_culturas"], "Pastagens forrageiras", "texto colado culturas primeira propriedade")
    assert_equal(collapsed["imoveis"][1]["nome"], "Fazenda Val da Onca", "texto colado segunda propriedade limpa")
    assert_equal(collapsed.get("benfeitorias_descricao"), "O projeto agropecuario fica em duas unidades produtivas.", "texto colado benfeitorias separadas")

    collapsed_group = parse_report_data(COLLAPSED_GROUP_TEXT)
    assert_equal(collapsed_group.get("imovel_nome"), "Grupo Pedra - Unidade Buriti (Ituverava-SP); Grupo Pedra - Unidade Aroeira (Tupaciguara-MG)", "grupo colado nomes limpos")
    assert_equal(collapsed_group["imoveis"][1]["principais_culturas"], "Cana-de-Acucar, Soja e Amendoim", "grupo colado culturas segunda unidade")
    assert_equal(collapsed_group.get("area_total_ha"), 3232.35, "grupo colado area consolidada")

    detail = parse_report_data(DETAIL_PROPERTY_TEXT)
    assert_equal(detail.get("area_total_ha"), 329.32, "detalhamento preserva area consolidada")
    assert_equal(detail["imoveis"][0]["area_total_ha"], 242.19, "detalhamento primeira unidade")
    assert_equal(detail["imoveis"][1]["area_cultivo_ha"], 26.13, "detalhamento calcula cultivo segunda unidade")

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
    prepared_photo = OUTPUT_DIR / "fotos-com-moldura-images" / "foto-01.jpg"
    with Image.open(prepared_photo) as image:
        assert_equal(image.size, (520, 330), "tamanho da foto preparada")
        left_edge = [image.getpixel((0, y)) for y in range(image.height)]
        right_edge = [image.getpixel((image.width - 1, y)) for y in range(image.height)]
        if all(pixel == (255, 255, 255) for pixel in left_edge + right_edge):
            raise AssertionError("foto preparada contem faixa branca lateral")

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
