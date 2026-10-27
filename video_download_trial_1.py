"""
Baixa vídeos do YouTube a partir de uma URL, salvando no caminho informado.

Requisitos:
    pip install yt-dlp

Para baixar na melhor qualidade (vídeo+áudio separados sendo juntados),
também é preciso ter o ffmpeg instalado. Se o ffmpeg não for encontrado,
o script detecta isso automaticamente e baixa um arquivo único já pronto
(sem precisar de merge), evitando erro.

Uso como script (o programa pergunta URL, destino e se é mp4 ou mp3):
    python video_download_trial_1.py

Uso como função:
    from video_download_trial_1 import baixar_video_youtube
    caminho = baixar_video_youtube(
        "https://www.youtube.com/watch?v=XXXXXXXXXXX",
        "C:/Users/voce/Videos/meu_video",
        formato_saida="mp3",  # ou "mp4"
    )
"""

from __future__ import annotations

import os
import shutil
import sys

try:
    import yt_dlp
except ImportError as exc:  # biblioteca não instalada
    raise ImportError(
        "A biblioteca 'yt-dlp' não está instalada. Rode: pip install yt-dlp"
    ) from exc


def baixar_video_youtube(
    url: str,
    output_path: str,
    melhor_qualidade: bool = True,
    formato_saida: str = "mp4",
) -> str:
    """
    Baixa um vídeo do YouTube e salva no caminho especificado.

    Args:
        url: URL do vídeo do YouTube.
        formato_saida: "mp4" (vídeo completo, com áudio) ou "mp3" (somente o
            áudio). O mp3 exige o ffmpeg instalado.
        output_path: Caminho de saída. Pode ser:
            - um caminho de arquivo completo, ex: "C:/videos/meu_video.mp4"
            - uma pasta existente, ex: "C:/videos" (o nome do arquivo vira o
              título do vídeo)
        melhor_qualidade: se True, tenta baixar o melhor vídeo+áudio
            disponíveis e juntar em um único .mp4 (requer ffmpeg instalado).
            Se o ffmpeg não estiver instalado, cai automaticamente para um
            arquivo único já pronto (sem merge). Se False, já baixa direto o
            melhor arquivo único, sem tentar merge.

    Returns:
        O caminho completo do arquivo baixado.

    Raises:
        ValueError: se a URL for inválida/vazia.
        yt_dlp.utils.DownloadError: se o download falhar (vídeo privado,
            removido, região bloqueada, etc.).
    """
    if not url or not url.strip():
        raise ValueError("A URL do vídeo não pode ser vazia.")

    formato_saida = formato_saida.strip().lower()
    if formato_saida not in ("mp4", "mp3"):
        raise ValueError("formato_saida deve ser 'mp4' ou 'mp3'.")

    if formato_saida == "mp3" and shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "Para baixar em mp3 é necessário ter o ffmpeg instalado e no PATH."
        )

    output_path = os.path.abspath(output_path)

    # Se output_path for uma pasta (existente ou terminando em separador),
    # deixa o yt-dlp nomear o arquivo com o título do vídeo.
    if os.path.isdir(output_path) or output_path.endswith(os.sep):
        os.makedirs(output_path, exist_ok=True)
        template = os.path.join(output_path, "%(title)s.%(ext)s")
    else:
        pasta = os.path.dirname(output_path)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        # Remove extensão do template; o yt-dlp define a extensão final
        # (ex: .mp4) de acordo com o formato baixado/mesclado.
        raiz, _ext = os.path.splitext(output_path)
        template = raiz + ".%(ext)s"

    ffmpeg_disponivel = shutil.which("ffmpeg") is not None
    usar_merge = melhor_qualidade and ffmpeg_disponivel

    if formato_saida == "mp4" and melhor_qualidade and not ffmpeg_disponivel:
        print(
            "Aviso: ffmpeg não encontrado. Baixando um arquivo único já pronto "
            "(sem juntar vídeo+áudio separados). Instale o ffmpeg para obter a "
            "melhor qualidade possível."
        )

    if usar_merge:
        formato = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        # best[ext=mp4] evita formatos que exigiriam merge; "best" como
        # fallback caso não exista um mp4 único disponível.
        formato = "best[ext=mp4]/best"

    ydl_opts = {
        "format": formato,
        "outtmpl": template,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
    }
    if formato_saida == "mp3":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    elif usar_merge:
        ydl_opts["merge_output_format"] = "mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        caminho_final = ydl.prepare_filename(info)
        if formato_saida == "mp3":
            # O pós-processador troca a extensão original por .mp3
            return os.path.splitext(caminho_final)[0] + ".mp3"
        # Quando há merge de vídeo+áudio, a extensão final costuma virar mp4
        if ydl_opts.get("merge_output_format"):
            raiz, _ext = os.path.splitext(caminho_final)
            possivel_mp4 = raiz + ".mp4"
            if os.path.exists(possivel_mp4):
                caminho_final = possivel_mp4

    return caminho_final


if __name__ == "__main__":
    print("=== Download de vídeos do YouTube ===")

    url_arg = input("URL do vídeo: ").strip()
    while not url_arg:
        url_arg = input("A URL não pode ser vazia. URL do vídeo: ").strip()

    output_arg = input(
        "Pasta ou caminho de destino (Enter para a pasta atual): "
    ).strip().strip('"')
    if not output_arg:
        output_arg = os.getcwd() + os.sep

    print("O que deseja baixar?")
    print("  [1] Vídeo completo (mp4)")
    print("  [2] Somente o áudio (mp3)")
    escolha = input("Escolha 1 ou 2 (Enter = 1): ").strip()
    while escolha not in ("", "1", "2"):
        escolha = input("Opção inválida. Escolha 1 ou 2: ").strip()
    formato_arg = "mp3" if escolha == "2" else "mp4"

    try:
        caminho = baixar_video_youtube(url_arg, output_arg, formato_saida=formato_arg)
        print(f"Vídeo baixado com sucesso em: {caminho}")
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        sys.exit(1)