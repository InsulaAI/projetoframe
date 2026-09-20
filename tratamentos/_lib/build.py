"""Renderiza tratamentos/<slug>/tratamento.json -> tratamentos/<slug>/index.html.

Determinístico: mesma entrada, mesma saída. Nenhuma chamada de rede, nenhuma
dependência fora da stdlib. A inteligência (pesquisa, redação, prompts) mora no
JSON; aqui só há diagramação no padrão craft da Insula.

Uso:
    python3 tratamentos/_lib/build.py <slug|caminho/para/tratamento.json>
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from craft import BASE_CSS, SCRIPT, TRATAMENTO_CSS, esc, head  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATUS_ROTULO = {
    "rascunho": "Rascunho",
    "em-revisao": "Em revisão",
    "entregue": "Entregue",
}


# Pasta do tratamento em edição. O renderizador confere se a imagem existe de
# fato antes de referenciá-la: prompt escrito não é arquivo gerado, e uma página
# com <img> quebrado é pior que um slot honestamente vazio.
_PASTA = [None]


def _arquivo(img):
    """Caminho da imagem se ela existir em disco; string vazia caso contrário."""
    if not img:
        return ""
    caminho = (img.get("arquivo") or "").strip()
    if not caminho:
        return ""
    if _PASTA[0] and not os.path.exists(os.path.join(_PASTA[0], caminho)):
        return ""
    return caminho


def _lista(dados, chave):
    """Devolve sempre uma lista — o JSON vem de um LLM e às vezes omite campos."""
    valor = dados.get(chave)
    if not valor:
        return []
    return valor if isinstance(valor, list) else [valor]


def _paragrafos(itens):
    return "".join("<p>%s</p>\n" % esc(p) for p in itens if p)


def _frame(img, wide=False, indice=None):
    """Um quadro do moodboard. Sem arquivo gerado, vira slot com o prompt."""
    arquivo = _arquivo(img)
    legenda = img.get("legenda") or img.get("alt") or ""
    if not legenda and indice is not None:
        legenda = "Quadro %02d" % indice
    classes = ["frame"]
    if wide or img.get("wide"):
        classes.append("wide")
    if arquivo:
        classes.append("has-img")
        corpo = (
            '<img src="%s" alt="%s" loading="lazy" decoding="async">'
            '<button class="zoom" type="button" data-cap="%s" aria-label="Ampliar: %s"></button>'
            % (esc(arquivo), esc(img.get("alt") or legenda), esc(legenda), esc(legenda))
        )
        rotulo = legenda
    else:
        corpo = ""
        rotulo = "%s — imagem pendente" % legenda if legenda else "Imagem pendente"
    return '<figure class="%s">%s<figcaption>%s</figcaption></figure>' % (
        " ".join(classes),
        corpo,
        esc(rotulo),
    )


def _tabela(tabela):
    cols = tabela.get("cols") or []
    linhas = tabela.get("linhas") or []
    if not linhas:
        return ""
    out = ['<div class="tw"><table>']
    if cols:
        out.append(
            "<thead><tr>%s</tr></thead>"
            % "".join("<th>%s</th>" % esc(c) for c in cols)
        )
    out.append("<tbody>")
    for linha in linhas:
        celulas = linha if isinstance(linha, list) else [linha]
        out.append(
            "<tr>%s</tr>"
            % "".join("<td>%s</td>" % esc(c) for c in celulas)
        )
    out.append("</tbody></table></div>")
    return "".join(out)


def _stats(metricas):
    if not metricas:
        return ""
    celulas = []
    for m in metricas:
        unidade = (
            "<span>%s</span>" % esc(m.get("u")) if m.get("u") else ""
        )
        celulas.append(
            '<div class="stat"><div class="v">%s%s</div><div class="k">%s</div></div>'
            % (esc(m.get("v")), unidade, esc(m.get("k")))
        )
    return '<div class="stats">%s</div>' % "".join(celulas)


class Pagina:
    """Acumula as seções e monta o rail a partir delas, na ordem de inserção."""

    def __init__(self):
        self.blocos = []
        self.rail = []

    def secao(self, html_, sid=None, rotulo=None, classe="", bg=None):
        atributos = []
        classes = [c for c in classe.split() if c]
        if sid:
            atributos.append('id="%s"' % esc(sid))
        if bg:
            classes.append("bg")
            atributos.append('style="--bg:url(%s)"' % esc(bg))
        if classes:
            atributos.insert(0, 'class="%s"' % " ".join(classes))
        self.blocos.append(
            "<section %s>\n<div class=\"in\">\n%s\n</div>\n</section>"
            % (" ".join(atributos), html_)
        )
        if sid and rotulo:
            self.rail.append((sid, rotulo))

    def rail_html(self, marca, submarca):
        itens = "".join(
            '<li><a href="#%s"><span class="n">%02d</span> %s</a></li>'
            % (esc(sid), i + 1, esc(rotulo))
            for i, (sid, rotulo) in enumerate(self.rail)
        )
        return (
            '<nav class="rail" aria-label="Seções">\n'
            '<a class="rail-mark" href="../">Insula AI</a>\n'
            '<div class="rail-sub">%s</div>\n'
            "<ol>%s</ol>\n"
            '<div class="rail-foot">%s</div>\n'
            "</nav>" % (esc(submarca), itens, marca)
        )


def montar(dados, pasta=None):
    """pasta: diretório do tratamento, usado para checar se as imagens existem."""
    _PASTA[0] = pasta
    titulo = dados.get("titulo") or dados.get("campanha") or "Tratamento"
    cliente = dados.get("cliente") or ""
    data = dados.get("data") or ""
    status = (dados.get("status") or "rascunho").strip()
    pg = Pagina()

    # ---- capa -------------------------------------------------------------
    capa = dados.get("capa") or {}
    kicker = dados.get("kicker") or " · ".join(
        [p for p in ["Tratamento de direção", cliente, data] if p]
    )
    confidencial = (
        '<div class="confidential">Documento confidencial · uso restrito</div>'
        if dados.get("confidencial", True)
        else ""
    )
    pg.secao(
        '<div class="cover-inner">\n'
        '<p class="kicker">%s</p>\n<h1>%s</h1>\n<p class="sub">%s</p>\n%s\n</div>'
        % (esc(kicker), esc(titulo), esc(dados.get("sinopse")), confidencial),
        sid="capa",
        classe="cover",
        bg=_arquivo(capa),
    )

    # ---- vídeo de referência (opcional) -----------------------------------
    video = dados.get("video") or {}
    if video.get("youtube"):
        pg.secao(
            '<figure class="vid"><iframe src="https://www.youtube-nocookie.com/embed/%s?rel=0&amp;modestbranding=1" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen title="%s"></iframe>'
            '<figcaption class="vidcap">%s</figcaption></figure>'
            % (
                esc(video["youtube"]),
                esc(video.get("titulo") or "Referência em vídeo"),
                esc(video.get("legenda") or ""),
            ),
            sid="filme",
        )

    # ---- painel (o dashboard do próprio tratamento) -----------------------
    painel = dados.get("painel") or {}
    metricas = _lista(dados, "metricas")
    if painel or metricas:
        celulas = [
            '<div class="cel"><div class="k">Status</div><div class="v">'
            '<span class="pill" data-st="%s">%s</span></div></div>'
            % (esc(status), esc(STATUS_ROTULO.get(status, status)))
        ]
        for chave, valor in painel.items():
            celulas.append(
                '<div class="cel"><div class="k">%s</div><div class="v">%s</div></div>'
                % (esc(chave), esc(valor))
            )
        corpo = (
            '<div class="eyebrow"><span>Painel de produção</span></div>\n'
            '<div class="painel">%s</div>\n%s' % ("".join(celulas), _stats(metricas))
        )
        pg.secao(corpo, sid="painel", rotulo="Painel")

    # ---- visão do diretor -------------------------------------------------
    visao = dados.get("visao") or {}
    if visao:
        corpo = ['<div class="eyebrow"><span>A visão</span></div>']
        if visao.get("titulo"):
            corpo.append("<h2>%s</h2>" % esc(visao["titulo"]))
        if visao.get("lede"):
            corpo.append('<p class="lede">%s</p>' % esc(visao["lede"]))
        corpo.append(_paragrafos(_lista(visao, "paragrafos")))
        if visao.get("citacao"):
            corpo.append('<div class="note"><p>%s</p></div>' % esc(visao["citacao"]))
        pg.secao(
            "\n".join(corpo),
            sid="visao",
            rotulo="A visão",
            bg=_arquivo(visao.get("imagem")),
        )

    # ---- seções livres ----------------------------------------------------
    for i, sec in enumerate(_lista(dados, "secoes")):
        sid = sec.get("id") or "secao-%d" % (i + 1)
        corpo = []
        if sec.get("eyebrow") or sec.get("titulo"):
            corpo.append(
                '<div class="eyebrow"><span>%s</span></div>'
                % esc(sec.get("eyebrow") or sec.get("titulo"))
            )
        if sec.get("titulo"):
            corpo.append("<h2>%s</h2>" % esc(sec["titulo"]))
        if sec.get("lede"):
            corpo.append('<p class="lede">%s</p>' % esc(sec["lede"]))
        corpo.append(_paragrafos(_lista(sec, "paragrafos")))
        itens = _lista(sec, "lista")
        if itens:
            lis = []
            for item in itens:
                if isinstance(item, dict):
                    forte = (
                        "<strong>%s</strong> " % esc(item.get("t")) if item.get("t") else ""
                    )
                    lis.append("<li>%s%s</li>" % (forte, esc(item.get("d"))))
                else:
                    lis.append("<li>%s</li>" % esc(item))
            corpo.append('<ul class="plain">%s</ul>' % "".join(lis))
        if sec.get("tabela"):
            corpo.append(_tabela(sec["tabela"]))
        quadros = _lista(sec, "board")
        if quadros:
            corpo.append(
                '<div class="board">%s</div>'
                % "".join(_frame(q, indice=n + 1) for n, q in enumerate(quadros))
            )
        if sec.get("nota"):
            corpo.append('<div class="note"><p>%s</p></div>' % esc(sec["nota"]))
        pg.secao(
            "\n".join(c for c in corpo if c),
            sid=sid,
            rotulo=sec.get("rail") or sec.get("titulo") or sid,
            bg=_arquivo(sec.get("imagem")),
        )

    # ---- beats de roteiro -------------------------------------------------
    beats = _lista(dados, "beats")
    if beats:
        linhas = []
        for b in beats:
            direcao = (
                '<p class="dir">%s</p>' % esc(b["direcao"]) if b.get("direcao") else ""
            )
            linhas.append(
                '<div class="beat"><div class="tc">%s</div><div>'
                "<h4>%s</h4><p>%s</p>%s</div></div>"
                % (
                    esc(b.get("tc")),
                    esc(b.get("titulo")),
                    esc(b.get("descricao")),
                    direcao,
                )
            )
        pg.secao(
            '<div class="eyebrow"><span>Decupagem</span></div>\n'
            "<h2>%s</h2>\n<div class=\"beats\">%s</div>"
            % (esc(dados.get("beats_titulo") or "Como o filme se move"), "".join(linhas)),
            sid="roteiro",
            rotulo="Decupagem",
        )

    # ---- direção de arte: paleta + moodboard ------------------------------
    paleta = _lista(dados, "paleta")
    mood = _lista(dados, "moodboard")
    if paleta or mood:
        corpo = ['<div class="eyebrow"><span>Direção de arte</span></div>']
        if dados.get("arte_titulo"):
            corpo.append("<h2>%s</h2>" % esc(dados["arte_titulo"]))
        if dados.get("arte_lede"):
            corpo.append('<p class="lede">%s</p>' % esc(dados["arte_lede"]))
        if paleta:
            swatches = []
            for cor in paleta:
                if isinstance(cor, str):
                    cor = {"hex": cor}
                swatches.append(
                    '<div class="sw" style="--c:%s"><i></i><b>%s</b><em>%s</em></div>'
                    % (esc(cor.get("hex")), esc(cor.get("hex")), esc(cor.get("uso") or cor.get("nome") or ""))
                )
            corpo.append('<div class="pal">%s</div>' % "".join(swatches))
        if mood:
            corpo.append(
                '<div class="board">%s</div>'
                % "".join(_frame(q, indice=n + 1) for n, q in enumerate(mood))
            )
            corpo.append(
                '<p class="board-note">Imagens geradas pela Insula AI '
                "· clique para ampliar</p>"
            )
        pg.secao("\n".join(corpo), sid="arte", rotulo="Direção de arte")

    # ---- referências ------------------------------------------------------
    refs = _lista(dados, "referencias")
    if refs:
        cartoes = []
        for i, r in enumerate(refs):
            meta = " · ".join(
                esc(x) for x in [r.get("autor"), r.get("ano"), r.get("fonte")] if x
            )
            link = (
                '<a class="lk" href="%s" target="_blank" rel="noopener noreferrer">Ver referência ↗</a>'
                % esc(r["url"])
                if r.get("url")
                else ""
            )
            cartoes.append(
                '<div class="ref"><div class="n">R%02d</div><div class="t">%s</div>'
                '<div class="m">%s</div><p class="w">%s</p>%s</div>'
                % (i + 1, esc(r.get("titulo")), meta, esc(r.get("porque")), link)
            )
        corpo = ['<div class="eyebrow"><span>Referências</span></div>']
        if dados.get("referencias_lede"):
            corpo.append('<p class="lede">%s</p>' % esc(dados["referencias_lede"]))
        corpo.append('<div class="refs">%s</div>' % "".join(cartoes))
        pg.secao("\n".join(corpo), sid="referencias", rotulo="Referências")

    # ---- produção e contato ----------------------------------------------
    producao = dados.get("producao") or {}
    contatos = _lista(dados, "contatos")
    if producao or contatos:
        corpo = ['<div class="eyebrow"><span>Produção</span></div>']
        if producao.get("titulo"):
            corpo.append("<h2>%s</h2>" % esc(producao["titulo"]))
        corpo.append(_paragrafos(_lista(producao, "paragrafos")))
        if producao.get("tabela"):
            corpo.append(_tabela(producao["tabela"]))
        if contatos:
            linhas = [
                [esc(c.get("nome")), esc(c.get("papel")), esc(c.get("email"))]
                for c in contatos
            ]
            corpo.append(
                _tabela({"cols": ["Nome", "Papel", "Contato"], "linhas": linhas})
            )
        pg.secao("\n".join(c for c in corpo if c), sid="producao", rotulo="Produção")

    # ---- ficha técnica dos prompts ---------------------------------------
    prompts = []
    for origem, img in _todas_imagens(dados):
        if img.get("prompt"):
            prompts.append(
                "<dt>%s</dt><dd>%s</dd>" % (esc(origem), esc(img["prompt"]))
            )
    if prompts:
        pg.blocos.append(
            "<section>\n<div class=\"in\">\n"
            '<details class="prompts"><summary>Ficha técnica · prompts das imagens</summary>'
            '<div class="bd"><dl>%s</dl></div></details>\n</div>\n</section>'
            % "".join(prompts)
        )

    rodape = dados.get("rodape") or (
        "Insula AI · insula-ai.com<br>Tratamento de direção preparado para %s. "
        "Material confidencial: o destinatário concorda em manter seu conteúdo "
        "restrito à avaliação desta proposta.<br>"
        "Todas as imagens desta página foram geradas pela Insula AI."
        % esc(cliente or "o cliente")
    )

    rail_foot = "Tratamento<br>%s<br>%s<br><br>Confidencial" % (
        esc(cliente),
        esc(data),
    )
    corpo_html = (
        '<div class="shell">\n%s\n<main>\n%s\n<footer>%s</footer>\n</main>\n</div>\n'
        '<div id="progress" aria-hidden="true"></div>\n'
        '<div id="lb" role="dialog" aria-modal="true" aria-label="Imagem ampliada">'
        '<button class="x" type="button">Fechar ✕</button><img alt=""><div class="cap"></div></div>\n'
        "<script>%s</script>"
        % (
            pg.rail_html(rail_foot, cliente or "Tratamento"),
            "\n\n".join(pg.blocos),
            rodape,
            SCRIPT,
        )
    )

    doc_titulo = " · ".join(p for p in [titulo, cliente, "Insula AI"] if p)
    return (
        '<!doctype html>\n<html lang="pt-BR">\n%s\n<body>\n%s\n</body>\n</html>\n'
        % (
            head(doc_titulo, BASE_CSS + TRATAMENTO_CSS, dados.get("sinopse")),
            corpo_html,
        )
    )


def _todas_imagens(dados):
    """(rótulo, dict de imagem) de tudo que pode virar arquivo gerado."""
    capa = dados.get("capa")
    if capa:
        yield "Capa", capa
    visao = dados.get("visao") or {}
    if visao.get("imagem"):
        yield "Visão — fundo", visao["imagem"]
    for i, sec in enumerate(_lista(dados, "secoes")):
        rotulo = sec.get("titulo") or "Seção %d" % (i + 1)
        if sec.get("imagem"):
            yield "%s — fundo" % rotulo, sec["imagem"]
        for n, q in enumerate(_lista(sec, "board")):
            yield "%s — quadro %02d" % (rotulo, n + 1), q
    for n, q in enumerate(_lista(dados, "moodboard")):
        yield "Moodboard %02d" % (n + 1), q


OBRIGATORIOS = ("titulo", "cliente", "data", "status")
STATUS_VALIDOS = ("rascunho", "em-revisao", "entregue")
CONHECIDOS = {
    "slug", "titulo", "cliente", "agencia", "campanha", "diretor", "data",
    "status", "confidencial", "kicker", "sinopse", "capa", "painel", "metricas",
    "visao", "secoes", "beats", "beats_titulo", "arte_titulo", "arte_lede",
    "paleta", "moodboard", "referencias", "referencias_lede", "producao",
    "contatos", "video", "rodape", "estilo_extra",
}


def conferir(dados):
    """Avisos sobre o manifesto. Não aborta: página parcial ainda é útil."""
    avisos = []
    for chave in OBRIGATORIOS:
        if not dados.get(chave):
            avisos.append("falta '%s'" % chave)
    status = dados.get("status")
    if status and status not in STATUS_VALIDOS:
        avisos.append(
            "status '%s' fora de %s — não entra nos filtros do dashboard"
            % (status, "/".join(STATUS_VALIDOS))
        )
    desconhecidas = sorted(set(dados) - CONHECIDOS - {"_slug", "_thumb", "_publicado"})
    if desconhecidas:
        avisos.append("chave(s) ignorada(s) pelo renderizador: %s" % ", ".join(desconhecidas))
    if not dados.get("visao"):
        avisos.append("sem 'visao' — o tratamento perde a seção que é o seu ponto")
    return avisos


def carregar(alvo):
    """Aceita slug, diretório ou caminho direto do tratamento.json."""
    if alvo.endswith(".json"):
        caminho = alvo
    elif os.path.isdir(alvo):
        caminho = os.path.join(alvo, "tratamento.json")
    else:
        caminho = os.path.join(RAIZ, alvo, "tratamento.json")
    caminho = os.path.abspath(caminho)
    if not os.path.exists(caminho):
        raise SystemExit("tratamento.json não encontrado: %s" % caminho)
    with open(caminho, encoding="utf-8") as fh:
        return caminho, json.load(fh)


def main(argv):
    if len(argv) != 1:
        raise SystemExit(__doc__)
    caminho, dados = carregar(argv[0])
    for aviso in conferir(dados):
        print("  aviso: %s" % aviso)
    pasta = os.path.dirname(caminho)
    destino = os.path.join(pasta, "index.html")
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(montar(dados, pasta))
    print("build: %s" % os.path.relpath(destino, os.path.dirname(RAIZ)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
