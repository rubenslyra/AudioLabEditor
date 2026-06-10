## AudioLab Editor

Capture, edite e separe áudio e vídeo com IA.

### Downloads

| Plataforma | Arquivo |
|---|---|
| Linux x86_64 | `audiolab-editor-linux-x86_64` |
| Windows x86_64 | `audiolab-editor-windows-x86_64.exe` |
| macOS x86_64 | `audiolab-editor-macos-x86_64` |

### Funcionalidades
- **Captura de mídia** — download de vídeo/áudio de URLs (yt-dlp)
- **Corte de áudio** — exportação em MP3, WAV, FLAC, OGG, AAC, M4A
- **Extração de áudio** — extraia áudio de vídeos
- **Separador de Stems** — isole vocais, baixo, bateria e outros instrumentos (Demucs, IA sob demanda)
- **Editor de vídeo** — corte com CRF + preset x264

### Instalação da IA
Os pacotes de IA (torch, Demucs) **não estão inclusos** no binário. Para usá-los:
1. Abra a aba **Stems**
2. Clique em **Instalar dependências**
3. O app instalará torch, Demucs e dependências via pip no Python do sistema

### Notas
- O app requer Python 3.11+ instalado no sistema para funcionalidades de IA
- FFmpeg deve estar disponível no PATH ou será baixado pelo app
