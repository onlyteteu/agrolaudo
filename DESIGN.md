---
name: AgroLaudo
description: Ferramenta que transforma anotações de vistoria em laudo bancário — Excel, texto técnico e fotos.
colors:
  forest-950: "#06150e"
  forest-900: "#0b271a"
  forest-800: "#123c28"
  forest-700: "#195636"
  forest-600: "#237a4b"
  forest-100: "#e4f1e1"
  forest-50: "#f1f7ec"
  lime: "#c2f24d"
  lime-strong: "#a7df2f"
  amber: "#eaa53d"
  gold: "#c79a52"
  warn: "#8f5b07"
  warn-bg: "#fff6e3"
  bg: "#f1f4ea"
  surface: "#ffffff"
  surface-soft: "#f8faf2"
  ink: "#101d15"
  muted: "#5d6b5c"
  line: "#e0e6d6"
  line-strong: "#cdd6c0"
typography:
  display:
    fontFamily: "Inter, 'Segoe UI', system-ui, Arial, sans-serif"
    fontSize: "clamp(30px, 4vw, 44px)"
    fontWeight: 900
    lineHeight: 1.04
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Inter, 'Segoe UI', system-ui, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 900
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Inter, 'Segoe UI', system-ui, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 850
  body:
    fontFamily: "Inter, 'Segoe UI', system-ui, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 500
    lineHeight: 1.55
  label:
    fontFamily: "Inter, 'Segoe UI', system-ui, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 900
    letterSpacing: "0.12em"
rounded:
  sm: "10px"
  control: "12px"
  md: "14px"
  lg: "22px"
  pill: "999px"
spacing:
  xs: "10px"
  sm: "14px"
  md: "18px"
  lg: "26px"
  page: "34px"
components:
  button-primary:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.forest-950}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "46px"
  button-dark:
    backgroundColor: "{colors.forest-950}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "46px"
  button-ghost:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.forest-900}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "46px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "18px"
  rail-tag:
    backgroundColor: "{colors.forest-950}"
    textColor: "{colors.lime}"
    rounded: "{rounded.pill}"
    padding: "5px 10px"
---

# Design System: AgroLaudo

## 1. Overview

**Creative North Star: "A Mesa do Agrônomo"**

O AgroLaudo é o escritório técnico de quem vive o campo: papel claro sobre a mesa, carimbo verde-floresta e um único toque de verde-lima onde há ação. A superfície é clara e tranquila (fundo `#f1f4ea` com leve textura de linhas diagonais), os painéis são folhas de papel branco com sombras suaves, e a autoridade vem do verde-floresta profundo — o hero e os elementos de marca são blocos escuros de `forest-950` a `forest-700`, como o carimbo oficial no laudo. A energia fica concentrada no verde-lima: é o "assinar aqui" da interface.

O sistema rejeita explicitamente as duas anti-referências do PRODUCT.md: o **sistema de banco antigo** (telas cinzas e formulários burocráticos — aqui o cinza puro não existe; todos os neutros carregam um tom de verde) e o **SaaS genérico de IA** (gradientes roxos, glassmorphism decorativo, selos "powered by AI"). A tecnologia trabalha em silêncio; a interface fala a língua do laudo.

**Key Characteristics:**
- Uma única família tipográfica (Inter) em pesos muito altos (750–900): sólida e confiante, nunca delicada.
- Neutros esverdeados em vez de cinza: até as bordas (`#e0e6d6`) têm clorofila.
- Verde-lima exclusivo para ação primária, estado ativo e marca.
- Sombras grandes, suaves e esverdeadas — atmosfera de papel sobre mesa, não hierarquia.
- Densidade de ferramenta: painéis compactos, chips informativos, fluxo de 3 passos sempre visível.

## 2. Colors

Paleta de dois verdes — o Verde-Floresta institucional e o Verde-Lima de ação — sobre neutros tingidos de verde.

