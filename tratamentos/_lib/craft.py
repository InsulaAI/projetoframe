"""Padrao craft da Insula AI: fonte unica dos tokens e do CSS dos tratamentos.

Regra herdada do index.html (ver CLAUDE.md na raiz): a pagina publicada nao tem
dependencia externa alem do Google Fonts. Todo o CSS sai daqui e e inlinado num
<style> no <head> do HTML gerado. Nao criar .css separado no output.

Os tokens abaixo sao os mesmos do Information Memorandum. Mexer neles aqui muda
todos os tratamentos de uma vez -- que e o ponto.
"""

import html
import re
import unicodedata

# ---------------------------------------------------------------- tokens ----

TOKENS = {
    "ink": "#080D18",
    "ground": "#0A1020",
    "surface": "#111931",
    "surface-2": "#16203C",
    "line": "#222E4E",
    "line-soft": "#1A2440",
    "text": "#E9E5DC",
    "text-2": "#B3BACE",
    "text-3": "#7F889F",
    "amber": "#D9A566",
    "amber-dim": "#8F7148",
    "amber-wash": "rgba(217,165,102,.10)",
}

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=Bodoni+Moda:opsz,wght@6..96,400..600&family=Archivo:wght@400;500;600"
    '&family=JetBrains+Mono:wght@400;500&display=swap">'
)

