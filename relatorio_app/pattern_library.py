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
    if has_normalized_token(normalized_text, "cria"):
        tags.add("cria")
    if has_normalized_token(normalized_text, "recria"):
        tags.add("recria")
    if has_normalized_token(normalized_text, "engorda"):
        tags.add("engorda")
    if (
        "cria_recria_engorda" in normalized_text
        or (
            has_normalized_token(normalized_text, "cria")
            and has_normalized_token(normalized_text, "recria")
            and has_normalized_token(normalized_text, "engorda")
        )
    ):
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
    if "nelore" in normalized_text:
        tags.add("nelore")
    if "silagem" in normalized_text:
        tags.add("silagem")
    if "ceasa" in normalized_text:
        tags.add("ceasa")
        tags.add("escoamento")
    if "galpao" in normalized_text or "galpao" in normalized_text:
        tags.add("galpao")
    if "casa_funcionarios" in normalized_text or "casas_funcionarios" in normalized_text or "caseiro" in normalized_text:
        tags.add("casas_funcionarios")
    if "casa_propria" in normalized_text or "casa_sede" in normalized_text:
        tags.add("casa_sede")
    if "futuros_projetos" in normalized_text or "projetos_futuros" in normalized_text:
        tags.add("projetos_futuros")
    if "reforma_de_pastagem" in normalized_text or "reforma_pastagem" in normalized_text:
        tags.add("reforma_pastagem")
    if "reforma_de_cerca" in normalized_text or "reforma_cerca" in normalized_text:
        tags.add("reforma_cerca")
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


