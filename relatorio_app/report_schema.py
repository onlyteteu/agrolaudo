"""Schema canonico dos dados do relatorio de credito rural.

Este modulo define o "contrato de dados" que alimenta a planilha. A ideia e que a
IA (Gemini) devolva os campos ja estruturados neste formato, em vez de escrever
prosa que depois precisa ser re-lida por regex. Assim a planilha e preenchida a
partir de dados confiaveis, eliminando a maior fonte de erro do pipeline antigo.

- ``REPORT_JSON_SCHEMA``: schema (subconjunto OpenAPI aceito pelo Gemini) usado em
  ``responseSchema`` para forcar a saida estruturada.
- ``build_extraction_prompt``: instrucoes de extracao enviadas junto.
- ``coerce_structured_data``: valida/normaliza o dicionario recebido (da IA ou de
  um teste) e o entrega no formato que ``report_engine.generate_report`` consome.
"""

from __future__ import annotations

import re
from typing import Any

from .report_engine import normalize_data, parse_decimal_pt

# Campos numericos (hectares) que devem virar float, no topo e por propriedade.
_AREA_NUMBER_FIELDS = (
    "area_total_ha",
    "area_pastagens_ha",
    "area_cultivo_ha",
    "area_financiada_bb_ha",
    "area_financiada_outros_ha",
)

# Schema enviado ao Gemini (responseSchema). Mantemos apenas tipos simples
# (STRING/NUMBER/ARRAY/OBJECT) porque e o subconjunto suportado pela API.
REPORT_JSON_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "cliente": {"type": "STRING", "description": "Nome do produtor/cliente, somente o nome."},
        "cpf_cnpj": {"type": "STRING"},
        "data_visita": {"type": "STRING", "description": "Data da visita no formato dd/mm/aaaa, se informada."},
        "cidade_uf": {"type": "STRING", "description": "Municipio e UF, ex.: Pirenopolis-GO."},
        "localizacao_1": {"type": "STRING"},
        "localizacao_2": {"type": "STRING"},
        "finalidade_vistoria": {"type": "STRING"},
        "comentario_localizacao": {"type": "STRING", "description": "Vias de acesso / observacoes de localizacao."},
        "imoveis": {
            "type": "ARRAY",
            "description": "Uma entrada por propriedade. Nao misturar dados entre propriedades.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "nome": {"type": "STRING"},
                    "area_total_ha": {"type": "NUMBER"},
                    "area_pastagens_ha": {"type": "NUMBER"},
                    "area_cultivo_ha": {"type": "NUMBER"},
                    "area_financiada_bb_ha": {"type": "NUMBER"},
                    "area_financiada_outros_ha": {"type": "NUMBER"},
                    "atividade_principal": {"type": "STRING"},
                    "principais_culturas": {"type": "STRING"},
                },
                "required": ["nome"],
            },
        },
        "atividade_principal": {"type": "STRING", "description": "Atividade principal consolidada, quando houver uma so propriedade."},
        "principais_culturas": {"type": "STRING"},
        "benfeitorias_descricao": {
            "type": "STRING",
            "description": "Benfeitorias e infraestrutura especificas das propriedades. Comece cada bloco com 'Na Fazenda X,' quando separar por unidade.",
        },
        "benfeitorias_conservacao": {
            "type": "STRING",
            "description": "Estado de conservacao: BOM, REGULAR ou RUIM.",
        },
        "benfeitorias_observacoes": {"type": "STRING"},
        "equipamentos": {
            "type": "ARRAY",
            "description": "Maquinas, equipamentos e implementos informados. Uma entrada por item.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "descricao": {"type": "STRING"},
                    "fabricante": {"type": "STRING"},
                    "modelo": {"type": "STRING"},
                    "estado": {"type": "STRING", "description": "BOM, REGULAR ou RUIM."},
                },
                "required": ["descricao"],
            },
        },
        "investimentos_comentarios": {"type": "STRING"},
        "insumos_comentarios": {"type": "STRING", "description": "Frase direta em caixa alta (padrao de matricula/visualizacao)."},
        "outros_comentarios": {"type": "STRING"},
        "conclusao": {"type": "STRING"},
        "rebanho": {"type": "STRING"},
        "insumos": {
            "type": "OBJECT",
            "description": (
                "Disponibilidade de insumos. Marque true SOMENTE quando o relatorio "
                "sustentar logicamente a existencia do item. Se nada indicar, deixe de fora. "
                "Nunca marque por suposicao."
            ),
            "properties": {
                "agua": {"type": "BOOLEAN"},
                "energia_eletrica": {"type": "BOOLEAN"},
                "estrutura_transporte": {"type": "BOOLEAN"},
                "mao_de_obra": {"type": "BOOLEAN"},
                "estrutura_armazenagem": {"type": "BOOLEAN"},
                "pastagens": {"type": "BOOLEAN"},
                "outros": {"type": "BOOLEAN"},
            },
        },
    },
    "required": ["cliente", "imoveis"],
    "propertyOrdering": [
        "cliente",
        "cpf_cnpj",
        "data_visita",
        "cidade_uf",
        "localizacao_1",
        "localizacao_2",
        "finalidade_vistoria",
        "comentario_localizacao",
        "imoveis",
        "atividade_principal",
        "principais_culturas",
        "benfeitorias_descricao",
        "benfeitorias_conservacao",
        "benfeitorias_observacoes",
        "equipamentos",
        "investimentos_comentarios",
        "insumos_comentarios",
        "outros_comentarios",
        "conclusao",
        "rebanho",
        "insumos",
    ],
}


