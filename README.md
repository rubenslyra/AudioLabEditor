# AudioLab Editor

Applied Multimedia Lab — fusão de MVP-AudioStemLab (v0.3.8) + RL Media Studio (v1.10.0-dev).

Aplicativo desktop para captura, edição e separação de áudio/vídeo com IA.

## Instalação

### Usuários Linux

```bash
# 1. Clone o repositório
git clone https://github.com/anomalyco/audiolab-editor
cd audiolab-editor

# 2. Instale (build + deploy)
./scripts/install.sh

# 3. Pronto! Procure por "AudioLab Editor" no menu
#    Ou execute no terminal:
audiolab-editor
```

### Usuários avançados (desenvolvimento)

```bash
# Rodar direto do código-fonte
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
./scripts/audiolab-editor
```

### Perfis de build

| Profile | Dependências | Tamanho |
|---------|-------------|---------|
| `base` (padrão) | customtkinter, pillow, yt-dlp | ~132 MB |
| `ai` | + demucs, faster-whisper, edge-tts, torch | ~4+ GB |
| `full` | + paddleocr, paddlepaddle | ~5+ GB |

```bash
AUDIO_LAB_EDITOR_PROFILE=ai ./scripts/install.sh
```

## Funcionalidades

- **Captura de mídia** — Baixa vídeo/áudio de URLs (YouTube, etc.)
- **Corte de áudio** — Apara arquivos com export MP3
- **Separação de stems** — IA para isolar vocais, bateria, baixo (Demucs)
- **Edição de vídeo** — Corte com presets de qualidade

## Desinstalação

```bash
./scripts/uninstall.sh
```

## Licença

MIT
