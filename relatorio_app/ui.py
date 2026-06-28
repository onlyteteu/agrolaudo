from __future__ import annotations

# Nome da marca exibido em toda a interface.
# Quando o nome final for decidido, basta trocar aqui.
BRAND = "AgroDesk"

# Marca grafica (broto de duas folhas) reutilizada no cabecalho e na barra lateral.
_LEAF_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M12 21V11" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'
    '<path d="M12 12.6C12 8 8.4 4.6 3.6 4.6 3.6 9.2 7.2 12.6 12 12.6Z" fill="currentColor"/>'
    '<path d="M13.1 10.4C13.1 6.8 15.9 4 19.6 4 19.6 7.6 16.8 10.4 13.1 10.4Z" '
    'fill="currentColor" opacity=".68"/>'
    '</svg>'
)


def _base_css() -> str:
    """Sistema de design compartilhado entre todas as paginas."""
    return """
    :root {
      --bg: #f1f4ea;
      --surface: #ffffff;
      --surface-soft: #f8faf2;
      --ink: #101d15;
      --muted: #5d6b5c;
      --line: #e0e6d6;
      --line-strong: #cdd6c0;

      --forest-950: #06150e;
      --forest-900: #0b271a;
      --forest-800: #123c28;
      --forest-700: #195636;
      --forest-600: #237a4b;
      --forest-100: #e4f1e1;
      --forest-50: #f1f7ec;

      --lime: #c2f24d;
      --lime-strong: #a7df2f;
      --amber: #eaa53d;
      --gold: #c79a52;

      --warn: #8f5b07;
      --warn-bg: #fff6e3;

      --radius: 14px;
      --radius-sm: 10px;
      --radius-lg: 22px;
      --shadow-sm: 0 8px 22px rgba(11, 39, 26, .07);
      --shadow: 0 22px 50px rgba(11, 39, 26, .12);
      --shadow-lg: 0 34px 80px rgba(7, 26, 17, .20);
      --ring: 0 0 0 3px rgba(35, 122, 75, .18);
    }
    * { box-sizing: border-box; }
    html { color-scheme: light; -webkit-font-smoothing: antialiased; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 88% -4%, rgba(194, 242, 77, .18), transparent 30rem),
        radial-gradient(circle at 6% 6%, rgba(35, 122, 75, .12), transparent 26rem),
        var(--bg);
      font-family: Inter, "Segoe UI", system-ui, Arial, sans-serif;
      letter-spacing: 0;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 0;
      opacity: .5;
      background-image:
        repeating-linear-gradient(115deg, rgba(18,60,40,.05) 0 1px, transparent 1px 26px),
        repeating-linear-gradient(25deg, rgba(199,154,82,.045) 0 1px, transparent 1px 34px);
      mask-image: linear-gradient(180deg, #000, transparent 78%);
    }
    a, button, input, textarea, summary { font: inherit; }
    svg { flex: 0 0 auto; }

    .app-shell {
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: grid;
      grid-template-columns: 252px minmax(0, 1fr);
    }

    /* ---------- Barra lateral ---------- */
    .rail {
      position: sticky;
      top: 0;
      align-self: start;
      height: 100vh;
      border-right: 1px solid var(--line);
      background: rgba(255, 255, 255, .72);
      backdrop-filter: blur(18px);
      padding: 20px 16px;
      display: flex;
      flex-direction: column;
      gap: 26px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 4px 6px;
      color: var(--forest-950);
      font-size: 18px;
      font-weight: 900;
      letter-spacing: -.02em;
    }
    .brand-mark {
      width: 42px;
      height: 42px;
      border-radius: 13px;
      display: grid;
      place-items: center;
      color: var(--lime);
      background: linear-gradient(150deg, var(--forest-700), var(--forest-950));
      box-shadow: 0 12px 26px rgba(11, 39, 26, .30), inset 0 1px 0 rgba(255,255,255,.14);
    }
    .brand-mark svg { width: 23px; height: 23px; }
    .nav-label {
      padding: 0 8px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    .nav { display: grid; gap: 5px; }
    .nav a {
      position: relative;
      min-height: 44px;
      padding: 0 12px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      gap: 11px;
      color: #43543f;
      text-decoration: none;
      font-size: 14px;
      font-weight: 750;
      transition: background .18s ease, color .18s ease, transform .18s ease;
    }
    .nav a svg { width: 19px; height: 19px; opacity: .85; }
    .nav a.active {
      color: var(--forest-950);
      background: linear-gradient(120deg, var(--forest-100), rgba(194,242,77,.28));
      box-shadow: inset 0 0 0 1px rgba(35,122,75,.14);
    }
    .nav a.active::before {
      content: "";
      position: absolute;
      left: -16px;
      top: 50%;
      transform: translateY(-50%);
      width: 4px;
      height: 22px;
      border-radius: 0 4px 4px 0;
      background: linear-gradient(var(--lime-strong), var(--forest-600));
    }
    .nav a:not(.active):hover { background: var(--forest-50); color: var(--forest-900); transform: translateX(2px); }
    .rail-foot { margin-top: auto; display: grid; gap: 12px; }
    .rail-card {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(160deg, #fff, var(--surface-soft));
      padding: 14px;
      box-shadow: var(--shadow-sm);
    }
    .rail-card strong { display: block; color: var(--forest-950); font-size: 13px; font-weight: 850; }
    .rail-card span { display: block; margin-top: 4px; color: var(--muted); font-size: 12px; line-height: 1.45; }
    .rail-tag {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 5px 10px;
      border-radius: 999px;
      background: var(--forest-950);
      color: var(--lime);
      font-size: 11px;
      font-weight: 850;
      letter-spacing: .02em;
      width: fit-content;
    }
    .rail-tag::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--lime); box-shadow: 0 0 10px var(--lime); }

    /* ---------- Pagina ---------- */
    .page { min-width: 0; padding: 30px 34px 56px; }
    .page-inner { width: min(1180px, 100%); margin: 0 auto; }

    /* ---------- Hero ---------- */
    .hero {
      position: relative;
      overflow: hidden;
      border-radius: var(--radius-lg);
      padding: 34px 34px 30px;
      color: #fff;
      background:
        radial-gradient(circle at 82% -30%, rgba(194,242,77,.30), transparent 44%),
        linear-gradient(135deg, var(--forest-950), var(--forest-800) 62%, var(--forest-700));
      box-shadow: var(--shadow-lg);
      border: 1px solid rgba(255,255,255,.06);
    }
    .hero::before {
      content: "";
      position: absolute;
      inset: 0;
      opacity: .5;
      background-image:
        repeating-linear-gradient(60deg, rgba(255,255,255,.05) 0 1px, transparent 1px 40px),
        radial-gradient(circle at 78% 120%, rgba(194,242,77,.18), transparent 40%);
      pointer-events: none;
    }
    .hero::after {
      content: "";
      position: absolute;
      right: -90px;
      top: -90px;
      width: 280px;
      height: 280px;
      border-radius: 50%;
      border: 1px solid rgba(194,242,77,.22);
      box-shadow: inset 0 0 0 28px rgba(255,255,255,.03);
      pointer-events: none;
    }
    .hero > * { position: relative; z-index: 1; }
    .hero-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 22px;
      flex-wrap: wrap;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 14px;
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(194,242,77,.14);
      border: 1px solid rgba(194,242,77,.28);
      color: #dff5b6;
      font-size: 11px;
      font-weight: 900;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    .hero h1 {
      margin: 0;
      font-size: clamp(30px, 4vw, 44px);
      line-height: 1.04;
      letter-spacing: -.03em;
      font-weight: 900;
    }
    .hero h1 .accent {
      background: linear-gradient(100deg, var(--lime), #f1d97a);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
    .hero .lead {
      max-width: 560px;
      margin: 14px 0 0;
      color: rgba(255,255,255,.80);
      font-size: 15px;
      line-height: 1.55;
    }
    .hero-strip { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 22px; }
    .hero-chip {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      padding: 0 13px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.16);
      color: rgba(255,255,255,.90);
      font-size: 12.5px;
      font-weight: 800;
    }
    .hero-chip svg { width: 15px; height: 15px; color: var(--lime); }
    .hero-actions { display: flex; gap: 10px; flex-wrap: wrap; }

    /* ---------- Botoes ---------- */
    .btn {
      min-height: 46px;
      border-radius: 12px;
      border: 1px solid transparent;
      padding: 0 18px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      font-weight: 850;
      text-decoration: none;
      cursor: pointer;
      white-space: nowrap;
      transition: transform .16s ease, box-shadow .16s ease, background .16s ease, border-color .16s ease;
    }
    .btn:hover { transform: translateY(-2px); }
    .btn svg { width: 18px; height: 18px; }
    .btn-primary {
      background: linear-gradient(135deg, var(--lime), var(--lime-strong));
      color: var(--forest-950);
      box-shadow: 0 14px 30px rgba(141, 196, 47, .34);
    }
    .btn-primary:hover { box-shadow: 0 20px 40px rgba(141, 196, 47, .42); }
    .btn-dark {
      background: linear-gradient(135deg, var(--forest-700), var(--forest-950));
      color: #fff;
      box-shadow: 0 14px 28px rgba(11, 39, 26, .26);
    }
    .btn-dark:hover { box-shadow: 0 20px 38px rgba(11, 39, 26, .34); }
    .btn-light {
      background: rgba(255,255,255,.12);
      border-color: rgba(255,255,255,.24);
      color: #fff;
    }
    .btn-light:hover { background: rgba(255,255,255,.20); }
    .btn-ghost {
      background: var(--surface);
      border-color: var(--line-strong);
      color: var(--forest-900);
    }
    .btn-ghost:hover { background: var(--forest-50); border-color: var(--forest-600); }
    .btn[disabled] { opacity: .6; cursor: wait; transform: none; }

    /* ---------- Paineis ---------- */
    .section-label {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 26px 2px 14px;
      color: var(--forest-950);
      font-size: 14px;
      font-weight: 900;
      letter-spacing: -.01em;
    }
    .section-label::after { content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, var(--line-strong), transparent); }
    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel-head {
      min-height: 56px;
      padding: 14px 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: linear-gradient(180deg, rgba(255,255,255,.9), var(--surface-soft));
    }
    .panel-title { display: flex; align-items: center; gap: 10px; color: var(--forest-950); font-weight: 900; }
    .panel-title svg { width: 19px; height: 19px; color: var(--forest-600); }
    .panel-kicker {
      padding: 5px 11px;
      border-radius: 999px;
      background: var(--forest-50);
      color: var(--forest-700);
      font-size: 11.5px;
      font-weight: 850;
    }
    .panel-body { padding: 18px; display: grid; gap: 14px; }

    .spinner {
      display: none;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(6,21,14,.25);
      border-top-color: var(--forest-950);
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    .btn[disabled] .spinner, button[disabled] .spinner { display: inline-block; }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ---------- Responsivo (shell) ---------- */
    @media (max-width: 980px) {
      .app-shell { grid-template-columns: 1fr; }
      .rail {
        position: static;
        height: auto;
        flex-direction: row;
        align-items: center;
        gap: 14px;
        padding: 12px 16px;
        overflow-x: auto;
      }
      .nav { grid-auto-flow: column; }
      .nav a.active::before { display: none; }
      .nav-label, .rail-foot { display: none; }
      .page { padding: 18px 16px 40px; }
      .hero { padding: 24px 22px; }
    }
    @media (max-width: 560px) {
      .nav a span { display: none; }
      .brand span { display: none; }
    }
    """


