# Insula AI — Information Memorandum

Página estática do InfoMemo. Documento confidencial: não indexar, não divulgar link.

## Estrutura
    index.html          página completa, CSS embutido
    img/                imagens de fundo (webp, 2560px)
    videos/             filmes — colocar os arquivos aqui

## Vídeos
`index.html` espera estes arquivos em `videos/`:

    brilhante.mp4           Brilhante Perfume Extraordinário
    brilhante-process.mp4   Brilhante — o processo
    clear-vinijr.mp4        Clear Men com Vini Jr.
    clear-process.mp4       Clear — o processo
    kfc-digital.mp4         KFC — corte digital
    cif-especialistas.mp4   CIF Especialistas
    natura-03.mp4           Natura, filme 03

Export recomendado: H.264, 1080p, ~4 Mbps, AAC 128k, faststart.

    ffmpeg -i entrada.mov -vf scale=1920:-2 -c:v libx264 -crf 22 \
      -preset slow -movflags +faststart -c:a aac -b:a 128k saida.mp4

GitHub bloqueia arquivos acima de 100 MB. Acima disso, usar Git LFS ou host externo.

## Publicação
GitHub Pages: Settings → Pages → branch `main`, pasta `/`.

**Atenção:** Pages não autentica. Quem tiver o link abre a página.
Para um InfoMemo sob NDA, considerar repositório privado com Pages restrito
(planos pagos), hospedagem com senha, ou manter fora da web e distribuir por
convite no data room.
