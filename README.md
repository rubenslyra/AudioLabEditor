# AudioLabEditor

Applied Multimedia Lab — fusão de MVP-AudioStemLab (v0.3.8) + RL Media Studio (v1.10.0-dev).

## Branches

| Branch | Agente | Foco |
|--------|--------|------|
| `opencode` | — | Base / coordenação |
| `fix/self-contained-deps` | codex (tty0) | Empacotar dependências, corrigir launchers |
| `feat/path-config-ui` | opencode (tty1) | Seletor de path, organização por projeto |

## Estrutura

```
AudioLabEditor/
├── docs-pre-req/           # Análises pré-requisito
├── MVP-AudioStemLab/       # Audio stem separation (CLI)
└── rl-media-studio-v1_6/   # Desktop multimedia studio (GUI)
```
