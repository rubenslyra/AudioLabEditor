# Handoff de Retorno — AudioLabEditor

## Instruções para retomar o desenvolvimento

---

## 1. Topologia

| Terminal | Ferramenta | Branch | Diretório |
|----------|-----------|--------|-----------|
| **tty0** | opencode (big-pickle) | `main` | `~/source/TestesTECNICOS/AudioLabEditor/` |

**Branch atual:** `main` (todas as features mergidas)
**Tag atual:** `v0.3.0` (latest no GitHub)
**Data do handoff:** 2026-06-10

---

## 2. Ao retomar

### Verificar estado

```bash
cd ~/source/TestesTECNICOS/AudioLabEditor
git status
git log --oneline -5
gh release list --limit 3
python3 -m pytest tests/ -v
```

### Commits recentes (do mais novo para o mais velho)

```
40dd012 fix: copiar artifacts para diretorio flat em vez de mv para mesma pasta
eddae6e fix: rename artifacts before upload para evitar conflito de basename
56b006d docs: screenshots, readme e documentos atualizados; feat: scripts instalacao...
9e2d6e0 fix: release workflow usa gh CLI em vez de action-gh-release (401 error)
d9dac79 feat: CI/CD multiplataforma e suporte a Windows/macOS
cd4d998 feat: README profissional com shields, creditos e documentacao completa
b6a208e feat: vendar demucs como pacote local, torch como gate de IA
74f2327 refactor: remove AppImage, instalar via install.sh com desktop integration
75a7f13 refactor: startup doctor split required/optional, Demucs opcional, profile base padrao
8c62ecc refactor: PyInstaller onefile (no more _internal folder)
```

---

## 3. Estado Atual

### Build e CI/CD

| Item | Status |
|------|--------|
| PyInstaller onefile | ✅ ~132MB Linux |
| CI (lint + test) 3 SOs | ✅ GitHub Actions |
| Release workflow 3 SOs | ✅ gera binarios + anexa à release |
| Release latest | ✅ v0.3.0 com assets Linux/macOS/Windows |
| UPX | ✅ 5.0.0 instalado, condicional (`sys.platform != "darwin"`) |

### Funcionalidades implementadas

| Feature | Aba | Status | Depoisncia |
|---------|-----|--------|-----------|
| Captura de mídia (yt-dlp) | Captura | ✅ | yt-dlp |
| Corte/Conversão de áudio | Audio | ✅ | ffmpeg |
| Separação de stems (Demucs) | Stems | ✅ | torch, demucs |
| **Transcrição (faster-whisper)** | **Transcricao** | **✅ Nova** | faster-whisper |
| **Síntese de voz (edge-tts)** | **TTS** | **✅ Nova** | edge-tts |
| Editor de vídeo | Video | ✅ | ffmpeg |

### Testes

| Suite | Resultado |
|-------|-----------|
| `ruff check src/ tests/ scripts/` | ✅ 0 erros |
| `pytest tests/` | ✅ 70/70 passam (0.41s) |

### Scripts de instalação

| Script | SO | Finalidade |
|--------|----|------------|
| `scripts/install.sh` | Linux | Integracao ao menu + PATH |
| `scripts/install.ps1` | Windows | Atalho Menu Iniciar + PATH |
| `scripts/install-macos.sh` | macOS | Bundle .app + /usr/local/bin |

### Screenshots (`docs/screenshots/`)

| Arquivo | Conteudo |
|---------|----------|
| `main_window.png` | Visao geral com logo + aba Captura |
| `tab_capture.png` | Aba Captura de Midia |
| `tab_trim.png` | Aba Corte de Audio com waveform |
| `tab_video.png` | Aba Editor de Video |
| `tab_stems.png` | Aba Separador de Stems com status IA |

---

## 4. Correções realizadas nesta sessão

### 🔴 Bugs corrigidos

| Arquivo | Problema | Correção |
|---------|----------|----------|
| `src/infrastructure/ai_runtime_manager.py` | `python3` hardcoded em frozen builds (quebra no Windows) | `_find_system_python()` prioriza `python` no Windows |
| `src/infrastructure/demucs_adapter.py` | `python3` hardcoded em frozen builds | `_resolve_python()` detecta Windows (`python` → `python3` → `py`) |
| `scripts/AudioLabEditor.spec` | `upx=True` quebra no macOS | `upx=sys.platform != "darwin"` |
| `.github/workflows/release.yml` | `mv` para mesma pasta causa erro "same file" | `cp` para `artifacts-out/` flat |

### 🟡 Melhorias

