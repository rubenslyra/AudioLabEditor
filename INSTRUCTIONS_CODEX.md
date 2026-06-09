# Instruções para codex (tty0)

## Contexto

Você é o Agente codex no terminal tty0. Deve **criar o novo projeto da aplicação
mesclada** em uma pasta chamada `AudioLabEditor/` (ao lado de `rl-media-studio-v1_6/`
e `MVP-AudioStemLab/`), e registrar o plano em `docs-pre-req/`.

## Sua Branch

**`fix/self-contained-deps`** — criada a partir de `opencode`.

## Tarefas

### 0. Criar estrutura do novo projeto

```
AudioLabEditor/          # nova pasta, nome da aplicacao alvo
├── src/
│   ├── presentation/    # GUI (CustomTkinter)
│   ├── application/     # use cases
│   ├── domain/          # entidades
│   └── infrastructure/  # ffmpeg, yt-dlp, demucs, storage
├── tests/
├── docs/
│   └── pre-req/         # novo arquivo nesta pasta
├── scripts/
└── pyproject.toml
```

### 1. Criar docs-pre-req/plano-integracao-codex.md

Registrar o plano de integração: dependências, launchers, path resolution.

### 2. Empacotar TODAS as dependências (PyInstaller)

- yt-dlp, ffmpeg/ffprobe, Demucs embarcados
- Nada em PATH/ambiente — tudo relativo ao executável

### 3. Launchers para duplo clique

- .sh / .bat / .desktop — caminhos relativos ao diretório do script
- Sem dependência de terminal — erros viram messagebox

### 4. Startup doctor

- Verificar yt-dlp, ffmpeg, Demucs na inicialização
- Se faltar, mostrar dialog claro — nunca crashar

---

## Commites

```
codex/
├── INSTRUCTIONS_CODEX.md        (instrucoes)
├── docs-pre-req/
│   └── plano-integracao-codex.md (seu plano)
└── AudioLabEditor/              (novo projeto)
    ├── src/...
    ├── scripts/...
    └── pyproject.toml
```

Commite na branch `fix/self-contained-deps`.
