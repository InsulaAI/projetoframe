---
name: tratamento
description: Monta um tratamento de direção da Insula AI a partir de briefing, notas de produção e visão do diretor — pesquisa referências reais, escreve o tratamento.json, gera o moodboard com o nano banana, renderiza a página no padrão craft da casa e atualiza o dashboard. Use quando pedirem "tratamento", "treatment", "proposta de direção" ou quando houver uma pasta em tratamentos/_entradas/ para processar.
---

# Tratamento de direção — Insula AI

Transformar três entradas cruas num tratamento publicado. A parte determinística
(render, imagens, dashboard, verificação) já existe em `tratamentos/_lib/`; o que
esta skill faz é a parte que precisa de julgamento: ler o material, pesquisar
referência de verdade e escrever o `tratamento.json`.

## Entradas

`tratamentos/_entradas/<slug>/` com:

| arquivo | o que é |
|---|---|
| `briefing.md` | o deck do cliente, em texto |
| `notas.md` | notas de produção — orçamento, prazo, equipe, o que é IA e o que é captação |
| `visao.md` | o primeiro texto do diretor, do jeito que saiu |

Se o deck chegar como PDF/PPTX, extraia o texto para `briefing.md` e **não
commite o binário** (o `.gitignore` da pasta já barra). Este repositório publica
no GitHub Pages; deck de cliente é confidencial.

Sem a pasta: `python3 tratamentos/_lib/tratamento.py novo <slug>` cria os três
modelos.

## Ordem de trabalho

### 1 · Ler antes de escrever

Leia os três arquivos inteiros. O `visao.md` é a espinha dorsal — o tratamento
final é a visão do diretor **organizada e sustentada**, nunca substituída por
texto seu. Se a visão diz "quero um filme silencioso", o tratamento explica
tecnicamente como o filme fica silencioso; não troca a ideia por outra melhor.

Anote as tensões entre briefing e visão (o cliente pede demonstração de produto,
o diretor quer sugestão). Elas viram seção, não são varridas para debaixo do
tapete — é justamente o que faz um tratamento valer a leitura.

### 2 · Pesquisar referências de verdade

Use `WebSearch`/`WebFetch`. Regras:

- **Quatro a seis referências, cada uma por um motivo técnico.** Fotografia,
  montagem, desenho de som, direção de arte, atuação. "É bonito" não é motivo.
- **Verifique antes de citar.** Título, diretor e ano errados aparecem na
  primeira reunião. Se não confirmou, não cite — descreva o princípio sem
  atribuir autoria.
- **Link só se você abriu.** URL inventada é pior que campo vazio.
- O campo `porque` diz o que aquela referência resolve **neste** filme, com
  ponteiro para o beat ou a seção onde ela é aplicada.

### 3 · Escrever o `tratamento.json`

Em `tratamentos/<slug>/tratamento.json`. Português, sempre. O esquema completo
está em `tratamentos/README.md`; o essencial:

```jsonc
{
  "titulo": "",            // o nome do tratamento, não o da campanha
  "cliente": "", "agencia": "", "campanha": "", "diretor": "",
  "data": "AAAA-MM-DD",
  "status": "rascunho",    // rascunho | em-revisao | entregue
  "sinopse": "",           // 1–2 frases, aparece na capa e no cartão do dashboard
  "capa":   { "prompt": "" },
  "painel": { "Formato": "", "Entrega": "", "Mídia": "" },
  "metricas": [{ "v": "18", "u": "dias", "k": "Do brief ao master" }],
  "visao":  { "titulo": "", "lede": "", "paragrafos": [], "citacao": "",
              "imagem": { "prompt": "" } },
  "secoes": [{ "id": "tom", "titulo": "", "lede": "", "paragrafos": [],
               "lista": [{ "t": "", "d": "" }], "tabela": {}, "nota": "" }],
  "beats":  [{ "tc": "0:00–0:08", "titulo": "", "descricao": "", "direcao": "" }],
  "paleta": [{ "hex": "#0A1020", "uso": "" }],
  "moodboard": [{ "legenda": "", "prompt": "", "wide": false }],
  "referencias": [{ "titulo": "", "autor": "", "ano": "", "fonte": "",
                    "url": "", "porque": "" }],
  "producao": { "titulo": "", "paragrafos": [], "tabela": {} },
  "contatos": [{ "nome": "", "papel": "", "email": "" }]
}
```

Como escrever:

- **Frase curta, afirmação concreta.** O padrão do `index.html` da raiz é a
  régua: nada de "soluções inovadoras", nada de adjetivo sem número atrás.
- **`lista` com `t` em negrito e `d` explicando** é o formato de argumento da
  casa. Use para as regras de direção — inclusive as negativas ("o que não
  entra" costuma ser o bloco mais útil do tratamento).
- **`beats` é a decupagem**: `tc` é o intervalo, `direcao` é a linha técnica
  (lente, luz, temperatura de cor, som). Se o filme tem duração definida, os
  beats têm que fechar nela.
- **`painel` e `metricas` saem de `notas.md`**, não de otimismo. Prazo que não
  está nas notas não entra.
- Não prometa o que a produção não assinou.

### 4 · Prompts de imagem

Todo slot com `prompt` vira imagem no nano banana. O prefixo de estilo da casa
(`ESTILO_CASA` em `tratamentos/_lib/imagens.py`) já entra sozinho — **não
repita** "cinematográfico", "premium", "35mm" no seu prompt.

Escreva só o que é deste filme: assunto, ação, hora do dia, ambiente,
enquadramento, temperatura de cor. Uma imagem por beat funciona melhor que seis
imagens genéricas. Sem texto dentro da imagem, sem logo, sem colagem.

Quantidade que costuma bastar: capa + fundo da visão + um quadro por beat.

### 5 · Publicar

```bash
python3 tratamentos/_lib/tratamento.py publicar <slug>   # imagens + build + dashboard
python3 tratamentos/_lib/verificar.py <slug>             # tem que sair limpo
```

Sem `GEMINI_API_KEY` no ambiente, a geração é pulada com aviso e a página sai
com os slots vazios e os prompts na ficha técnica — o resto funciona igual.

Depois: `git add`, commit descritivo, `git push -u origin <branch>`.

## Limites

- **Não editar `tratamentos/index.html` à mão** — é gerado pelo `dashboard.py`.
- **Não criar CSS por tratamento.** Tudo sai de `_lib/craft.py`. Se um
  tratamento precisa de um componente novo, ele entra no craft e serve a todos.
- **Não mexer no `opsz` da Bodoni** sem reler o CLAUDE.md da raiz: em texto
  claro sobre fundo escuro os fios finos da Didone somem.
- **Vídeo é YouTube (`youtube-nocookie`), nunca Drive.** O Drive não carrega em
  iframe de outro domínio.
- O `noindex` e o selo de confidencial ficam. Tratamento é material sob NDA.
