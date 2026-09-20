"""CLI único do pipeline de tratamentos da Insula.

    python3 tratamentos/_lib/tratamento.py novo <slug>        # pasta de entradas
    python3 tratamentos/_lib/tratamento.py imagens <slug>     # nano banana
    python3 tratamentos/_lib/tratamento.py build <slug>       # JSON -> index.html
    python3 tratamentos/_lib/tratamento.py publicar <slug>    # imagens + build + dashboard
    python3 tratamentos/_lib/tratamento.py dashboard          # só o índice
    python3 tratamentos/_lib/tratamento.py todos              # reconstrói tudo

A etapa que falta de propósito é a redação: transformar briefing + notas +
visão em tratamento.json é trabalho de modelo, feito pela skill /tratamento ou
pela Action. Este CLI cuida de tudo que é determinístico.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build as mod_build  # noqa: E402
import dashboard as mod_dashboard  # noqa: E402
import imagens as mod_imagens  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADAS = os.path.join(RAIZ, "_entradas")

MODELOS = {
    "briefing.md": """# Briefing — <cliente> / <campanha>

> Cole aqui o conteúdo do deck de briefing. Se o deck for PDF ou PPTX, extraia
> o texto para cá: o pipeline lê markdown, não binário, e o deck original não
> deve ser commitado (ver .gitignore desta pasta).

## Cliente e produto

## Desafio de negócio

## Público

## Mensagem principal

## Entregáveis e formatos

## Prazo e janela de mídia

## Restrições (legal, marca, obrigatórios)
""",
    "notas.md": """# Notas de produção — <cliente> / <campanha>

## Orçamento e escopo

## Janela de produção

## Equipe prevista

## Locações / talento / set

## O que é IA e o que é captação

## Riscos e pontos de atenção
""",
    "visao.md": """# Visão do diretor — primeiro texto

> Texto livre, do jeito que saiu. O pipeline usa isto como espinha dorsal do
> tratamento: não escreva bonito aqui, escreva verdadeiro.

## A ideia em uma frase

## Por que este filme, deste jeito

## Tom e sensação

## Como ele se move

## Referências que já estão na cabeça
""",
}

GITIGNORE_ENTRADAS = """# Deck de cliente é confidencial e este repositório publica no GitHub Pages.
# O pipeline lê os .md; o binário original fica fora do versionamento.
*.pdf
*.pptx
*.ppt
*.key
*.docx
*.mov
*.mp4
"""


def cmd_novo(slug):
    pasta = os.path.join(ENTRADAS, slug)
    os.makedirs(pasta, exist_ok=True)
    for nome, conteudo in MODELOS.items():
        caminho = os.path.join(pasta, nome)
        if os.path.exists(caminho):
            print("  = %s (mantido)" % nome)
            continue
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(conteudo)
        print("  + %s" % nome)
    ignore = os.path.join(ENTRADAS, ".gitignore")
    if not os.path.exists(ignore):
        with open(ignore, "w", encoding="utf-8") as fh:
            fh.write(GITIGNORE_ENTRADAS)
    print("entradas prontas: tratamentos/_entradas/%s/" % slug)
    print("preencha os três arquivos e rode /tratamento %s no Claude Code" % slug)
    return 0


def cmd_todos():
    falhas = 0
    for nome in sorted(os.listdir(RAIZ)):
        if nome.startswith("_") or nome.startswith("."):
            continue
        if not os.path.exists(os.path.join(RAIZ, nome, "tratamento.json")):
            continue
        try:
            mod_build.main([nome])
        except SystemExit as erro:
            if erro.code:
                print("falhou: %s (%s)" % (nome, erro.code))
                falhas += 1
    mod_dashboard.main()
    return 1 if falhas else 0


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    cmd, resto = argv[0], argv[1:]

    if cmd == "novo":
        if not resto:
            raise SystemExit("uso: novo <slug>")
        return cmd_novo(resto[0])
    if cmd == "imagens":
        return mod_imagens.main(resto)
    if cmd == "build":
        return mod_build.main(resto)
    if cmd == "dashboard":
        return mod_dashboard.main()
    if cmd == "todos":
        return cmd_todos()
    if cmd == "publicar":
        if not resto:
            raise SystemExit("uso: publicar <slug>")
        codigo = mod_imagens.main(resto)
        if codigo:
            return codigo
        codigo = mod_build.main(resto[:1])
        if codigo:
            return codigo
        return mod_dashboard.main()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
