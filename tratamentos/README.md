# Tratamentos — pipeline

Sistema que transforma **deck de briefing + notas de produção + visão do
diretor** num tratamento publicado no GitHub Pages, com referências
pesquisadas, moodboard gerado e dashboard próprio.

Publica em `https://insulaai.github.io/projetoframe/tratamentos/`.

```
tratamentos/
  index.html            dashboard — GERADO, não editar
  _lib/                 o pipeline (Python stdlib, sem dependência)
    craft.py            tokens e CSS do padrão Insula — fonte única
    build.py            tratamento.json -> index.html
    dashboard.py        varre os tratamentos -> index.html do índice
    imagens.py          nano banana (Gemini) -> img/*.webp
    verificar.py        checagem estática + navegador
    tratamento.py       CLI que amarra tudo
  _entradas/<slug>/     briefing.md, notas.md, visao.md  (entrada humana)
  <slug>/               tratamento.json + index.html + img/  (saída)
```

Pastas com `_` no começo não são publicadas pelo GitHub Pages — é por isso que
as entradas ficam em `_entradas/`.

## Os três caminhos

**1 · Claude Code (controle editorial)**

```bash
python3 tratamentos/_lib/tratamento.py novo natura-fonte   # cria as entradas
# preencha briefing.md, notas.md e visao.md
/tratamento natura-fonte                                   # pesquisa, escreve, publica
```

**2 · GitHub Actions (automático)**

Faça push de `tratamentos/_entradas/<slug>/` com os três `.md`. A Action
`tratamento.yml` detecta que falta o `tratamento.json`, redige (se houver
`ANTHROPIC_API_KEY`), gera as imagens (se houver `GEMINI_API_KEY`), renderiza,
verifica e commita de volta.

**3 · Só os passos determinísticos**

```bash
python3 tratamentos/_lib/tratamento.py imagens <slug>    # --forcar, --seco
python3 tratamentos/_lib/tratamento.py build <slug>
python3 tratamentos/_lib/tratamento.py dashboard
python3 tratamentos/_lib/tratamento.py publicar <slug>   # os três acima
python3 tratamentos/_lib/tratamento.py todos             # reconstrói tudo
python3 tratamentos/_lib/verificar.py [slug ...]
```

## Secrets

| nome | onde | para quê |
|---|---|---|
| `GEMINI_API_KEY` | Settings → Secrets → Actions | gerar as imagens (nano banana) |
| `ANTHROPIC_API_KEY` | Settings → Secrets → Actions | redigir o tratamento dentro da Action |
| `INSULA_IMG_MODEL` | Settings → Variables (opcional) | trocar o modelo de imagem |
| `INSULA_IMG_SIZE` | Settings → Variables (opcional) | `512`, `1K`, `2K` (padrão) ou `4K` |

Sem chave nenhuma nada quebra: a página sai com os slots de imagem vazios e os
prompts visíveis na ficha técnica, e o dashboard funciona igual.

Modelo padrão: `gemini-2.5-flash-image`. Para o Pro:
`INSULA_IMG_MODEL=gemini-3-pro-image-preview`.

## `tratamento.json`

Só `titulo`, `cliente`, `data` e `status` são obrigatórios — o resto é opcional
e a seção correspondente simplesmente não aparece.

