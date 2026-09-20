# projetoframe — Insula AI

Duas coisas moram aqui, no mesmo GitHub Pages (`https://insulaai.github.io/projetoframe/`):

1. **O Information Memorandum** — `index.html` na raiz, página única, para o processo
   de M&A conduzido pela MAGMA.
2. **O pipeline de tratamentos** — `tratamentos/`, que gera uma página de tratamento de
   direção por projeto, mais um dashboard.

Ambos são confidenciais: `robots.txt` bloqueia indexação e todo `<head>` traz
`noindex, nofollow, noarchive`.

## Estrutura do repositório

```
index.html      o InfoMemo inteiro — HTML, CSS e JS inline, sem build
img/            10 imagens .webp de fundo (01-capa … 10-mercado), ~510 KB no total
robots.txt      bloqueio de indexação
tratamentos/    pipeline de tratamentos de direção — ver tratamentos/README.md
  _lib/         Python stdlib: craft.py (tokens e CSS), build, dashboard, imagens, verificar
  _entradas/    briefing.md + notas.md + visao.md por projeto (não publicado: prefixo _)
  <slug>/       tratamento.json + index.html + img/ gerados
.claude/skills/tratamento/   a skill que redige o tratamento.json
.github/workflows/tratamento.yml   a mesma coisa, automática, no push
```

O InfoMemo não tem build: editar `index.html` e dar push é o ciclo completo.
Os tratamentos têm um pipeline, mas sem dependência — só a stdlib do Python.

## Convenções

- **Tudo inline.** CSS num `<style>` no `<head>`, JS num `<script>` antes de `</body>`. Não criar arquivos separados.
- **Tokens de design** ficam em `:root`. Cores, fontes e largura máxima saem de lá — não escrever valor cru no meio do CSS.
  - `--ground:#0A1020` fundo · `--amber:#D9A566` acento · `--text/-2/-3` hierarquia de texto
  - `--serif` Bodoni Moda (títulos) · `--sans` Archivo (corpo) · `--mono` JetBrains Mono (rótulos)
  - `--maxw:92ch` é a coluna de conteúdo; `.in` a centraliza dentro da seção
- **Seções** são `<section id="...">` com um `.in` dentro. As que têm imagem de fundo levam `class="bg"` e `style="--bg:url(img/NN-nome.webp)"`.
- **Português** em todo o conteúdo. Uma versão em inglês está prevista mas não existe ainda.

## Decisões que não devem ser revertidas sem motivo

**Vídeos vivem no YouTube, não no Google Drive.** O Drive entrega vídeo por URL autenticada por cookie; dentro de um iframe de outro domínio esse cookie é de terceiros e o Chrome bloqueia por padrão — o player carrega e o vídeo dá "Não foi possível carregar o vídeo". Vale para Safari e Firefox também. Os 6 embeds usam `youtube-nocookie.com`, com vídeos não listados no canal Insula AI. Não voltar para o Drive.

**Títulos têm `font-variation-settings` travado.** Bodoni Moda é uma Didone: contraste altíssimo entre traço e fio. Em texto claro sobre fundo escuro os fios finos somem. Por isso `h1`, `h2`, `.stat .v` e `.rail-mark` travam `"opsz"` num corte de texto (16–32, não o de display que o navegador escolheria) e `"wght" 520`, e desligam `-webkit-font-smoothing`, que afina o traço. Mexer no tamanho desses títulos sem revisar o `opsz` traz o problema de volta.

**`-webkit-font-smoothing:antialiased` fica só no corpo**, nunca nos títulos.

**Natura é marco de origem, não produto atual.** O case 05 está datado de dezembro de 2024 e
rotulado como marco de origem. A frase não cita o Brilhante — o Natura é bem anterior.

**O título da seção de cases não menciona "dois anos".** O intervalo real não chega a isso e
vira pergunta em due diligence.

**Teste de vídeo só vale no endereço publicado.** Abrir o `index.html` local (`file://`) faz o YouTube devolver *Error 153* — embed sem origem válida. Não é bug da página.

## Tratamentos

O `index.html` da raiz é escrito à mão. As páginas em `tratamentos/` **não são** —
saem de `tratamentos/_lib/build.py` a partir de um `tratamento.json`, e
`tratamentos/index.html` sai de `dashboard.py`. Editar qualquer um dos dois à mão
é trabalho que o próximo build apaga.

O CSS dos tratamentos vive em `tratamentos/_lib/craft.py` e repete os tokens do
InfoMemo. São duas cópias conscientes: o InfoMemo continua sem dependência de
build, e o pipeline continua servindo a todos os tratamentos de uma vez.
Mudou um token de cor ou de fonte? Mude nos dois.

Detalhes de esquema, secrets e comandos: `tratamentos/README.md`.

## Verificação antes de dar push

No InfoMemo, vale renderizar com Playwright e conferir:

1. Os 6 iframes existem e estão em 16:9 (`document.querySelectorAll('.vid iframe')`)
2. Sem estouro horizontal em 390px de largura
3. Sem erro de JavaScript no console
4. O `#progress` e o `.rail a.on` (seção ativa) respondem ao scroll

Nos tratamentos, essa mesma lista está automatizada:

```bash
python3 tratamentos/_lib/verificar.py        # tudo
python3 tratamentos/_lib/verificar.py <slug> # um só
```

O Google Fonts pode estar bloqueado no ambiente de quem renderiza — nesse caso a Bodoni cai para uma fonte substituta e a tipografia dos títulos não pode ser julgada ali.

## Fluxo de trabalho

O ciclo é git normal: editar, commitar, `git push`. O histórico antigo do repositório tem
pares "Add files via upload" / "Delete index.html" porque as alterações vinham do GitHub web —
não repetir esse padrão.

Duas armadilhas daquele tempo, para quem voltar ao upload manual: o Chrome renomeia o download
para `index_1.html` quando já existe um `index.html` na pasta (isso já derrubou a página com um
404), e apagar o `index.html` antes de subir o novo deixa a página fora do ar no intervalo.