def has_normalized_token(normalized_text: str, token: str) -> bool:
    return token in normalized_text.split("_")


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
    quality_rules = """
REGRAS GERAIS (inegociaveis):
- Escreva um laudo de vistoria para analise de credito rural bancario (Banco do Brasil, Sicredi e afins): linguagem formal, objetiva, tecnica e conservadora.
- NAO invente dados (cadastro, area, rebanho, maquinas, benfeitorias, culturas, produtividade, localizacao ou recursos hidricos). Nao assuma o que nao foi informado; quando faltar um dado importante, escreva "Nao informado".
- Converta alqueires para hectares (1 alqueire mineiro/goiano = 4,84 ha) e padronize numeros e unidades (ex.: 20.000 arvores, 450 cabecas, 5,80 ha).
- Area de Cultivo (ha) = Area Total menos Area de Pastagens quando NAO houver lavoura declarada; havendo lavoura, use a area de lavoura informada. Em pecuaria pura, cultivo = 0 e pastagem = area total. Nunca invente divisao de area (nao use 70/30 nem similar).
- Uma propriedade por bloco: nunca misture areas, benfeitorias ou atividades entre propriedades diferentes.
- Nao use tabelas em markdown, nem linguagem promocional ou opinativa. Entregue apenas o laudo final, sem comentarios sobre o processo.

ESTRUTURA OBRIGATORIA (use exatamente estes titulos, nesta ordem):

1. DISCRIMINACAO
Abra com os dados de cabecalho, quando informados: Cliente; CPF/CNPJ; Municipio/UF; Vias de acesso (descreva o trajeto informado); Finalidade da vistoria. Em seguida, para CADA propriedade, apresente em topicos: Nome da propriedade; Tipo de exploracao (propria, arrendada, comodato ou "Nao informado"); Atividades desenvolvidas; Situacao produtiva (ativa, estruturada etc.). Depois, apresente os Dados de Area e Exploracao por Propriedade, em linhas separadas: Area Total (ha); Area de Pastagens (ha); Area de Cultivo (ha); Atividade principal desenvolvida; Principais culturas.

2. TIPO (Benfeitorias e Infraestrutura)
Descreva as benfeitorias de CADA propriedade em UM UNICO bloco de texto corrido e denso (comece com "Na Fazenda <nome>," ou "<Nome da Fazenda> - "), no estilo de inventario tecnico de vistoria. Cubra, quando informado: tipo de uso da propriedade; estrutura de pastagens (numero de pastos/piquetes e tipo de cerca, ex.: arame liso com 5 fios); especies forrageiras; currais, cochos e cercas com suas caracteristicas (ex.: curral em cordoalha, cochos cobertos); condicoes das pastagens (areas que necessitam de reforma ou recuperacao); estruturas de apoio (galpao para insumos/maquinarios, casa sede, casas de funcionarios, alojamentos); recursos hidricos (reservatorio com capacidade, represa, rio, nascente, bebedouros distribuidos nos pastos). Preserve numeros e especificacoes; nao dilua em texto generico e NAO use conectores vazios como "a infraestrutura de suporte ao rebanho inclui" ou "a estrutura de apoio as operacoes conta com". Indique o estado de conservacao (BOM, REGULAR ou RUIM) e registre observacoes tecnicas relevantes (ex.: potencial produtivo, taxa de lotacao das pastagens), sem exageros.

3. DESCRICAO (Maquinas, Equipamentos e Implementos)
Relacione maquinas, equipamentos, veiculos, implementos e sistemas de irrigacao informados, UM item por linha, indicando fabricante, modelo e estado de conservacao quando houver. Se nada for informado, escreva "Nao informado". Nao use tabela em markdown.

INVESTIMENTOS EM ANDAMENTO (Comentarios)
Comente obras, aquisicoes ou estruturas em andamento e sua finalidade, quando informados. Se nao houver, registre que nao foram informados investimentos em andamento alem das estruturas ja declaradas.

OUTROS COMENTARIOS
Sintetize o quadro geral, somente com o que constar das anotacoes: perfil e escala da atividade; disponibilidade de insumos (agua, energia eletrica, estrutura de transporte, mao de obra, estrutura de armazenagem, pastagens); recursos hidricos; perspectivas e necessidades futuras (ex.: aquisicao de animais/insumos/maquinas, reforma de pastagens, correcao de solo, novas culturas, armazenagem/irrigacao); forma de comercializacao; aspectos ambientais; arrendamento ou espolio; e demais particularidades relevantes.

CONCLUSAO
Emita parecer tecnico de credito rural: capacidade produtiva e de pagamento (apenas com base no informado), coerencia e prazo do investimento pretendido, e condicione a recomendacao a conferencia documental, cadastral e patrimonial. Sem promessas de retorno nem linguagem promocional.

FRASES DIRETAS (PADRAO DE MATRICULA/VISUALIZACAO)
Uma frase curta, em CAIXA ALTA, reunindo atividade principal, area total informada e o ponto tecnico central da vistoria.

PADRAO DE QUALIDADE:
- IMPORTANTE: "denso" significa RICO EM CONTEUDO TECNICO, nunca curto. Desenvolva CADA secao com profundidade, aproveitando todos os dados informados. O laudo deve ser completo e extenso o suficiente para analise bancaria (nao entregue respostas curtas ou econômicas).
- A secao 2. TIPO e a mais importante: deve ser a mais desenvolvida, densa, especifica e fiel aos numeros informados.
- Texto tecnico e verificavel; evite adjetivos vazios ("excelente", "robusto", "altissimo") sem dado que sustente, mas nao economize em detalhes tecnicos reais.
- Em casos com poucos dados brutos, enriqueca a redacao com base no que existe, sem criar estrutura nao informada.
""".strip()
    parts = [
        "Voce e um agronomo responsavel por redigir relatorio tecnico para analise de credito rural.",
        "Siga rigorosamente o guia de estilo e a estrutura do relatorio.",
    ]
    if style_guide:
        parts.extend(["", "GUIA DE ESTILO:", style_guide])
    parts.extend(["", "REGRAS COMPLEMENTARES OBRIGATORIAS:", quality_rules])

    approved_examples = [example for example in selection.examples if example.has_expected]
    if approved_examples:
        parts.extend(["", "EXEMPLOS APROVADOS PARA IMITAR O PADRÃO:"])
        for index, example in enumerate(approved_examples, start=1):
            parts.extend(
                [
                    "",
                    f"EXEMPLO {index}: {example.title}",
                    f"TAGS: {', '.join(example.tags)}",
                    "DADOS BRUTOS DO EXEMPLO:",
                    clip_text(example.raw_text, 1800),
                    "SAIDA APROVADA:",
                    clip_text(example.expected_text, 4600),
                ]
            )

    if local_draft.strip():
        parts.extend(
            [
                "",
                "RASCUNHO LOCAL ESTRUTURADO:",
                "Use como apoio de campos e calculos, mas melhore a redacao tecnica quando necessario.",
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
            "Gere apenas o relatorio tecnico final, sem explicacoes adicionais, mantendo as secoes obrigatorias.",
            "Antes de finalizar, verifique se a secao 2 ficou suficientemente desenvolvida e se o texto nao ficou curto demais para analise de credito rural.",
        ]
    )
    return "\n".join(parts).strip() + "\n"