### Primary
- **Verde-Floresta** (`forest-950` #06150e → `forest-600` #237a4b): a autoridade do sistema. Fundos do hero e da marca (gradientes de `forest-950` para `forest-700`), texto de títulos (`forest-950`), botão escuro, estados ativos da navegação (`forest-100`/`forest-50` como lastro claro).
- **Verde-Lima** (#c2f24d, hover #a7df2f): a ação. Botão primário (gradiente lima → lima-strong com texto `forest-950`), ícones de destaque no hero, ponto pulsante da tag "Beta", indicador ativo da navegação. Sempre acompanhado de texto escuro — nunca texto branco sobre lima.

### Secondary
- **Âmbar** (#eaa53d) e **Ouro** (#c79a52): calor pontual — texturas de fundo (linhas diagonais douradas a 4,5% de opacidade) e detalhes de destaque no hero. Papel decorativo mínimo.

### Neutral
- **Tinta** (#101d15): texto padrão — um preto esverdeado, não `#000`.
- **Verde-Apagado** (#5d6b5c): texto secundário, rótulos, descrições.
- **Papel** (#f1f4ea): fundo geral da página.
- **Superfície** (#ffffff) e **Superfície-Suave** (#f8faf2): painéis e cabeçalhos de painéis.
- **Linha** (#e0e6d6) e **Linha-Forte** (#cdd6c0): bordas e divisores.
- **Alerta** (#8f5b07 sobre #fff6e3): avisos e campos faltando.

### Named Rules
**A Regra do Verde-Lima.** O verde-lima marca exatamente três coisas: a ação primária, o estado ativo e a marca. Nunca aparece como decoração de fundo, borda de card ou cor de texto corrido. Sua raridade é a razão de ele funcionar.

**A Regra do Cinza Proibido.** Não existe cinza puro no sistema. Todo neutro (fundo, borda, texto secundário) carrega tom de verde. Se um hex novo tem R=G=B, está errado.

## 3. Typography

**Display Font:** Inter (com "Segoe UI", system-ui, Arial de fallback)
**Body Font:** Inter — a mesma família em toda a interface.

**Character:** Uma família só, esticada nos pesos: o peso faz o trabalho que outros sistemas pedem a uma segunda fonte. Nos títulos e botões, Inter em 850–900 com tracking negativo transmite a solidez de documento técnico; no corpo, 500 em tamanhos compactos mantém a densidade de ferramenta.

### Hierarchy
- **Display** (900, clamp(30px, 4vw, 44px), lh 1.04, ls -0.03em): título do hero, um por página.
- **Headline** (900, 18px, ls -0.02em): marca na barra lateral, títulos de painel.
- **Title** (850, 13–14px): botões, chips, rótulos fortes, cartões da barra lateral.
- **Body** (500, 14–15px, lh 1.45–1.55): descrições, leads, textos de apoio. Máx. ~65ch.
- **Label** (900, 11px, ls 0.12em, CAIXA ALTA): rótulos de navegação e eyebrow do hero — usar com extrema parcimônia (ver Don'ts).

### Named Rules
**A Regra da Família Única.** Nenhuma segunda fonte, nunca. Variação vem de peso (500 → 750 → 850 → 900) e tamanho, não de família. Fontes display/serifadas quebram o registro de ferramenta.

## 4. Elevation

O sistema usa **sombra ambiente**: sombras grandes, difusas e esverdeadas que dão a profundidade de papel sobre mesa — atmosfera, não hierarquia. A importância de um elemento não é comunicada por elevação e sim por cor (verde-floresta), peso tipográfico e posição. Estados interativos usam borda e anel de foco, não aumento de sombra estrutural.

### Shadow Vocabulary
- **Sombra-suave** (`box-shadow: 0 8px 22px rgba(11, 39, 26, .07)`): cartões pequenos da barra lateral.
- **Sombra-padrão** (`box-shadow: 0 22px 50px rgba(11, 39, 26, .12)`): painéis de conteúdo.
- **Sombra-hero** (`box-shadow: 0 34px 80px rgba(7, 26, 17, .20)`): o bloco escuro do hero.
- **Anel de foco** (`box-shadow: 0 0 0 3px rgba(35, 122, 75, .18)`): foco em campos e controles.

### Named Rules
**A Regra da Sombra Verde.** Toda sombra deriva de `rgba(11, 39, 26, …)` — o verde-floresta escurecido. Sombra preta pura (`rgba(0,0,0,…)`) denuncia elemento estranho ao sistema.

## 5. Components

Sólidos e confiantes: pesos altos, formas firmes, delimitação clara. O usuário sente que a ferramenta aguenta o peso de um laudo bancário.

### Buttons
- **Shape:** cantos firmes mas amigáveis (12px), altura mínima 46px, peso 850.
- **Primary:** gradiente verde-lima (135deg, #c2f24d → #a7df2f) com texto `forest-950` e brilho esverdeado (`0 14px 30px rgba(141,196,47,.34)`). Um por tela.
- **Dark:** gradiente verde-floresta (#195636 → #06150e) com texto branco — a ação forte secundária.
- **Ghost:** superfície branca com borda `line-strong` e texto `forest-900`; hover ganha fundo `forest-50`.
- **Hover / Focus:** elevação de -2px com transição de 160ms; desabilitado = opacidade .6 + spinner embutido.

### Chips
- **Hero-chip:** pílula translúcida sobre o hero escuro (fundo branco 8%, borda branca 16%, texto branco 90%, ícone lima), 34px de altura.
- **Panel-kicker / Rail-tag:** pílulas informativas — kicker claro (`forest-50` + texto `forest-700`), tag da marca escura (`forest-950` + texto lima com ponto pulsante).

### Cards / Containers
- **Panel:** o container padrão. Borda `line` 1px, raio 14px, fundo branco, sombra-padrão; cabeçalho de 56px com gradiente sutil para `surface-soft` e divisor.
- **Rail-card:** cartão menor da barra lateral, raio 14px, gradiente branco → `surface-soft`, sombra-suave.
- **Hero:** o único bloco escuro — raio 22px, gradiente de floresta com texturas de linha e círculo, texto branco.

### Inputs / Fields
- **Style:** campos claros com borda `line-strong`, raio 10–12px, fonte herdada.
- **Focus:** anel verde (`0 0 0 3px rgba(35,122,75,.18)`).
- **Error / Missing:** aviso âmbar (`warn` sobre `warn-bg`) com selo "faltando" nos campos obrigatórios vazios.

### Navigation
- **Barra lateral fixa de 252px** (vidro branco 72% + blur) com marca, links de 44px (peso 750, raio 12px). Ativo = fundo `forest-100`→lima 28% com indicador lateral em gradiente lima→floresta; hover = `forest-50` + deslize de 2px. Em ≤980px vira barra horizontal rolável; em ≤560px só ícones.

### Overlay de geração (componente-assinatura)
Tela de espera do download: card central com loader, barra de progresso e botão de cancelar. É o momento de maior ansiedade do fluxo — mantém o usuário informado do passo atual ("Gerando planilha…") e sempre oferece saída.

## 6. Do's and Don'ts

### Do:
- **Do** concentrar o verde-lima na ação primária da tela — um botão primário por página, texto sempre `forest-950` sobre lima.
- **Do** usar os neutros esverdeados do sistema (`#f1f4ea`, `#e0e6d6`, `#5d6b5c`) para qualquer superfície ou borda nova.
- **Do** manter o peso alto (850–900) em títulos e botões; a solidez é a personalidade.
- **Do** mostrar estado com honestidade: campos faltando em âmbar com selo "faltando", motor usado (Gemini × local) registrado, progresso visível durante a geração.
- **Do** manter todo o fluxo principal funcional no celular (barra vira horizontal em ≤980px; rótulos somem em ≤560px, ícones ficam).

### Don't:
- **Don't** parecer **sistema de banco antigo** (anti-referência do PRODUCT.md): nada de telas cinzas, tabelas densas sem respiro ou formulários burocráticos em série.
- **Don't** parecer **SaaS genérico de IA** (anti-referência do PRODUCT.md): proibido gradiente roxo, glassmorphism decorativo, selo "powered by AI" e brilhos de template.
- **Don't** usar cinza puro (R=G=B) em qualquer papel — viola a Regra do Cinza Proibido.
- **Don't** estender o texto-gradiente do hero (`background-clip: text` no `.accent`) a nenhum outro elemento; é uma dívida visual do hero atual, não um padrão — na primeira revisão do hero, substituir por lima sólido.
- **Don't** multiplicar o eyebrow em caixa alta: ele existe só no hero. Seções internas usam `section-label` (peso 900, sem caixa alta, com régua).
- **Don't** usar sombra preta pura ou sombras pequenas e duras — toda sombra segue o vocabulário verde da seção Elevation.
- **Don't** adicionar segunda família tipográfica, fontes display ou serifadas em qualquer papel.
