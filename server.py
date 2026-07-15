from __future__ import annotations

from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
import html
import io
import json
import mimetypes
import os
import re
import uuid

from PIL import Image as PILImage
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
    {"key": "comentario_localizacao", "label": "Vias de acesso", "required": False, "type": "textarea"},
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

        # Valida as fotos ANTES de gerar, nomeando os arquivos originais com
        # problema — evita falhar no fim do fluxo com mensagem generica.
        bad_photos = invalid_photo_names(form)
        if bad_photos:
            message = (
                "Estas fotos não puderam ser lidas: "
                + ", ".join(bad_photos)
                + ". Remova-as da lista ou gere sem as fotos."
            )
            if "application/json" in (self.headers.get("Accept") or ""):
                self.respond_json({"error": message, "kind": "photos"}, status=400)
            else:
                self.respond_html(render_error(message), status=400)
            return

        photos = save_uploaded_files(form, upload_dir, "photos")
        writer_meta = parse_writer_meta(form.getfirst("writer_meta", ""))
        output_path = DEFAULT_OUTPUT_DIR / f"relatorio-{run_id}.xlsx"

        try:
            generated = generate_report(review_data or data_text, photos, output_path, writer_meta=writer_meta)
        except Exception as exc:
            # Fetch do front pede JSON (mostra a mensagem + "Tentar de novo" na
            # propria pagina, sem perder o formulario); sem JS cai no HTML.
            message = friendly_error_message(exc)
            if "application/json" in (self.headers.get("Accept") or ""):
                self.respond_json({"error": message}, status=500)
            else:
                self.respond_html(render_error(message), status=500)
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
        requested = unquote(self.path.split("?", 1)[0].removeprefix("/outputs/"))
        path = (DEFAULT_OUTPUT_DIR / requested).resolve()
        if not path.is_relative_to(DEFAULT_OUTPUT_DIR.resolve()) or not path.is_file():
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


def invalid_photo_names(form: ParsedForm) -> list[str]:
    """Nomes originais das fotos que o PIL nao consegue abrir."""
    bad: list[str] = []
    for item in form.files("photos"):
        if not item.filename or not item.content:
            continue
        try:
            with PILImage.open(io.BytesIO(item.content)) as image:
                image.verify()
        except Exception:
            bad.append(item.filename)
    return bad


def save_uploaded_files(form: ParsedForm, upload_dir: Path, field_name: str) -> list[Path]:
    saved: list[Path] = []

    for index, item in enumerate(form.files(field_name), start=1):
        # Sem conteudo (upload falhou no navegador) nao vira arquivo: um
        # 0-byte passava na validacao e estourava na hora de montar a foto.
        if not item.filename or not item.content:
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


def parse_writer_meta(raw: str) -> dict | None:
    """Le o JSON com o status do motor (Gemini x local) enviado pelo front, para
    gravar no Excel qual IA gerou o laudo. Tolerante a valores ausentes/invalidos."""
    if not raw:
        return None
    try:
        meta = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return meta if isinstance(meta, dict) else None


def friendly_error_message(exc: Exception) -> str:
    """Mensagem de erro para o usuario, sem vazar caminhos nem jargao interno."""
    text = str(exc)
    if "identify image" in text or "image file" in text:
        return "Uma das fotos não pôde ser lida. Remova a foto com problema e tente de novo."
    # Caminho de disco, traceback ou nome de excecao: nada disso ajuda o usuario.
    if not text or re.search(r"[A-Za-z]:\\|Traceback|Error\b|Exception\b", text):
        return "Falha interna ao montar a planilha. Tente de novo; se persistir, gere sem as fotos."
    return text


def render_error(message: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgroLaudo | Erro</title>
  <style>
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f1f4ea; font-family: Inter, "Segoe UI", system-ui, Arial, sans-serif; color: #101d15; }}
    .box {{ width: min(640px, calc(100vw - 32px)); background: #fff; border: 1px solid #e0e6d6; border-radius: 14px; padding: 26px; box-shadow: 0 22px 50px rgba(11, 39, 26, .12); }}
    h1 {{ margin: 0 0 8px; font-size: 20px; font-weight: 900; letter-spacing: -.02em; color: #06150e; }}
    p {{ margin: 0 0 14px; color: #5d6b5c; font-size: 14px; line-height: 1.5; }}
    pre {{ white-space: pre-wrap; margin: 0 0 18px; background: #fff6e3; border: 1px solid #efd8a5; border-radius: 10px; padding: 13px; color: #6c4a07; font: 600 13px/1.5 Inter, "Segoe UI", Arial, sans-serif; }}
    a {{ display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; border-radius: 12px; background: linear-gradient(135deg, #195636, #06150e); color: #fff; font-weight: 850; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="box">
    <h1>Não consegui gerar a planilha</h1>
    <p>Suas anotações não foram perdidas — volte e clique em "Gerar" novamente.</p>
    <pre>{html.escape(message)}</pre>
    <a href="/relatorio-credito">Voltar para a ferramenta</a>
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