def build_extraction_prompt(raw_text: str, report_text: str = "") -> str:
    """Prompt de extracao estruturada (acompanha o REPORT_JSON_SCHEMA)."""
    parts = [
        "Voce e um agronomo extraindo dados de uma vistoria rural para preencher uma planilha de credito.",
        "Extraia SOMENTE informacoes presentes nas anotacoes. Nao invente dados.",
        "Quando um campo nao for informado, deixe-o vazio (string vazia) ou fora do JSON.",
        "Converta alqueires para hectares usando 1 alqueire = 4,84 ha.",
        "Use ponto decimal nos numeros (ex.: 19.36). Nao use separador de milhar.",
        "Cada propriedade vira um item em 'imoveis', sem misturar areas entre elas.",
        "No 'nome' de cada imovel, inclua o municipio-UF quando conhecido, no formato "
        "'Fazenda X - Cidade-UF' (ex.: 'Fazenda Aguas Vertentes - Anicuns-GO').",
        "'principais_culturas' deve listar APENAS lavouras/culturas agricolas (ex.: Milho, Soja). "
        "Nao inclua 'pastagem' generica como cultura. Em pecuaria sem lavoura, deixe principais_culturas "
        "vazio ou cite o capim especifico (ex.: Brachiaria), nunca a palavra 'pastagem' solta.",
        "REGRA DE AREA (importante): 'area_cultivo_ha' so existe quando ha lavoura ou confinamento "
        "declarados. Em pecuaria pura (sem lavoura informada), use area_cultivo_ha = 0 e "
        "area_pastagens_ha = area total. NUNCA invente uma divisao de area (nao use 70/30 nem similar).",
        "EXEMPLO de mapeamento de area: a anotacao '45,4 hectares, 35 de pastagem, 3 de milho para "
        "silagem' vira area_total_ha=45.4, area_pastagens_ha=35, area_cultivo_ha=3 e "
        "principais_culturas='Milho'. Sempre preencha as areas como numeros nos campos corretos; "
        "nunca deixe area total em 0 quando ela foi informada.",
        "REDACAO RICA: nos campos de texto (benfeitorias_descricao, investimentos_comentarios, "
        "outros_comentarios, conclusao, insumos_comentarios), escreva em frases tecnicas completas e "
        "bem desenvolvidas, no padrao de laudo bancario, aproveitando a redacao do texto tecnico ja "
        "redigido. Desenvolver a redacao NAO e inventar fatos: nao acrescente dados nao informados.",
        "Para 'benfeitorias_descricao', quando houver varias propriedades, separe blocos comecando com 'Na Fazenda <nome>,'.",
        "Liste cada maquina/implemento como um item em 'equipamentos'.",
        "INSUMOS (use logica, nao invente): em 'insumos', marque true apenas quando o relatorio "
        "sustentar logicamente o item. Exemplos de raciocinio (nao sao regras fixas): bebedouro, poco, "
        "corrego, represa, tanque ou nascente indicam agua; mencao a energia, rede eletrica, placa solar "
        "ou gerador indica energia_eletrica; caminhao indica estrutura_transporte; funcionarios ou caseiro "
        "indicam mao_de_obra; galpao, silo ou armazem indicam estrutura_armazenagem; pasto ou pastagem "
        "indicam pastagens. Se nada no relatorio indicar o item, NAO o marque (deixe de fora). "
        "Nunca marque por suposicao.",
    ]
    parts.extend(
        [
            "",
            "EXEMPLOS DE EXTRACAO (siga exatamente este padrao):",
            "Anotacao: 'Joao Silva, Fazenda Boa Vista - Goiania-GO, 10 alqueires, gado nelore cria, 6 piquetes, bebedouro, pasto brachiaria'",
            'JSON: {"cliente":"Joao Silva","imoveis":[{"nome":"Fazenda Boa Vista - Goiania-GO",'
            '"area_total_ha":48.4,"area_pastagens_ha":48.4,"area_cultivo_ha":0,'
            '"atividade_principal":"Pecuaria de corte (Cria)","principais_culturas":"Brachiaria"}],'
            '"insumos":{"agua":true,"pastagens":true}}',
            "Anotacao: 'Maria Souza, Sitio Boa Esperanca - Rio Verde-GO, 45 hectares, 35 ha de pastagem, "
            "10 ha de soja, pecuaria leiteira, represa, 1 caminhao'",
            'JSON: {"cliente":"Maria Souza","imoveis":[{"nome":"Sitio Boa Esperanca - Rio Verde-GO",'
            '"area_total_ha":45,"area_pastagens_ha":35,"area_cultivo_ha":10,'
            '"atividade_principal":"Pecuaria leiteira","principais_culturas":"Soja"}],'
            '"insumos":{"agua":true,"pastagens":true,"estrutura_transporte":true}}',
        ]
    )
    if report_text.strip():
        parts.extend(["", "TEXTO TECNICO JA REDIGIDO (use como apoio, mas a fonte da verdade sao as anotacoes brutas):", report_text.strip()])
    parts.extend(["", "ANOTACOES BRUTAS DA VISITA:", raw_text.strip(), "", "Responda APENAS com o JSON no schema definido."])
    return "\n".join(parts).strip() + "\n"


