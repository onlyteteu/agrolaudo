from __future__ import annotations


def render_home() -> str:
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Central Agro</title>
  <style>
    :root {
      --bg: #f7f6f0;
      --surface: #ffffff;
      --surface-soft: #fbfaf5;
      --ink: #14231b;
      --muted: #667165;
      --line: #dfe4d9;
      --line-strong: #c9d2c3;
      --green-950: #0b2119;
      --green-900: #123629;
      --green-800: #1f4c39;
      --green-700: #2d7450;
      --green-600: #3f8f61;
      --green-100: #e9f2e6;
      --green-50: #f4f8f0;
      --sand: #b8945d;
      --sand-soft: #f2ebdd;
      --shadow: 0 22px 55px rgba(20, 49, 35, .11);
      --soft-shadow: 0 12px 32px rgba(20, 49, 35, .08);
      --radius: 10px;
    }
    * { box-sizing: border-box; }
    html { color-scheme: light; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 82% 12%, rgba(184, 148, 93, .12), transparent 26rem),
        radial-gradient(circle at 38% -10%, rgba(45, 116, 80, .12), transparent 24rem),
        linear-gradient(180deg, rgba(255,255,255,.68), rgba(247,246,240,0) 25rem),
        var(--bg);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: .36;
      background-image:
        linear-gradient(135deg, transparent 0 47%, rgba(31,76,57,.08) 48% 49%, transparent 50% 100%),
        linear-gradient(45deg, transparent 0 47%, rgba(184,148,93,.07) 48% 49%, transparent 50% 100%);
      background-size: 82px 82px, 118px 118px;
      mask-image: linear-gradient(180deg, #000, transparent 72%);
    }
    a, button, input, textarea, summary { font: inherit; }
    svg { flex: 0 0 auto; }
    .app-shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 214px minmax(0, 1fr);
      position: relative;
    }
    .rail {
      border-right: 1px solid var(--line);
      background: rgba(255,255,255,.76);
      backdrop-filter: blur(18px);
      padding: 18px 12px;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }
    .brand {
      min-height: 46px;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 7px;
      color: var(--green-950);
      font-size: 17px;
      font-weight: 900;
    }
    .brand-mark {
      width: 40px;
      height: 40px;
      border-radius: var(--radius);
      display: grid;
      place-items: center;
      color: #fff;
      background:
        linear-gradient(145deg, rgba(255,255,255,.14), transparent),
        var(--green-950);
      box-shadow: 0 12px 26px rgba(11,33,25,.18);
    }
    .nav {
      display: grid;
      gap: 6px;
    }
    .nav a {
      min-height: 42px;
      padding: 0 10px;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      gap: 10px;
      color: #46574b;
      text-decoration: none;
      font-size: 14px;
      font-weight: 760;
      transition: background .18s ease, color .18s ease, transform .18s ease;
    }
    .nav a.active {
      color: var(--green-950);
      background: #edf4e8;
      box-shadow: inset 0 0 0 1px rgba(45,116,80,.08);
    }
    .nav a:not(.active):hover {
      background: #f4f7f0;
      color: var(--green-900);
      transform: translateX(2px);
    }
    .rail-note {
      margin-top: auto;
      min-height: 1px;
    }
    .page {
      min-width: 0;
      padding: 36px 34px 44px;
    }
    .page-inner {
      width: min(1040px, 100%);
      margin: 0 auto;
    }
    .page-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 22px;
      margin-bottom: 20px;
    }
    .eyebrow {
      margin-bottom: 8px;
      color: var(--green-700);
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      color: var(--green-950);
      font-size: 33px;
      line-height: 1.1;
      letter-spacing: 0;
    }
    .lead {
      max-width: 590px;
      margin: 9px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }
    .page-badge {
      min-height: 38px;
      padding: 0 11px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255,255,255,.74);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--green-900);
      font-size: 13px;
      font-weight: 850;
      white-space: nowrap;
    }
    .section-label {
      margin: 18px 0 12px;
      color: var(--green-950);
      font-size: 15px;
      font-weight: 900;
    }
    .tool-card {
      position: relative;
      border: 1px solid rgba(201,210,195,.9);
      border-radius: 12px;
      background:
        linear-gradient(145deg, rgba(255,255,255,.98), rgba(251,250,245,.93)),
        var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
      transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
    }
    .tool-card:hover {
      transform: translateY(-2px);
      border-color: rgba(47,116,80,.28);
      box-shadow: 0 28px 70px rgba(20,49,35,.14);
    }
    .tool-card::before {
      content: "";
      position: absolute;
      inset: auto 0 0;
      height: 4px;
      background: linear-gradient(90deg, var(--green-800), var(--sand));
      opacity: .9;
    }
    .tool-card-inner {
      display: grid;
      grid-template-columns: minmax(0, .92fr) minmax(340px, .78fr);
      gap: 18px;
      min-height: 356px;
      padding: 26px;
    }
    .tool-main {
      display: grid;
      align-content: space-between;
      gap: 24px;
      padding: 6px 0 4px;
    }
    .tool-copy {
      display: flex;
      gap: 16px;
      align-items: flex-start;
    }
    .tool-icon {
      width: 50px;
      height: 50px;
      border-radius: var(--radius);
      display: grid;
      place-items: center;
      color: var(--green-900);
      background:
        linear-gradient(145deg, rgba(255,255,255,.65), transparent),
        var(--green-100);
      box-shadow: inset 0 0 0 1px rgba(47,116,80,.10);
    }
    h2 {
      margin: 0;
      color: var(--green-950);
      font-size: 25px;
      line-height: 1.16;
      letter-spacing: 0;
    }
    .tool-text {
      max-width: 560px;
      margin: 8px 0 0;
      color: var(--muted);
      line-height: 1.52;
    }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
    }
    .chip {
      min-height: 30px;
      display: inline-flex;
      align-items: center;
      padding: 0 10px;
      border-radius: 999px;
      border: 1px solid rgba(201,210,195,.72);
      background: rgba(244,248,240,.72);
      color: var(--green-800);
      font-size: 12px;
      font-weight: 900;
    }
    .primary-action {
      width: fit-content;
      min-height: 46px;
      padding: 0 17px;
      border-radius: var(--radius);
      border: 1px solid var(--green-700);
      background: var(--green-800);
      color: #fff;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      font-weight: 900;
      box-shadow: 0 14px 28px rgba(34,82,61,.16);
      transition: background .18s ease, transform .18s ease, box-shadow .18s ease;
    }
    .primary-action:hover {
      background: var(--green-950);
      transform: translateY(-1px);
      box-shadow: 0 18px 34px rgba(34,82,61,.20);
    }
    .visual-panel {
      position: relative;
      min-height: 304px;
      border: 1px solid rgba(223,228,217,.95);
      border-radius: 12px;
      background:
        radial-gradient(circle at 84% 12%, rgba(184,148,93,.18), transparent 9rem),
        linear-gradient(160deg, #fbfcf8, #eef5ea);
      overflow: hidden;
    }
    .visual-panel::before {
      content: "";
      position: absolute;
      inset: 0;
      opacity: .34;
      background-image:
        linear-gradient(135deg, transparent 0 48%, rgba(18,54,41,.12) 49%, transparent 50%),
        linear-gradient(45deg, transparent 0 48%, rgba(184,148,93,.12) 49%, transparent 50%);
      background-size: 58px 58px, 92px 92px;
    }
    .visual-orbit {
      position: absolute;
      width: 190px;
      height: 190px;
      right: -48px;
      top: -58px;
      border: 1px solid rgba(47,116,80,.16);
      border-radius: 50%;
    }
    .visual-orbit::after {
      content: "";
      position: absolute;
      width: 120px;
      height: 120px;
      inset: 34px;
      border: 1px solid rgba(184,148,93,.18);
      border-radius: 50%;
    }
    .report-sheet {
      position: absolute;
      left: 36px;
      top: 34px;
      width: 188px;
      height: 238px;
      border: 1px solid rgba(201,210,195,.9);
      border-radius: 10px;
      background: rgba(255,255,255,.94);
      box-shadow: var(--soft-shadow);
      padding: 18px;
    }
    .sheet-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
    }
    .sheet-title {
      width: 92px;
      height: 9px;
      border-radius: 999px;
      background: var(--green-900);
    }
    .sheet-dot {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      color: var(--green-800);
      background: var(--green-100);
    }
    .sheet-line {
      height: 8px;
      border-radius: 999px;
      background: #e7ece2;
      margin-bottom: 10px;
    }
    .sheet-line.short { width: 66%; }
    .sheet-line.mid { width: 82%; }
    .sheet-block {
      margin-top: 18px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .sheet-cell {
      min-height: 42px;
      border-radius: 8px;
      background: #f4f8f0;
      border: 1px solid #e0e8dc;
      padding: 8px;
    }
    .sheet-cell::before,
    .sheet-cell::after {
      content: "";
      display: block;
      height: 6px;
      border-radius: 999px;
      background: #d7e3d3;
    }
    .sheet-cell::after {
      width: 58%;
      margin-top: 7px;
      background: #e2cfae;
    }
    .photo-card {
      position: absolute;
      right: 36px;
      bottom: 42px;
      width: 128px;
      height: 98px;
      border-radius: 12px;
      border: 1px solid rgba(201,210,195,.95);
      background:
        linear-gradient(135deg, rgba(47,116,80,.22), rgba(184,148,93,.17)),
        #f6f3ea;
      box-shadow: var(--soft-shadow);
      overflow: hidden;
    }
    .photo-card::before {
      content: "";
      position: absolute;
      left: 16px;
      right: 16px;
      bottom: 20px;
      height: 34px;
      border-radius: 50% 50% 0 0;
      background: rgba(18,54,41,.42);
      transform: skewX(-14deg);
    }
    .photo-card::after {
      content: "";
      position: absolute;
      right: 18px;
      top: 17px;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: rgba(255,255,255,.72);
    }
    .info-stack {
      position: absolute;
      right: 28px;
      top: 62px;
      width: 142px;
      display: grid;
      gap: 9px;
    }
    .info-pill {
      min-height: 34px;
      border-radius: 9px;
      border: 1px solid rgba(201,210,195,.9);
      background: rgba(255,255,255,.82);
      box-shadow: 0 10px 24px rgba(20,49,35,.07);
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 10px;
    }
    .info-mark {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green-700);
    }
    .info-pill span:last-child {
      flex: 1;
      height: 7px;
      border-radius: 999px;
      background: #dfe8db;
    }
    .seal {
      position: absolute;
      left: 190px;
      bottom: 28px;
      width: 74px;
      height: 74px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      color: var(--green-900);
      background: rgba(242,235,221,.92);
      border: 1px solid rgba(184,148,93,.38);
      box-shadow: 0 12px 28px rgba(184,148,93,.15);
    }
    .seal svg { width: 30px; height: 30px; }
    .visual-caption {
      position: absolute;
      left: 232px;
      top: 36px;
      min-height: 34px;
      padding: 0 10px;
      border-radius: 999px;
      border: 1px solid rgba(47,116,80,.14);
      background: rgba(255,255,255,.72);
      color: var(--green-900);
      display: inline-flex;
      align-items: center;
      font-size: 12px;
      font-weight: 850;
    }
    @media (max-width: 920px) {
      .app-shell { grid-template-columns: 1fr; }
      .rail {
        min-height: auto;
        padding: 12px 14px;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
      }
      .rail-note { display: none; }
      .nav { display: flex; }
      .nav a { padding: 0 9px; }
      .nav a span { display: none; }
      .page { padding: 24px 14px 34px; }
      .page-header { flex-direction: column; }
      .tool-card-inner { grid-template-columns: 1fr; }
      h1 { font-size: 29px; }
      .tool-copy { flex-direction: column; }
      .visual-panel { min-height: 300px; }
    }
    @media (max-width: 560px) {
      .brand { font-size: 0; gap: 0; }
      .brand-mark { width: 38px; height: 38px; }
      .page-badge { display: none; }
      .tool-card-inner { padding: 18px; }
      .visual-panel { min-height: 270px; }
      .report-sheet { left: 18px; top: 24px; width: 162px; height: 216px; }
      .info-stack { right: 18px; top: 52px; width: 120px; }
      .photo-card { right: 18px; bottom: 28px; width: 112px; }
      .seal { left: 142px; bottom: 24px; width: 62px; height: 62px; }
      .visual-caption { left: 176px; top: 24px; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M5 19c8 0 13-6 13-14-8 0-13 6-13 14Z" stroke="currentColor" stroke-width="2"/><path d="M5 19c3-5 7-8 13-10" stroke="currentColor" stroke-width="2"/></svg>
        </div>
        Central Agro
      </div>
      <nav class="nav" aria-label="Navegação principal">
        <a class="active" href="/">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8Z" stroke="currentColor" stroke-width="2"/></svg>
          <span>Início</span>
        </a>
        <a href="/relatorio-credito">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2"/></svg>
          <span>Relatório de crédito</span>
        </a>
      </nav>
      <div class="rail-note" aria-hidden="true"></div>
    </aside>

    <main class="page">
      <div class="page-inner">
        <header class="page-header">
          <div>
            <div class="eyebrow">Painel de ferramentas</div>
            <h1>Central Agro</h1>
            <p class="lead">Ferramentas para transformar dados de vistoria em documentos organizados, com clareza para a rotina técnica.</p>
          </div>
          <div class="page-badge">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M12 21s7-4.4 7-11a7 7 0 0 0-14 0c0 6.6 7 11 7 11Z" stroke="currentColor" stroke-width="2"/><path d="M12 10.5h.01" stroke="currentColor" stroke-width="3"/></svg>
            Agro
          </div>
        </header>

        <div class="section-label">Ferramentas disponíveis</div>
        <section class="tool-card" aria-label="Relatório de crédito rural">
          <div class="tool-card-inner">
            <article class="tool-main">
              <div class="tool-copy">
                <div class="tool-icon" aria-hidden="true">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2"/></svg>
                </div>
                <div>
                  <h2>Relatório de crédito rural</h2>
                  <p class="tool-text">Cole as anotações da visita, gere o texto técnico, revise os principais dados e baixe a planilha final com fotos.</p>
                  <div class="chips" aria-label="Características">
                    <span class="chip">Texto técnico</span>
                    <span class="chip">Revisão</span>
                    <span class="chip">Fotos</span>
                    <span class="chip">Excel</span>
                  </div>
                </div>
              </div>
              <a class="primary-action" href="/relatorio-credito">
                Abrir ferramenta
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2"/></svg>
              </a>
            </article>

            <aside class="visual-panel" aria-label="Prévia visual do relatório">
              <div class="visual-orbit" aria-hidden="true"></div>
              <div class="visual-caption">Relatório pronto</div>
              <div class="report-sheet">
                <div class="sheet-top">
                  <div class="sheet-title"></div>
                  <div class="sheet-dot">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2"/></svg>
                  </div>
                </div>
                <div class="sheet-line"></div>
                <div class="sheet-line mid"></div>
                <div class="sheet-line short"></div>
                <div class="sheet-block">
                  <div class="sheet-cell"></div>
                  <div class="sheet-cell"></div>
                  <div class="sheet-cell"></div>
                  <div class="sheet-cell"></div>
                </div>
              </div>
              <div class="info-stack" aria-hidden="true">
                <div class="info-pill"><span class="info-mark"></span><span></span></div>
                <div class="info-pill"><span class="info-mark"></span><span></span></div>
                <div class="info-pill"><span class="info-mark"></span><span></span></div>
              </div>
              <div class="photo-card" aria-hidden="true"></div>
              <div class="seal" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2.3"/></svg>
              </div>
            </aside>
          </div>
        </section>
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
  <title>Central Agro | Relatório de crédito</title>
  <style>
    :root {
      --bg: #f5f7f2;
      --surface: #ffffff;
      --surface-soft: #fbfcf8;
      --ink: #15231b;
      --muted: #667568;
      --line: #dce4d7;
      --line-strong: #c7d4c2;
      --green-950: #0f2a20;
      --green-900: #17382c;
      --green-800: #22523d;
      --green-700: #2f7650;
      --green-100: #e9f3e8;
      --green-50: #f2f7ef;
      --earth: #9b7043;
      --earth-soft: #f4eee6;
      --warn: #98630f;
      --warn-bg: #fff8e8;
      --shadow: 0 18px 42px rgba(21, 52, 37, .08);
      --radius: 10px;
    }
    * { box-sizing: border-box; }
    html { color-scheme: light; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(180deg, rgba(233, 243, 232, .66), rgba(245, 247, 242, 0) 300px),
        var(--bg);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }
    a, button, input, textarea, summary { font: inherit; }
    svg { flex: 0 0 auto; }
    .app-shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 264px minmax(0, 1fr);
    }
    .rail {
      border-right: 1px solid var(--line);
      background: rgba(255,255,255,.82);
      padding: 22px 16px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .brand {
      min-height: 44px;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 8px;
      color: var(--green-950);
      font-size: 18px;
      font-weight: 850;
    }
    .brand-mark {
      width: 38px;
      height: 38px;
      border-radius: var(--radius);
      display: grid;
      place-items: center;
      color: #fff;
      background: var(--green-900);
      box-shadow: 0 10px 24px rgba(15,42,32,.16);
    }
    .nav {
      display: grid;
      gap: 6px;
    }
    .nav a {
      min-height: 42px;
      padding: 0 10px;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      gap: 10px;
      color: #46574b;
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }
    .nav a.active {
      color: var(--green-950);
      background: var(--green-100);
    }
    .nav a:not(.active):hover {
      background: #f4f7f0;
      color: var(--green-900);
    }
    .rail-note {
      margin-top: auto;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface-soft);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .page {
      min-width: 0;
      padding: 30px;
    }
    .page-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 22px;
    }
    .eyebrow {
      margin-bottom: 8px;
      color: var(--green-700);
      font-size: 12px;
      font-weight: 850;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      color: var(--green-950);
      font-size: 30px;
      line-height: 1.15;
      letter-spacing: 0;
    }
    .lead {
      max-width: 660px;
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }
    .head-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .button, button {
      min-height: 42px;
      border-radius: var(--radius);
      border: 1px solid transparent;
      padding: 0 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      font-weight: 850;
      text-decoration: none;
      cursor: pointer;
      white-space: nowrap;
    }
    .primary {
      border-color: var(--green-700);
      background: var(--green-800);
      color: #fff;
      box-shadow: 0 12px 24px rgba(34,82,61,.14);
    }
    .primary:hover { background: var(--green-950); }
    .secondary {
      border-color: var(--line);
      background: var(--surface);
      color: var(--green-900);
    }
    .secondary:hover { background: var(--green-50); }
    button[disabled] {
      opacity: .62;
      cursor: wait;
    }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, .92fr) minmax(0, 1.08fr);
      gap: 16px;
      align-items: start;
    }
    .workspace.start {
      grid-template-columns: minmax(0, 820px);
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel-head {
      min-height: 58px;
      padding: 15px 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: var(--surface-soft);
    }
    .panel-title {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--green-950);
      font-weight: 900;
    }
    .panel-kicker {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }
    .panel-body {
      padding: 18px;
      display: grid;
      gap: 14px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      color: #2e4236;
      font-size: 13px;
      font-weight: 850;
    }
    textarea, input[type="text"] {
      width: 100%;
      border: 1px solid #c9d5c5;
      border-radius: var(--radius);
      color: var(--ink);
      background: #fffefc;
      outline-color: var(--green-700);
      transition: border-color .15s ease, box-shadow .15s ease, background .15s ease;
    }
    textarea:focus, input[type="text"]:focus {
      border-color: var(--green-700);
      box-shadow: 0 0 0 3px rgba(47,118,80,.12);
    }
    textarea {
      min-height: 450px;
      resize: vertical;
      padding: 14px;
      font: 14px/1.55 Consolas, "Courier New", monospace;
    }
    input[type="text"] {
      min-height: 40px;
      padding: 10px 11px;
      font-size: 14px;
      line-height: 1.45;
    }
    #dados { min-height: 520px; }
    .output-panel, .review-panel { display: none; }
    .output-panel.show, .review-panel.show { display: block; }
    .workspace.start .output-panel,
    .workspace.start .review-panel { display: none; }
    .review-panel {
      grid-column: 1 / -1;
    }
    .review-panel .panel-body {
      grid-template-columns: minmax(230px, .75fr) minmax(0, 1fr) minmax(240px, .75fr);
      align-items: start;
    }
    .review-panel #okBox,
    .review-panel #missingBox {
      grid-column: 1 / -1;
    }
    .review-panel .summary { grid-column: 1; }
    .review-panel details { grid-column: 2; }
    .review-panel .upload-card,
    .review-panel .download-row {
      grid-column: 3;
    }
    .action-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .muted {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .notice {
      display: none;
      padding: 12px 14px;
      border: 1px solid #efd8a5;
      border-radius: var(--radius);
      background: var(--warn-bg);
      color: #664705;
      font-size: 13px;
      line-height: 1.45;
    }
    .notice.success {
      border-color: #bfd8c1;
      background: var(--green-100);
      color: var(--green-900);
    }
    .notice.show { display: block; }
    .summary {
      display: grid;
      gap: 10px;
    }
    .summary-row {
      border: 1px solid #e0e7dc;
      border-radius: var(--radius);
      padding: 11px 12px;
      background: var(--surface-soft);
    }
    .summary-row small {
      display: block;
      margin-bottom: 5px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 850;
      text-transform: uppercase;
    }
    .summary-row strong {
      display: block;
      color: var(--green-950);
      font-size: 14px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    .summary-row.wide strong {
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    details {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      overflow: hidden;
    }
    summary {
      min-height: 46px;
      padding: 0 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      color: var(--green-900);
      font-weight: 850;
      cursor: pointer;
    }
    .fields {
      border-top: 1px solid var(--line);
      padding: 14px;
      display: grid;
      gap: 12px;
    }
    .field textarea {
      min-height: 92px;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }
    .missing input,
    .missing textarea {
      border-color: #d59b32;
      background: #fffaf0;
    }
    .required {
      margin-left: 6px;
      color: var(--warn);
      font-size: 11px;
      font-weight: 850;
    }
    .upload-card {
      border: 1px dashed var(--line-strong);
      border-radius: var(--radius);
      background: var(--surface-soft);
      padding: 14px;
      display: grid;
      gap: 11px;
    }
    .upload-line {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }
    input[type="file"] {
      max-width: 100%;
      color: var(--muted);
      font-size: 13px;
    }
    .file-count {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }
    .download-row {
      display: grid;
      gap: 10px;
    }
    .download-row .primary {
      width: 100%;
      min-height: 48px;
    }
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
    @media (min-width: 1500px) {
      .workspace {
        grid-template-columns: minmax(360px, .9fr) minmax(440px, 1.1fr) 340px;
      }
      .review-panel { grid-column: auto; }
      .review-panel .panel-body { grid-template-columns: 1fr; }
      .review-panel #okBox,
      .review-panel #missingBox,
      .review-panel .summary,
      .review-panel details,
      .review-panel .upload-card,
      .review-panel .download-row {
        grid-column: auto;
      }
    }
    @media (max-width: 1180px) {
      .workspace,
      .workspace.start { grid-template-columns: 1fr; }
      .review-panel { order: 3; }
      .review-panel .panel-body { grid-template-columns: 1fr; }
      .review-panel #okBox,
      .review-panel #missingBox,
      .review-panel .summary,
      .review-panel details,
      .review-panel .upload-card,
      .review-panel .download-row {
        grid-column: auto;
      }
      #dados { min-height: 420px; }
    }
    @media (max-width: 920px) {
      .app-shell { grid-template-columns: 1fr; }
      .rail {
        min-height: auto;
        padding: 12px 14px;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
      }
      .nav, .rail-note { display: none; }
      .page { padding: 22px 14px 34px; }
      .page-header { flex-direction: column; }
      .head-actions { justify-content: flex-start; }
      h1 { font-size: 25px; }
      textarea, #dados { min-height: 360px; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M5 19c8 0 13-6 13-14-8 0-13 6-13 14Z" stroke="currentColor" stroke-width="2"/><path d="M5 19c3-5 7-8 13-10" stroke="currentColor" stroke-width="2"/></svg>
        </div>
        Central Agro
      </div>
      <nav class="nav" aria-label="Navegação principal">
        <a href="/">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8Z" stroke="currentColor" stroke-width="2"/></svg>
          Início
        </a>
        <a class="active" href="/relatorio-credito">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2"/></svg>
          Relatório de crédito
        </a>
      </nav>
      <div class="rail-note">Dados brutos entram de um lado. Relatório e planilha saem prontos do outro.</div>
    </aside>

    <main class="page">
      <header class="page-header">
        <div>
          <div class="eyebrow">Ferramenta</div>
          <h1>Relatório de crédito rural</h1>
          <p class="lead">Cole as anotações da visita, gere o texto técnico, revise somente o essencial e baixe a planilha final.</p>
        </div>
        <div class="head-actions">
          <a class="button secondary" href="/">Início</a>
          <button class="secondary" type="button" id="clearBtn">Limpar</button>
        </div>
      </header>

      <form id="reportForm" method="post" action="/generate" enctype="multipart/form-data" class="workspace start">
        <section class="panel">
          <div class="panel-head">
            <div class="panel-title">
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none"><path d="M4 5h16M4 12h16M4 19h10" stroke="currentColor" stroke-width="2"/></svg>
              Dados da visita
            </div>
            <span class="panel-kicker">Entrada</span>
          </div>
          <div class="panel-body">
            <div>
              <label for="rawData">Anotações do agrônomo</label>
              <textarea id="rawData" placeholder="Cole aqui produtor, propriedades, áreas, rebanho, lavouras, benfeitorias, maquinários e observações relevantes."></textarea>
            </div>
            <div id="writerNotice" class="notice"></div>
            <div class="action-row">
              <p class="muted">O texto técnico será gerado a partir dessas informações.</p>
              <button class="primary" type="button" id="writeBtn" data-label="Gerar texto técnico">
                <span class="spinner" aria-hidden="true"></span>
                <span class="btn-label">Gerar texto técnico</span>
              </button>
            </div>
          </div>
        </section>

        <section class="panel output-panel" id="technicalSection">
          <div class="panel-head">
            <div class="panel-title">
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2"/></svg>
              Texto técnico
            </div>
            <span class="panel-kicker">Editável</span>
          </div>
          <div class="panel-body">
            <div>
              <label for="dados">Relatório gerado</label>
              <textarea id="dados" name="dados" placeholder="O relatório técnico gerado aparecerá aqui."></textarea>
            </div>
            <div class="action-row">
              <p class="muted">Se editar o texto, atualize o resumo antes de gerar a planilha.</p>
              <button class="secondary" type="button" id="extractBtn" data-label="Atualizar resumo">
                <span class="spinner" aria-hidden="true"></span>
                <span class="btn-label">Atualizar resumo</span>
              </button>
            </div>
          </div>
        </section>

        <aside class="review-panel" id="review">
          <section class="panel">
            <div class="panel-head">
              <div class="panel-title">
                <svg width="19" height="19" viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2"/></svg>
                Revisão final
              </div>
            </div>
            <div class="panel-body">
              <div id="okBox" class="notice success show">Resumo reconhecido. Revise antes de baixar.</div>
              <div id="missingBox" class="notice"></div>
              <div class="summary" id="summaryItems"></div>

              <details>
                <summary>Ajustar campos reconhecidos</summary>
                <div id="fields" class="fields"></div>
              </details>

              <div class="upload-card">
                <label for="photos">Fotos da visita</label>
                <div class="upload-line">
                  <input id="photos" name="photos" type="file" accept="image/*" multiple>
                  <span class="file-count" id="fileCount">Nenhuma foto selecionada</span>
                </div>
              </div>

              <input type="hidden" id="reviewData" name="review_data">
              <div class="download-row">
                <button class="primary" type="submit" id="submitBtn" data-label="Gerar e baixar Excel">
                  <span class="spinner" aria-hidden="true"></span>
                  <span class="btn-label">Gerar e baixar Excel</span>
                </button>
                <p class="muted">A planilha será baixada no modelo atual, incluindo as fotos selecionadas.</p>
              </div>
            </div>
          </section>
        </aside>
      </form>
    </main>
  </div>

<script>
  const rawData = document.getElementById('rawData');
  const technicalText = document.getElementById('dados');
  const writeBtn = document.getElementById('writeBtn');
  const writerNotice = document.getElementById('writerNotice');
  const technicalSection = document.getElementById('technicalSection');
  const extractBtn = document.getElementById('extractBtn');
  const review = document.getElementById('review');
  const fieldsEl = document.getElementById('fields');
  const summaryItems = document.getElementById('summaryItems');
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
    summaryItems.innerHTML = '';
    review.classList.remove('show');
    technicalSection.classList.remove('show');
    form.classList.add('start');
    writerNotice.className = 'notice';
    writerNotice.textContent = '';
    missingBox.className = 'notice';
    missingBox.textContent = '';
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
      review.classList.add('show');
      form.classList.remove('start');
      renderFields(payload.review);
      renderWriterNotice();
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

  function renderWriterNotice() {
    writerNotice.className = 'notice success show';
    writerNotice.textContent = 'Texto técnico gerado. Revise o resultado antes de baixar a planilha.';
  }

  technicalText.addEventListener('input', () => {
    reviewData.value = '';
    lastExtraction = null;
    fieldsEl.innerHTML = '';
    summaryItems.innerHTML = '';
    missingBox.textContent = 'Texto alterado. Atualize o resumo antes de gerar a planilha.';
    missingBox.className = 'notice show';
    okBox.textContent = 'Resumo pendente de atualização.';
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
      if (!response.ok) throw new Error(payload.error || 'Não consegui atualizar o resumo.');
      renderFields(payload);
      review.classList.add('show');
      return true;
    } catch (error) {
      missingBox.textContent = error.message;
      missingBox.className = 'notice show';
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
    renderSummary(payload);

    if (payload.missing.length) {
      okBox.textContent = `${payload.summary.found} campos encontrados. Complete o que estiver faltando.`;
      missingBox.textContent = `Campos faltando: ${payload.missing.join(', ')}.`;
      missingBox.className = 'notice show';
    } else {
      okBox.textContent = 'Campos essenciais reconhecidos. Revise o resumo antes de baixar.';
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
        required.textContent = field.missing ? 'faltando' : 'obrigatório';
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
    return item && item.value ? item.value : 'Não informado';
  }

  function renderSummary(payload) {
    const items = [
      ['Cliente', fieldValue(payload, 'cliente')],
      ['Propriedades', fieldValue(payload, 'imovel_nome')],
      ['Área total', fieldValue(payload, 'area_total_ha')],
      ['Atividade', fieldValue(payload, 'atividade_principal')],
      ['Culturas', fieldValue(payload, 'principais_culturas')]
    ];
    summaryItems.innerHTML = items.map(([label, value], index) => `
      <div class="summary-row ${index > 2 ? 'wide' : ''}">
        <small>${label}</small>
        <strong>${escapeHtml(value)}</strong>
      </div>
    `).join('');
  }

  function renderSummaryFromInputs() {
    const getValue = (key) => {
      const input = fieldsEl.querySelector(`[data-key="${key}"]`);
      return input && input.value ? input.value : 'Não informado';
    };
    renderSummary({
      fields: [
        { key: 'cliente', value: getValue('cliente') },
        { key: 'imovel_nome', value: getValue('imovel_nome') },
        { key: 'area_total_ha', value: getValue('area_total_ha') },
        { key: 'atividade_principal', value: getValue('atividade_principal') },
        { key: 'principais_culturas', value: getValue('principais_culturas') }
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
      const ok = await refreshFieldsFromTechnicalText();
      if (ok) form.requestSubmit();
      return;
    }
    syncReviewData();
    setBusy(submitBtn, true, 'Gerando');
    setTimeout(() => { setBusy(submitBtn, false, ''); }, 5000);
  });
</script>
</body>
</html>"""


def render_credit_report_page() -> str:
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Central Agro | Relat&oacute;rio de cr&eacute;dito</title>
  <style>
    :root {
      --bg: #eef3e9;
      --surface: #ffffff;
      --surface-soft: #f8faf4;
      --ink: #15231b;
      --muted: #647265;
      --line: #d8e2d2;
      --line-strong: #bbcbb5;
      --green-950: #0b241a;
      --green-900: #14382a;
      --green-800: #20523d;
      --green-700: #2d7650;
      --green-100: #e6f2e4;
      --green-50: #f4f8ef;
      --gold: #b78a43;
      --gold-soft: #f6ecd9;
      --warn: #9a5c06;
      --warn-bg: #fff8e8;
      --shadow: 0 22px 58px rgba(21, 52, 37, .10);
      --soft-shadow: 0 12px 28px rgba(21, 52, 37, .08);
      --radius: 8px;
    }
    * { box-sizing: border-box; }
    html { color-scheme: light; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(115deg, rgba(20,56,42,.08), transparent 38%),
        linear-gradient(180deg, rgba(255,255,255,.74), rgba(255,255,255,0) 320px),
        var(--bg);
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: .26;
      background-image:
        linear-gradient(90deg, rgba(20,56,42,.10) 1px, transparent 1px),
        linear-gradient(180deg, rgba(20,56,42,.08) 1px, transparent 1px);
      background-size: 42px 42px;
      mask-image: linear-gradient(180deg, #000, transparent 72%);
    }
    a, button, input, textarea, summary { font: inherit; }
    svg { flex: 0 0 auto; }
    .app-shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 230px minmax(0, 1fr);
      position: relative;
    }
    .rail {
      border-right: 1px solid var(--line);
      background: rgba(255,255,255,.78);
      backdrop-filter: blur(16px);
      padding: 18px 14px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .brand {
      min-height: 44px;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 8px;
      color: var(--green-950);
      font-size: 18px;
      font-weight: 900;
    }
    .brand-mark {
      width: 38px;
      height: 38px;
      border-radius: var(--radius);
      display: grid;
      place-items: center;
      color: #fff;
      background: linear-gradient(145deg, var(--green-900), var(--green-950));
      box-shadow: 0 10px 24px rgba(15,42,32,.16);
    }
    .nav {
      display: grid;
      gap: 6px;
    }
    .nav a {
      min-height: 42px;
      padding: 0 10px;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      gap: 10px;
      color: #46574b;
      text-decoration: none;
      font-size: 14px;
      font-weight: 760;
    }
    .nav a.active {
      color: var(--green-950);
      background: var(--green-100);
    }
    .nav a:not(.active):hover {
      background: #f4f7f0;
      color: var(--green-900);
    }
    .rail-note {
      margin-top: auto;
      padding: 13px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface-soft);
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .page {
      min-width: 0;
      padding: 28px;
    }
    .page-inner {
      width: min(1280px, 100%);
      margin: 0 auto;
    }
    .page-header {
      position: relative;
      overflow: hidden;
      min-height: 190px;
      border: 1px solid rgba(12,36,26,.18);
      border-radius: var(--radius);
      padding: 24px;
      color: #fff;
      background:
        linear-gradient(135deg, rgba(255,255,255,.10), rgba(255,255,255,0) 44%),
        linear-gradient(120deg, var(--green-950), var(--green-800));
      box-shadow: var(--shadow);
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 22px;
      margin-bottom: 18px;
    }
    .page-header::after {
      content: "";
      position: absolute;
      right: 24px;
      bottom: 20px;
      width: 260px;
      height: 92px;
      opacity: .22;
      background:
        linear-gradient(90deg, transparent 0 18px, rgba(255,255,255,.68) 18px 20px, transparent 20px 42px),
        linear-gradient(180deg, transparent 0 28px, rgba(255,255,255,.44) 28px 30px, transparent 30px 56px);
      background-size: 42px 56px;
    }
    .header-copy, .head-actions { position: relative; z-index: 1; }
    .eyebrow {
      margin-bottom: 8px;
      color: #d8e9cb;
      font-size: 12px;
      font-weight: 900;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      color: #fff;
      font-size: 34px;
      line-height: 1.08;
      letter-spacing: 0;
    }
    .lead {
      max-width: 600px;
      margin: 10px 0 0;
      color: rgba(255,255,255,.78);
      font-size: 14px;
      line-height: 1.5;
    }
    .hero-strip {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 20px;
    }
    .hero-chip {
      min-height: 34px;
      border: 1px solid rgba(255,255,255,.18);
      border-radius: var(--radius);
      padding: 0 11px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255,255,255,.10);
      color: rgba(255,255,255,.88);
      font-size: 12px;
      font-weight: 850;
    }
    .head-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .button, button {
      min-height: 42px;
      border-radius: var(--radius);
      border: 1px solid transparent;
      padding: 0 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      font-weight: 850;
      text-decoration: none;
      cursor: pointer;
      white-space: nowrap;
      transition: transform .16s ease, background .16s ease, border-color .16s ease, box-shadow .16s ease;
    }
    .button:hover, button:hover { transform: translateY(-1px); }
    .primary {
      border-color: #1f6f4c;
      background: linear-gradient(135deg, #2e7b50, #174630);
      color: #fff;
      box-shadow: 0 14px 28px rgba(20,68,43,.20);
    }
    .primary:hover { background: var(--green-950); }
    .secondary {
      border-color: rgba(255,255,255,.30);
      background: rgba(255,255,255,.12);
      color: #fff;
    }
    .secondary:hover { background: rgba(255,255,255,.18); }
    .ghost {
      border-color: var(--line);
      background: #fff;
      color: var(--green-900);
    }
    .ghost:hover { background: var(--green-50); }
    button[disabled] {
      opacity: .62;
      cursor: wait;
      transform: none;
    }
    .workspace {
      display: grid;
      grid-template-columns: 1fr;
      gap: 18px;
      align-items: start;
    }
    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .main-panel { min-height: 660px; }
    .main-panel .panel-body {
      grid-template-columns: minmax(0, 1fr) 330px;
      align-items: start;
      gap: 18px;
    }
    .main-panel .panel-body > div:first-child {
      grid-column: 1;
      grid-row: 1 / span 4;
    }
    .main-panel .upload-card,
    .main-panel .notice,
    .main-panel .primary-action {
      grid-column: 2;
    }
    .panel-head {
      min-height: 56px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.85), rgba(248,250,244,.92)),
        var(--surface-soft);
    }
    .panel-title {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--green-950);
      font-weight: 900;
    }
    .panel-kicker {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }
    .panel-body {
      padding: 16px;
      display: grid;
      gap: 14px;
    }
    .notes-card {
      min-height: 100%;
      border: 1px solid #dfe8d9;
      border-radius: var(--radius);
      background:
        linear-gradient(180deg, rgba(255,255,255,.98), rgba(250,252,246,.94)),
        var(--surface);
      padding: 14px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,.80);
    }
    .notes-head {
      min-height: 38px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 10px;
    }
    .notes-head label { margin-bottom: 0; }
    .notes-badge {
      border: 1px solid #dfe8d9;
      border-radius: 999px;
      padding: 6px 10px;
      background: #f5f9ef;
      color: var(--green-900);
      font-size: 12px;
      font-weight: 850;
      white-space: nowrap;
    }
    label {
      display: block;
      margin-bottom: 7px;
      color: #2e4236;
      font-size: 13px;
      font-weight: 850;
    }
    textarea, input[type="text"] {
      width: 100%;
      border: 1px solid #c9d5c5;
      border-radius: var(--radius);
      color: var(--ink);
      background: #fffefc;
      outline-color: var(--green-700);
      transition: border-color .15s ease, box-shadow .15s ease, background .15s ease;
    }
    textarea:focus, input[type="text"]:focus {
      border-color: var(--green-700);
      box-shadow: 0 0 0 3px rgba(47,118,80,.12);
    }
    textarea {
      min-height: 540px;
      resize: vertical;
      padding: 18px;
      font: 15px/1.62 "Segoe UI", Arial, sans-serif;
    }
    #rawData {
      border-color: #bfcfc0;
      background:
        linear-gradient(180deg, rgba(255,255,255,.98), rgba(255,253,248,.98));
      box-shadow: inset 0 1px 0 rgba(255,255,255,.90);
    }
    #rawData::placeholder { color: #879386; }
    input[type="text"] {
      min-height: 40px;
      padding: 10px 11px;
      font-size: 14px;
      line-height: 1.45;
    }
    #dados { min-height: 300px; font-size: 13px; }
    .action-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .primary-action {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      align-items: center;
    }
    .primary-action .primary {
      min-height: 58px;
      padding-inline: 20px;
      font-size: 15px;
      width: 100%;
    }
    .muted {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }
    .notice {
      display: none;
      padding: 11px 12px;
      border: 1px solid #efd8a5;
      border-radius: var(--radius);
      background: var(--warn-bg);
      color: #664705;
      font-size: 13px;
      line-height: 1.45;
    }
    .notice.success {
      border-color: #bfd8c1;
      background: var(--green-100);
      color: var(--green-900);
    }
    .notice.show { display: block; }
    .summary {
      display: none;
      grid-template-columns: 1fr 1fr;
      gap: 9px;
    }
    .summary-row {
      border: 1px solid #e0e7dc;
      border-radius: var(--radius);
      padding: 10px 11px;
      background: var(--surface-soft);
    }
    .summary-row small {
      display: block;
      margin-bottom: 5px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 850;
      text-transform: uppercase;
    }
    .summary-row strong {
      display: block;
      color: var(--green-950);
      font-size: 14px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    .summary-row.wide {
      grid-column: 1 / -1;
    }
    .summary-row.wide strong {
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    details {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      overflow: hidden;
    }
    summary {
      min-height: 46px;
      padding: 0 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      color: var(--green-900);
      font-weight: 850;
      cursor: pointer;
    }
    .fields {
      border-top: 1px solid var(--line);
      padding: 12px;
      display: grid;
      gap: 12px;
      max-height: 380px;
      overflow: auto;
    }
    .field textarea {
      min-height: 92px;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }
    .missing input,
    .missing textarea {
      border-color: #d59b32;
      background: #fffaf0;
    }
    .required {
      margin-left: 6px;
      color: var(--warn);
      font-size: 11px;
      font-weight: 850;
    }
    .upload-card {
      border: 1px solid var(--line-strong);
      border-radius: var(--radius);
      background:
        linear-gradient(180deg, rgba(255,255,255,.76), rgba(246,250,242,.94)),
        var(--surface-soft);
      padding: 14px;
      display: grid;
      gap: 12px;
      box-shadow: 0 12px 28px rgba(23,70,48,.08);
    }
    .upload-button {
      min-height: 122px;
      border: 1.5px dashed rgba(45, 107, 63, .52);
      border-radius: var(--radius);
      background:
        linear-gradient(135deg, rgba(45,107,63,.10), rgba(199,163,82,.13)),
        #fffef9;
      color: var(--green-900);
      display: grid;
      place-items: center;
      gap: 8px;
      padding: 18px;
      text-align: center;
      cursor: pointer;
      transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
    }
    .upload-button:hover {
      border-color: var(--green-700);
      transform: translateY(-1px);
      box-shadow: 0 14px 30px rgba(18, 48, 31, .10);
    }
    .upload-button.drag-over {
      border-color: var(--gold);
      background:
        linear-gradient(135deg, rgba(45,107,63,.16), rgba(199,163,82,.22)),
        #fffef9;
    }
    .upload-button input { display: none; }
    .upload-button strong {
      display: block;
      font-size: 15px;
      line-height: 1.2;
    }
    .upload-button small {
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }
    .upload-icon {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: var(--green-700);
      color: white;
      box-shadow: 0 10px 22px rgba(45,107,63,.22);
    }
    .file-count {
      min-height: 22px;
      align-items: center;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }
    .file-list {
      display: grid;
      gap: 6px;
      max-height: 112px;
      overflow: auto;
    }
    .file-pill {
      min-height: 30px;
      border: 1px solid #dce7d8;
      border-radius: 999px;
      background: white;
      color: var(--green-950);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 6px 10px;
      font-size: 12px;
      line-height: 1.25;
    }
    .file-pill span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .file-pill small {
      color: var(--muted);
      flex: 0 0 auto;
    }
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
    .side-panel {
      position: sticky;
      top: 18px;
    }
    .side-panel .panel-body { gap: 12px; }
    .status-tile {
      min-height: 70px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 12px;
      background: var(--green-50);
      display: grid;
      gap: 5px;
    }
    .status-tile small {
      color: var(--muted);
      font-size: 11px;
      font-weight: 850;
      text-transform: uppercase;
    }
    .status-tile strong {
      color: var(--green-950);
      font-size: 16px;
      line-height: 1.25;
    }
    .advanced-panel {
      display: none;
      margin-top: 18px;
      grid-column: 1 / -1;
    }
    .advanced-panel.show { display: block; }
    .hidden-workspace { display: none; }
    .preview-box {
      min-height: 300px;
      max-height: 430px;
      overflow: auto;
      border: 1px solid #dfe8d9;
      border-radius: var(--radius);
      background:
        linear-gradient(180deg, #fffef9, #fbf8ef);
      padding: 14px;
      color: var(--green-950);
      font-size: 13px;
      line-height: 1.55;
      white-space: pre-wrap;
    }
    .preview-box.empty {
      color: var(--muted);
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    .preview-hint {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    .overlay {
      position: fixed;
      inset: 0;
      z-index: 20;
      display: none;
      place-items: center;
      padding: 18px;
      background: rgba(11, 25, 19, .58);
      backdrop-filter: blur(7px);
    }
    .overlay.show { display: grid; }
    .overlay-card {
      width: min(430px, 100%);
      border: 1px solid rgba(255,255,255,.20);
      border-radius: var(--radius);
      padding: 22px;
      background: #fffef9;
      box-shadow: 0 30px 80px rgba(0,0,0,.22);
    }
    .loader {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      border: 4px solid #dfe8d9;
      border-top-color: var(--green-700);
      animation: spin .8s linear infinite;
      margin-bottom: 16px;
    }
    .overlay-card h2 {
      margin: 0;
      color: var(--green-950);
      font-size: 20px;
      line-height: 1.2;
    }
    .overlay-card p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }
    .progress-track {
      height: 8px;
      border-radius: 999px;
      margin-top: 18px;
      overflow: hidden;
      background: #e7eddf;
    }
    .progress-bar {
      width: 42%;
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--green-700), var(--gold));
      animation: progress 1.5s ease-in-out infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes progress {
      0% { transform: translateX(-80%); }
      55% { transform: translateX(85%); }
      100% { transform: translateX(180%); }
    }
    @media (max-width: 1180px) {
      .workspace { grid-template-columns: 1fr; }
      .side-panel { position: static; }
      .main-panel .panel-body { grid-template-columns: minmax(0, 1fr) 280px; }
      textarea { min-height: 360px; }
    }
    @media (max-width: 920px) {
      .app-shell { grid-template-columns: 1fr; }
      .rail {
        min-height: auto;
        padding: 12px 14px;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
      }
      .nav, .rail-note { display: none; }
      .page { padding: 14px; }
      .page-header {
        min-height: auto;
        padding: 18px;
        flex-direction: column;
      }
      h1 { font-size: 25px; }
      .main-panel .panel-body { grid-template-columns: 1fr; }
      .main-panel .panel-body > div:first-child,
      .main-panel .upload-card,
      .main-panel .notice,
      .main-panel .primary-action {
        grid-column: auto;
      }
      .primary-action { grid-template-columns: 1fr; }
      .summary { grid-template-columns: 1fr; }
      textarea { min-height: 320px; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="rail">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M5 19c8 0 13-6 13-14-8 0-13 6-13 14Z" stroke="currentColor" stroke-width="2"/><path d="M5 19c3-5 7-8 13-10" stroke="currentColor" stroke-width="2"/></svg>
        </div>
        Central Agro
      </div>
      <nav class="nav" aria-label="Navegacao principal">
        <a href="/">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 11 12 4l8 7v8a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8Z" stroke="currentColor" stroke-width="2"/></svg>
          Inicio
        </a>
        <a class="active" href="/relatorio-credito">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/><path d="M14 3v4h4M9 13h6M9 17h6M9 9h2" stroke="currentColor" stroke-width="2"/></svg>
          Relatorio
        </a>
      </nav>
      <div class="rail-note">Fluxo local para testar antes de enviar ao site.</div>
    </aside>

    <main class="page">
      <div class="page-inner">
        <header class="page-header">
          <div class="header-copy">
            <div class="eyebrow">Credito rural</div>
            <h1>Gerador de planilha final</h1>
            <p class="lead">Cole as anotacoes da vistoria, anexe as fotos e baixe o Excel no padrao do laudo.</p>
            <div class="hero-strip">
              <span class="hero-chip"><svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2"/></svg>Extracao automatica</span>
              <span class="hero-chip"><svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M4 7h16v13H4V7Z" stroke="currentColor" stroke-width="2"/><path d="m8 7 2-3h4l2 3" stroke="currentColor" stroke-width="2"/></svg>Fotos numeradas</span>
              <span class="hero-chip"><svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" stroke-width="2"/></svg>XLSX</span>
            </div>
          </div>
          <div class="head-actions">
            <a class="button secondary" href="/">Inicio</a>
            <button class="secondary" type="button" id="clearBtn">Limpar</button>
          </div>
        </header>

        <form id="reportForm" method="post" action="/generate" enctype="multipart/form-data" class="workspace">
          <section class="panel main-panel">
            <div class="panel-head">
              <div class="panel-title">
                <svg width="19" height="19" viewBox="0 0 24 24" fill="none"><path d="M4 5h16M4 12h16M4 19h10" stroke="currentColor" stroke-width="2"/></svg>
                Entrada do relatorio
              </div>
              <span class="panel-kicker">Rascunho</span>
            </div>
            <div class="panel-body">
              <div class="notes-card">
                <div class="notes-head">
                  <label for="rawData">Anotacoes da vistoria</label>
                  <span class="notes-badge">Texto da visita</span>
                </div>
                <textarea id="rawData" placeholder="Cole aqui os dados brutos da visita, do jeito que recebeu."></textarea>
              </div>

              <div class="upload-card">
                <label class="upload-button" for="photos">
                  <input id="photos" name="photos" type="file" accept="image/*" multiple>
                  <span class="upload-icon" aria-hidden="true">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M4 7h16v13H4V7Z" stroke="currentColor" stroke-width="2"/><path d="m8 7 2-3h4l2 3" stroke="currentColor" stroke-width="2"/><path d="m8 15 2-2 3 3 2-2 3 4" stroke="currentColor" stroke-width="2"/></svg>
                  </span>
                  <span>
                    <strong>Selecionar fotos da vistoria</strong>
                    <small>Escolha varias imagens de uma vez</small>
                  </span>
                </label>
                <span class="file-count" id="fileCount">Nenhuma foto selecionada</span>
                <div class="file-list" id="fileList"></div>
              </div>

              <div id="writerNotice" class="notice"></div>

              <div class="primary-action">
                <button class="primary" type="submit" id="submitBtn" data-label="Gerar e baixar planilha">
                  <span class="spinner" aria-hidden="true"></span>
                  <span class="btn-label">Gerar e baixar planilha</span>
                </button>
              </div>

              <input type="hidden" id="reviewData" name="review_data">
              <textarea id="dados" name="dados" hidden></textarea>
            </div>
          </section>

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
    statusText.textContent = 'Pronto para gerar';
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
    statusText.textContent = 'Extracao pendente';
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
    statusText.textContent = 'Dados prontos';
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
      statusText.textContent = 'Extracao pronta';
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
    statusText.textContent = 'Atencao';
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
      statusText.textContent = 'Planilha baixada';
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
</html>"""