| Arquivo | Mudança |
|---------|---------|
| `src/infrastructure/runtime_paths.py` | Linux usa `APP_NAME.lower()` em vez de `"audiolabeditor"` hardcoded |
| `.github/workflows/release.yml` | Renomeacao de artifacts com nome unico por plataforma |
| `src/presentation/tabs/stem_tab.py` | `_reveal_file` → `_reveal_output_dir` (nomenclatura) |

### 📄 Documentação

| Arquivo | Mudança |
|---------|---------|
| `README.md` | Seção de Screenshots + instruções Windows/macOS |
| `APRESENTACAO.md` | Screenshot, estado atual reescrito, instalação sem AppImage |
| `DEVELOPER_HANDBOOK.md` | Estrutura de diretórios real, comandos, checkboxes preenchidos |

### 🆕 Novas funcionalidades

| Arquivo | Descrição |
|---------|-----------|
| `src/domain/interfaces.py` | `TranscriptionPort`, `TtsPort` + requests/results; `BatchStemResult` |
| `src/domain/entities.py` | `MediaType.TRANSCRIPTION/TTS`, `OutputCategory.TRANSCRIPTION/TTS` |
| `src/infrastructure/whisper_adapter.py` | `WhisperSubprocessAdapter` — transcrição via faster-whisper |
| `src/infrastructure/edge_tts_adapter.py` | `EdgeTtsSubprocessAdapter` — síntese de voz via edge-tts |
| `src/application/transcribe_audio_use_case.py` | Use case de transcrição |
| `src/application/generate_tts_use_case.py` | Use case de TTS |
| `src/application/batch_separate_audio_use_case.py` | Use case de lote de stems (N arquivos) |
| `src/presentation/tabs/transcription_tab.py` | Aba "Transcricao" com detector de runtime, install, SRT/TXT output |
| `src/presentation/tabs/tts_tab.py` | Aba "TTS" com 18 vozes, seletor de voz, texto multilinha |
| `src/presentation/tabs/stem_tab.py` | Refatorado: suporte a múltiplos arquivos + processamento em lote |
| `src/presentation/main.py` | Registro das abas "Transcricao" e "TTS" no seletor |
| `scripts/AudioLabEditor.spec` | hiddenimports atualizados com todos os novos módulos |
| `pyproject.toml` | Adicionado `pytest-timeout` às dependências dev |
| `tests/test_ai_modules.py` | 38 novos testes (domínio, adapters, use cases, lote) |
| `tests/test_build_configuration.py` | Verificação dos novos hiddenimports no spec |
| `RETURN_HANDOFF.md` | Atualizado com novo estado |

---

## 5. Problemas conhecidos

1. **Node.js 20 deprecated** nos runners do GH Actions — aviso nas annotations, precisa atualizar para `actions/checkout@v5`, `actions/setup-python@v6` etc. até 2026-09-16
2. **windows-latest será redirecionado** para `windows-2025-vs2026` a partir de 2026-06-15
3. **UPX compressão mínima** (~0.02%) em binários PyInstaller — pode ser desligado sem impacto

---

## 6. Problemas corrigidos nesta sessão

| Problema | Correção |
|----------|----------|
| CI quebra com `--timeout=30` (plugin ausente) | `pytest-timeout>=2` adicionado às dev deps |
| PyInstaller build frozen não incluiria novas abas | `hiddenimports` atualizados no `.spec` |
| Spec sem verificação dos novos módulos | Teste `test_pyinstaller_spec_includes_core_packages` ampliado |

## 7. Próximos passos sugeridos

### Próximos
- [ ] Adicionar screenshots das abas Transcricao, TTS e lote de stems
- [ ] Testar integração real com faster-whisper e edge-tts (requer GPU/Internet)
- [ ] Fazer release `v0.4.0` com as novas funcionalidades

### Médio prazo
- [ ] OCR em vídeos (PaddleOCR)
- [ ] Versão portátil (zero instalação) para Windows/macOS
- [ ] Atualizar actions para Node.js 24

---

## 7. Comandos rápidos

```bash
# Executar GUI
cd ~/source/TestesTECNICOS/AudioLabEditor
PYTHONPATH=src python3 src/presentation/main.py

# Build
python3 -m PyInstaller scripts/AudioLabEditor.spec --log-level WARN

# Testes
python3 -m pytest tests/ -v

# Lint
ruff check src/ tests/

# Criar nova release
git tag v0.4.0
git push origin v0.4.0

# Ver ultimos commits
git log --oneline -10

# Ver binary buildado
ls -lh dist/AudioLabEditor
file dist/AudioLabEditor
```
