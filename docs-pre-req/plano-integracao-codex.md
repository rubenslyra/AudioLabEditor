# Plano de integracao Codex - infraestrutura portavel

Data: 2026-06-09
Responsavel: codex / tty0
Branch: `fix/self-contained-deps`

## Objetivo

Criar a base do novo `AudioLabEditor/` como aplicacao mesclada entre:

- `rl-media-studio-v1_6/`: GUI desktop, captura de midia, edicao rapida e compliance.
- `MVP-AudioStemLab/`: separacao de stems por IA.

O primeiro incremento foca a fase 0: portabilidade, duplo clique e resolucao de dependencias sem depender de `PATH`, variaveis de ambiente ou diretorios globais no executavel final.

## Dependencias obrigatorias

### Base

- Python 3.11+
- CustomTkinter
- yt-dlp como pacote Python embarcado
- ffmpeg e ffprobe como binarios dentro do bundle

### Perfil `ai`

- Demucs
- faster-whisper
- edge-tts
- cache local de modelos ao lado do executavel ou em pasta local da aplicacao

### Perfil `full`

- Dependencias do perfil `ai`
- PaddleOCR/PaddlePaddle para OCR

## Path resolution

Regra alvo:

- Em desenvolvimento, permitir fallback para ferramentas no sistema para facilitar testes locais.
- Em build congelado, procurar somente em caminhos relativos ao executavel:
  - diretorio do executavel;
  - `_internal/`;
  - `_internal/bin/`;
  - `bin/`;
  - `lib/`;
  - `tools/bin/`;
  - `ffmpeg/bin/`.

Nao usar `PATH`, `APPDATA`, `XDG_*` ou `~` como fonte primaria para localizar binarios no executavel final.

## Startup doctor

Antes de abrir a janela principal:

1. Verificar `ffmpeg` e `ffprobe`.
2. Verificar `yt-dlp`.
3. No perfil `ai`, verificar `demucs`, `faster-whisper` e `edge-tts`.
4. No perfil `full`, verificar tambem `paddleocr`.
5. Se faltar algo, mostrar `messagebox.showerror` com lista objetiva de itens ausentes.
6. Encerrar com codigo diferente de zero, sem crash silencioso.

## Launchers

### Linux

- `run-linux.sh` resolve o diretorio real do script com `dirname`.
- Se encontrar binario empacotado no mesmo diretorio ou no diretorio pai, executa diretamente.
- Caso contrario, usa `PYTHONPATH=src` e roda o entrypoint de desenvolvimento.
- `.desktop` usa comando sem terminal.

### Windows

- `run-windows.bat` usa `%~dp0` para resolver o diretorio do script.
- Se encontrar `AudioLabEditor.exe`, inicia por duplo clique com `start`.
- Caso contrario, roda o entrypoint de desenvolvimento.

### macOS

- A estrategia final deve gerar `.app` via PyInstaller.
- O doctor deve continuar funcionando usando `sys._MEIPASS` e diretorio do executavel como ancoras.

## PyInstaller

O spec inicial `AudioLabEditor/scripts/AudioLabEditor.spec` deve:

- incluir `ffmpeg` e `ffprobe` via variaveis explicitas ou `shutil.which` no momento do build;
- coletar submodulos e metadados de `yt_dlp`;
- coletar `demucs`, `faster_whisper` e `edge_tts` nos perfis `ai/full`;
- coletar `paddleocr` e `paddle` no perfil `full`;
- gerar bundle com `console=False`.

## Criterios de aceite da fase 0

- `AudioLabEditor/` existe com camadas `presentation`, `application`, `domain` e `infrastructure`.
- `docs-pre-req/plano-integracao-codex.md` documenta a estrategia.
- Startup doctor e path resolver estao implementados.
- Launchers `.sh`, `.bat` e `.desktop` existem.
- Em modo congelado, o resolver nao usa `PATH`.
- O projeto compila com `compileall`.
- Mudancas commitadas com Conventional Commit.

## Proximos passos

- Integrar o servico de stems do `MVP-AudioStemLab` ao `AudioLabEditor/src/application`.
- Integrar captura de midia do `rl-media-studio-v1_6` via adapters em `infrastructure`.
- Criar job runner comum com progresso e cancelamento.
- Definir modelo de projeto e organizacao de saida junto ao trabalho do tty1.
