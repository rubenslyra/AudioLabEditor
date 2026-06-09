# Plano de Organização de Saída — tty1 (opencode)

## Objetivo

Portar o `PathConfig` do `rl-media-studio-v1_6` para o novo projeto `AudioLabEditor/`
e implementar organização consistente de saída de arquivos entre todas as abas.

## Estrutura de Diretórios Alvo

```
AudioLabEditor/                    # raiz do novo projeto
├── src/
│   ├── domain/                    # entidades de domínio
│   │   └── entities.py
│   ├── application/               # use cases
│   │   └── output_organizer.py
│   ├── infrastructure/            # adapters de infraestrutura
│   │   ├── settings_store.py      # persistência JSON (portado)
│   │   └── path_config.py         # PathConfig (portado + estendido)
│   └── presentation/              # GUI futura (CustomTkinter)
│       └── __init__.py
├── tests/
│   └── test_output_organizer.py
├── docs/
│   └── pre-req/
├── scripts/
├── pyproject.toml
└── .gitignore
```

## Componentes Portados

### 1. SettingsStore (`rl-media-studio-v1_6`)
- Persistência JSON com escrita atômica via arquivo temporário
- Thread-safe com `threading.Lock`
- Salvo em `~/.config/audiolab-editor/settings.json`

### 2. PathConfig (`rl-media-studio-v1_6`)
- `source_dir` / `dest_dir` por tipo de mídia
- `build_output_path()` → `{dest}/{project_name}/{prefix}-{suffix}-{timestamp}.{ext}`

## Output Organization — Regras

| Campo | Regra |
|---|---|
| `dest` | Configurado via PathConfig, default `~/AudiolabOutput` |
| `project_name` | Se vazio, usa `"ALE"` |
| `prefix` | `audio`, `video`, `stem` conforme o tipo |
| `suffix` | Descrição curta: `trimmed`, `captured`, `vocals`, `full4` |
| `timestamp` | Formato `YYYYMMDD_HHmmSS` |
| `ext` | Extraído do output format ou do arquivo original |

Exemplos:
- `~/AudiolabOutput/MinhaMusica/audio-trimmed-20260609_143022.mp3`
- `~/AudiolabOutput/ALE/stem-vocals-20260609_143022.wav`
- `~/AudiolabOutput/ProjetoX/video-captured-20260609_143022.mp4`

## Integração com Abas

- **CaptureTab**: usa PathConfig + OutputOrganizer para salvar downloads
- **TrimTab**: usa PathConfig + OutputOrganizer para salvar cortes
- **VideoEditorTab**: usa PathConfig + OutputOrganizer para salvar renders
- **StemTab**: já usa project_name → estender com prefixo padronizado

## Commits

```
feat(infrastructure): port SettingsStore and PathConfig from rl-media-studio
feat(output): create OutputOrganizer service with standardized naming
feat(presentation): integrate PathConfig into CaptureTab, TrimTab, VideoEditorTab
```
