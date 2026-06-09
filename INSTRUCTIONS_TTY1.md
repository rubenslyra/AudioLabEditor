# Instruções para opencode (tty1)

## Contexto

Você é o Agente opencode no terminal tty1. O coordenador (tty2) concluiu a
Fase 1 e 2 do `AudioLabEditor.md` (path config + stem tab).

## Sua Branch

**`feat-output-organization`** — crie a partir de `opencode` no top-level repo,
ou a partir de `develop` em `rl-media-studio-v1_6/`.

## Tarefas

### 1. Organização de saída por projeto

Já existe um `PathConfig` em `core/storage/path_config.py` e um `StemService`
em `core/media/stem_service.py`. Verifique se a lógica de saída atende:

- `{dest}/{project_name}/` — se project_name vazio, usar "ALE"
- Arquivos nomeados como `audio-{tipo}-{YYYYMMDD_HHMMSS}.{ext}`
- Se for vídeo: `video-{tipo}-{timestamp}.{ext}`
- Se for compliance: `compliance-{tipo}-{timestamp}.{ext}`

### 2. Integrar path config nas outras abas

- `CaptureTab`: remover default `Path.home() / "Videos"` — usar o `PathConfig`
- `TrimTab`: adicionar seletor de destino com `PathConfig`
- `VideoEditorTab`: adicionar seletor de destino com `PathConfig`

### 3. Persistir paths escolhidos

`PathConfig` já persiste via `SettingsStore`. Garanta que ao reabrir o app,
os últimos paths usados apareçam (sem default na primeira execução).

### 4. Validar antes de executar

- Se path de origem não existe → messagebox, não crash
- Se path de destino não existe → oferecer para criar
- Se Demucs não está instalado → mensagem clara com instrução

## Regras

- Siga o `TESTING_PROTOCOL.md` — cada task passa por white box + black box
- Compile com `python3 -m compileall -q src/` antes de commitar
- Commite na branch `feat-output-organization`
- Após concluir, o tester (usuário) fará o black box

## Documento de Referência

`AudioLabEditor.md` — plano base consolidado com fases e critérios de aceite.
