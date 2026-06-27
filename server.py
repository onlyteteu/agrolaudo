from __future__ import annotations

from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
import html
import json
import mimetypes
import os
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote

from relatorio_app.ai_writer import generate_technical_report_auto
from relatorio_app.pattern_library import select_pattern_examples
from relatorio_app.report_engine import DEFAULT_OUTPUT_DIR, generate_report, parse_decimal_pt, parse_report_data
from relatorio_app.ui import render_credit_report_page as render_premium_credit_report_page
from relatorio_app.ui import render_home as render_premium_home

ROOT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT_DIR / "uploads"

REVIEW_FIELDS = [
    {"key": "cliente", "label": "Produtor / cliente", "required": True, "type": "text"},
    {"key": "data_visita", "label": "Data da visita", "required": False, "type": "text"},
    {"key": "cpf_cnpj", "label": "CPF/CNPJ", "required": False, "type": "text"},
    {"key": "localizacao_1", "label": "Município / localização", "required": True, "type": "text"},
    {"key": "imovel_nome", "label": "Propriedade(s)", "required": True, "type": "text"},
    {"key": "area_total_ha", "label": "Área total (ha)", "required": True, "type": "number"},
    {"key": "area_pastagens_ha", "label": "Pastagens (ha)", "required": False, "type": "number"},
    {"key": "area_cultivo_ha", "label": "Cultivo (ha)", "required": False, "type": "number"},
    {"key": "atividade_principal", "label": "Atividade principal", "required": True, "type": "text"},
    {"key": "principais_culturas", "label": "Principais culturas", "required": True, "type": "text"},
    {"key": "benfeitorias_descricao", "label": "Benfeitorias e infraestrutura", "required": True, "type": "textarea"},
    {"key": "investimentos_comentarios", "label": "Investimentos em andamento", "required": False, "type": "textarea"},
    {"key": "insumos_comentarios", "label": "Frase direta / visualização", "required": False, "type": "textarea"},
    {"key": "outros_comentarios", "label": "Outros comentários", "required": True, "type": "textarea"},
    {"key": "conclusao", "label": "Conclusão", "required": True, "type": "textarea"},
]

NUMBER_FIELDS = {"area_total_ha", "area_pastagens_ha", "area_cultivo_ha", "area_financiada_bb_ha", "area_financiada_outros_ha"}


