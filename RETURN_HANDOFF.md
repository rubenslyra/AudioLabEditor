# Handoff de Retorno — AudioLabEditor

## Instruções para retomar o desenvolvimento

---

## 1. Topologia

| Terminal | Ferramenta | Branch | Diretório |
|----------|-----------|--------|-----------|
| **tty0** | opencode (big-pickle) | `main` | `~/source/TestesTECNICOS/AudioLabEditor/` |

**Branch atual:** `main`
**Versão:** `1.3.0` (pyproject.toml)
**Tags:** `v1.3.0`, `v1.2.1`, `v1.2.0`, `v0.5.0`
**Latest release GitHub:** `v0.5.0` (última release criada manualmente; tags `v1.*` aguardam CI)
**Data do handoff:** 2026-06-12

---

## 2. Ao retomar

### Verificar estado

```bash
git status
git log --oneline -10
gh release list --limit 3
python3 -m pytest tests/ -v
ruff check src/ tests/
```

### Commits recentes (mais novo → mais velho)

```
02ea147 fix: comprime com xz binários >1.9GB no release (contorna limite 2GB do GitHub)
a9d1492 fix: corrige constraint julius >=0.2 (versão real no PyPI é 0.2.x)
cd65117 fix: corrige constraint dora-search >=0.1.4 (versão real no PyPI é 0.1.x)
dda4477 v1.3.0: embarca dependências AI (torch, demucs, etc.) no build PyInstaller
55f3b90 feat: embarcar dependencias de IA (torch, demucs, faster-whisper, edge-tts) no build PyInstaller
8d81dd3 chore: remove docs/wiki/ (moved to GitHub Wiki)
94dbdb3 docs: add wiki content
c98126f fix: move _validate_environment para depois de start_btn/ env_status_label em stem_tab
dd0d3d5 bump: version 0.5.0 -> 1.2.0
d3d1df3 fix: remove sys.executable fallback em _check_bundled_or_system
17dcca6 fix: splash visibility and tab safety guards
4c80662 fix: splash visivel (remove withdraw), abas sincronas (sem thread, sem loop)
a90e259 fix: tkinter thread-safety — todo widget ops na main thread via after()
9b8d0df feat: runtime downloader com curl/wget, ffmpeg estatico embarcado, faster-whisper + edge-tts no build
c7a3dd0 fix: remove venv/pip runtime — executavel auto-contido
11bbc25 feat: v0.5.0 — splash funcional, abas async, runtime isolado (venv), cleanup centralizado
c74b903 feat: transcricao (faster-whisper), TTS (edge-tts) e processamento em lote de stems
```

---

## 3. Estado Atual

### Build e CI/CD

| Item | Status |
|------|--------|
| PyInstaller onefile | ✅ (~132MB Linux, >1.9GB com torch/demucs embarcados) |
| CI (lint + test) 3 SOs | ✅ GitHub Actions |
| Release workflow 3 SOs | ✅ gera binários + anexa à release com gh CLI |
| Release latest | ⚠️ `v0.5.0` (tags `v1.*` não geraram release ainda) |
| Compressão xz | ✅ binários >1.9GB comprimidos com `xz -9 -T0` no release workflow |
| UPX | ✅ condicional (`sys.platform != "darwin"`) |

### Funcionalidades implementadas

| Feature | Aba | Status | Dependência |
|---------|-----|--------|-----------|
| Captura de mídia (yt-dlp) | Captura | ✅ | yt-dlp |
| Corte/Conversão de áudio | Audio | ✅ | ffmpeg |
| Separação de stems (Demucs) | Stems | ✅ | torch, demucs |
| Transcrição (faster-whisper) | Transcricao | ✅ | faster-whisper |
| Síntese de voz (edge-tts) | TTS | ✅ | edge-tts |
| Editor de vídeo | Video | ✅ | ffmpeg |

### Testes

| Suite | Resultado |
|-------|-----------|
| `ruff check src/ tests/` | ✅ 0 erros |
| `pytest tests/` | ✅ 70/70 passam (0.45s) |

### Scripts de instalação

| Script | SO | Finalidade |
|--------|----|------------|
| `scripts/install.sh` | Linux | Integração ao menu + PATH |
| `scripts/install.ps1` | Windows | Atalho Menu Iniciar + PATH |
| `scripts/install-macos.sh` | macOS | Bundle .app + /usr/local/bin |

### Screenshots (`docs/screenshots/`)

| Arquivo | Conteúdo |
|---------|----------|
| `main_window.png` | Visão geral com logo + aba Captura |
| `tab_capture.png` | Aba Captura de Mídia |
| `tab_trim.png` | Aba Corte de Áudio com waveform |
| `tab_video.png` | Aba Editor de Vídeo |
| `tab_stems.png` | Aba Separador de Stems com status IA |

