# AudioLab Editor

<p align="center">
  <img src="src/presentation/assets/logo.png" alt="AudioLab Editor" width="200"/>
</p>

<p align="center">
  <strong>Capture, edite e separe áudio e vídeo com IA</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.14-blue?logo=python" alt="Python 3.14">
  <img src="https://img.shields.io/badge/platform-linux--x64-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/build-PyInstaller%206.20-orange" alt="Build">
  <img src="https://img.shields.io/badge/UI-CustomTkinter%205.2-ff69b4" alt="UI">
</p>

---

AudioLab Editor é um aplicativo desktop para **captura**, **corte**, **separação de stems** (fontes sonoras) e **transcrição** de mídia, construído com Python e CustomTkinter. Utiliza IA (Demucs) para separação de instrumentos e vocais, yt-dlp para captura de mídia online e FFmpeg para processamento audiovisual.

---

## Funcionalidades

### Captura de Mídia
- Download de vídeo/áudio de URLs (YouTube, Vimeo, etc.) via yt-dlp
- Preservação de qualidade original
- Compressão com presets (Alta / Balanceada / Compacta)
- Extração de áudio em MP3, M4A, WAV, FLAC, OGG, AAC

### Editor de Áudio
- Corte rápido com seleção de início/fim
- Exportação em MP3, WAV, FLAC, OGG, AAC, M4A
- Qualidade ajustável por formato
- Extração de áudio de arquivos de vídeo

### Editor de Vídeo
- Corte com precisão de tempo
- Presets de qualidade (CRF + preset x264)
- Formatos: MP4, MKV, AVI

### Separador de Stems (IA)
- Separação de vocais, baixo, bateria e outros instrumentos
- Modos: apenas vocais, 4 stems, 6 stems
- Formatos de saída: WAV, MP3, FLAC
- Engine: Demucs (Hybrid Transformer Demucs)
- **Sob demanda**: os pacotes de IA são instalados apenas quando o usuário opta por usar o recurso

---

## Arquitetura

```
AudioLabEditor/
├── src/
│   ├── domain/          # Entidades, interfaces, DTOs
│   ├── application/     # Casos de uso (orquestração)
│   ├── infrastructure/  # Adaptadores (FFmpeg, yt-dlp, Demucs, runtime)
│   └── presentation/    # UI CustomTkinter (abas, widgets, splash)
├── demucs/              # Código fonte do Demucs v4.1.0a2 (vendado)
├── scripts/             # Build, instalação, dev launcher
└── tests/               # Testes pytest
```

### Princípios
- **Clean Architecture**: domínio isolado, infraestrutura plugável
- **IA sob demanda**: torch, Demucs e dependências são instalados pelo próprio app, não embarcados no binário
- **Lazy loading**: módulos de IA carregados apenas quando necessários
- **Runtime detection**: `AiRuntimeManager` detecta Python, pip e pacotes do sistema

---

## Instalação

### Pré-requisitos
- **Python 3.14+** e **pip** instalados no sistema
- **FFmpeg** (`ffmpeg` e `ffprobe` disponíveis no PATH ou baixados automaticamente)
- Linux x86_64 (builds para outras plataformas em desenvolvimento)

### Via instalador (recomendado)

```bash
# Baixe o binário da última release
chmod +x audiolab-editor

# Execute diretamente
./audiolab-editor
```

### Via script de instalação

```bash
# Build + instala em ~/.local/bin
./scripts/install.sh

# Para instalar em /usr/local (requer sudo)
sudo ./scripts/install.sh --system
```

### Desenvolvimento

```bash
git clone https://github.com/rubenslyra/AudioLabEditor.git
cd AudioLabEditor

# Crie um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale dependências base
pip install -e .

# Dependências de IA (opcional, para stems)
pip install -e ".[ai]"

# Execute
python3 src/presentation/main.py
```

---

## Dependências

### Core (embarcadas no binário)

| Pacote | Versão | Função |
|---|---|---|
| Python | 3.14.4 | Runtime |
| CustomTkinter | 5.2.2 | Interface gráfica |
| Pillow | 12.2.0 | Manipulação de imagens |
| yt-dlp | 2026.03.17 | Download de mídia |
| PyInstaller | 6.20.0 | Empacotamento do binário |
| FFmpeg | 8.0.1 | Processamento audiovisual |

### IA (instaladas sob demanda via `pip install`)

| Pacote | Versão | Função |
|---|---|---|
| torch | 2.12.0 | Engine de deep learning |
| torchaudio | 2.11.0 | Processamento de áudio |
| demucs | 4.1.0a2 | Separação de fontes musicais |
| dora-search | 0.1.12 | Framework de configuração |
| julius | 0.2.8 | DSP e aumentação de áudio |
| einops | 0.8.2 | Manipulação tensorial |
| PyYAML | 6.0.3 | Parsing de configuração |
| omegaconf | 2.3.0 | Sistema de configuração |
| numpy | 2.3.5 | Computação numérica |
| tqdm | 4.68.2 | Barras de progresso |
| lameenc | 1.8.2 | Codificação MP3 |
| openunmix | 1.3.0 | Filtragem Wiener |

---

## Build

### Binário base (132 MB, sem IA)

```bash
./scripts/install.sh
```

O binário inclui apenas as funcionalidades core: captura, corte, editor de vídeo. Os recursos de IA (separação de stems) são baixados sob demanda pelo próprio aplicativo.

### Perfil IA (desenvolvimento)

```bash
AUDIO_LAB_EDITOR_PROFILE=ai python3 -m PyInstaller scripts/AudioLabEditor.spec --log-level WARN
```

---

## Testes

```bash
python3 -m pytest tests/ -v
```

---

## Estrutura de Releases

Cada release inclui:

- `audiolab-editor` — binário Linux x86_64 (core)
- `audiolab-editor-ai` — binário Linux x86_64 (com IA embarcada)
- `Source code` — zip / tar.gz

---

## Licença

MIT License

---

## Créditos

**Rubens Lyra (Rubinho Lyra)**

Desenvolvedor de software, produtor independente, músico e pesquisador criativo de Vila Velha, Espírito Santo. Atua no desenvolvimento de aplicações multiplataforma, soluções audiovisuais, automações, ferramentas educacionais e projetos voltados à interseção entre tecnologia, música, inteligência artificial e experiência do usuário.

Como desenvolvedor independente, mantém projetos open source e experimentais publicados no GitHub, explorando áreas como engenharia de software, interfaces modernas, processamento de áudio e vídeo, automação de workflows, aplicações desktop e arquitetura de sistemas multiplataforma.

Na área artística e criativa, Rubinho Lyra desenvolve trabalhos autorais como produtor musical, multi-instrumentista e compositor, unindo influências da música brasileira, R&B, Neo Soul, música instrumental, world music e música eletrônica.

Seu trabalho busca aproximar tecnologia, educação, arte e acessibilidade por meio de soluções independentes, experimentais e orientadas à comunidade.

- **Site oficial:** [https://rubinholyra.com.br](https://rubinholyra.com.br)
- **GitHub:** [https://github.com/rubenslyra](https://github.com/rubenslyra)
- **YouTube:** [Rubinho Lyra](https://youtube.com/@rubinholyra)
- **Email:** [rubens.lyra@outlook.com](mailto:rubens.lyra@outlook.com)

---

*AudioLab Editor — mergulhe no som, extraia o que importa.*
