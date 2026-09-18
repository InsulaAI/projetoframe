# projetoframe — InfoMemo Insula AI

Página única (`index.html`) servida por GitHub Pages em `https://insulaai.github.io/projetoframe/`.
É o Information Memorandum da Insula AI para o processo de M&A conduzido pela MAGMA.
Documento confidencial: `robots.txt` bloqueia indexação e o `<head>` traz `noindex, nofollow, noarchive`.

## Estrutura do repositório

```
index.html      página inteira — HTML, CSS e JS inline, sem build
img/            10 imagens .webp de fundo (01-capa … 10-mercado), ~510 KB no total
robots.txt      bloqueio de indexação
```

Não há build, bundler nem dependência. Editar `index.html` e dar push é o ciclo completo.

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

## Verificação antes de dar push

Vale renderizar com Playwright e conferir:

1. Os 6 iframes existem e estão em 16:9 (`document.querySelectorAll('.vid iframe')`)
2. Sem estouro horizontal em 390px de largura
3. Sem erro de JavaScript no console
4. O `#progress` e o `.rail a.on` (seção ativa) respondem ao scroll

O Google Fonts pode estar bloqueado no ambiente de quem renderiza — nesse caso a Bodoni cai para uma fonte substituta e a tipografia dos títulos não pode ser julgada ali.

## Fluxo de trabalho

O ciclo é git normal: editar, commitar, `git push`. O histórico antigo do repositório tem
pares "Add files via upload" / "Delete index.html" porque as alterações vinham do GitHub web —
não repetir esse padrão.

Duas armadilhas daquele tempo, para quem voltar ao upload manual: o Chrome renomeia o download
para `index_1.html` quando já existe um `index.html` na pasta (isso já derrubou a página com um
404), e apagar o `index.html` antes de subir o novo deixa a página fora do ar no intervalo.
