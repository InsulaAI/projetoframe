"""Confere as páginas geradas antes do push.

Checagem estática (sempre): HTML bem formado, ids únicos, todo link do rail
apontando para seção existente, nenhum src local quebrado, tokens do craft no
lugar e os travamentos de opsz da Bodoni preservados.

Checagem no navegador (se o Playwright estiver instalado): sem estouro
horizontal em 390px, sem erro de JavaScript no console, #progress e .rail a.on
respondendo ao scroll. É a lista do CLAUDE.md, aplicada aos tratamentos.

Uso:
    python3 tratamentos/_lib/verificar.py [slug ...]
"""

import os
import re
import sys
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAZIOS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class Estrutura(HTMLParser):
    """Coleta ids, âncoras internas e srcs; acusa tag aberta sem fechar."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha = []
        self.ids = []
        self.ancoras = []
        self.srcs = []
        self.erros = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get("id"):
            self.ids.append(d["id"])
        href = d.get("href") or ""
        if href.startswith("#") and len(href) > 1:
            self.ancoras.append(href[1:])
        for chave in ("src", "srcset"):
            valor = d.get(chave)
            if valor and not re.match(r"^(https?:|data:|//)", valor):
                self.srcs.append(valor.split()[0])
        if tag not in VAZIOS:
            self.pilha.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.pilha and self.pilha[-1][0] == tag:
            self.pilha.pop()

    def handle_endtag(self, tag):
        if tag in VAZIOS:
            return
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                for orfao, linha in self.pilha[i + 1:]:
                    self.erros.append("<%s> aberta na linha %d sem fechar" % (orfao, linha))
                del self.pilha[i:]
                return
        self.erros.append("</%s> sem abertura correspondente" % tag)


def estatica(pagina):
    falhas = []
    pasta = os.path.dirname(pagina)
    with open(pagina, encoding="utf-8") as fh:
        html = fh.read()

    p = Estrutura()
    p.feed(html)
    falhas += p.erros
    falhas += ["<%s> na linha %d nunca fecha" % (t, l) for t, l in p.pilha]

    repetidos = {i for i in p.ids if p.ids.count(i) > 1}
    falhas += ["id duplicado: #%s" % i for i in sorted(repetidos)]

    faltando = sorted(set(p.ancoras) - set(p.ids))
    falhas += ["âncora #%s sem seção correspondente" % a for a in faltando]

    for src in sorted(set(p.srcs)):
        if not os.path.exists(os.path.join(pasta, src)):
            falhas.append("arquivo referenciado não existe: %s" % src)

    for url in re.findall(r"--bg:url\(([^)]+)\)", html):
        if not re.match(r"^(https?:|data:|//)", url) and not os.path.exists(
            os.path.join(pasta, url)
        ):
            falhas.append("fundo inexistente: %s" % url)

    if "--amber:#D9A566" not in html:
        falhas.append("token --amber fora do padrão da casa")
    if 'font-variation-settings:"opsz"' not in html:
        falhas.append("Bodoni sem opsz travado — fios finos somem no fundo escuro")
    if "noindex" not in html:
        falhas.append("falta o noindex: tratamento é material confidencial")

    for iframe in re.findall(r"<iframe[^>]*src=\"([^\"]+)\"", html):
        if "youtube" in iframe and "nocookie" not in iframe:
            falhas.append("iframe de vídeo fora do youtube-nocookie: %s" % iframe)
        if "drive.google" in iframe:
            falhas.append("vídeo no Drive não carrega em iframe — usar YouTube")

    return falhas


def _chromium():
    """Caminho do Chromium, quando o instalado não bate com a versão do pacote.

    Ambientes remotos costumam trazer o browser pré-instalado numa revisão
    diferente da que o pip acabou de resolver. INSULA_CHROMIUM manda; senão
    procuramos em PLAYWRIGHT_BROWSERS_PATH. None = deixa o Playwright decidir.
    """
    explicito = os.environ.get("INSULA_CHROMIUM")
    if explicito and os.path.exists(explicito):
        return explicito
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if not base or not os.path.isdir(base):
        return None
    for pasta in sorted(os.listdir(base), reverse=True):
        for sufixo in ("chrome-linux/chrome", "chrome-linux/headless_shell"):
            alvo = os.path.join(base, pasta, sufixo)
            if os.path.exists(alvo):
                return alvo
    return None


def navegador(paginas):
    """Retorna (falhas, executou). executou=False quando falta Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return [], False

    falhas = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=_chromium())
        for pagina in paginas:
            rotulo = os.path.relpath(pagina, RAIZ)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            erros = []
            page.on("pageerror", lambda e: erros.append(str(e)))
            page.on(
                "console",
                lambda m: erros.append(m.text) if m.type == "error" else None,
            )
            page.goto("file://%s" % pagina, wait_until="load")
            page.wait_for_timeout(400)

            largura = page.evaluate(
                "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
            )
            if largura > 1:
                falhas.append("%s: estouro horizontal de %dpx em 390px" % (rotulo, largura))

            # Fontes do Google podem estar bloqueadas; erro de rede não conta.
            for erro in erros:
                if "fonts.g" in erro or "ERR_" in erro or "153" in erro:
                    continue
                falhas.append("%s: erro de JS — %s" % (rotulo, erro))

            page.set_viewport_size({"width": 1280, "height": 900})
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.6)")
            page.wait_for_timeout(500)
            largura_barra = page.evaluate(
                "() => { var b = document.getElementById('progress');"
                " return b ? parseFloat(b.style.width) || 0 : -1; }"
            )
            if largura_barra == 0:
                falhas.append("%s: #progress não respondeu ao scroll" % rotulo)
            ativos = page.evaluate("() => document.querySelectorAll('.rail a.on').length")
            tem_rail = page.evaluate("() => document.querySelectorAll('.rail a').length")
            if tem_rail and ativos != 1:
                falhas.append("%s: %d seções ativas no rail (esperado 1)" % (rotulo, ativos))
            page.close()
        browser.close()
    return falhas, True


def main(argv):
    if argv:
        paginas = [os.path.join(RAIZ, s, "index.html") for s in argv]
    else:
        paginas = [os.path.join(RAIZ, "index.html")]
        for nome in sorted(os.listdir(RAIZ)):
            alvo = os.path.join(RAIZ, nome, "index.html")
            if not nome.startswith(("_", ".")) and os.path.exists(alvo):
                paginas.append(alvo)

    paginas = [p for p in paginas if os.path.exists(p)]
    if not paginas:
        print("nada para verificar — rode o build antes")
        return 1

    falhas = []
    for pagina in paginas:
        for f in estatica(pagina):
            falhas.append("%s: %s" % (os.path.relpath(pagina, RAIZ), f))

    do_navegador, rodou = navegador(paginas)
    falhas += do_navegador

    print("verificação: %d página(s)%s" % (len(paginas), "" if rodou else " (estática apenas — Playwright ausente)"))
    for f in falhas:
        print("  ✗ %s" % f)
    if not falhas:
        print("  ✓ tudo no padrão")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
