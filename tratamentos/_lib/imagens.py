"""Gera as imagens do tratamento com o nano banana (Gemini Image) e grava os
caminhos de volta no tratamento.json.

Sem SDK: a API do Gemini é REST e urllib dá conta. Isso mantém o repositório na
regra da casa — sem build, sem dependência.

Chave: GEMINI_API_KEY (ou GOOGLE_API_KEY) no ambiente / nos secrets do repo.
Modelo: INSULA_IMG_MODEL, padrão gemini-2.5-flash-image ("nano banana").
        Para o Pro: INSULA_IMG_MODEL=gemini-3-pro-image-preview
Tamanho: INSULA_IMG_SIZE, padrão 2K (aceita 512, 1K, 2K, 4K)

Sem chave, o script não falha: lista o que geraria e devolve código 0, deixando
os slots vazios na página com o prompt visível na ficha técnica.

Uso:
    python3 tratamentos/_lib/imagens.py <slug> [--forcar] [--seco]
"""

import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import _todas_imagens, carregar  # noqa: E402
from craft import slugify  # noqa: E402

ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"
)
MODELO_PADRAO = "gemini-2.5-flash-image"
# 1K basta para a página; 2K para quem vai levar o quadro para apresentação.
TAMANHO_PADRAO = "2K"
EXTENSOES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
# Erros que nenhuma variante de configuração conserta.
FATAIS = (
    "API_KEY_INVALID",
    "API key not valid",
    "PERMISSION_DENIED",
    "is not found",
    "not supported",
    "billing",
)

# Prefixo aplicado a todo prompt: é o que mantém o moodboard parecendo Insula e
# não banco de imagem. Ajustar aqui muda a casa inteira.
ESTILO_CASA = (
    "Still de filme publicitário, fotografia cinematográfica premium. "
    "Luz motivada e direcional, sombra densa com detalhe, contraste alto sem "
    "estourar altas-luzes. Lente 35mm ou 50mm, profundidade de campo rasa, "
    "grão fino de película. Paleta de azul-noite profundo e âmbar quente. "
    "Enquadramento de diretor: composição limpa, um assunto claro, sem colagem "
    "e sem texto na imagem. Fotorrealista, sem aparência de render 3D."
)


def _contexto_ssl():
    """Respeita CA bundle customizado (proxy corporativo/sandbox)."""
    bundle = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if bundle and os.path.exists(bundle):
        return ssl.create_default_context(cafile=bundle)
    return ssl.create_default_context()


def _variantes(proporcao, tamanho):
    """Configurações a tentar, da mais rica para a mais conservadora.

    Nem todo modelo de imagem aceita imageConfig, e alguns exigem TEXT junto de
    IMAGE em responseModalities. Em vez de adivinhar pelo nome do modelo,
    descemos a escada a cada 400.
    """
    cfgs = []
    if proporcao and tamanho:
        cfgs.append({
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": proporcao, "imageSize": tamanho},
        })
    if proporcao:
        cfgs.append({
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": proporcao},
        })
        cfgs.append({
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": proporcao},
        })
    cfgs.append({"responseModalities": ["IMAGE"]})
    cfgs.append({"responseModalities": ["TEXT", "IMAGE"]})
    return cfgs


def _extrair(resposta):
    """(mime, bytes) da primeira parte com imagem, ou None."""
    for candidato in resposta.get("candidates") or []:
        for parte in (candidato.get("content") or {}).get("parts") or []:
            inline = parte.get("inlineData") or parte.get("inline_data")
            if inline and inline.get("data"):
                mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                return mime, base64.b64decode(inline["data"])
    return None


def _post(modelo, chave, corpo):
    req = urllib.request.Request(
        ENDPOINT % modelo,
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": chave},
    )
    with urllib.request.urlopen(req, timeout=180, context=_contexto_ssl()) as r:
        return json.loads(r.read().decode("utf-8"))