# CSS compartilhado entre a pagina de tratamento e o dashboard.
# Os blocos de font-variation-settings em h1/h2/.stat .v/.rail-mark sao
# deliberados: Bodoni Moda e uma Didone e, em texto claro sobre fundo escuro,
# o opsz de display some. Ver CLAUDE.md, "Titulos tem font-variation-settings
# travado". Nao mexer no tamanho desses titulos sem revisar o opsz.
BASE_CSS = """
:root{
  --ink:#080D18;
  --ground:#0A1020;
  --surface:#111931;
  --surface-2:#16203C;
  --line:#222E4E;
  --line-soft:#1A2440;
  --text:#E9E5DC;
  --text-2:#B3BACE;
  --text-3:#7F889F;
  --amber:#D9A566;
  --amber-dim:#8F7148;
  --amber-wash:rgba(217,165,102,.10);
  --serif:"Bodoni Moda","Didot","Times New Roman",serif;
  --sans:"Archivo","Helvetica Neue",Arial,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,monospace;
  --maxw:92ch;
  padding-top:env(safe-area-inset-top,0px);
  padding-bottom:env(safe-area-inset-bottom,0px);
}
*{box-sizing:border-box}
img{max-width:100%}
body{
  margin:0;background:var(--ground);color:var(--text);
  font-family:var(--sans);font-size:17px;line-height:1.68;
  -webkit-font-smoothing:antialiased;
}
html{scroll-behavior:smooth}

/* ---------- shell ---------- */
.shell{display:grid;grid-template-columns:minmax(0,1fr)}
@media(min-width:1040px){.shell{grid-template-columns:232px minmax(0,1fr)}}
nav.rail{
  display:none;position:sticky;top:env(safe-area-inset-top,0px);align-self:start;
  height:100vh;padding:40px 24px 40px 32px;border-right:1px solid var(--line-soft);
  overflow-y:auto;
}
@media(min-width:1040px){nav.rail{display:block}}
.rail-mark{
  font-family:var(--serif);font-weight:500;
  font-variation-settings:"opsz" 16,"wght" 520;
  font-size:19px;letter-spacing:.04em;-webkit-font-smoothing:auto;
  margin-bottom:6px;color:var(--text);display:block;text-decoration:none;
}
.rail-sub{
  font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--amber-dim);margin-bottom:30px;
}
.rail ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
.rail a{
  display:flex;gap:10px;align-items:baseline;position:relative;
  text-decoration:none;color:var(--text-3);
  font-size:12.5px;letter-spacing:.02em;padding:5px 0;transition:color .18s ease;
}
.rail a:hover,.rail a:focus-visible{color:var(--text)}
.rail a .n{font-family:var(--mono);font-size:10.5px;color:var(--amber-dim);letter-spacing:.06em}
.rail a.on{color:var(--text)}
.rail a.on .n{color:var(--amber)}
.rail a.on::before{
  content:"";position:absolute;left:-32px;top:50%;transform:translateY(-50%);
  width:2px;height:15px;background:var(--amber);
}
.rail-foot{
  margin-top:30px;padding-top:18px;border-top:1px solid var(--line-soft);
  font-family:var(--mono);font-size:9.5px;line-height:1.7;letter-spacing:.07em;
  text-transform:uppercase;color:var(--text-3);
}
main{min-width:0}

/* ---------- secoes ---------- */
section{
  max-width:none;padding-inline:20px;padding-block:84px;position:relative;isolation:isolate;
  border-bottom:1px solid var(--line-soft);scroll-margin-top:24px;
}
@media(min-width:720px){section{padding-inline:56px}}
@media(min-width:1040px){section{padding-inline:min(88px,7vw)}}
section:last-of-type{border-bottom:0}
.in{max-width:var(--maxw);margin-inline:auto;position:relative;z-index:1}

.eyebrow{
  display:flex;align-items:center;gap:12px;
  font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--amber);margin-bottom:22px;
}
.eyebrow::after{content:"";flex:1;height:1px;background:var(--line)}

h1{
  font-family:var(--serif);font-weight:500;
  font-variation-settings:"opsz" 32,"wght" 520;
  font-size:clamp(40px,8.4vw,74px);line-height:1.07;letter-spacing:0;
  margin:0 0 20px;text-wrap:balance;max-width:14ch;
  -webkit-font-smoothing:auto;-moz-osx-font-smoothing:auto;
}
h2{
  font-family:var(--serif);font-weight:500;
  font-variation-settings:"opsz" 20,"wght" 520;
  font-size:clamp(28px,4.4vw,41px);line-height:1.21;letter-spacing:.002em;
  margin:0 0 18px;text-wrap:balance;max-width:26ch;
  -webkit-font-smoothing:auto;-moz-osx-font-smoothing:auto;
}
h3{font-family:var(--sans);font-weight:600;font-size:15.5px;letter-spacing:.02em;margin:44px 0 12px;color:var(--text)}
p{margin:0 0 19px;color:var(--text-2);max-width:68ch}
p strong{color:var(--text);font-weight:600}
.lede{font-size:19.5px;line-height:1.58;color:var(--text);max-width:62ch}
a{color:var(--amber)}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:1px solid var(--amber);outline-offset:3px}

ul.plain{list-style:none;margin:0 0 19px;padding:0;display:flex;flex-direction:column;gap:16px}
ul.plain li{color:var(--text-2);padding-left:22px;position:relative;max-width:68ch}
ul.plain li::before{content:"";position:absolute;left:0;top:.78em;width:10px;height:1px;background:var(--amber)}
ul.plain li strong{color:var(--text);font-weight:600}

/* ---------- capa ---------- */
.cover{border-bottom:1px solid var(--line-soft);padding-block:clamp(120px,26vh,210px) clamp(70px,14vh,120px)}
.cover .kicker{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--text-3);margin-bottom:30px}
.cover .sub{font-size:19px;color:var(--text-2);max-width:56ch;margin:0 0 34px}
.confidential{
  display:inline-flex;align-items:center;gap:9px;border:1px solid var(--line);border-radius:2px;
  padding:7px 13px;font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3);
}
.confidential::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--amber);flex:none}

/* ---------- fundos ---------- */
section.bg::before{
  content:"";position:absolute;inset:0;z-index:-2;background-image:var(--bg);
  background-size:cover;background-position:center;opacity:.38;
}
section.bg::after{
  content:"";position:absolute;inset:0;z-index:-1;
  background:
    linear-gradient(90deg,rgba(10,16,32,.97) 0%,rgba(10,16,32,.86) 46%,rgba(10,16,32,.55) 100%),
    linear-gradient(180deg,rgba(10,16,32,.96) 0%,rgba(10,16,32,.88) 16%,rgba(10,16,32,.38) 42%,rgba(10,16,32,.38) 70%,rgba(10,16,32,.92) 100%);
}
section.cover.bg::before{opacity:.55}
@media(max-width:720px){
  section.bg::before{opacity:.3}
  section.bg::after{background:linear-gradient(180deg,rgba(10,16,32,.9),rgba(10,16,32,.78))}
}

/* ---------- stats ---------- */
.stats{
  display:grid;gap:1px;background:var(--line-soft);border:1px solid var(--line-soft);
  grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:30px 0;
}
.stat{background:var(--ground);padding:20px 18px}
.stat .v{
  font-family:var(--serif);font-weight:500;
  font-variation-settings:"opsz" 20,"wght" 520;
  font-size:clamp(28px,5vw,38px);line-height:1;color:var(--text);font-variant-numeric:tabular-nums;
  -webkit-font-smoothing:auto;-moz-osx-font-smoothing:auto;
}
.stat .v span{font-size:.52em;color:var(--amber);margin-left:3px}
.stat .k{font-family:var(--mono);font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--text-3);margin-top:9px;line-height:1.55}

/* ---------- tabelas ---------- */
.tw{overflow-x:auto;margin:26px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
table{border-collapse:collapse;width:100%;min-width:440px;font-size:15px}
th,td{text-align:left;padding:14px 18px 14px 0;border-bottom:1px solid var(--line-soft);vertical-align:top;color:var(--text-2)}
tr:last-child td{border-bottom:0}
th{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-3);font-weight:400;padding-top:15px;padding-bottom:12px}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--text)}
td.nw{white-space:nowrap}
td strong{color:var(--text);font-weight:600}

/* ---------- callouts ---------- */
.note{border-left:2px solid var(--amber-dim);padding:2px 0 2px 18px;margin:26px 0}
.note p:last-child{margin-bottom:0}

/* ---------- video ---------- */
.vid{margin:18px 0 6px;max-width:100%}
.vid iframe{display:block;width:100%;aspect-ratio:16/9;max-width:100%;border:1px solid var(--line-soft);background:#0A1020}
.vidcap{margin-top:11px;font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:var(--text-3)}
.vidcap a{color:var(--amber-dim);text-decoration:none}
.vidcap a:hover{color:var(--amber)}

/* ---------- progresso ---------- */
#progress{position:fixed;top:0;left:0;height:2px;width:0;background:var(--amber);z-index:50;transition:width .08s linear}

footer{
  max-width:var(--maxw);margin-inline:auto;padding:34px 20px 60px;
  font-family:var(--mono);font-size:10px;letter-spacing:.07em;line-height:1.9;color:var(--text-3);
}
@media(min-width:720px){footer{padding-inline:56px}}

@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  #progress{transition:none}
  *{animation:none!important;transition:none!important}
}
"""

