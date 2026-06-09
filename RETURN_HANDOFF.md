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

Resultado esperado:

| Agente | Branch | Status esperado |
|--------|--------|----------------|
| codex | `fix/self-contained-deps` | ⏳ pode ter commits pendentes |
| opencode (tty1) | `feat-output-organization` | ⏳ pode ter commits pendentes |
| coordenador | `feat/path-config-ui` | ✅ concluído (marco-zero tagueado) |

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

## 3. Estado Atual (marco-zero)

**Tag:** `marco-zero`  
**Commit:** `b6e7c08`  
**Data:** 2026-06-09 13:48 UTC

```
Top-level:  8 arquivos de coordenação
RLMS repo:  7436947 (stem tab + path config + cleanup)
AudioLab:   7bfa410 (original, untouched)
Peso total: 67MB (source-only)
```

### Arquivos de coordenação criados

| Arquivo | Propósito |
|---------|-----------|
| `AudioLabEditor.md` | Plano base com 7 fases |
| `TESTING_PROTOCOL.md` | Gates ISO 25010 / IEC / LGPD |
| `INSTRUCTIONS_CODEX.md` | Instruções para codex (tty0) |
| `INSTRUCTIONS_TTY1.md` | Instruções para opencode (tty1) |
| `DEVELOPER_HANDBOOK.md` | Manual para desenvolvimento manual |
| `MARCO_ZERO.md` | Checkpoint do estado inicial |
| `scripts/monitor.py` | Daemon de monitoramento |
| `scripts/monitor.sh` | Wrapper start/stop/status |

### Código entregue (em rl-media-studio-v1_6/)

| Arquivo | O que faz |
|---------|-----------|
| `src/rlmedia/core/storage/path_config.py` | Persistência de paths origem/destino |
| `src/rlmedia/core/media/stem_service.py` | Serviço Demucs com progresso |
| `src/rlmedia/ui/tabs/stem_tab.py` | Aba "Separador de Stems" na GUI |
| `src/rlmedia/ui/navigation.py` | +1 tab label |
| `src/rlmedia/ui/main_window.py` | Import + instância do StemTab |

---

## 4. Próximas tarefas (Fase 0 e 1)

### Fase 0 — codex (tty0) `fix/self-contained-deps`

- [ ] Criar pasta `AudioLabEditor/` (novo projeto alvo)
- [ ] Criar `docs-pre-req/plano-integracao-codex.md`
- [ ] Embutir yt-dlp, ffmpeg, Demucs no PyInstaller
- [ ] Launchers .sh/.bat/.desktop para duplo clique
- [ ] Startup doctor

### Fase 1 — opencode (tty1) `feat-output-organization`

- [ ] Criar pasta `AudioLabEditor/` (novo projeto alvo)
- [ ] Criar `docs-pre-req/plano-saida-projeto-tty1.md`
- [ ] Portar PathConfig para o novo projeto
- [ ] Output: `{dest}/{projeto}/{tipo}-{timestamp}.{ext}`
- [ ] Integrar PathConfig nas abas CaptureTab, TrimTab, VideoEditorTab

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
