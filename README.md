# AgroLaudo MVP

MVP local para gerar um relatorio de visita em Excel a partir do modelo `templates/relatorio-modelo.xlsx`.

## Como rodar

Crie um ambiente Python e instale as dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\server.py
```

Depois acesse:

```text
http://127.0.0.1:8000
```

## Configurar Gemini

Crie um arquivo `.env` na raiz do projeto, ao lado do `server.py`, usando `.env.example` como base:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` e coloque sua chave do Google AI Studio:

```text
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT_SECONDS=45
```

Depois reinicie o servidor. Se `GEMINI_API_KEY` não estiver configurada, o sistema usa o gerador local como fallback.

## Gerar pela linha de comando

```powershell
python -m relatorio_app.report_engine --data-file .\sample_data.json --photos .\sample_photos --out .\outputs\teste.xlsx
```

## Validar exemplos

```powershell
python .\scripts\validate_samples.py
```

## Formato aceito

Por enquanto o motor aceita:

- JSON, como `sample_data.json`.
- Texto simples com uma linha por campo, no formato `campo: valor`.
- Texto narrativo gerado pelo chat, como `sample_gemini_text.txt`, com seções de discriminação, benfeitorias, máquinas, investimentos, comentários e conclusão.
- Fotos em `.jpg`, `.jpeg`, `.png`, `.bmp` ou `.webp`.

Quando o formato definitivo dos comandos estiver pronto, o parser pode ser ajustado sem mexer na parte que escreve o Excel.