| campo | tipo | o que faz |
|---|---|---|
| `titulo` `cliente` `agencia` `campanha` `diretor` | texto | cabeçalho e cartão do dashboard |
| `data` | `AAAA-MM-DD` | ordena o dashboard, mais recente primeiro |
| `status` | `rascunho` \| `em-revisao` \| `entregue` | pílula e filtro do dashboard |
| `sinopse` | texto | subtítulo da capa e resumo do cartão |
| `confidencial` | bool (padrão `true`) | selo de NDA na capa |
| `capa` | `{arquivo, prompt, alt}` | fundo da capa e thumb do dashboard |
| `painel` | objeto chave→valor | o painel de produção, na ordem escrita |
| `metricas` | `[{v, u, k}]` | números grandes — `v` valor, `u` unidade, `k` rótulo |
| `visao` | `{titulo, lede, paragrafos[], citacao, imagem}` | a seção da visão do diretor |
| `secoes` | `[{id, titulo, eyebrow, lede, paragrafos[], lista[], tabela, board[], imagem, nota, rail}]` | seções livres, na ordem |
| `beats` | `[{tc, titulo, descricao, direcao}]` | a decupagem |
| `paleta` | `[{hex, uso}]` | amostras de cor |
| `moodboard` | `[{arquivo, prompt, legenda, alt, wide}]` | grade de imagens; `wide` ocupa a linha |
| `referencias` | `[{titulo, autor, ano, fonte, url, porque}]` | cartões de referência |
| `producao` | `{titulo, paragrafos[], tabela}` | cronograma e escopo |
| `contatos` | `[{nome, papel, email}]` | tabela de contato |
| `video` | `{youtube, titulo, legenda}` | embed — **ID do YouTube**, nunca Drive |
| `rodape` `kicker` `arte_titulo` `arte_lede` `referencias_lede` `beats_titulo` `estilo_extra` | texto | ajustes finos |

`tabela` é `{"cols": [...], "linhas": [[...], [...]]}`.
`lista` aceita `{"t": "negrito", "d": "resto"}` ou string solta.

Campo desconhecido não quebra o build: sai um aviso e ele é ignorado.

### Imagens

Todo slot com `prompt` e sem `arquivo` ganha um nome estável na primeira vez que
`imagens` roda, e o caminho é gravado de volta no JSON. Rodar de novo não
regenera o que já existe — para isso, `--forcar`.

O prefixo de estilo da casa (`ESTILO_CASA` em `_lib/imagens.py`) entra sozinho
em todo prompt. Não repita "cinematográfico", "35mm", "premium" no prompt do
tratamento: escreva só o que é daquele filme.

Se o Pillow estiver instalado, o PNG da API vira `.webp` (~5× menor). Sem
Pillow, fica PNG e funciona igual.

## Verificação antes do push

`verificar.py` roda a lista do `CLAUDE.md` da raiz, adaptada:

- HTML bem formado, ids únicos, âncora do rail com seção correspondente
- nenhum `src` ou `--bg` apontando para arquivo que não existe
- tokens do craft presentes e `opsz` da Bodoni travado
- `noindex` presente — tratamento é material sob NDA
- vídeo em `youtube-nocookie`, nunca Drive
- **com Playwright**: sem estouro horizontal em 390px, sem erro de JS,
  `#progress` e `.rail a.on` respondendo ao scroll

Se o Playwright não estiver instalado, a checagem estática roda sozinha e o
script avisa. `INSULA_CHROMIUM` aponta o binário quando a versão instalada não
bate com a do pacote.

## Regras da casa

- **O dashboard é derivado.** Nunca editar `tratamentos/index.html` à mão.
- **CSS só em `_lib/craft.py`.** Componente novo entra no craft e serve a todos
  os tratamentos — nada de estilo por tratamento.
- **Bodoni com `opsz` travado.** Ver `CLAUDE.md` da raiz antes de mexer em
  tamanho de título.
- **Vídeo no YouTube, nunca no Drive.** O Drive não carrega em iframe de outro
  domínio.
- **Deck de cliente não é commitado.** `_entradas/.gitignore` barra binário;
  extraia o texto para `briefing.md`.
- **Teste de vídeo só vale no endereço publicado** — `file://` devolve
  *Error 153* do YouTube, e não é bug da página.

## A pasta `exemplo/`

É demonstração do pipeline, com cliente fictício. Pode apagar:

```bash
rm -rf tratamentos/exemplo && python3 tratamentos/_lib/tratamento.py dashboard
```