# Componentes que so existem no tratamento: moodboard, referencias, paleta,
# beats de roteiro e o painel de producao.
TRATAMENTO_CSS = """
/* ---------- painel ---------- */
.painel{display:grid;gap:1px;background:var(--line-soft);border:1px solid var(--line-soft);grid-template-columns:repeat(auto-fit,minmax(170px,1fr));margin:34px 0 8px}
.painel .cel{background:var(--ground);padding:18px}
.painel .cel .k{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-3);margin-bottom:9px}
.painel .cel .v{font-size:15px;color:var(--text);line-height:1.5}
.pill{
  display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:2px;
  padding:5px 11px;font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-2);
}
.pill::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--text-3);flex:none}
.pill[data-st="entregue"]::before{background:var(--amber)}
.pill[data-st="em-revisao"]::before{background:var(--amber-dim)}
.pill[data-st="rascunho"]::before{background:var(--text-3)}

/* ---------- moodboard ---------- */
.board{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));margin:34px 0 10px}
.frame{
  position:relative;aspect-ratio:16/9;border:1px solid var(--line-soft);overflow:hidden;
  background:radial-gradient(120% 90% at 78% 18%,rgba(217,165,102,.13),transparent 62%),linear-gradient(168deg,#101A33 0%,#0A1020 74%);
  margin:0;padding:0;
}
.frame.wide{grid-column:1/-1;aspect-ratio:2.6/1}
.frame img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.frame figcaption{
  position:absolute;left:12px;right:12px;bottom:10px;z-index:2;
  font-family:var(--mono);font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--text-3);
  text-shadow:0 1px 6px rgba(10,16,32,.9);
}
.frame.has-img figcaption{color:var(--text-2)}
.frame .zoom{position:absolute;inset:0;z-index:1;border:0;padding:0;margin:0;background:transparent;cursor:zoom-in;width:100%;height:100%}
.frame .zoom:focus-visible{outline:1px solid var(--amber);outline-offset:-2px}
.board-note{font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:var(--text-3);margin:0 0 30px}

/* ---------- lightbox ---------- */
#lb{position:fixed;inset:0;z-index:90;background:rgba(8,13,24,.96);display:none;align-items:center;justify-content:center;padding:28px}
#lb.on{display:flex}
#lb img{max-width:100%;max-height:86vh;object-fit:contain;border:1px solid var(--line)}
#lb .cap{position:absolute;left:0;right:0;bottom:16px;text-align:center;font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-3);padding-inline:28px}
#lb .x{position:absolute;top:16px;right:20px;background:none;border:0;color:var(--text-2);font-family:var(--mono);font-size:12px;letter-spacing:.1em;cursor:pointer;padding:8px}

/* ---------- referencias ---------- */
.refs{display:grid;gap:1px;background:var(--line-soft);border:1px solid var(--line-soft);grid-template-columns:repeat(auto-fit,minmax(270px,1fr));margin:30px 0}
.ref{background:var(--ground);padding:20px 18px;display:flex;flex-direction:column;gap:9px}
.ref .n{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;color:var(--amber-dim)}
.ref .t{font-family:var(--serif);font-weight:400;font-size:19px;line-height:1.24;color:var(--text);-webkit-font-smoothing:auto}
.ref .m{font-family:var(--mono);font-size:9.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--text-3);line-height:1.7}
.ref .w{font-size:14px;line-height:1.6;color:var(--text-2);margin:0}
.ref .lk{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--amber-dim);text-decoration:none;margin-top:auto;padding-top:6px}
.ref .lk:hover,.ref .lk:focus-visible{color:var(--amber)}

/* ---------- paleta ---------- */
.pal{display:flex;flex-wrap:wrap;gap:1px;background:var(--line-soft);border:1px solid var(--line-soft);margin:28px 0}
.pal .sw{flex:1 1 92px;min-width:0;background:var(--ground);padding:0 0 12px}
.pal .sw i{display:block;height:64px;background:var(--c)}
.pal .sw b{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.08em;color:var(--text-3);font-weight:400;padding:10px 10px 3px}
.pal .sw em{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.06em;color:var(--amber-dim);font-style:normal;padding:0 10px}

/* ---------- beats de roteiro ---------- */
.beats{border-top:1px solid var(--line-soft);margin:30px 0 0}
.beat{border-bottom:1px solid var(--line-soft);padding-block:24px;display:grid;gap:4px 22px;grid-template-columns:minmax(0,1fr)}
@media(min-width:720px){.beat{grid-template-columns:78px minmax(0,1fr)}}
.beat .tc{font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;color:var(--amber);padding-top:4px}
.beat h4{margin:0 0 6px;font-family:var(--sans);font-weight:600;font-size:15.5px;letter-spacing:.02em;color:var(--text)}
.beat p{margin:0 0 8px;font-size:15px}
.beat p:last-child{margin-bottom:0}
.beat .dir{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;line-height:1.75;color:var(--text-3)}

/* ---------- prompts (ficha tecnica das imagens) ---------- */
details.prompts{border:1px solid var(--line-soft);background:var(--surface);padding:0;margin:30px 0}
details.prompts summary{
  cursor:pointer;padding:14px 18px;list-style:none;
  font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--amber);
}
details.prompts summary::-webkit-details-marker{display:none}
details.prompts summary::after{content:" +";color:var(--text-3)}
details.prompts[open] summary::after{content:" \\2212";color:var(--text-3)}
details.prompts .bd{padding:0 18px 16px;border-top:1px solid var(--line-soft)}
details.prompts dl{margin:0;font-size:13.5px}
details.prompts dt{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-3);margin-top:16px}
details.prompts dd{margin:6px 0 0;color:var(--text-2);line-height:1.6}
"""

