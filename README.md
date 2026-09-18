# Insula AI — Information Memorandum

Página estática do InfoMemo, publicada em `https://insulaai.github.io/projetoframe/`.
Documento confidencial: não indexar, não divulgar link.

## Estrutura

    index.html   página inteira — HTML, CSS e JS inline, sem build
    img/         10 imagens de fundo (.webp, ~510 KB no total)
    robots.txt   bloqueio de indexação
    CLAUDE.md    convenções, decisões travadas e armadilhas do repositório

Não há build, bundler nem dependência. Editar `index.html` e dar push é o ciclo completo.

## Vídeos

Os seis filmes são embeds de YouTube **não listado** (canal Insula AI), servidos por
`youtube-nocookie.com`. Não existe pasta `videos/` nem arquivo de vídeo no repositório.

| Posição | Vídeo | ID |
|---|---|---|
| topo | Teaser institucional (EN) | `lUPPoYyPSsI` |
| case 01 | Brilhante Perfume Extraordinário | `J1M5u7rtXgI` |
| case 02 | Clear Men, director's cut | `DWOG4plvsco` |
| case 03 | KFC, corte digital | `eqpwXXicUG4` |
| case 04 | CIF Especialistas | `ozeYzsmZTJU` |
| case 05 | Natura, filme 03 | `PyXNMhzCaPA` |

Google Drive não serve para isso: o Drive entrega o vídeo por URL autenticada por
cookie e, dentro de um iframe de outro domínio, esse cookie é de terceiros — o Chrome
bloqueia por padrão (Safari e Firefox idem) e o player exibe "Não foi possível carregar
o vídeo". É arquitetura do Drive, não permissão nem formato.

Os dois filmes de processo (Brilhante e Clear) ficam fora da página por decisão; a seção
"O pipeline filmado" mantém o argumento e remete ao data room.

## Publicação

GitHub Pages: Settings → Pages → branch `main`, pasta `/`.

Depois de subir, recarregar com Ctrl+Shift+R — o HTML antigo fica em cache.
Teste de vídeo só vale no endereço publicado: em `file://` o YouTube devolve *Error 153*.

**Atenção:** Pages não autentica. Quem tiver o link abre a página.
Para um InfoMemo sob NDA, considerar repositório privado com Pages restrito
(planos pagos), hospedagem com senha, ou manter fora da web e distribuir por
convite no data room.