def coerce_structured_data(ai_data: Any) -> dict[str, Any]:
    """Valida e normaliza o dicionario estruturado para o formato da planilha.

    Aceita o dict cru vindo da IA (ou de um teste), limpa tipos, converte numeros
    de area e delega a ``normalize_data`` o tratamento de aliases, propriedades,
    datas e equipamentos ja existente e testado.
    """
    if not isinstance(ai_data, dict):
        return {}

    cleaned: dict[str, Any] = {}
    for key, value in ai_data.items():
        if value in (None, ""):
            continue
        if key == "imoveis":
            cleaned[key] = _coerce_properties(value)
        elif key == "equipamentos":
            cleaned[key] = _coerce_equipment(value)
        elif key == "insumos":
            cleaned[key] = _coerce_insumos(value)
        elif key == "cpf_cnpj":
            cleaned[key] = _clean_cpf_cnpj(value)
        elif key in _AREA_NUMBER_FIELDS:
            cleaned[key] = parse_decimal_pt(value)
        else:
            cleaned[key] = value.strip() if isinstance(value, str) else value

    # Marca para o servidor saber que estes dados vieram estruturados (fonte de
    # verdade) e nao devem ser sobrescritos pela releitura por regex.
    normalized = normalize_data(cleaned)
    normalized["_structured"] = True
    return normalized


def _coerce_properties(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        item: dict[str, Any] = {}
        for key, raw_value in entry.items():
            if raw_value in (None, ""):
                continue
            if key in _AREA_NUMBER_FIELDS:
                item[key] = parse_decimal_pt(raw_value)
            else:
                item[key] = raw_value.strip() if isinstance(raw_value, str) else raw_value
        if item.get("nome"):
            items.append(item)
    return items


def _clean_cpf_cnpj(value: Any) -> str:
    """Remove rotulos que a IA as vezes inclui no valor (ex.: 'CPF 123...')."""
    text = str(value or "").strip()
    text = re.sub(r"^(?:cpf\s*/\s*cnpj|cnpj\s*/\s*cpf|cpf|cnpj)\s*[:.\-]?\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def _coerce_insumos(value: Any) -> dict[str, bool]:
    """So mantem itens marcados como verdadeiros pela IA (true)."""
    if not isinstance(value, dict):
        return {}
    marks: dict[str, bool] = {}
    for key, raw in value.items():
        truthy = raw is True or (isinstance(raw, str) and raw.strip().lower() in {"true", "sim", "x", "1"})
        if truthy:
            marks[key] = True
    return marks


def _coerce_equipment(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for entry in value:
        if isinstance(entry, dict):
            descricao = str(entry.get("descricao", "")).strip()
            if not descricao:
                continue
            items.append(
                {
                    "descricao": descricao,
                    "fabricante": str(entry.get("fabricante", "") or "-").strip() or "-",
                    "modelo": str(entry.get("modelo", "") or "-").strip() or "-",
                    "estado": (str(entry.get("estado", "") or "BOM").strip() or "BOM").upper(),
                    "financiado_bb": "NÃO",
                    "financiado_outros": "NÃO",
                    "segurado": "NÃO",
                    "gravame": "NÃO",
                    "outras_informacoes": "",
                }
            )
        elif isinstance(entry, str) and entry.strip():
            items.append(
                {
                    "descricao": entry.strip(),
                    "fabricante": "-",
                    "modelo": "-",
                    "estado": "BOM",
                    "financiado_bb": "NÃO",
                    "financiado_outros": "NÃO",
                    "segurado": "NÃO",
                    "gravame": "NÃO",
                    "outras_informacoes": "",
                }
            )
    return items