DASHBOARD_CSS = """
/* O dashboard nao tem rail: sem isto o <main> cai na coluna de 232px do
   .shell e o texto quebra palavra a palavra. */
.shell.solo{grid-template-columns:minmax(0,1fr)}
@media(min-width:1040px){.shell.solo{grid-template-columns:minmax(0,1fr)}}
.dash-head{padding-block:clamp(72px,16vh,132px) 40px}
.dash-head .kicker{font-family:var(--mono);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--text-3);margin-bottom:30px}
.dash-head .sub{font-size:19px;color:var(--text-2);max-width:56ch;margin:0 0 34px}
/* Hairline por gap+background so funciona com as faixas todas ocupadas; com
   um cartao so a faixa vazia vira um bloco solido. Borda no cartao resolve. */
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));margin:8px 0 0}
.card{background:var(--ground);border:1px solid var(--line-soft);display:flex;flex-direction:column;text-decoration:none;color:inherit;transition:background-color .2s ease,border-color .2s ease}
.card:hover,.card:focus-visible{background:var(--surface);border-color:var(--amber-dim)}
.card .thumb{
  position:relative;aspect-ratio:16/9;overflow:hidden;
  background:radial-gradient(130% 110% at 30% 22%,rgba(217,165,102,.09),transparent 58%),linear-gradient(162deg,#0F1830,#0A1020);
  border-bottom:1px solid var(--line-soft);
}
.card .thumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;opacity:.86;transition:opacity .2s ease}
.card .thumb[data-vazio]::after{
  content:attr(data-vazio);position:absolute;left:14px;bottom:11px;
  font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-3);
}
.card:hover .thumb img{opacity:1}
.card .bd{padding:18px;display:flex;flex-direction:column;gap:8px;flex:1}
.card .cl{font-family:var(--mono);font-size:9.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--amber-dim)}
.card .t{font-family:var(--serif);font-weight:500;font-variation-settings:"opsz" 18,"wght" 520;font-size:22px;line-height:1.2;color:var(--text);-webkit-font-smoothing:auto}
.card .dz{font-size:14px;color:var(--text-2);line-height:1.55;margin:0}
.card .ft{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin-top:auto;padding-top:10px;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-3)}
.empty{border:1px dashed var(--line);padding:34px 22px;margin:30px 0;font-family:var(--mono);font-size:11.5px;line-height:1.9;letter-spacing:.04em;color:var(--text-3)}
.empty code{color:var(--amber-dim)}
.filtros{display:flex;flex-wrap:wrap;gap:8px;margin:28px 0 18px}
.filtros button{
  background:none;border:1px solid var(--line);border-radius:2px;padding:6px 13px;cursor:pointer;
  font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-3);
  transition:color .18s ease,border-color .18s ease;
}
.filtros button:hover{color:var(--text-2)}
.filtros button[aria-pressed="true"]{color:var(--amber);border-color:var(--amber-dim)}
.card[hidden]{display:none}
"""