class ReportHandler(BaseHTTPRequestHandler):
    server_version = "RelatorioAgronomoMVP/0.1"

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path.startswith("/outputs/"):
            self.serve_output_file()
            return
        if path in ("", "/", "/index.html"):
            self.respond_html(render_premium_home())
            return
        if path == "/relatorio-credito":
            self.respond_html(render_premium_credit_report_page())
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/write-technical-report":
            self.handle_write_technical_report()
            return

        if self.path == "/extract":
            self.handle_extract()
            return

        if self.path != "/generate":
            self.send_error(404)
            return

        run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        upload_dir = UPLOAD_DIR / run_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length)
        form = parse_form_data(self.headers.get("Content-Type", ""), body)

        data_text = form.getfirst("dados", "")
        review_data = parse_review_data(form.getfirst("review_data", ""), data_text)
        photos = save_uploaded_files(form, upload_dir, "photos")
        output_path = DEFAULT_OUTPUT_DIR / f"relatorio-{run_id}.xlsx"

        try:
            generated = generate_report(review_data or data_text, photos, output_path)
        except Exception as exc:
            self.respond_html(render_error(str(exc)), status=500)
            return

        self.serve_file(generated, download_name=generated.name)

    def handle_extract(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(body or "{}")
            text = payload.get("dados", "")
        except json.JSONDecodeError:
            self.respond_json({"error": "JSON inválido."}, status=400)
            return

        parsed = parse_report_data(text)
        review = build_review_payload(parsed)
        self.respond_json(review)

    def handle_write_technical_report(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(body or "{}")
            raw_value = payload.get("raw_text", "")
            if isinstance(raw_value, dict) and "value" in raw_value:
                raw_value = raw_value["value"]
            raw_text = str(raw_value or "")
        except json.JSONDecodeError:
            self.respond_json({"error": "JSON inválido."}, status=400)
            return

        if not raw_text.strip():
            self.respond_json({"error": "Informe os dados brutos da visita."}, status=400)
            return

        writer_run = generate_technical_report_auto(raw_text)
        result = writer_run.result
        pattern_selection = select_pattern_examples(raw_text)
        response = writer_run.to_payload()
        response["pattern_library"] = pattern_selection.to_payload()
        structured = writer_run.structured if writer_run.structured is not None else parse_report_data(result.report_text)
        response["review"] = build_review_payload(structured)
        self.respond_json(response)

    def serve_output_file(self) -> None:
        requested = unquote(self.path.removeprefix("/outputs/"))
        path = (DEFAULT_OUTPUT_DIR / requested).resolve()
        if not str(path).startswith(str(DEFAULT_OUTPUT_DIR.resolve())) or not path.exists():
            self.send_error(404)
            return
        self.serve_file(path, download_name=path.name)

    def serve_file(self, path: Path, download_name: str | None = None) -> None:
        data = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if download_name:
            self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.end_headers()
        self.wfile.write(data)

    def respond_html(self, content: str, status: int = 200) -> None:
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def respond_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@dataclass(frozen=True)
class UploadedFile:
    filename: str
    content: bytes


class ParsedForm:
    def __init__(self) -> None:
        self._fields: dict[str, list[str]] = {}
        self._files: dict[str, list[UploadedFile]] = {}

    def add_field(self, name: str, value: str) -> None:
        self._fields.setdefault(name, []).append(value)

    def add_file(self, name: str, uploaded_file: UploadedFile) -> None:
        self._files.setdefault(name, []).append(uploaded_file)

    def getfirst(self, name: str, default: str = "") -> str:
        values = self._fields.get(name)
        if not values:
            return default
        return values[0]

    def files(self, name: str) -> list[UploadedFile]:
        return self._files.get(name, [])


def parse_form_data(content_type: str, body: bytes) -> ParsedForm:
    form = ParsedForm()
    if content_type.startswith("multipart/form-data"):
        headers = (
            f"Content-Type: {content_type}\r\n"
            "MIME-Version: 1.0\r\n\r\n"
        ).encode("utf-8")
        message = BytesParser(policy=policy.default).parsebytes(headers + body)
        for part in message.iter_parts():
            if part.get_content_disposition() != "form-data":
                continue
            name = part.get_param("name", header="content-disposition")
            if not name:
                continue
            payload = part.get_payload(decode=True) or b""
            filename = part.get_filename()
            if filename:
                form.add_file(name, UploadedFile(filename=filename, content=payload))
                continue
            charset = part.get_content_charset() or "utf-8"
            form.add_field(name, payload.decode(charset, errors="replace"))
        return form

    if content_type.startswith("application/x-www-form-urlencoded"):
        decoded = body.decode("utf-8", errors="replace")
        for name, values in parse_qs(decoded, keep_blank_values=True).items():
            for value in values:
                form.add_field(name, value)

    return form


def save_uploaded_files(form: ParsedForm, upload_dir: Path, field_name: str) -> list[Path]:
    saved: list[Path] = []

    for index, item in enumerate(form.files(field_name), start=1):
        if not item.filename:
            continue
        suffix = Path(item.filename).suffix.lower() or ".jpg"
        destination = upload_dir / f"foto-{index:02d}{suffix}"
        destination.write_bytes(item.content)
        saved.append(destination)

    return saved


def build_review_payload(parsed: dict) -> dict:
    fields = []
    missing = []
    for field in REVIEW_FIELDS:
        value = parsed.get(field["key"], "")
        if value is None:
            value = ""
        value = str(value)
        is_missing = field["required"] and not value.strip()
        if is_missing:
            missing.append(field["label"])
        fields.append(
            {
                "key": field["key"],
                "label": field["label"],
                "required": field["required"],
                "type": field["type"],
                "value": value,
                "missing": is_missing,
            }
        )

    return {
        "fields": fields,
        "missing": missing,
        "parsed": parsed,
        "summary": {
            "found": len([field for field in fields if field["value"].strip()]),
            "missing": len(missing),
        },
    }


def parse_review_data(review_data_raw: str, original_text: str) -> dict | None:
    if not review_data_raw:
        return None

    try:
        reviewed = json.loads(review_data_raw)
    except json.JSONDecodeError:
        return parse_report_data(original_text)

    if not isinstance(reviewed, dict):
        return parse_report_data(original_text)

    parsed = reviewed.get("parsed")
    if isinstance(parsed, dict) and parsed.get("_structured"):
        # Dados vieram estruturados da IA: sao a fonte de verdade, sem releitura
        # por regex que poderia reintroduzir valores antigos.
        base = dict(parsed)
    else:
        base = parse_report_data(original_text)
        if isinstance(parsed, dict):
            base.update(parsed)

    edited_fields = reviewed.get("fields")
    if isinstance(edited_fields, dict):
        for key, value in edited_fields.items():
            base[key] = coerce_review_value(key, value)

    sync_single_property(base)
    return base


def sync_single_property(data: dict) -> None:
    """Numa propriedade unica, os campos revisados (areas, atividade, culturas)
    representam essa propriedade. Sincroniza o item para a correcao do agronomo
    aparecer nas celulas D18/E18/F18 etc."""
    properties = data.get("imoveis")
    if not isinstance(properties, list) or len(properties) != 1:
        return
    item = properties[0]
    if not isinstance(item, dict):
        return
    for key in (
        "area_total_ha",
        "area_pastagens_ha",
        "area_cultivo_ha",
        "area_financiada_bb_ha",
        "area_financiada_outros_ha",
        "atividade_principal",
        "principais_culturas",
    ):
        if data.get(key) not in (None, ""):
            item[key] = data[key]
    if data.get("imovel_nome"):
        item["nome"] = data["imovel_nome"]


def coerce_review_value(key: str, value):
    if isinstance(value, str):
        value = value.strip()
    if key in NUMBER_FIELDS and value not in (None, ""):
        return parse_decimal_pt(value)
    return value


def render_sample_dashboard_home() -> str:
    pecuaria_sample = read_sample_text("sample_gemini_text.txt")
    mandioca_sample = read_sample_text("sample_mandioca_text.txt")
    placeholder = html.escape("Cole aqui o texto estruturado gerado pelo chat.")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgroLaudo</title>
  <style>
    :root {{
      --leaf-900: #123c2d;
      --leaf-800: #185138;
      --leaf-700: #1f6b49;
      --leaf-100: #dfeee5;
      --field-50: #f5f7f2;
      --paper: #ffffff;
      --line: #d7dfd2;
      --text: #17221c;
      --muted: #607066;
      --soil: #8a6b3f;
      --amber: #c7922b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--field-50);
      color: var(--text);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }}
    .app {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 248px minmax(0, 1fr);
    }}
    aside {{
      background: var(--leaf-900);
      color: #edf7f0;
      padding: 24px 18px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 800;
      font-size: 20px;
    }}
    .brand-mark {{
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      background: #e4f3dd;
      color: var(--leaf-800);
    }}
    nav {{ display: grid; gap: 8px; }}
    .nav-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 40px;
      padding: 0 12px;
      border-radius: 8px;
      color: #d5e8dc;
      font-size: 14px;
    }}
    .nav-item.active {{
      background: #e4f3dd;
      color: var(--leaf-900);
      font-weight: 700;
    }}
    .side-note {{
      margin-top: auto;
      padding: 14px;
      border: 1px solid rgba(255,255,255,.16);
      border-radius: 8px;
      color: #cfe2d4;
      font-size: 13px;
      line-height: 1.45;
    }}
    main {{ min-width: 0; padding: 28px; }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 20px;
    }}
    h1 {{ margin: 0; font-size: 26px; line-height: 1.2; }}
    .subtitle {{ margin: 6px 0 0; color: var(--muted); font-size: 14px; }}
    .status-strip {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .status {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      min-height: 76px;
    }}
    .status small {{
      color: var(--muted);
      display: block;
      margin-bottom: 6px;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .status strong {{ font-size: 18px; }}
    .workspace {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 18px;
      align-items: start;
    }}
    .panel {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .panel-head {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .panel-title {{ font-weight: 800; }}
    .samples {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .sample-btn, .ghost-btn {{
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcf8;
      color: var(--leaf-800);
      font-weight: 700;
      cursor: pointer;
    }}
    .form-body {{ padding: 18px; }}
    label {{ display: block; font-weight: 800; margin-bottom: 8px; }}
    textarea {{
      width: 100%;
      min-height: 430px;
      resize: vertical;
      border: 1px solid #bdcabc;
      border-radius: 8px;
      padding: 14px;
      color: var(--text);
      background: #fffefb;
      font: 14px/1.55 Consolas, "Courier New", monospace;
      outline-color: var(--leaf-700);
    }}
    .action-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: 16px;
      flex-wrap: wrap;
    }}
    .primary-btn {{
      min-height: 44px;
      border: 0;
      border-radius: 8px;
      padding: 0 18px;
      background: var(--leaf-700);
      color: white;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
    }}
    .primary-btn:hover {{ background: var(--leaf-800); }}
    .primary-btn[disabled] {{ cursor: wait; opacity: .74; }}
    .spinner {{
      display: none;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255,255,255,.45);
      border-top-color: white;
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }}
    .primary-btn[disabled] .spinner {{ display: inline-block; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .upload-box {{
      display: grid;
      gap: 14px;
      padding: 18px;
    }}
    .dropzone {{
      border: 1px dashed #94ad98;
      border-radius: 8px;
      background: #fbfcf8;
      min-height: 146px;
      display: grid;
      place-items: center;
      text-align: center;
      padding: 18px;
      cursor: pointer;
    }}
    .dropzone input {{ display: none; }}
    .dropzone strong {{ display: block; color: var(--leaf-800); margin-top: 8px; }}
    .dropzone span {{ color: var(--muted); font-size: 13px; }}
    .file-count {{
      min-height: 36px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-radius: 8px;
      background: var(--leaf-100);
      padding: 0 12px;
      color: var(--leaf-900);
      font-weight: 700;
      font-size: 13px;
    }}
    .checklist {{
      border-top: 1px solid var(--line);
      padding: 16px 18px;
      display: grid;
      gap: 12px;
      color: #33443a;
      font-size: 14px;
    }}
    .check-item {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--amber);
      flex: 0 0 auto;
    }}
    svg {{ flex: 0 0 auto; }}
    @media (max-width: 980px) {{
      .app {{ grid-template-columns: 1fr; }}
      aside {{ display: none; }}
      main {{ padding: 18px; }}
      .workspace, .status-strip {{ grid-template-columns: 1fr; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      textarea {{ min-height: 360px; }}
    }}
  </style>
</head>
<body>
<div class="app">
  <aside>
    <div class="brand">
      <div class="brand-mark" aria-hidden="true">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M5 19c8 0 13-6 13-14-8 0-13 6-13 14Z" stroke="currentColor" stroke-width="2"/><path d="M5 19c3-5 7-8 13-10" stroke="currentColor" stroke-width="2"/></svg>
      </div>
      AgroLaudo
    </div>
    <nav aria-label="Navegação">
      <div class="nav-item active">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M9 13h6M9 17h6M9 9h3" stroke="currentColor" stroke-width="2"/></svg>
        Relatórios
      </div>
      <div class="nav-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 20h16M6 20V9l6-4 6 4v11" stroke="currentColor" stroke-width="2"/><path d="M10 20v-6h4v6" stroke="currentColor" stroke-width="2"/></svg>
        Propriedades
      </div>
      <div class="nav-item">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 6h16M4 12h16M4 18h10" stroke="currentColor" stroke-width="2"/></svg>
        Modelos
      </div>
    </nav>
    <div class="side-note">Motor local conectado ao modelo Excel de vistoria rural.</div>
  </aside>
  <main>
    <div class="topbar">
      <div>
        <h1>Novo relatório de vistoria</h1>
        <div class="subtitle">Planilha pronta para análise de crédito rural</div>
      </div>
      <button class="ghost-btn" type="button" id="clearBtn">Limpar</button>
    </div>

    <section class="status-strip" aria-label="Status">
      <div class="status"><small>Modelo</small><strong>BB rural</strong></div>
      <div class="status"><small>Fotos</small><strong>até 39</strong></div>
      <div class="status"><small>Saída</small><strong>.xlsx</strong></div>
    </section>

    <form id="reportForm" method="post" action="/generate" enctype="multipart/form-data" class="workspace">
      <section class="panel">
        <div class="panel-head">
          <div class="panel-title">Dados do laudo</div>
          <div class="samples">
            <button class="sample-btn" type="button" data-sample="pecuaria">Pecuária</button>
            <button class="sample-btn" type="button" data-sample="mandioca">Mandioca</button>
          </div>
        </div>
        <div class="form-body">
          <label for="dados">Texto estruturado</label>
          <textarea id="dados" name="dados" placeholder="{placeholder}"></textarea>
          <div class="action-row">
            <button class="primary-btn" type="submit" id="submitBtn">
              <span class="spinner" aria-hidden="true"></span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/><path d="M7 10l5 5 5-5M12 15V3" stroke="currentColor" stroke-width="2"/></svg>
              Gerar Excel
            </button>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div class="panel-title">Fotos da visita</div>
        </div>
        <div class="upload-box">
          <label class="dropzone" for="photos">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" stroke="currentColor" stroke-width="2"/><path d="M8 8l4-4 4 4M12 4v12" stroke="currentColor" stroke-width="2"/></svg>
            <strong>Selecionar fotos</strong>
            <span>JPG, PNG, BMP ou WEBP</span>
            <input id="photos" name="photos" type="file" accept="image/*" multiple>
          </label>
          <div class="file-count"><span id="fileCount">Nenhuma foto selecionada</span><span>slots 39</span></div>
        </div>
        <div class="checklist">
          <div class="check-item"><span class="dot"></span>Dados principais</div>
          <div class="check-item"><span class="dot"></span>Textos técnicos</div>
          <div class="check-item"><span class="dot"></span>Imagens no anexo</div>
        </div>
      </section>
    </form>
  </main>
</div>
<script id="sample-data" type="application/json">{json.dumps({"pecuaria": pecuaria_sample, "mandioca": mandioca_sample}, ensure_ascii=False)}</script>
<script>
  const samples = JSON.parse(document.getElementById('sample-data').textContent);
  const textarea = document.getElementById('dados');
  const fileInput = document.getElementById('photos');
  const fileCount = document.getElementById('fileCount');
  const form = document.getElementById('reportForm');
  const submitBtn = document.getElementById('submitBtn');

  document.querySelectorAll('[data-sample]').forEach((button) => {{
    button.addEventListener('click', () => {{
      textarea.value = samples[button.dataset.sample] || '';
      textarea.focus();
    }});
  }});

  document.getElementById('clearBtn').addEventListener('click', () => {{
    textarea.value = '';
    fileInput.value = '';
    fileCount.textContent = 'Nenhuma foto selecionada';
    textarea.focus();
  }});

  fileInput.addEventListener('change', () => {{
    const total = fileInput.files.length;
    fileCount.textContent = total === 1 ? '1 foto selecionada' : `${{total}} fotos selecionadas`;
  }});

  form.addEventListener('submit', () => {{
    submitBtn.disabled = true;
    submitBtn.lastChild.textContent = ' Gerando';
    setTimeout(() => {{ submitBtn.disabled = false; submitBtn.lastChild.textContent = ' Gerar Excel'; }}, 4000);
  }});
</script>
</body>
</html>"""


def read_sample_text(file_name: str) -> str:
    path = ROOT_DIR / file_name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def render_home() -> str:
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Central Agro</title>
  <style>
    :root {
      --canopy-950: #102a22;
      --canopy-900: #173b2c;
      --canopy-800: #1f533b;
      --leaf-700: #2b7a4b;
      --leaf-600: #348e56;
      --leaf-100: #e8f3ea;
      --field-50: #f6f8f3;
      --paper: #ffffff;
      --line: #d8e1d4;
      --text: #17231c;
      --muted: #657568;
      --soil: #8a6b3f;
      --sun: #d7a83f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(180deg, rgba(232,243,234,.78), rgba(246,248,243,0) 280px),
        var(--field-50);
      color: var(--text);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }
    .shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 256px minmax(0, 1fr);
    }
    aside {
      background: var(--canopy-950);
      color: #edf7ef;
      padding: 24px 18px;
      display: flex;
      flex-direction: column;
      gap: 26px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      font-weight: 850;
      font-size: 19px;
      letter-spacing: 0;
    }
    .brand-mark {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      color: var(--canopy-900);
      background: #e6f3df;
    }
    nav { display: grid; gap: 8px; }
    .nav-item {
      min-height: 42px;
      padding: 0 12px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #d8eadc;
      font-size: 14px;
      text-decoration: none;
    }
    .nav-item.active {
      background: #e6f3df;
      color: var(--canopy-950);
      font-weight: 800;
    }
    .side-panel {
      margin-top: auto;
      border: 1px solid rgba(255,255,255,.14);
      border-radius: 8px;
      padding: 14px;
      color: #cbded0;
      font-size: 13px;
      line-height: 1.45;
    }
    main {
      min-width: 0;
      padding: 30px;
    }
    .topbar {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 24px;
    }
    .eyebrow {
      color: var(--leaf-700);
      font-weight: 850;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 8px;
    }
    h1 {
      margin: 0;
      font-size: 32px;
      line-height: 1.15;
      letter-spacing: 0;
    }
    .subtitle {
      margin: 8px 0 0;
      max-width: 620px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.5;
    }
    .user-chip {
      min-height: 40px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,.78);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--canopy-900);
      font-weight: 800;
      white-space: nowrap;
    }
    .overview {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 22px;
    }
    .metric {
      min-height: 88px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,.86);
      padding: 16px;
    }
    .metric small {
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      font-weight: 800;
    }
    .metric strong {
      font-size: 22px;
      line-height: 1.1;
    }
    .section-head {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 18px;
      margin: 26px 0 14px;
    }
    h2 {
      margin: 0;
      font-size: 20px;
      letter-spacing: 0;
    }
    .section-note {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }
    .tools-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr);
      gap: 16px;
      align-items: stretch;
    }
    .tool-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      min-height: 260px;
      padding: 22px;
      display: grid;
      align-content: space-between;
      gap: 24px;
      box-shadow: 0 14px 32px rgba(31,83,59,.08);
    }
    .tool-main {
      display: flex;
      align-items: flex-start;
      gap: 16px;
    }
    .tool-icon {
      width: 48px;
      height: 48px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      color: var(--canopy-900);
      background: var(--leaf-100);
    }
    .tool-title {
      margin: 0;
      font-size: 23px;
      line-height: 1.2;
    }
    .tool-text {
      margin: 8px 0 0;
      color: var(--muted);
      line-height: 1.5;
      max-width: 650px;
    }
    .tag-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
    }
    .tag {
      min-height: 30px;
      display: inline-flex;
      align-items: center;
      padding: 0 10px;
      border-radius: 8px;
      background: #f3f7f0;
      color: var(--canopy-800);
      font-size: 13px;
      font-weight: 800;
    }
    .tool-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }
    .primary-action {
      min-height: 44px;
      padding: 0 16px;
      border-radius: 8px;
      border: 0;
      background: var(--leaf-700);
      color: #fff;
      font-weight: 850;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 10px;
    }
    .primary-action:hover { background: var(--canopy-800); }
    .muted-action {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }
    .roadmap {
      border: 1px dashed #b8c8b2;
      border-radius: 8px;
      background: rgba(255,255,255,.58);
      padding: 22px;
      min-height: 260px;
      display: grid;
      align-content: center;
      gap: 12px;
    }
    .roadmap strong {
      font-size: 17px;
      color: var(--canopy-900);
    }
    .roadmap p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
      font-size: 14px;
    }
    .leaf-line {
      height: 4px;
      width: 84px;
      border-radius: 8px;
      background: linear-gradient(90deg, var(--leaf-700), var(--sun));
    }
    svg { flex: 0 0 auto; }
    @media (max-width: 900px) {
      .shell { grid-template-columns: 1fr; }
      aside {
        min-height: auto;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        padding: 14px 16px;
      }
      nav, .side-panel { display: none; }
      main { padding: 22px 16px 34px; }
      .topbar { flex-direction: column; }
      .overview, .tools-grid { grid-template-columns: 1fr; }
      h1 { font-size: 28px; }
      .tool-main { flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 19c8 0 13-6 13-14-8 0-13 6-13 14Z" stroke="currentColor" stroke-width="2"/><path d="M5 19c3-5 7-8 13-10" stroke="currentColor" stroke-width="2"/></svg>
        </div>
        Central Agro
      </div>
      <nav aria-label="Navegação principal">
        <a class="nav-item active" href="/">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8Z" stroke="currentColor" stroke-width="2"/></svg>
          Início
        </a>
        <a class="nav-item" href="/relatorio-credito">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M9 13h6M9 17h6M9 9h3" stroke="currentColor" stroke-width="2"/></svg>
          Relatório de crédito
        </a>
      </nav>
      <div class="side-panel">Ferramentas simples para organizar análise, vistoria e documentação rural.</div>
    </aside>

    <main>
      <div class="topbar">
        <div>
          <div class="eyebrow">Painel de ferramentas</div>
          <h1>Seu centro de trabalho para operações agro</h1>
          <p class="subtitle">Escolha a ferramenta que precisa agora. A primeira entrega é o relatório de crédito rural; os próximos módulos entram aqui sem bagunçar o fluxo.</p>
        </div>
        <div class="user-chip" aria-label="Ambiente local">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M12 21s7-4.4 7-11a7 7 0 0 0-14 0c0 6.6 7 11 7 11Z" stroke="currentColor" stroke-width="2"/><path d="M12 10.5h.01" stroke="currentColor" stroke-width="3"/></svg>
          Local
        </div>
      </div>

      <section class="overview" aria-label="Resumo">
        <div class="metric"><small>Ferramentas ativas</small><strong>1</strong></div>
        <div class="metric"><small>Foco atual</small><strong>Crédito rural</strong></div>
        <div class="metric"><small>Saída principal</small><strong>Excel</strong></div>
      </section>

      <div class="section-head">
        <div>
          <h2>Ferramentas</h2>
          <div class="section-note">Acesse somente o que já está pronto para uso.</div>
        </div>
      </div>

      <section class="tools-grid" aria-label="Ferramentas disponíveis">
        <article class="tool-card">
          <div class="tool-main">
            <div class="tool-icon" aria-hidden="true">
              <svg width="27" height="27" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2"/></svg>
            </div>
            <div>
              <h3 class="tool-title">Relatório de crédito rural</h3>
              <p class="tool-text">Cole os dados brutos da visita, gere o texto técnico no padrão do laudo, revise os campos e anexe as fotos.</p>
              <div class="tag-row" aria-label="Características">
                <span class="tag">Vistoria</span>
                <span class="tag">Fotos</span>
                <span class="tag">XLSX</span>
              </div>
            </div>
          </div>
          <div class="tool-actions">
            <a class="primary-action" href="/relatorio-credito">
              Abrir ferramenta
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2"/></svg>
            </a>
            <span class="muted-action">Texto técnico e Excel no mesmo fluxo.</span>
          </div>
        </article>

        <aside class="roadmap" aria-label="Área para próximas ferramentas">
          <div class="leaf-line"></div>
          <strong>Próximas ferramentas entram neste painel</strong>
          <p>Este espaço fica reservado para novos módulos do sistema agro, mantendo a página inicial limpa e fácil de expandir.</p>
        </aside>
      </section>
    </main>
  </div>
</body>
</html>"""


def render_credit_report_page() -> str:
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Central Agro | Relatório de crédito</title>
  <style>
    :root {
      --green-900: #173b2c;
      --green-800: #1f533b;
      --green-700: #26734d;
      --green-600: #338957;
      --green-100: #e7f1e8;
      --bg: #f7f9f5;
      --card: #ffffff;
      --line: #dbe3d8;
      --text: #16221b;
      --muted: #607064;
      --warn: #a76613;
      --warn-bg: #fff7df;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }
    main {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 34px 0 46px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 22px;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-icon {
      width: 42px;
      height: 42px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      background: var(--green-100);
      color: var(--green-700);
    }
    h1 { margin: 0; font-size: 26px; line-height: 1.2; }
    .subtitle { margin: 4px 0 0; color: var(--muted); font-size: 14px; }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
      gap: 18px;
      align-items: start;
    }
    .workspace.start {
      display: block;
    }
    .workspace.start > .card:first-child {
      max-width: 760px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
    }
    .panel-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    .panel-title h2 {
      margin: 0;
      font-size: 18px;
      line-height: 1.25;
    }
    .step {
      width: 30px;
      height: 30px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      background: var(--green-100);
      color: var(--green-900);
      font-weight: 900;
      flex: 0 0 auto;
    }
    .output-card { display: none; }
    .output-card.show { display: block; }
    label { display: block; font-weight: 800; margin-bottom: 8px; }
    textarea {
      width: 100%;
      resize: vertical;
      border: 1px solid #c8d4c5;
      border-radius: 8px;
      padding: 14px;
      color: var(--text);
      background: #fffefc;
      font: 14px/1.55 Consolas, "Courier New", monospace;
      outline-color: var(--green-700);
    }
    #rawData { min-height: 430px; }
    #dados { min-height: 430px; }
    .row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }
    .actions { margin-top: 14px; }
    .stack { display: grid; gap: 14px; }
    button {
      min-height: 44px;
      border: 0;
      border-radius: 8px;
      padding: 0 18px;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
    }
    .primary { background: var(--green-700); color: white; }
    .primary:hover { background: var(--green-900); }
    .secondary { background: var(--green-100); color: var(--green-900); }
    .secondary:hover { background: #dcebdd; }
    .home-link {
      min-height: 44px;
      border-radius: 8px;
      padding: 0 18px;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      text-decoration: none;
    }
    button[disabled] { opacity: .6; cursor: wait; }
    .review {
      display: none;
      margin-top: 18px;
      border-top: 1px solid var(--line);
      padding-top: 18px;
    }
    .review.show { display: block; }
    .notice {
      display: none;
      margin-bottom: 14px;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--warn-bg);
      color: #6d4b00;
      border: 1px solid #f0d48a;
      font-size: 14px;
      line-height: 1.45;
    }
    .notice.success {
      background: var(--green-100);
      color: var(--green-900);
      border-color: #b8d3bd;
    }
    .notice.show { display: block; }
    .ok-box {
      margin-bottom: 14px;
      padding: 12px 14px;
      border-radius: 8px;
      background: var(--green-100);
      color: var(--green-900);
      font-weight: 700;
      font-size: 14px;
    }
    .fields {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .field.full { grid-column: 1 / -1; }
    input[type="text"], .field textarea {
      width: 100%;
      border: 1px solid #c8d4c5;
      border-radius: 8px;
      padding: 11px 12px;
      font: 14px/1.45 Inter, "Segoe UI", Arial, sans-serif;
      outline-color: var(--green-700);
    }
    .field textarea { min-height: 94px; }
    .missing input, .missing textarea { border-color: #d69e2e; background: #fffaf0; }
    .required { color: var(--warn); font-size: 12px; margin-left: 6px; }
    .upload {
      margin-top: 18px;
      padding: 16px;
      border: 1px dashed #9fb39e;
      border-radius: 8px;
      background: #fbfdf9;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
      flex-wrap: wrap;
    }
    input[type="file"] { max-width: 100%; }
    .file-count { color: var(--muted); font-size: 14px; }
    .generate-row { margin-top: 16px; justify-content: flex-end; }
    .muted { color: var(--muted); font-size: 13px; line-height: 1.45; }
    .spinner {
      display: none;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255,255,255,.45);
      border-top-color: white;
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    button[disabled] .spinner { display: inline-block; }
    @keyframes spin { to { transform: rotate(360deg); } }
    svg { flex: 0 0 auto; }
    @media (max-width: 760px) {
      main { width: min(100% - 24px, 1040px); padding-top: 22px; }
      header { align-items: flex-start; }
      .workspace { grid-template-columns: 1fr; }
      .fields { grid-template-columns: 1fr; }
      .card { padding: 16px; }
      h1 { font-size: 23px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand">
        <div class="brand-icon" aria-hidden="true">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M5 19c8 0 13-6 13-14-8 0-13 6-13 14Z" stroke="currentColor" stroke-width="2"/><path d="M5 19c3-5 7-8 13-10" stroke="currentColor" stroke-width="2"/></svg>
        </div>
        <div>
          <h1>Relatório de crédito rural</h1>
          <div class="subtitle">Cole os dados brutos da visita, gere o texto técnico e baixe a planilha pronta.</div>
        </div>
      </div>
      <div class="header-actions">
        <a class="secondary home-link" href="/">Início</a>
        <button class="secondary" type="button" id="clearBtn">Limpar</button>
      </div>
    </header>

    <form id="reportForm" method="post" action="/generate" enctype="multipart/form-data" class="workspace start">
      <section class="card">
        <div class="panel-title">
          <h2>Dados brutos da visita</h2>
          <span class="step">1</span>
        </div>
        <label for="rawData">Anotações do agrônomo</label>
        <textarea id="rawData" placeholder="Cole aqui os dados brutos: produtor, propriedades, áreas, rebanho, lavouras, benfeitorias e maquinários."></textarea>
        <div id="writerNotice" class="notice"></div>
        <div class="row actions">
          <p class="muted">O sistema transforma essas anotações em um texto técnico padronizado.</p>
          <button class="primary" type="button" id="writeBtn" data-label="Gerar relatório técnico">
            <span class="spinner" aria-hidden="true"></span>
            <span class="btn-label">Gerar relatório técnico</span>
          </button>
        </div>
      </section>

      <section class="card output-card" id="technicalSection">
        <div class="panel-title">
          <h2>Relatório técnico gerado</h2>
          <span class="step">2</span>
        </div>
        <label for="dados">Texto técnico editável</label>
        <textarea id="dados" name="dados" placeholder="O texto técnico gerado aparecerá aqui."></textarea>
        <div class="row actions">
          <p class="muted">Revise o texto. Se alterar algo, atualize os campos antes de gerar a planilha.</p>
          <button class="secondary" type="button" id="extractBtn" data-label="Atualizar campos">
            <span class="spinner" aria-hidden="true"></span>
            <span class="btn-label">Atualizar campos</span>
          </button>
        </div>

        <section class="review" id="review">
          <div id="okBox" class="ok-box">Campos reconhecidos. Revise antes de gerar.</div>
          <div id="missingBox" class="notice"></div>
          <div id="fields" class="fields"></div>

          <div class="upload">
            <label for="photos">Fotos da visita</label>
            <input id="photos" name="photos" type="file" accept="image/*" multiple>
            <span class="file-count" id="fileCount">Nenhuma foto selecionada</span>
          </div>

          <input type="hidden" id="reviewData" name="review_data">
          <div class="row generate-row">
            <button class="primary" type="submit" id="submitBtn" data-label="Gerar e baixar Excel">
              <span class="spinner" aria-hidden="true"></span>
              <span class="btn-label">Gerar e baixar Excel</span>
            </button>
          </div>
        </section>
      </section>
    </form>
  </main>
<script>
  const rawData = document.getElementById('rawData');
  const technicalText = document.getElementById('dados');
  const writeBtn = document.getElementById('writeBtn');
  const writerNotice = document.getElementById('writerNotice');
  const technicalSection = document.getElementById('technicalSection');
  const extractBtn = document.getElementById('extractBtn');
  const review = document.getElementById('review');
  const fieldsEl = document.getElementById('fields');
  const missingBox = document.getElementById('missingBox');
  const okBox = document.getElementById('okBox');
  const reviewData = document.getElementById('reviewData');
  const fileInput = document.getElementById('photos');
  const fileCount = document.getElementById('fileCount');
  const form = document.getElementById('reportForm');
  const submitBtn = document.getElementById('submitBtn');
  let lastExtraction = null;

  document.getElementById('clearBtn').addEventListener('click', () => {
    rawData.value = '';
    technicalText.value = '';
    fieldsEl.innerHTML = '';
    review.classList.remove('show');
    technicalSection.classList.remove('show');
    form.classList.add('start');
    writerNotice.className = 'notice';
    writerNotice.textContent = '';
    reviewData.value = '';
    lastExtraction = null;
    if (fileInput) fileInput.value = '';
    if (fileCount) fileCount.textContent = 'Nenhuma foto selecionada';
    rawData.focus();
  });

  function setBusy(button, busy, label) {
    button.disabled = busy;
    const text = button.querySelector('.btn-label');
    if (text) text.textContent = busy ? label : button.dataset.label;
  }

  writeBtn.addEventListener('click', async () => {
    const rawText = rawData.value.trim();
    if (!rawText) {
      rawData.focus();
      return;
    }
    setBusy(writeBtn, true, 'Gerando');
    writerNotice.className = 'notice';
    writerNotice.textContent = '';
    try {
      const response = await fetch('/write-technical-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: rawText })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Não consegui gerar o texto técnico.');
      technicalText.value = payload.report_text || '';
      technicalSection.classList.add('show');
      form.classList.remove('start');
      renderFields(payload.review);
      renderWriterNotice(payload.writer);
      review.classList.add('show');
      technicalSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      writerNotice.className = 'notice';
      writerNotice.textContent = error.message;
      writerNotice.classList.add('show');
    } finally {
      setBusy(writeBtn, false, '');
    }
  });

  extractBtn.addEventListener('click', refreshFieldsFromTechnicalText);

  function renderWriterNotice(writer) {
    if (!writer) return;
    writerNotice.className = 'notice';
    if (writer.used_ai) {
      writerNotice.textContent = `Texto gerado com Gemini (${writer.model}).`;
      writerNotice.classList.add('success', 'show');
      return;
    }
    writerNotice.textContent = writer.fallback_reason
      ? `Texto gerado pelo modo local. ${writer.fallback_reason}`
      : 'Texto gerado pelo modo local.';
    writerNotice.classList.add('show');
  }

  technicalText.addEventListener('input', () => {
    reviewData.value = '';
    lastExtraction = null;
    fieldsEl.innerHTML = '';
    missingBox.textContent = 'Texto alterado. Atualize os campos antes de gerar a planilha.';
    missingBox.classList.add('show');
    review.classList.add('show');
  });

  async function refreshFieldsFromTechnicalText() {
    const dados = technicalText.value.trim();
    if (!dados) {
      technicalText.focus();
      return false;
    }
    setBusy(extractBtn, true, 'Atualizando');
    try {
      const response = await fetch('/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dados })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || 'Não consegui atualizar os campos.');
      renderFields(payload);
      review.classList.add('show');
      return true;
    } catch (error) {
      missingBox.textContent = error.message;
      missingBox.classList.add('show');
      review.classList.add('show');
      return false;
    } finally {
      setBusy(extractBtn, false, '');
    }
  }

  function renderFields(payload) {
    if (!payload) return;
    lastExtraction = payload;
    fieldsEl.innerHTML = '';
    okBox.textContent = `${payload.summary.found} campos encontrados. Revise e ajuste se precisar.`;
    if (payload.missing.length) {
      missingBox.textContent = `Campos faltando: ${payload.missing.join(', ')}. Você pode preencher manualmente abaixo.`;
      missingBox.classList.add('show');
    } else {
      missingBox.classList.remove('show');
      missingBox.textContent = '';
    }

    payload.fields.forEach((field) => {
      const wrapper = document.createElement('div');
      wrapper.className = `field ${field.type === 'textarea' ? 'full' : ''} ${field.missing ? 'missing' : ''}`;
      const label = document.createElement('label');
      label.htmlFor = `field-${field.key}`;
      label.textContent = field.label;
      if (field.required) {
        const required = document.createElement('span');
        required.className = 'required';
        required.textContent = field.missing ? 'faltando' : 'obrigatório';
        label.appendChild(required);
      }
      const input = field.type === 'textarea' ? document.createElement('textarea') : document.createElement('input');
      input.id = `field-${field.key}`;
      input.dataset.key = field.key;
      if (field.type !== 'textarea') input.type = 'text';
      input.value = field.value || '';
      input.addEventListener('input', syncReviewData);
      wrapper.appendChild(label);
      wrapper.appendChild(input);
      fieldsEl.appendChild(wrapper);
    });
    syncReviewData();
  }

  function syncReviewData() {
    if (!lastExtraction) return;
    const fields = {};
    fieldsEl.querySelectorAll('[data-key]').forEach((input) => {
      fields[input.dataset.key] = input.value;
    });
    reviewData.value = JSON.stringify({ parsed: lastExtraction.parsed, fields });
  }

  fileInput.addEventListener('change', () => {
    const total = fileInput.files.length;
    fileCount.textContent = total === 1 ? '1 foto selecionada' : `${total} fotos selecionadas`;
  });

  form.addEventListener('submit', async (event) => {
    if (!technicalText.value.trim()) {
      event.preventDefault();
      writeBtn.click();
      return;
    }
    if (!reviewData.value) {
      event.preventDefault();
      await refreshFieldsFromTechnicalText();
      return;
    }
    syncReviewData();
    setBusy(submitBtn, true, 'Gerando');
    setTimeout(() => { setBusy(submitBtn, false, ''); }, 5000);
  });
</script>
</body>
</html>"""


def render_error(message: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgroLaudo | Erro</title>
  <style>
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f5f7f2; font-family: "Segoe UI", Arial, sans-serif; color: #17221c; }}
    .box {{ width: min(680px, calc(100vw - 32px)); background: white; border: 1px solid #d7dfd2; border-radius: 8px; padding: 22px; }}
    h1 {{ margin: 0 0 14px; font-size: 22px; }}
    pre {{ white-space: pre-wrap; background: #fff7ed; border: 1px solid #f0d8b0; border-radius: 8px; padding: 14px; }}
    a {{ color: #1f6b49; font-weight: 800; }}
  </style>
</head>
<body>
  <div class="box">
    <h1>Não consegui gerar o relatório</h1>
    <pre>{html.escape(message)}</pre>
    <a href="/">Voltar</a>
  </div>
</body>
</html>"""


def main() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "127.0.0.1")
    server = ThreadingHTTPServer((host, port), ReportHandler)
    display_host = "127.0.0.1" if host == "0.0.0.0" else host
    print(f"Servidor rodando em http://{display_host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
