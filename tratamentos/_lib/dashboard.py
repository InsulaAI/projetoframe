"""Varre tratamentos/*/tratamento.json e escreve tratamentos/index.html.

O dashboard é derivado: nunca se edita à mão. Rodar de novo depois de criar,
renomear ou mudar o status de qualquer tratamento.

Uso:
    python3 tratamentos/_lib/dashboard.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from craft import BASE_CSS, DASHBOARD_CSS, SCRIPT, esc, head  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATUS_ROTULO = {
    "rascunho": "Rascunho",
    "em-revisao": "Em revisão",
    "entregue": "Entregue",
}
ORDEM_STATUS = ["entregue", "em-revisao", "rascunho"]


def coletar():
    """Lê todos os tratamentos. Diretórios com _ no início são internos."""
    achados = []
    for nome in sorted(os.listdir(RAIZ)):
        if nome.startswith("_") or nome.startswith("."):
            continue
        pasta = os.path.join(RAIZ, nome)
        manifesto = os.path.join(pasta, "tratamento.json")
        if not os.path.isdir(pasta) or not os.path.exists(manifesto):
            continue
        try:
            with open(manifesto, encoding="utf-8") as fh:
                dados = json.load(fh)
        except (OSError, ValueError) as erro:
            print("aviso: %s ilegível (%s) — fora do dashboard" % (nome, erro))
            continue
        dados["_slug"] = nome
        dados["_publicado"] = os.path.exists(os.path.join(pasta, "index.html"))
        capa = (dados.get("capa") or {}).get("arquivo") or ""
        dados["_thumb"] = "%s/%s" % (nome, capa) if capa and os.path.exists(
            os.path.join(pasta, capa)
        ) else ""
        achados.append(dados)
    # Mais recentes primeiro; sem data, vai para o fim.
    achados.sort(key=lambda d: (d.get("data") or "", d["_slug"]), reverse=True)
    return achados


def _cartao(t):
    status = (t.get("status") or "rascunho").strip()
    if t["_thumb"]:
        thumb = '<div class="thumb"><img src="%s" alt="" loading="lazy" decoding="async"></div>' % esc(
            t["_thumb"]
        )
    else:
        thumb = '<div class="thumb" data-vazio="Capa pendente"></div>' 
    rodape = [
        '<span class="pill" data-st="%s">%s</span>'
        % (esc(status), esc(STATUS_ROTULO.get(status, status)))
    ]
    if t.get("data"):
        rodape.append("<span>%s</span>" % esc(t["data"]))
    if t.get("diretor"):
        rodape.append("<span>Dir. %s</span>" % esc(t["diretor"]))
    return (
        '<a class="card" href="%s/" data-st="%s">'
        "%s"
        '<div class="bd"><div class="cl">%s</div><div class="t">%s</div>'
        '<p class="dz">%s</p><div class="ft">%s</div></div></a>'
        % (
            esc(t["_slug"]),
            esc(status),
            thumb,
            esc(t.get("cliente") or "—"),
            esc(t.get("titulo") or t.get("campanha") or t["_slug"]),
            esc(t.get("sinopse") or ""),
            "".join(rodape),
        )
    )


def montar(tratamentos):
    total = len(tratamentos)
    por_status = {s: 0 for s in ORDEM_STATUS}
    for t in tratamentos:
        chave = (t.get("status") or "rascunho").strip()
        por_status[chave] = por_status.get(chave, 0) + 1

    celulas = [('<div class="stat"><div class="v">%d</div>'
                '<div class="k">Tratamentos</div></div>' % total)]
    for chave in ORDEM_STATUS:
        celulas.append(
            '<div class="stat"><div class="v">%d</div><div class="k">%s</div></div>'
            % (por_status.get(chave, 0), esc(STATUS_ROTULO[chave]))
        )
    stats = '<div class="stats">%s</div>' % "".join(celulas)

    if tratamentos:
        filtros = ['<div class="filtros" role="group" aria-label="Filtrar por status">'
                   '<button type="button" data-f="all" aria-pressed="true">Todos</button>']
        for chave in ORDEM_STATUS:
            if por_status.get(chave):
                filtros.append(
                    '<button type="button" data-f="%s" aria-pressed="false">%s</button>'
                    % (esc(chave), esc(STATUS_ROTULO[chave]))
                )
        filtros.append("</div>")
        corpo = "%s\n%s\n<div class=\"grid\">%s</div>" % (
            stats,
            "".join(filtros),
            "".join(_cartao(t) for t in tratamentos),
        )
    else:
        corpo = (
            stats
            + '<div class="empty">Nenhum tratamento ainda.<br><br>'
            "1 · crie <code>tratamentos/_entradas/&lt;slug&gt;/</code> com "
            "<code>briefing.md</code>, <code>notas.md</code> e <code>visao.md</code><br>"
            "2 · rode <code>/tratamento &lt;slug&gt;</code> no Claude Code, ou dê push "
            "e deixe a Action <code>tratamento.yml</code> rodar<br>"
            "3 · o dashboard se reconstrói sozinho</div>"
        )

    cabecalho = (
        '<section class="dash-head" id="topo">\n<div class="in">\n'
        '<p class="kicker">Insula AI · Tratamentos de direção</p>\n'
        "<h1>Tratamentos</h1>\n"
        '<p class="sub">Cada proposta de direção vira uma página própria, no padrão '
        "craft da casa, com referências, moodboard gerado e painel de produção.</p>\n"
        '<div class="confidential">Material confidencial · uso restrito</div>\n'
        "</div>\n</section>"
    )

    script = SCRIPT + """
(function(){
  var botoes = Array.prototype.slice.call(document.querySelectorAll('.filtros button'));
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  botoes.forEach(function(b){
    b.addEventListener('click', function(){
      var f = b.getAttribute('data-f');
      botoes.forEach(function(o){ o.setAttribute('aria-pressed', String(o === b)); });
      cards.forEach(function(c){
        c.hidden = (f !== 'all' && c.getAttribute('data-st') !== f);
      });
    });
  });
})();
"""

    return (
        '<!doctype html>\n<html lang="pt-BR">\n%s\n<body>\n'
        '<div class="shell solo">\n<main>\n%s\n<section>\n<div class="in">\n%s\n</div>\n</section>\n'
        "<footer>Insula AI · insula-ai.com<br>"
        "Página gerada por <code>tratamentos/_lib/dashboard.py</code> — não editar à mão."
        "<br>Todas as imagens foram geradas pela Insula AI.</footer>\n"
        "</main>\n</div>\n"
        '<div id="progress" aria-hidden="true"></div>\n<script>%s</script>\n'
        "</body>\n</html>\n"
        % (
            head(
                "Tratamentos · Insula AI",
                BASE_CSS + DASHBOARD_CSS,
                "Índice dos tratamentos de direção da Insula AI.",
            ),
            cabecalho,
            corpo,
            script,
        )
    )


def main():
    tratamentos = coletar()
    destino = os.path.join(RAIZ, "index.html")
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(montar(tratamentos))
    print("dashboard: %d tratamento(s) -> tratamentos/index.html" % len(tratamentos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
