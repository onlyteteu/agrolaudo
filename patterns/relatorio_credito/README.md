# Biblioteca de padrões - Relatório de crédito rural

Esta pasta guarda o conhecimento próprio do produto.

Cada exemplo aprovado deve ficar em `examples/<id>/` com:

- `metadata.json`: tags, título, tipo de caso e observações.
- `raw.txt`: dados brutos da visita.
- `expected.txt`: resposta técnica aprovada.

O sistema usa essa biblioteca para:

- escolher exemplos semelhantes;
- montar o prompt oficial para IA;
- manter consistência de estilo;
- validar se o relatório gerado segue a estrutura da planilha.

Quando novos casos reais forem aprovados, adicione-os aqui. Essa biblioteca é mais importante que um prompt solto, porque vira um ativo acumulativo do SaaS.