# --------------------------------------------------------------- helpers ----


def esc(value):
    """Escapa para texto/atributo HTML. None vira string vazia."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def slugify(value):
    """'Natura — Essencial 2026' -> 'natura-essencial-2026'."""
    txt = unicodedata.normalize("NFKD", str(value))
    txt = txt.encode("ascii", "ignore").decode("ascii").lower()
    txt = re.sub(r"[^a-z0-9]+", "-", txt).strip("-")
    return re.sub(r"-{2,}", "-", txt) or "tratamento"


def head(title, css, description="", base_prefix=""):
    """<head> completo, com o CSS ja inlinado.

    Tratamento e material de cliente sob NDA: o noindex acompanha o robots.txt
    da raiz e nao deve ser removido.
    """
    desc = (
        '\n<meta name="description" content="%s">' % esc(description)
        if description
        else ""
    )
    icon = (
        '\n<link rel="icon" href="data:image/svg+xml,'
        "%3Csvg xmlns=&#39;http://www.w3.org/2000/svg&#39; viewBox=&#39;0 0 32 32&#39;"
        "%3E%3Crect width=&#39;32&#39; height=&#39;32&#39; fill=&#39;%230A1020&#39;/%3E"
        "%3Ccircle cx=&#39;16&#39; cy=&#39;16&#39; r=&#39;5&#39; fill=&#39;%23D9A566&#39;/%3E%3C/svg%3E\">"
    )
    return (
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="robots" content="noindex, nofollow, noarchive">\n'
        "<title>%s</title>%s%s\n%s\n<style>%s</style>\n</head>"
        % (esc(title), desc, icon, FONTS, css)
    )


# JS identico ao do Information Memorandum (barra de progresso + secao ativa),
# mais o lightbox do moodboard. Sem dependencia, sem framework.
SCRIPT = """
(function(){
  var bar = document.getElementById('progress');
  var links = Array.prototype.slice.call(document.querySelectorAll('.rail a[href^="#"]'));
  var map = {};
  links.forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });

  if (bar) {
    var onScroll = function(){
      var d = document.documentElement;
      var max = d.scrollHeight - d.clientHeight;
      bar.style.width = (max > 0 ? (d.scrollTop / max) * 100 : 0) + '%';
    };
    onScroll();
    addEventListener('scroll', onScroll, {passive:true});
    addEventListener('resize', onScroll);
  }

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        var a = map[e.target.id];
        if (!a) return;
        if (e.isIntersecting) {
          links.forEach(function(l){ l.classList.remove('on'); });
          a.classList.add('on');
        }
      });
    }, {rootMargin:'-45% 0px -50% 0px', threshold:0});
    Object.keys(map).forEach(function(id){
      var s = document.getElementById(id);
      if (s) io.observe(s);
    });
  }

  var lb = document.getElementById('lb');
  if (lb) {
    var lbImg = lb.querySelector('img');
    var lbCap = lb.querySelector('.cap');
    var last = null;
    var close = function(){
      lb.classList.remove('on');
      lbImg.removeAttribute('src');
      if (last) { last.focus(); last = null; }
    };
    document.addEventListener('click', function(ev){
      var btn = ev.target.closest('.frame .zoom');
      if (btn) {
        var img = btn.parentNode.querySelector('img');
        if (!img) return;
        last = btn;
        lbImg.src = img.currentSrc || img.src;
        lbImg.alt = img.alt || '';
        lbCap.textContent = btn.getAttribute('data-cap') || '';
        lb.classList.add('on');
        lb.querySelector('.x').focus();
        return;
      }
      if (ev.target === lb || ev.target.closest('#lb .x')) close();
    });
    document.addEventListener('keydown', function(ev){
      if (ev.key === 'Escape' && lb.classList.contains('on')) close();
    });
  }
})();
"""