def _rail(active: str) -> str:
    """Barra lateral compartilhada. active = 'home' | 'tool'."""
    home_cls = "active" if active == "home" else ""
    tool_cls = "active" if active == "tool" else ""
    return f"""
    <aside class="rail">
      <div class="brand">
        <span class="brand-mark">{_LEAF_SVG}</span>
        <span>{BRAND}</span>
      </div>
      <div>
        <div class="nav-label">Menu</div>
        <nav class="nav" aria-label="Navegacao principal">
          <a class="{home_cls}" href="/">
            <svg viewBox="0 0 24 24" fill="none"><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
            <span>Inicio</span>
          </a>
          <a class="{tool_cls}" href="/relatorio-credito">
            <svg viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            <span>Relatorio de credito</span>
          </a>
        </nav>
      </div>
      <div class="rail-foot">
        <div class="rail-card">
          <strong>Relatorio em minutos</strong>
          <span>Cole as anotacoes da vistoria e baixe a planilha pronta no padrao do laudo.</span>
        </div>
        <span class="rail-tag">Beta</span>
      </div>
    </aside>
    """


def render_home() -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{BRAND}</title>
  <style>
    {_base_css()}
    .tool-card {{
      position: relative;
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      background: linear-gradient(160deg, #fff, var(--surface-soft));
      box-shadow: var(--shadow);
      overflow: hidden;
      transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
    }}
    .tool-card::before {{
      content: "";
      position: absolute;
      inset: 0 0 auto;
      height: 5px;
      background: linear-gradient(90deg, var(--lime-strong), var(--forest-600), var(--gold));
    }}
    .tool-card:hover {{ transform: translateY(-4px); border-color: rgba(35,122,75,.30); box-shadow: var(--shadow-lg); }}
    .tool-inner {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(280px, .82fr);
      gap: 22px;
      padding: 28px;
      min-height: 340px;
    }}
    .tool-main {{ display: flex; flex-direction: column; gap: 18px; }}
    .tool-icon {{
      width: 54px;
      height: 54px;
      border-radius: 15px;
      display: grid;
      place-items: center;
      color: var(--forest-700);
      background: linear-gradient(150deg, var(--forest-100), rgba(194,242,77,.32));
      box-shadow: inset 0 0 0 1px rgba(35,122,75,.14);
    }}
    .tool-icon svg {{ width: 28px; height: 28px; }}
    .tool-card h2 {{ margin: 0; font-size: 26px; line-height: 1.12; letter-spacing: -.02em; color: var(--forest-950); }}
    .tool-text {{ margin: 8px 0 0; max-width: 440px; color: var(--muted); font-size: 14.5px; line-height: 1.55; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 30px;
      padding: 0 12px;
      border-radius: 999px;
      border: 1px solid var(--line-strong);
      background: var(--surface);
      color: var(--forest-800);
      font-size: 12px;
      font-weight: 850;
    }}
    .chip::before {{ content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--forest-600); }}
    .tool-cta {{ margin-top: auto; }}

    /* Painel visual da previa */
    .visual {{
      position: relative;
      border-radius: var(--radius);
      overflow: hidden;
      background:
        radial-gradient(circle at 85% 8%, rgba(194,242,77,.26), transparent 45%),
        linear-gradient(160deg, var(--forest-900), var(--forest-700));
      border: 1px solid rgba(255,255,255,.08);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
    }}
    .visual {{ min-height: 340px; }}
    .visual::before {{
      content: "";
      position: absolute;
      inset: 0;
      opacity: .5;
      background-image: repeating-linear-gradient(58deg, rgba(255,255,255,.05) 0 1px, transparent 1px 30px);
    }}
    .sheet {{
      position: absolute;
      left: 24px;
      top: 64px;
      width: 200px;
      max-width: 64%;
      border-radius: 12px;
      background: #fff;
      box-shadow: 0 22px 44px rgba(0,0,0,.30);
      padding: 16px;
    }}
    .sheet-top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }}
    .sheet-title {{ width: 84px; height: 9px; border-radius: 999px; background: var(--forest-800); }}
    .sheet-check {{ width: 26px; height: 26px; border-radius: 8px; display: grid; place-items: center; color: var(--forest-700); background: var(--forest-100); }}
    .sheet-check svg {{ width: 16px; height: 16px; }}
    .sheet-line {{ height: 8px; border-radius: 999px; background: #e7ece2; margin-bottom: 9px; }}
    .sheet-line.mid {{ width: 82%; }}
    .sheet-line.short {{ width: 60%; }}
    .sheet-cells {{ margin-top: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }}
    .sheet-cell {{ height: 40px; border-radius: 8px; background: var(--forest-50); border: 1px solid #e0e8dc; }}
    .photo-card {{
      position: absolute;
      right: 22px;
      bottom: 22px;
      width: 126px;
      height: 96px;
      border-radius: 12px;
      overflow: hidden;
      border: 2px solid rgba(255,255,255,.85);
      background: linear-gradient(150deg, #3f8f61, var(--gold));
      box-shadow: 0 18px 36px rgba(0,0,0,.32);
    }}
    .photo-card::after {{
      content: "";
      position: absolute;
      left: 14px; right: 14px; bottom: 0;
      height: 38px;
      background: rgba(6,21,14,.42);
      border-radius: 50% 50% 0 0;
      transform: skewX(-12deg);
    }}
    .visual-caption {{
      position: absolute;
      left: 22px;
      top: 20px;
      z-index: 2;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 13px;
      border-radius: 999px;
      background: rgba(255,255,255,.94);
      color: var(--forest-900);
      font-size: 12px;
      font-weight: 850;
      box-shadow: 0 12px 26px rgba(0,0,0,.22);
    }}
    .visual-caption .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--lime-strong); box-shadow: 0 0 0 3px rgba(167,223,47,.28); }}
    .visual-badge {{
      position: absolute;
      right: 20px;
      top: 18px;
      z-index: 2;
      width: 40px;
      height: 40px;
      border-radius: 12px;
      display: grid;
      place-items: center;
      color: var(--forest-700);
      background: rgba(255,255,255,.94);
      box-shadow: 0 12px 26px rgba(0,0,0,.20);
    }}
    .visual-badge svg {{ width: 22px; height: 22px; }}

    /* Como funciona (passos) */
    .steps-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }}
    .step-card {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(160deg, #fff, var(--surface-soft));
      padding: 20px;
      box-shadow: var(--shadow-sm);
    }}
    .step-card .num {{
      width: 34px;
      height: 34px;
      border-radius: 11px;
      display: grid;
      place-items: center;
      font-weight: 900;
      color: var(--forest-950);
      background: linear-gradient(135deg, var(--lime), var(--lime-strong));
      margin-bottom: 13px;
    }}
    .step-card h4 {{ margin: 0 0 5px; font-size: 15.5px; color: var(--forest-950); letter-spacing: -.01em; }}
    .step-card p {{ margin: 0; color: var(--muted); font-size: 13.5px; line-height: 1.5; }}

    /* Por que usar (beneficios) */
    .benefits {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }}
    .benefit {{
      display: flex;
      gap: 13px;
      align-items: flex-start;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(160deg, #fff, var(--surface-soft));
      padding: 18px;
      box-shadow: var(--shadow-sm);
    }}
    .benefit-icon {{
      width: 42px;
      height: 42px;
      flex: 0 0 auto;
      border-radius: 12px;
      display: grid;
      place-items: center;
      color: var(--forest-700);
      background: linear-gradient(150deg, var(--forest-100), rgba(194,242,77,.32));
      box-shadow: inset 0 0 0 1px rgba(35,122,75,.14);
    }}
    .benefit-icon svg {{ width: 22px; height: 22px; }}
    .benefit h4 {{ margin: 0 0 4px; font-size: 15px; color: var(--forest-950); letter-spacing: -.01em; }}
    .benefit p {{ margin: 0; color: var(--muted); font-size: 13.5px; line-height: 1.5; }}

    /* Faixa de chamada */
    .cta-band {{
      margin-top: 18px;
      border-radius: var(--radius-lg);
      padding: 22px 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      flex-wrap: wrap;
      color: #fff;
      background:
        radial-gradient(circle at 90% -40%, rgba(194,242,77,.30), transparent 50%),
        linear-gradient(120deg, var(--forest-950), var(--forest-700));
      box-shadow: var(--shadow);
    }}
    .cta-band strong {{ display: block; font-size: 18px; letter-spacing: -.01em; }}
    .cta-band span {{ display: block; margin-top: 3px; color: rgba(255,255,255,.8); font-size: 14px; }}

    @media (max-width: 720px) {{
      .tool-inner {{ grid-template-columns: 1fr; }}
      .visual {{ min-height: 280px; }}
      .steps-row {{ grid-template-columns: 1fr; }}
      .benefits {{ grid-template-columns: 1fr; }}
      .cta-band {{ flex-direction: column; align-items: flex-start; }}
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    {_rail("home")}
    <main class="page">
      <div class="page-inner">
        <section class="hero">
          <div class="hero-top">
            <div>
              <span class="eyebrow">Relatorio de credito rural</span>
              <h1>Do campo ao documento,<br><span class="accent">sem retrabalho.</span></h1>
              <p class="lead">Com <strong style="color:#dff5b6;font-weight:850">IA integrada</strong>, transforme as anotacoes da vistoria em uma planilha de credito rural completa &mdash; com texto tecnico, fotos numeradas e tudo no padrao do laudo.</p>
            </div>
          </div>
          <div class="hero-actions" style="margin-top:24px">
            <a class="btn btn-primary" href="/relatorio-credito">
              Abrir relatorio de credito
              <svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </a>
            <span class="hero-chip"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5 10.2 7.7 12 3Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>IA integrada</span>
            <span class="hero-chip"><svg viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>Texto tecnico automatico</span>
          </div>
        </section>

        <section class="tool-card" aria-label="Relatorio de credito rural">
            <div class="tool-inner">
              <article class="tool-main">
                <div class="tool-icon">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                </div>
                <div>
                  <h2>Relatorio de credito rural</h2>
                  <p class="tool-text">Cole as anotacoes da visita, gere o texto tecnico, revise o essencial e baixe a planilha final ja com as fotos no padrao do laudo.</p>
                </div>
                <div class="chips">
                  <span class="chip">IA integrada</span>
                  <span class="chip">Texto tecnico</span>
                  <span class="chip">Fotos</span>
                  <span class="chip">Excel</span>
                </div>
                <div class="tool-cta">
                  <a class="btn btn-dark" href="/relatorio-credito">
                    Abrir ferramenta
                    <svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </a>
                </div>
              </article>
              <aside class="visual" aria-hidden="true">
                <span class="visual-caption"><span class="dot"></span>Relatorio pronto</span>
                <span class="visual-badge"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5 10.2 7.7 12 3Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg></span>
                <div class="sheet">
                  <div class="sheet-top">
                    <div class="sheet-title"></div>
                    <div class="sheet-check"><svg viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
                  </div>
                  <div class="sheet-line"></div>
                  <div class="sheet-line mid"></div>
                  <div class="sheet-line short"></div>
                  <div class="sheet-cells">
                    <div class="sheet-cell"></div>
                    <div class="sheet-cell"></div>
                    <div class="sheet-cell"></div>
                    <div class="sheet-cell"></div>
                  </div>
                </div>
                <div class="photo-card"></div>
              </aside>
            </div>
          </section>

        <div class="section-label">Como funciona</div>
        <div class="steps-row">
          <div class="step-card">
            <div class="num">1</div>
            <h4>Cole as anotacoes</h4>
            <p>Jogue o texto bruto da vistoria e anexe as fotos, do jeito que recebeu do campo.</p>
          </div>
          <div class="step-card">
            <div class="num">2</div>
            <h4>A IA monta o laudo</h4>
            <p>O texto tecnico e os dados sao gerados e organizados no padrao do relatorio.</p>
          </div>
          <div class="step-card">
            <div class="num">3</div>
            <h4>Baixe a planilha</h4>
            <p>O Excel sai pronto, com as fotos numeradas e os campos preenchidos.</p>
          </div>
        </div>

        <div class="section-label">Por que usar</div>
        <div class="benefits">
          <div class="benefit">
            <span class="benefit-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/></svg></span>
            <div><h4>Horas viram minutos</h4><p>Do texto bruto da visita ao laudo final em poucos minutos, sem digitar a planilha na mao.</p></div>
          </div>
          <div class="benefit">
            <span class="benefit-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M14 3v4h4M9 13h6M9 17h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></span>
            <div><h4>No padrao do laudo</h4><p>A planilha sai no modelo aprovado, com as fotos da vistoria numeradas no lugar certo.</p></div>
          </div>
          <div class="benefit">
            <span class="benefit-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3 4 6v6c0 5 3.5 7.5 8 9 4.5-1.5 8-4 8-9V6l-8-3Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="m9 12 2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
            <div><h4>IA que nao inventa</h4><p>So preenche o que esta nas anotacoes. O que nao foi informado fica em branco &mdash; nada de dado inventado.</p></div>
          </div>
          <div class="benefit">
            <span class="benefit-icon"><svg viewBox="0 0 24 24" fill="none"><path d="M4 7h16v13H4V7Z" stroke="currentColor" stroke-width="2"/><path d="m8 7 2-3h4l2 3M8 14l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
            <div><h4>Texto tecnico pronto</h4><p>Transforma anotacoes pobres em redacao tecnica de qualidade, no tom de analise de credito.</p></div>
          </div>
        </div>

        <div class="cta-band">
          <div>
            <strong>Pronto para testar?</strong>
            <span>Abra a ferramenta, clique em &ldquo;Ver exemplo&rdquo; e gere um laudo em segundos.</span>
          </div>
          <a class="btn btn-primary" href="/relatorio-credito">
            Abrir ferramenta
            <svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </a>
        </div>
      </div>
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
  <title>__BRAND__ | Relatorio de credito</title>
  <style>
    __BASE_CSS__
    .hero.compact { padding: 22px 28px 20px; }
    .hero.compact h1 { font-size: clamp(23px, 3vw, 31px); }
    .hero.compact .eyebrow { margin-bottom: 10px; }
    .hero.compact .lead { margin-top: 7px; font-size: 14px; }
    .hero.compact .hero-strip { margin-top: 14px; }
    .hero.compact::after { width: 200px; height: 200px; right: -70px; top: -70px; }
    .clear-btn {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      min-height: 36px;
      padding: 0 13px;
      border-radius: 10px;
      border: 1px solid var(--line-strong);
      background: var(--surface);
      color: var(--forest-800);
      font-size: 13px;
      font-weight: 800;
      cursor: pointer;
      transition: background .15s ease, border-color .15s ease, transform .15s ease;
    }
    .clear-btn:hover { background: var(--forest-50); border-color: var(--forest-600); transform: translateY(-1px); }
    .clear-btn svg { width: 16px; height: 16px; }
    .workspace { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 18px; align-items: start; margin-top: 18px; }
    .main-panel { min-height: 0; }
    .notes-card {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(180deg, #fff, var(--surface-soft));
      padding: 16px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,.8);
    }
    .notes-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
    .notes-head label { margin: 0; }
    .notes-badge {
      padding: 6px 11px;
      border-radius: 999px;
      background: var(--forest-50);
      color: var(--forest-800);
      font-size: 12px;
      font-weight: 850;
      white-space: nowrap;
    }
    label { display: block; margin-bottom: 7px; color: #2e4236; font-size: 13px; font-weight: 850; }
    textarea, input[type="text"] {
      width: 100%;
      border: 1px solid var(--line-strong);
      border-radius: var(--radius-sm);
      color: var(--ink);
      background: #fffefb;
      outline: none;
      transition: border-color .15s ease, box-shadow .15s ease;
    }
    textarea:focus, input[type="text"]:focus { border-color: var(--forest-600); box-shadow: var(--ring); }
    textarea { min-height: 250px; resize: vertical; padding: 16px; font: 15px/1.6 "Segoe UI", Arial, sans-serif; }
    #rawData::placeholder { color: #97a397; line-height: 1.7; }
    input[type="text"] { min-height: 40px; padding: 10px 12px; font-size: 14px; }
    .link-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 10px;
      border-radius: 999px;
      border: 1px solid var(--line-strong);
      background: var(--forest-50);
      color: var(--forest-700);
      font-size: 12.5px;
      font-weight: 850;
      cursor: pointer;
      transition: background .15s ease, border-color .15s ease, transform .15s ease;
    }
    .link-btn:hover { background: var(--forest-100); border-color: var(--forest-600); transform: translateY(-1px); }
    .link-btn svg { width: 15px; height: 15px; }

    .upload-card {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(180deg, rgba(255,255,255,.8), var(--surface-soft));
      padding: 14px;
      display: grid;
      gap: 12px;
      box-shadow: var(--shadow-sm);
    }
    .upload-button {
      min-height: 128px;
      border: 1.5px dashed rgba(35,122,75,.45);
      border-radius: var(--radius-sm);
      background: linear-gradient(140deg, rgba(35,122,75,.07), rgba(194,242,77,.14)), #fffef9;
      color: var(--forest-900);
      display: grid;
      place-items: center;
      gap: 8px;
      padding: 18px;
      text-align: center;
      cursor: pointer;
      transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease, background .18s ease;
    }
    .upload-button:hover { border-color: var(--forest-600); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
    .upload-button.drag-over { border-color: var(--lime-strong); background: linear-gradient(140deg, rgba(35,122,75,.12), rgba(194,242,77,.26)), #fffef9; }
    .upload-button input { display: none; }
    .upload-button strong { display: block; font-size: 15px; }
    .upload-button small { display: block; color: var(--muted); font-size: 12px; font-weight: 600; }
    .upload-icon {
      width: 46px; height: 46px;
      border-radius: 50%;
      display: grid; place-items: center;
      color: var(--forest-950);
      background: linear-gradient(135deg, var(--lime), var(--lime-strong));
      box-shadow: 0 10px 22px rgba(141,196,47,.34);
    }
    .upload-icon svg { width: 22px; height: 22px; }
    .file-count { color: var(--muted); font-size: 13px; }
    .file-list { display: grid; gap: 6px; max-height: 120px; overflow: auto; }
    .file-pill {
      min-height: 30px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      color: var(--forest-950);
      display: flex; align-items: center; justify-content: space-between; gap: 8px;
      padding: 6px 11px;
      font-size: 12px;
    }
    .file-pill span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .file-pill small { color: var(--muted); flex: 0 0 auto; }

    .submit-wrap { display: grid; gap: 8px; }
    .submit-wrap .btn-primary { min-height: 56px; font-size: 15.5px; width: 100%; }
    .muted { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.45; }

    .notice {
      display: none;
      padding: 11px 13px;
      border: 1px solid #efd8a5;
      border-radius: var(--radius-sm);
      background: var(--warn-bg);
      color: #6c4a07;
      font-size: 13px;
      line-height: 1.45;
    }
    .notice.success { border-color: #bfd8c1; background: var(--forest-100); color: var(--forest-900); }
    .notice.show { display: block; }

    /* Painel lateral de etapas */
    .side-panel { position: sticky; top: 18px; }
    .steps { display: grid; gap: 12px; }
    .step {
      display: flex;
      gap: 12px;
      align-items: flex-start;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      background: var(--surface-soft);
    }
    .step-num {
      width: 28px; height: 28px;
      flex: 0 0 auto;
      border-radius: 9px;
      display: grid; place-items: center;
      font-size: 13px; font-weight: 900;
      color: var(--forest-950);
      background: linear-gradient(135deg, var(--lime), var(--lime-strong));
    }
    .step strong { display: block; color: var(--forest-950); font-size: 13.5px; }
    .step span { display: block; margin-top: 3px; color: var(--muted); font-size: 12.5px; line-height: 1.45; }
    .status-tile {
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 13px;
      background: linear-gradient(150deg, var(--forest-100), rgba(194,242,77,.18));
      display: grid; gap: 4px;
    }
    .status-tile small { color: var(--forest-700); font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: .04em; }
    .status-tile strong { color: var(--forest-950); font-size: 16px; }

    .hidden-workspace { display: none; }

    /* Overlay de progresso */
    .overlay {
      position: fixed; inset: 0; z-index: 30;
      display: none; place-items: center;
      padding: 18px;
      background: rgba(6,21,14,.62);
      backdrop-filter: blur(8px);
    }
    .overlay.show { display: grid; }
    .overlay-card {
      width: min(440px, 100%);
      border-radius: var(--radius);
      padding: 26px;
      background: #fffef9;
      box-shadow: 0 40px 90px rgba(0,0,0,.4);
      text-align: center;
    }
    .loader {
      width: 46px; height: 46px;
      margin: 0 auto 16px;
      border-radius: 50%;
      border: 4px solid var(--forest-100);
      border-top-color: var(--forest-600);
      animation: spin .8s linear infinite;
    }
    .overlay-card h2 { margin: 0; color: var(--forest-950); font-size: 20px; }
    .overlay-card p { margin: 8px 0 0; color: var(--muted); font-size: 14px; }
    .progress-track { height: 8px; border-radius: 999px; margin-top: 18px; overflow: hidden; background: #e7eddf; }
    .progress-bar {
      width: 42%; height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--forest-600), var(--lime-strong));
      animation: progress 1.5s ease-in-out infinite;
    }
    @keyframes progress { 0% { transform: translateX(-90%);} 55% { transform: translateX(95%);} 100% { transform: translateX(190%);} }

    @media (max-width: 1100px) {
      .workspace { grid-template-columns: 1fr; }
      .side-panel { position: static; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    __RAIL__
    <main class="page">
      <div class="page-inner">
        <section class="hero compact">
          <div class="hero-top">
            <div>
              <span class="eyebrow">Ferramenta &middot; Credito rural</span>
              <h1>Gerador de <span class="accent">planilha final</span></h1>
              <p class="lead">Cole as anotacoes da vistoria, anexe as fotos e baixe o Excel ja no padrao do laudo.</p>
              <div class="hero-strip">
                <span class="hero-chip"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3l1.8 4.7L18.5 9.5 13.8 11.3 12 16l-1.8-4.7L5.5 9.5 10.2 7.7 12 3Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>IA integrada</span>
                <span class="hero-chip"><svg viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>Extracao automatica</span>
                <span class="hero-chip"><svg viewBox="0 0 24 24" fill="none"><path d="M4 7h16v13H4V7Z" stroke="currentColor" stroke-width="2"/><path d="m8 7 2-3h4l2 3" stroke="currentColor" stroke-width="2"/></svg>Fotos numeradas</span>
                <span class="hero-chip"><svg viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/></svg>XLSX</span>
              </div>
            </div>
          </div>
        </section>

        <form id="reportForm" method="post" action="/generate" enctype="multipart/form-data" class="workspace">
          <section class="panel main-panel">
            <div class="panel-head">
              <div class="panel-title">
                <svg viewBox="0 0 24 24" fill="none"><path d="M4 5h16M4 12h16M4 19h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                Entrada do relatorio
              </div>
              <button class="clear-btn" type="button" id="clearBtn">
                <svg viewBox="0 0 24 24" fill="none"><path d="M4 12a8 8 0 1 0 2.4-5.7M4 4v3.6h3.6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Limpar
              </button>
            </div>
            <div class="panel-body">
              <div class="notes-card">
                <div class="notes-head">
                  <label for="rawData">Anotacoes da vistoria</label>
                  <button type="button" id="sampleBtn" class="link-btn">
                    <svg viewBox="0 0 24 24" fill="none"><path d="M12 3l1.6 4.2L18 9l-4.4 1.8L12 15l-1.6-4.2L6 9l4.4-1.8L12 3Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
                    Ver exemplo
                  </button>
                </div>
                <textarea id="rawData" placeholder="Cole aqui as anotacoes da vistoria, do jeito que voce recebeu do campo &mdash; nao precisa organizar.&#10;&#10;Se tiver, ajuda incluir:&#10;&bull; Produtor, propriedade e municipio&#10;&bull; Area (alqueires ou hectares)&#10;&bull; Rebanho ou lavouras&#10;&bull; Benfeitorias (curral, cochos, bebedouros, galpao...)&#10;&bull; Maquinarios"></textarea>
              </div>

              <div class="upload-card">
                <label class="upload-button" for="photos">
                  <input id="photos" name="photos" type="file" accept="image/*" multiple>
                  <span class="upload-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none"><path d="M4 7h16v13H4V7Z" stroke="currentColor" stroke-width="2"/><path d="m8 7 2-3h4l2 3" stroke="currentColor" stroke-width="2"/><path d="m8 15 2-2 3 3 2-2 3 4" stroke="currentColor" stroke-width="2"/></svg>
                  </span>
                  <span>
                    <strong>Selecionar fotos da vistoria</strong>
                    <small>Escolha varias imagens de uma vez ou arraste aqui</small>
                  </span>
                </label>
                <span class="file-count" id="fileCount">Nenhuma foto selecionada</span>
                <div class="file-list" id="fileList"></div>
              </div>

              <div id="writerNotice" class="notice"></div>

              <div class="submit-wrap">
                <button class="btn btn-primary" type="submit" id="submitBtn" data-label="Gerar e baixar planilha">
                  <span class="spinner" aria-hidden="true"></span>
                  <span class="btn-label">Gerar e baixar planilha</span>
                </button>
                <p class="muted">O texto tecnico e a extracao acontecem automaticamente antes do download.</p>
              </div>

              <input type="hidden" id="reviewData" name="review_data">
              <textarea id="dados" name="dados" hidden></textarea>
            </div>
          </section>

          <aside class="side-panel">
            <section class="panel">
              <div class="panel-head">
                <div class="panel-title">
                  <svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  Como funciona
                </div>
              </div>
              <div class="panel-body">
                <div class="status-tile">
                  <small>Status</small>
                  <strong id="statusTile">Pronto para gerar</strong>
                </div>
                <div class="steps">
                  <div class="step"><span class="step-num">1</span><div><strong>Cole as anotacoes</strong><span>Texto bruto da visita, do jeito que recebeu.</span></div></div>
                  <div class="step"><span class="step-num">2</span><div><strong>Anexe as fotos</strong><span>Elas entram numeradas no padrao do laudo.</span></div></div>
                  <div class="step"><span class="step-num">3</span><div><strong>Baixe a planilha</strong><span>Texto tecnico e campos preenchidos automaticamente.</span></div></div>
                </div>
              </div>
            </section>
          </aside>

          <div class="hidden-workspace" aria-hidden="true">
            <div class="summary" id="summaryItems"></div>
            <div id="fields" class="fields"></div>
            <textarea id="technicalPreview"></textarea>
            <button type="button" id="writeBtn" data-label="Gerar texto tecnico"></button>
            <button type="button" id="extractBtn" data-label="Atualizar extracao"></button>
            <strong id="statusText">Pronto para gerar</strong>
            <div id="previewBox"></div>
            <div id="okBox"></div>
            <div id="missingBox"></div>
          </div>
        </form>
      </div>
    </main>
  </div>

  <div class="overlay" id="downloadOverlay" role="status" aria-live="polite">
    <div class="overlay-card">
      <div class="loader" aria-hidden="true"></div>
      <h2 id="overlayTitle">Gerando planilha</h2>
      <p id="overlayText">Preparando o arquivo para download.</p>
      <div class="progress-track"><div class="progress-bar"></div></div>
    </div>
  </div>

<script>
  const rawData = document.getElementById('rawData');
  const technicalText = document.getElementById('dados');
  const technicalPreview = document.getElementById('technicalPreview');
  const writeBtn = document.getElementById('writeBtn');
  const writerNotice = document.getElementById('writerNotice');
  const extractBtn = document.getElementById('extractBtn');
  const fieldsEl = document.getElementById('fields');
  const summaryItems = document.getElementById('summaryItems');
  const previewBox = document.getElementById('previewBox');
  const missingBox = document.getElementById('missingBox');
  const okBox = document.getElementById('okBox');
  const statusText = document.getElementById('statusText');
  const statusTile = document.getElementById('statusTile');
  const reviewData = document.getElementById('reviewData');
  const fileInput = document.getElementById('photos');
  const uploadButton = document.querySelector('.upload-button');
  const fileCount = document.getElementById('fileCount');
  const fileList = document.getElementById('fileList');
  const form = document.getElementById('reportForm');
  const submitBtn = document.getElementById('submitBtn');
  const overlay = document.getElementById('downloadOverlay');
  const overlayTitle = document.getElementById('overlayTitle');
  const overlayText = document.getElementById('overlayText');
  let lastExtraction = null;

  function setStatus(text) {
    if (statusText) statusText.textContent = text;
    if (statusTile) statusTile.textContent = text;
  }

  const SAMPLE_NOTES = [
    'Jose Carlos Ferreira',
    'CPF 123.456.789-00',
    'Acesso: saindo de Rio Verde-GO pela GO-174, ande 12 km e vire a direita na estrada de chao, mais 3 km ate a porteira',
    '',
    'Fazenda Boa Esperanca - Rio Verde-GO',
    '80 hectares',
    '55 hectares de pastagem',
    '20 hectares de soja',
    'Pecuaria de corte e lavoura de soja',
    '320 cabecas de gado nelore - cria e recria',
    'Pastagem de brachiaria',
    '2 currais',
    'cochos cobertos nos piquetes',
    'bebedouros nos piquetes',
    '1 represa',
    'galpao de armazenagem de maquinarios',
    '2 funcionarios fixos',
    '',
    'Trator Massey Ferguson 4292',
    'Colheitadeira John Deere 1550',
    'Plantadeira Tatu 12 linhas'
  ].join('\\n');

  const sampleBtn = document.getElementById('sampleBtn');
  if (sampleBtn) {
    sampleBtn.addEventListener('click', () => {
      rawData.value = SAMPLE_NOTES;
      rawData.focus();
      rawData.scrollTop = 0;
      setStatus('Exemplo carregado');
    });
  }

  document.getElementById('clearBtn').addEventListener('click', () => {
    rawData.value = '';
    technicalText.value = '';
    technicalPreview.value = '';
    fieldsEl.innerHTML = '';
    summaryItems.innerHTML = '';
    setPreview('');
    writerNotice.className = 'notice';
    writerNotice.textContent = '';
    okBox.className = 'notice success';
    okBox.textContent = '';
    missingBox.className = 'notice';
    missingBox.textContent = '';
    setStatus('Pronto para gerar');
    reviewData.value = '';
    lastExtraction = null;
    if (fileInput) fileInput.value = '';
    if (fileCount) fileCount.textContent = 'Nenhuma foto selecionada';
    if (fileList) fileList.innerHTML = '';
    rawData.focus();
  });

  function setBusy(button, busy, label) {
    if (!button) return;
    button.disabled = busy;
    const text = button.querySelector('.btn-label');
    if (text) text.textContent = busy ? label : button.dataset.label;
  }

  function setAllBusy(busy, label = 'Gerando') {
    setBusy(submitBtn, busy, label);
    setBusy(writeBtn, busy, 'Aguarde');
    setBusy(extractBtn, busy, 'Aguarde');
  }

  function showOverlay(title, text) {
    overlayTitle.textContent = title;
    overlayText.textContent = text;
    overlay.classList.add('show');
  }

  function hideOverlay() {
    overlay.classList.remove('show');
  }

  extractBtn.addEventListener('click', refreshFieldsFromTechnicalText);

  technicalPreview.addEventListener('input', () => {
    technicalText.value = technicalPreview.value;
    reviewData.value = '';
    lastExtraction = null;
    setStatus('Extracao pendente');
    missingBox.textContent = 'Texto alterado. Atualize a extracao antes de gerar.';
    missingBox.className = 'notice show';
  });

  async function generateTechnicalReport() {
    const rawText = rawData.value.trim();
    if (!rawText) throw new Error('Cole as anotacoes da vistoria.');
    writerNotice.className = 'notice';
    writerNotice.textContent = '';

    const response = await fetch('/write-technical-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: rawText })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'Nao consegui gerar o relatorio.');

    technicalText.value = payload.report_text || '';
    technicalPreview.value = payload.report_text || '';
    setPreview(payload.report_text || '');
    renderFields(payload.review);
    writerNotice.className = 'notice success show';
    writerNotice.textContent = 'Dados preparados. Gerando a planilha.';
    setStatus('Dados prontos');
    return payload;
  }

  async function refreshFieldsFromTechnicalText() {
    const dados = technicalText.value.trim();
    if (!dados) {
      technicalPreview.focus();
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
      if (!response.ok) throw new Error(payload.error || 'Nao consegui atualizar a extracao.');
      renderFields(payload);
      setStatus('Extracao pronta');
      return true;
    } catch (error) {
      showError(error.message);
      return false;
    } finally {
      setBusy(extractBtn, false, '');
    }
  }

  function renderFields(payload) {
    if (!payload) return;
    lastExtraction = payload;
    fieldsEl.innerHTML = '';
    renderSummary(payload);

    if (payload.missing.length) {
      okBox.textContent = `${payload.summary.found} campos encontrados.`;
      okBox.className = 'notice success show';
      missingBox.textContent = `Campos faltando: ${payload.missing.join(', ')}.`;
      missingBox.className = 'notice show';
    } else {
      okBox.textContent = 'Campos essenciais reconhecidos.';
      okBox.className = 'notice success show';
      missingBox.className = 'notice';
      missingBox.textContent = '';
    }

    payload.fields.forEach((field) => {
      const wrapper = document.createElement('div');
      wrapper.className = `field ${field.missing ? 'missing' : ''}`;
      const label = document.createElement('label');
      label.htmlFor = `field-${field.key}`;
      label.textContent = field.label;
      if (field.required) {
        const required = document.createElement('span');
        required.className = 'required';
        required.textContent = field.missing ? 'faltando' : 'obrigatorio';
        label.appendChild(required);
      }
      const input = field.type === 'textarea' ? document.createElement('textarea') : document.createElement('input');
      input.id = `field-${field.key}`;
      input.dataset.key = field.key;
      if (field.type !== 'textarea') input.type = 'text';
      input.value = field.value || '';
      input.addEventListener('input', () => {
        syncReviewData();
        renderSummaryFromInputs();
      });
      wrapper.appendChild(label);
      wrapper.appendChild(input);
      fieldsEl.appendChild(wrapper);
    });
    syncReviewData();
  }

  function fieldValue(payload, key) {
    const item = payload.fields.find((field) => field.key === key);
    return item && item.value ? item.value : 'Nao informado';
  }

  function renderSummary(payload) {
    summaryItems.innerHTML = '';
  }

  function renderSummaryFromInputs() {
    const getValue = (key) => {
      const input = fieldsEl.querySelector(`[data-key="${key}"]`);
      return input && input.value ? input.value : 'Nao informado';
    };
    renderSummary({
      fields: [
        { key: 'cliente', value: getValue('cliente') },
        { key: 'area_total_ha', value: getValue('area_total_ha') },
        { key: 'imovel_nome', value: getValue('imovel_nome') },
        { key: 'atividade_principal', value: getValue('atividade_principal') }
      ]
    });
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function setPreview(text) {
    const clean = String(text || '').trim();
    if (!clean) {
      previewBox.textContent = '';
      previewBox.className = 'preview-box empty';
      return;
    }
    const limit = 1500;
    previewBox.textContent = clean.length > limit ? `${clean.slice(0, limit).trim()}...` : clean;
    previewBox.className = 'preview-box';
  }

  function syncReviewData() {
    if (!lastExtraction) return;
    const fields = {};
    fieldsEl.querySelectorAll('[data-key]').forEach((input) => {
      fields[input.dataset.key] = input.value;
    });
    reviewData.value = JSON.stringify({ parsed: lastExtraction.parsed, fields });
  }

  function showError(message) {
    writerNotice.textContent = message;
    writerNotice.className = 'notice show';
    missingBox.textContent = message;
    missingBox.className = 'notice show';
    setStatus('Atencao');
  }

  function filenameFromResponse(response) {
    const header = response.headers.get('content-disposition') || '';
    const match = header.match(/filename="?([^"]+)"?/i);
    return match ? match[1] : 'relatorio-agrolaudo.xlsx';
  }

  async function downloadWorkbook() {
    const formData = new FormData(form);
    const response = await fetch('/generate', { method: 'POST', body: formData });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text.replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim() || 'Nao consegui gerar a planilha.');
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filenameFromResponse(response);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  fileInput.addEventListener('change', () => {
    const files = Array.from(fileInput.files || []);
    const total = files.length;
    fileCount.textContent = total === 0
      ? 'Nenhuma foto selecionada'
      : total === 1
        ? '1 foto selecionada'
        : `${total} fotos selecionadas`;
    fileList.innerHTML = files.slice(0, 6).map((file, index) => `
      <div class="file-pill">
        <span>Foto ${String(index + 1).padStart(2, '0')} - ${escapeHtml(file.name)}</span>
        <small>${Math.max(1, Math.round(file.size / 1024))} KB</small>
      </div>
    `).join('');
    if (total > 6) {
      fileList.insertAdjacentHTML('beforeend', `<div class="file-pill"><span>Mais ${total - 6} foto(s)</span><small>incluidas</small></div>`);
    }
  });

  ['dragenter', 'dragover'].forEach((eventName) => {
    uploadButton.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadButton.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach((eventName) => {
    uploadButton.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadButton.classList.remove('drag-over');
    });
  });

  uploadButton.addEventListener('drop', (event) => {
    const files = Array.from(event.dataTransfer.files || []).filter((file) => file.type.startsWith('image/'));
    if (!files.length) return;
    fileInput.files = event.dataTransfer.files;
    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!rawData.value.trim() && !technicalText.value.trim()) {
      rawData.focus();
      return;
    }

    setAllBusy(true, 'Gerando');
    try {
      if (!technicalText.value.trim()) {
        showOverlay('Escrevendo relatorio', 'Convertendo as anotacoes em texto tecnico.');
        await generateTechnicalReport();
      }
      if (!reviewData.value) {
        showOverlay('Extraindo campos', 'Separando cliente, areas e propriedades.');
        const ok = await refreshFieldsFromTechnicalText();
        if (!ok) return;
      }
      syncReviewData();
      showOverlay('Gerando planilha', 'Preparando o arquivo para download.');
      await downloadWorkbook();
      overlayTitle.textContent = 'Download iniciado';
      overlayText.textContent = 'A planilha foi enviada para o navegador.';
      setStatus('Planilha baixada');
      setTimeout(hideOverlay, 1200);
    } catch (error) {
      hideOverlay();
      showError(error.message);
    } finally {
      setAllBusy(false);
    }
  });
</script>
</body>
</html>""".replace("__BASE_CSS__", _base_css()).replace("__RAIL__", _rail("tool")).replace("__BRAND__", BRAND)
