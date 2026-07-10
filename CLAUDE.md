# AgroLaudo

Ferramenta web (servidor Python puro, sem framework) que transforma anotações brutas de vistoria rural em laudo bancário: texto técnico, planilha Excel no modelo do banco e fotos numeradas. UI renderizada em `relatorio_app/ui.py`; motor em `relatorio_app/report_engine.py` e `relatorio_app/technical_writer.py`.

## Design Context

- **PRODUCT.md** (raiz): registro `product`, plataforma `web`, usuários (agrônomos de crédito rural), posicionamento ("anotações cruas → Excel do banco"), personalidade (confiável, técnico, direto), anti-referências e princípios de design. Leia antes de qualquer trabalho de UI.
- **DESIGN.md** (raiz): sistema visual — Estrela-guia "A Mesa do Agrônomo", paleta Verde-Floresta/Verde-Lima, tokens, componentes e as regras nomeadas (Verde-Lima só em ação; sem cinza puro; família única Inter; sombras verdes).
- `.impeccable/design.json`: sidecar com rampas tonais, sombras, motion e snippets de componentes.

## Validação

```powershell
python -X utf8 scripts/validate_samples.py
python -X utf8 scripts/validate_structured.py
```

## Commits

Sem linha Co-Authored-By nas mensagens de commit.
