# Plano de Integracao Codex — Infraestrutura Portavel

Data: 2026-06-09 | Responsavel: codex / tty0 | Branch: fix/self-contained-deps

## Objetivo
Empacotar todas as dependencias (yt-dlp, ffmpeg, Demucs) dentro do executavel
PyInstaller, com path resolution relocatable e startup doctor.

## Dependencias Obrigatorias
- **Base:** Python 3.11+, CustomTkinter, yt-dlp (embarcado), ffmpeg/ffprobe (binarios no bundle)
- **Perfil ai:** Demucs, faster-whisper, edge-tts
- **Perfil full:** Perfil ai + PaddleOCR/PaddlePaddle

## Path Resolution
Modo congelado: buscar apenas em caminhos relativos ao executavel:
diretorio do .exe, _internal/, _internal/bin/, bin/, tools/bin/, ffmpeg/bin/.
Nao usar PATH, APPDATA, XDG_* ou ~ como fonte primaria.

## Startup Doctor
Antes de abrir janela principal: verificar ffmpeg, ffprobe, yt-dlp, demucs
(perfil ai). Se faltar, messagebox.showerror com lista de itens ausentes.
Encerrar com codigo != 0 sem crash silencioso.

## PyInstaller Spec
AudioLabEditor.spec deve:
- Incluir ffmpeg/ffprobe via variavel explicita ou shutil.which
- Coletar submodulos e metadados de yt_dlp
- Coletar demucs, faster_whisper, edge_tts nos perfis ai/full
- Coletar paddleocr e paddle no perfil full
- console=False

## Launchers
- Linux: run-linux.sh com dirname, fallback PYTHONPATH=src
- Windows: run-windows.bat com %~dp0, fallback dev
- .desktop: sem terminal

## Criterios de Aceite (Fase 0)
- compileall ok, shell=False, <500 linhas/arquivo
- Modo congelado nao usa PATH
- Launchers funcionam por duplo clique
- Startup doctor mostra erro amigavel sem crash
- Commit com Conventional Commit
