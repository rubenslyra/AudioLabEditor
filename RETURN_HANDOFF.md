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

## 3. Estado Atual (após agentes trabalharem)

**Tag base:** `marco-zero` (`b6e7c08`)  
**Data:** 2026-06-09

```
Top-level:  9 arquivos de coordenação
Peso total: ~70MB (source-only, limpo)
```

### Commits dos agentes

**codex (tty0) — `fix/self-contained-deps`:**
```
2f07815 feat(scaffold): create AudioLabEditor portable app base
```
Criou a pasta `AudioLabEditor/` com estrutura portátil.

**opencode (tty1) — `feat-output-organization`:**
```
13d753b feat(stem): add SeparateAudioUseCase, Demucs adapter, port StemTab
f95648c feat(capture): add clean architecture layers and port CaptureTab
cb9a773 feat(output): add OutputOrganizer and port PathConfig
```
Portou PathConfig, OutputOrganizer, CaptureTab e StemTab para clean arch.

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

### Fase 0 (continuação) — codex (tty0)

- [x] ~~Criar `AudioLabEditor/`~~ ✅ feito (`2f07815`)
- [ ] Criar `docs-pre-req/plano-integracao-codex.md`
- [ ] Embutir yt-dlp, ffmpeg, Demucs no PyInstaller
- [ ] Launchers .sh/.bat/.desktop para duplo clique
- [ ] Startup doctor

### Fase 1 (continuação) — opencode (tty1)

- [x] ~~Portar PathConfig~~ ✅ feito (`cb9a773`)
- [x] ~~Portar CaptureTab~~ ✅ feito (`f95648c`)
- [x] ~~Portar StemTab + SeparateAudioUseCase~~ ✅ feito (`13d753b`)
- [ ] Criar `docs-pre-req/plano-saida-projeto-tty1.md`
- [ ] Output: `{dest}/{projeto}/{tipo}-{timestamp}.{ext}`
- [ ] Integrar PathConfig no TrimTab e VideoEditorTab

---

## 5. Comandos rápidos

```bash
# Compilar tudo
python -m compileall -q rl-media-studio-v1_6/

# Executar GUI
cd rl-media-studio-v1_6 && python -m rlmedia

# Status dos branches
./scripts/monitor.sh status

# Iniciar monitor
./scripts/monitor.sh start

# Ver ultimos commits
git log --oneline -5 --all --graph
```