def build_enrichment_prompt(draft_text: str, raw_text: str = "", max_examples: int = 1) -> str:
    """Prompt de ENRIQUECIMENTO: a IA reescreve um rascunho ja correto (feito pelo
    nosso motor), deixando-o mais rico, SEM alterar numeros/fatos nem inventar.

    Diferente de build_writer_prompt (que pedia o laudo do zero), aqui a IA tem
    uma unica funcao: linguagem. Os dados sao responsabilidade do motor."""
    style_guide = load_style_guide().strip()
    rules = """
TAREFA: ENRIQUECER (reescrever) o rascunho tecnico abaixo, deixando-o mais completo, denso e bem desenvolvido, no padrao de laudo de vistoria para analise bancaria de credito rural.

REGRAS INEGOCIAVEIS:
- MANTENHA EXATAMENTE todos os numeros, nomes, areas, quantidades, culturas e fatos do rascunho. NUNCA altere valores nem unidades.
- NAO invente nada que nao esteja no rascunho (nem benfeitorias, nem culturas, nem numeros, nem recursos).
- Mantenha EXATAMENTE os mesmos titulos de secao do rascunho, na mesma ordem: 1. DISCRIMINACAO; 2. TIPO (Benfeitorias e Infraestrutura); 3. DESCRICAO (Maquinas, Equipamentos e Implementos); INVESTIMENTOS EM ANDAMENTO (Comentarios); OUTROS COMENTARIOS; CONCLUSAO; FRASES DIRETAS.
- PRESERVE VERBATIM as linhas rotuladas da secao 1 (Cliente:, CPF/CNPJ:, Municipio/UF:, Data da visita:, Vias de acesso:, Nome da propriedade:, Tipo de exploracao:, Area Total (ha):, Area de Pastagens (ha):, Area de Cultivo (ha):, Atividade principal desenvolvida:, Principais culturas:) - o sistema le esses rotulos automaticamente para preencher a planilha. Nao renomeie, nao remova e nao funda essas linhas.
- Se o rascunho contiver a frase do plantel ("O plantel total informado e de X cabecas"), mantenha-a com essa mesma redacao.
- Desenvolva CADA secao com profundidade e linguagem tecnica de agronomo. A secao 2. TIPO deve ser a mais rica, em UM UNICO bloco denso por propriedade (comece com "Na Fazenda <nome>,"), sem picotar.
- 'Denso' = rico em conteudo tecnico, nunca curto. Aproveite cada dado do rascunho.
- Linguagem formal, objetiva e conservadora; sem adjetivos vazios ("excelente", "robusto", "altissimo") sem dado que sustente.
- Entregue APENAS o relatorio final reescrito, sem comentarios sobre o processo.
""".strip()

    parts = ["Voce e um engenheiro agronomo que aprimora a redacao de laudos tecnicos de credito rural."]
    if style_guide:
        parts.extend(["", "GUIA DE ESTILO:", style_guide])
    parts.extend(["", rules])

    if raw_text.strip():
        approved = [ex for ex in select_pattern_examples(raw_text, limit=max_examples).examples if ex.has_expected]
        if approved:
            parts.extend(
                [
                    "",
                    "EXEMPLO DE PADRAO APROVADO (imite o ESTILO, nao copie os dados):",
                    clip_text(approved[0].expected_text, 4200),
                ]
            )

    parts.extend(
        [
            "",
            "RASCUNHO A ENRIQUECER (fonte da verdade dos fatos e numeros; nao altere valores):",
            draft_text.strip(),
            "",
            "Reescreva o relatorio final, mais rico e desenvolvido, mantendo exatamente os mesmos fatos, numeros e titulos de secao.",
        ]
    )
    return "\n".join(parts).strip() + "\n"


def clip_text(value: str, max_chars: int) -> str:
    text = value.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[trecho reduzido]"