> Faltam: `tab_transcription.png`, `tab_tts.png`

---

## 4. Correções realizadas (sessões v0.5.0 → v1.3.0)

### 🔴 Bugs corrigidos

| Arquivo | Problema | Correção |
|---------|----------|----------|
| `src/infrastructure/ai_runtime_manager.py` | `python3` hardcoded em frozen builds (quebra no Windows) | `_find_system_python()` prioriza `python` no Windows |
| `src/infrastructure/demucs_adapter.py` | `python3` hardcoded em frozen builds | `_resolve_python()` detecta Windows |
| `.github/workflows/release.yml` | `mv` para mesma pasta causa erro "same file" | `cp` para `artifacts-out/` flat |
| `.github/workflows/release.yml` | Limite 2GB GitHub para assets >1.9GB | compressão `xz -9 -T0` condicional |
| `pyproject.toml` | Constraint `julius>=0.3` incompatível (real é 0.2.x) | `julius >=0.2` |
| `pyproject.toml` | Constraint `dora-search>=0.2` incompatível (real é 0.1.x) | `dora-search >=0.1.4` |

### 🟡 Melhorias

| Arquivo | Mudança |
|---------|---------|
| `scripts/AudioLabEditor.spec` | `upx=sys.platform != "darwin"`, `excludes` para torch/demucs no CI |
| `src/infrastructure/runtime_paths.py` | Linux usa `APP_NAME.lower()` em vez de hardcoded |
| `src/presentation/main.py` | Splash funcional, abas síncronas (sem loop), tkinter thread-safe via `after()` |
| `src/presentation/tabs/stem_tab.py` | `_reveal_output_dir`, `_validate_environment` movido pós-criação de widgets |

### 🆕 Funcionalidades adicionadas

| Funcionalidade | Detalhes |
|----------------|----------|
| Runtime auto-contido | Remove venv/pip — executável autocontido com ffmpeg estático embarcado |
| Runtime downloader | `curl`/`wget` para baixar runtimes sob demanda |
| torch + demucs embarcados | No build PyInstaller (`scripts/AudioLabEditor.spec`) |
| Transcrição (faster-whisper) | `WhisperSubprocessAdapter`, aba Transcricao, output SRT/TXT |
| TTS (edge-tts) | `EdgeTtsSubprocessAdapter`, aba TTS com 18 vozes |
| Lote de stems | `batch_separate_audio_use_case.py`, suporte N arquivos |
| Splash screen | Funcional, sem thread, sem loop, `after()` para tkinter |

### 📄 Documentação

| Arquivo | Mudança |
|---------|---------|
| `README.md` | Screenshots, instruções Windows/macOS |
| `APRESENTACAO.md` | Estado atual, instalação sem AppImage |
| `docs/wiki/` → GitHub Wiki | Conteúdo migrado (Home, Instalação, Funcionalidades, FAQ) |

---

## 5. Problemas conhecidos

1. **Node.js 20 deprecated** nos runners GH Actions — precisa atualizar `actions/checkout@v5`, `actions/setup-python@v6` etc. até 2026-09-16
2. **windows-latest será redirecionado** para `windows-2025-vs2026` a partir de 2026-06-15
3. **UPX compressão mínima** (~0.02%) em binários PyInstaller — pode ser desligado
4. **`v1.3.0` sem release no GitHub** — última release é `v0.5.0` (tags `v1.*` foram criadas localmente mas CI não rodou)
5. **Faltam screenshots** das abas Transcricao e TTS em `docs/screenshots/`

---

## 6. Próximos passos sugeridos

### Imediatos
- [ ] Fazer release `v1.3.0` — `git push origin v1.3.0` para acionar CI
- [ ] Adicionar screenshots: `tab_transcription.png`, `tab_tts.png`
- [ ] Testar integração real faster-whisper e edge-tts (requer GPU/Internet)

### Curto prazo
- [ ] Atualizar actions (checkout@v5, setup-python@v6) para Node.js 24
- [ ] Migrar `windows-latest` → `windows-2025` no matrix

### Médio prazo
- [ ] OCR em vídeos (PaddleOCR)
- [ ] Versão portátil (zero instalação) para Windows/macOS

---

## 7. Comandos rápidos

```bash
# Executar GUI
PYTHONPATH=src python3 src/presentation/main.py

# Build
python3 -m PyInstaller scripts/AudioLabEditor.spec --log-level WARN

# Testes
python3 -m pytest tests/ -v

# Lint
ruff check src/ tests/

# Criar nova release (push tag → aciona CI)
git tag v1.3.0
git push origin v1.3.0

# Ver útimos commits
git log --oneline -10

# Ver binary buildado
ls -lh dist/AudioLabEditor
file dist/AudioLabEditor
```
