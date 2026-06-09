# Instruções para opencode (tty1)

## Contexto

Você é o Agente opencode no terminal tty1. Deve **criar o novo projeto da aplicação
mesclada** em uma pasta chamada `AudioLabEditor/` (ao lado de `rl-media-studio-v1_6/`
e `MVP-AudioStemLab/`), e registrar o plano em `docs-pre-req/`.

## Sua Branch

**`feat-output-organization`** — crie a partir de `opencode`.

## Tarefas

### 0. Criar estrutura do novo projeto

```
AudioLabEditor/          # nova pasta, nome da aplicacao alvo
├── src/
│   ├── presentation/    # GUI (CustomTkinter)
│   ├── application/     # use cases
│   ├── domain/          # entidades
│   └── infrastructure/  # storage, paths
├── tests/
├── docs/
│   └── pre-req/         # novo arquivo nesta pasta
├── scripts/
└── pyproject.toml
```

### 1. Criar docs-pre-req/plano-saida-projeto-tty1.md

Registrar o plano: organização de saída, path config, nomeação de arquivos.

### 2. PathConfig no novo projeto

Portar `PathConfig` do `rl-media-studio-v1_6/` para o novo `AudioLabEditor/src/infrastructure/`.

### 3. Output organization

- `{dest}/{project_name}/` (se vazio, "ALE")
- Arquivos: `audio-{tipo}-{timestamp}.{ext}` / `video-{tipo}-{timestamp}.{ext}`

### 4. Integrar PathConfig nas abas

- CaptureTab, TrimTab, VideoEditorTab — sem default paths
- Usar PathConfig como fonte única

---

Commite na branch `feat-output-organization`.