def _chamar(modelo, chave, prompt, proporcao, tamanho, tentativas=3):
    """Uma imagem. Devolve (mime, bytes) ou levanta RuntimeError."""
    ultimo = "falhou sem detalhe"

    for config in _variantes(proporcao, tamanho):
        corpo = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": config,
        }
        for tentativa in range(tentativas):
            try:
                resposta = _post(modelo, chave, corpo)
            except urllib.error.HTTPError as erro:
                detalhe = erro.read().decode("utf-8", "replace")[:300]
                ultimo = "HTTP %s: %s" % (erro.code, detalhe)
                # Chave inválida ou modelo inexistente não melhoram descendo a
                # escada: aborta na primeira, sem gastar mais cinco chamadas.
                if any(m in detalhe for m in FATAIS):
                    raise RuntimeError(ultimo)
                if erro.code == 400:
                    break  # configuração recusada: desce um degrau
                if erro.code == 429 or erro.code >= 500:
                    if tentativa < tentativas - 1:
                        espera = 2 ** (tentativa + 1)
                        print("    %s — nova tentativa em %ds" % (erro.code, espera))
                        time.sleep(espera)
                        continue
                    break
                raise RuntimeError(ultimo)  # 401/403: chave errada, não insista
            except urllib.error.URLError as erro:
                ultimo = "rede: %s" % erro.reason
                if tentativa < tentativas - 1:
                    espera = 2 ** (tentativa + 1)
                    print("    rede falhou (%s) — nova tentativa em %ds" % (erro.reason, espera))
                    time.sleep(espera)
                    continue
                break

            imagem = _extrair(resposta)
            if imagem:
                return imagem
            ultimo = "resposta sem imagem: %s" % json.dumps(
                resposta.get("promptFeedback") or resposta
            )[:300]
            break  # sem imagem nesta configuração: desce um degrau

    raise RuntimeError(ultimo)


def _para_webp(caminho):
    """Converte para .webp se Pillow estiver disponível. Opcional de propósito."""
    if caminho.endswith(".webp"):
        return caminho
    try:
        from PIL import Image
    except ImportError:
        return caminho
    destino = os.path.splitext(caminho)[0] + ".webp"
    with Image.open(caminho) as im:
        im.convert("RGB").save(destino, "WEBP", quality=82, method=6)
    os.remove(caminho)
    return destino


def _proporcao(img):
    """16:9 serve para still de filme; o quadro 'wide' da página é recorte."""
    return img.get("proporcao") or "16:9"


def gerar(alvo, forcar=False, seco=False):
    caminho, dados = carregar(alvo)
    pasta = os.path.dirname(caminho)
    chave = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    modelo = os.environ.get("INSULA_IMG_MODEL") or MODELO_PADRAO
    tamanho = os.environ.get("INSULA_IMG_SIZE") or TAMANHO_PADRAO

    slots = list(_todas_imagens(dados))
    pendentes = []
    for i, (rotulo, img) in enumerate(slots):
        if not img.get("prompt"):
            continue
        if not img.get("arquivo"):
            img["arquivo"] = "img/%02d-%s.webp" % (i + 1, slugify(rotulo)[:36])
        destino = os.path.join(pasta, img["arquivo"])
        if os.path.exists(destino) and not forcar:
            print("  = %s (já existe)" % img["arquivo"])
            continue
        pendentes.append((rotulo, img, destino))

    if not pendentes:
        print("imagens: nada a gerar")
    elif seco or not chave:
        motivo = "--seco" if seco else "sem GEMINI_API_KEY"
        print("imagens: %d slot(s) pendente(s) — %s, nada gerado" % (len(pendentes), motivo))
        for rotulo, img, _ in pendentes:
            print("  · %s -> %s" % (rotulo, img["arquivo"]))
        if not seco:
            print("  defina GEMINI_API_KEY para gerar; a página sai com os slots vazios")
    else:
        print("imagens: %d slot(s) em %s (%s)" % (len(pendentes), modelo, tamanho))
        for rotulo, img, destino in pendentes:
            prompt = "%s\n\n%s" % (ESTILO_CASA, img["prompt"])
            if dados.get("estilo_extra"):
                prompt += "\n\n%s" % dados["estilo_extra"]
            print("  · %s" % rotulo)
            try:
                mime, blob = _chamar(modelo, chave, prompt, _proporcao(img), tamanho)
            except RuntimeError as erro:
                print("    ✗ %s" % erro)
                continue
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            bruto = os.path.splitext(destino)[0] + EXTENSOES.get(mime, ".png")
            with open(bruto, "wb") as fh:
                fh.write(blob)
            final = _para_webp(bruto)
            img["arquivo"] = os.path.relpath(final, pasta).replace(os.sep, "/")
            print("    ✓ %s (%.0f KB)" % (img["arquivo"], len(blob) / 1024))

    # Grava de volta: os caminhos de arquivo atribuídos acima ficam no manifesto.
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return 0


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        raise SystemExit(__doc__)
    return gerar(args[0], forcar="--forcar" in argv, seco="--seco" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
