# Handoff de Retorno — AudioLabEditor

## Instruções para retomar o desenvolvimento

---

## 1. Topologia dos Terminais

| Terminal | Aplicação | Branch | Diretório |
|----------|-----------|--------|-----------|
| **tty0** (Terminator) | codex | `fix/self-contained-deps` | `~/source/TestesTECNICOS/AudioLabEditor/` |
| **tty1** (Terminator) | opencode | `feat-output-organization` | `~/source/TestesTECNICOS/AudioLabEditor/` |
| **tty2** (bash normal) | opencode (coordenação) | `feat/path-config-ui` | `~/source/TestesTECNICOS/AudioLabEditor/` |

---

## 2. Ao retomar

### 2.1 Iniciar o monitor

```bash
# No tty2 (coordenação):
cd ~/source/TestesTECNICOS/AudioLabEditor
./scripts/monitor.sh start
```

### 2.2 Verificar branches

```bash
./scripts/monitor.sh status
```

Resultado esperado (atualizado em 2026-06-09):

| Agente | Branch | Status | Último commit |
|--------|--------|--------|---------------|
| codex (tty0) | `fix/self-contained-deps` | ✅ trabalhou | `2f07815` — criou `AudioLabEditor/` base |
| opencode (tty1) | `feat-output-organization` | ✅ trabalhou | `13d753b` — portou stems com clean arch |
| coordenador | `feat/path-config-ui` | ✅ coordenação | `42a175b` — handoff document |

### 2.3 Se houver novos commits (agentes trabalharam)

O monitor emite alertas. Seguir o `TESTING_PROTOCOL.md`:

1. **White box:** `python -m compileall -q .`
2. **Black box:** tester (você) valida a funcionalidade
3. **Gate:** relatório → aprovado → merge

### 2.4 Se NÃO houver novos commits (agentes não trabalharam)

```bash
# tty0: reenviar ordem ao codex
echo "cat INSTRUCTIONS_CODEX.md && comecar" > /dev/pts/0

# tty1: reenviar ordem ao opencode
echo "cat INSTRUCTIONS_TTY1.md && comecar" > /dev/pts/1
```

Ou, se os terminais foram fechados:

```bash
# Abrir Terminator com:
terminator --new-tab -e "codex" &
terminator --new-tab -e "opencode" &
```

E manualmente executar em cada um:

**tty0 (codex):**
```bash
cd ~/source/TestesTECNICOS/AudioLabEditor
git checkout fix/self-contained-deps
cat INSTRUCTIONS_CODEX.md
```

**tty1 (opencode):**
```bash
cd ~/source/TestesTECNICOS/AudioLabEditor
git checkout feat-output-organization
cat INSTRUCTIONS_TTY1.md
```

---

## 3. Estado Atual (após merge + white box)

**Branch coordenador (merged):** `feat/path-config-ui`  
**Data:** 2026-06-09

```
Merge completo:
├── código codex:  PyInstaller spec, startup doctor, runtime_paths, bootstrap, launchers
├── código opencode: PathConfig, OutputOrganizer, CaptureTab, StemTab, TrimTab, VideoEditorTab
├── pyproject.toml: deps unificadas, ruff/pytest config
└── tests/  → 10/10 passam ✅
```

### White Box Gate ✅

| Critério | Resultado |
|----------|-----------|
| `compileall -q src/` | ✅ 0 erros |
| `ruff check src/` | ✅ 0 erros |
| `shell=True` | ✅ 0 ocorrências |
| `<500 linhas/arquivo src/` | ✅ max `254` linhas |
| Testes | ✅ 10/10 passam |
| GUI smoke test | ✅ "Tabs rendered successfully" |
| subprocess `shell=False` | ✅ padrão seguro |

### Commits no `feat/path-config-ui`

```
92fc67b docs: update return handoff with real agent progress
42a175b docs: add return handoff document
d481502 feat(output): add OutputOrganizer and port PathConfig
...
```

### Arquivos de coordenação

| Arquivo | Propósito |
|---------|-----------|
| `AudioLabEditor.md` | Plano base com 7 fases |
| `TESTING_PROTOCOL.md` | Gates ISO 25010 / IEC / LGPD |
| `INSTRUCTIONS_CODEX.md` | Instruções para codex (tty0) |
| `INSTRUCTIONS_TTY1.md` | Instruções para opencode (tty1) |
| `DEVELOPER_HANDBOOK.md` | Manual para desenvolvimento manual |
| `RETURN_HANDOFF.md` | Este documento — handoff de retorno |
| `MARCO_ZERO.md` | Checkpoint do estado inicial |
| `scripts/monitor.py` | Daemon de monitoramento |
| `scripts/monitor.sh` | Wrapper start/stop/status |

---

## 4. Próximas tarefas

### Fase 0 (continuação) — codex (tty0) em `fix/self-contained-deps`

- [x] ~~Criar `AudioLabEditor/` base~~ ✅ feito
- [x] ~~Startup doctor~~ ✅ feito (merged)
- [x] ~~Launchers .sh/.bat/.desktop~~ ✅ feito (merged)
- [x] ~~PyInstaller spec~~ ✅ feito (merged)
- [x] ~~runtime_paths relocatable~~ ✅ feito (merged)
- [ ] **Criar** `docs-pre-req/plano-integracao-codex.md`
- [ ] **Embutir yt-dlp, ffmpeg, Demucs no PyInstaller** — spec precisa das dependências reais
- [ ] **Fase 0.5 Gate:** tester executa com duplo clique sem erro

### Fase 1 (continuação) — opencode (tty1) em `feat-output-organization`

- [x] ~~Portar PathConfig~~ ✅ feito (merged)
- [x] ~~Portar CaptureTab~~ ✅ feito (merged)
- [x] ~~Portar StemTab + SeparateAudioUseCase~~ ✅ feito (merged)
- [x] ~~Portar TrimTab~~ ✅ feito (merged)
- [x] ~~Portar VideoEditorTab~~ ✅ feito (merged)
- [x] ~~OutputOrganizer~~ ✅ feito (merged)
- [x] ~~Output: `{dest}/{projeto}/{tipo}-{timestamp}.{ext}`~~ ✅ feito
- [x] ~~PathConfig em todas as 4 abas~~ ✅ feito
- [ ] **Criar** `docs-pre-req/plano-saida-projeto-tty1.md`
- [ ] **Fase 1.5 Gate:** tester abre app, configura paths, gera stem

### Próximo marco — Black Box Gate

Após agents completarem tarefas acima, coordenador:
1. Verifica novos commits no monitor
2. Executa white box novamente
3. Tester valida black box (checklist abaixo)
4. Aprova → merge para `opencode`

**Black Box Checklist:**
- [ ] 4 abas renderizadas (Capturar, Stems, Cortar, Editor)
- [ ] Browse source + dest sem paths default
- [ ] Output folder criado em `{dest}/{projeto}/audio-stem-{modo}-{timestamp}/`
- [ ] Janela redimensiona sem travamentos
- [ ] Startup Doctor avisa se ffmpeg faltar
- [ ] shell=False verificado por auditoria de código

---

## 5. Comandos rápidos

```bash
# Compilar tudo
python -m compileall -q AudioLabEditor/src/

# Executar GUI (após merge)
cd AudioLabEditor && python -m presentation.main

# Status dos branches
./scripts/monitor.sh status

# Iniciar monitor
./scripts/monitor.sh start

# Ver ultimos commits
git log --oneline -5 --all --graph
```
