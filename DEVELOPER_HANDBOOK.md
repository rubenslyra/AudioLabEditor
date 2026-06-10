# Manual do Desenvolvedor — AudioLabEditor

Para continuar o desenvolvimento manualmente sem os agentes.

---

## 1. Ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate

# Instalar core + dev
pip install -e ".[dev]"

# Opcional: IA (Demucs, torch, etc.)
pip install -e ".[ai]"

# Build com PyInstaller
pip install pyinstaller
```

**Dependências externas:** ffmpeg, ffprobe (no PATH ou junto ao executável)

---

## 2. Onde está o quê

```
AudioLabEditor/
├── src/
│   ├── presentation/              → GUI (CustomTkinter)
│   │   ├── main.py                → entrypoint
│   │   ├── tabs/                  → abas da interface
│   │   │   ├── capture_tab.py     → captura de midia
│   │   │   ├── stem_tab.py        → separador de stems
│   │   │   ├── trim_tab.py        → editor de audio
│   │   │   └── video_editor_tab.py→ editor de video
│   │   └── assets/                → logo, icones
│   ├── application/               → use cases
│   │   ├── bootstrap.py           → validacao de startup
│   │   ├── capture_media_use_case.py
│   │   ├── separate_audio_use_case.py
│   │   └── output_organizer.py
│   ├── domain/                    → entidades, interfaces
│   │   ├── entities.py
│   │   ├── interfaces.py
│   │   └── dependencies.py
│   └── infrastructure/            → adaptadores
│       ├── runtime_paths.py       → resolucao de paths
│       ├── startup_doctor.py      → verificacao de deps
│       ├── ffmpeg_adapter.py      → processamento audiovisual
│       ├── demucs_adapter.py      → separacao de stems
│       ├── ai_runtime_manager.py  → gerenciamento de IA
│       ├── downloader_adapter.py  → yt-dlp wrapper
│       ├── settings_store.py      → persistencia JSON
│       └── path_config.py         → config de diretorios
├── demucs/                        → codigo fonte do Demucs v4 (vendado)
├── scripts/                       → build, instalacao
│   ├── AudioLabEditor.spec        → config PyInstaller
│   ├── install.sh                 → instalador Linux
│   ├── install.ps1                → instalador Windows
│   └── install-macos.sh           → instalador macOS
├── docs/
│   └── screenshots/               → capturas de tela
├── tests/                         → testes pytest
└── .github/workflows/
    ├── ci.yml                     → CI (lint + test)
    └── release.yml                → build + release nos 3 SOs
```

---

## 3. Comandos essenciais

```bash
# Executar a GUI
cd AudioLabEditor
PYTHONPATH=src python3 src/presentation/main.py

# Verificar sintaxe
python3 -m compileall -q src/

# Rodar testes
python3 -m pytest tests/ -v

# Lint
ruff check src/ tests/

# Build single-file (PyInstaller)
python3 -m PyInstaller scripts/AudioLabEditor.spec --log-level WARN

# Executar binário compilado
./dist/AudioLabEditor
```

---

## 4. Fluxo de trabalho

```bash
git checkout -b feat/minha-feature
# ... desenvolver ...
ruff check src/ tests/
python3 -m pytest tests/ -v
git add -A && git commit -m "feat: descricao"
# Abrir PR para revisao
```

### Convenção de commits

| Prefixo | Uso |
|---------|-----|
| `feat:` | nova funcionalidade |
| `fix:` | correcao de bug |
| `refactor:` | refatoracao sem mudar comportamento |
| `chore:` | tarefa de manutencao |
| `docs:` | documentacao |
| `gate:` | marco de teste / aprovacao |

---

## 5. Arquitetura (Clean Architecture)

```
presentation/  (CustomTkinter)  →  application/  (use cases)  →  domain/  (entidades)
                                      ↓
                               infrastructure/  (ffmpeg, storage, demucs, yt-dlp)
```

**Regras:**
- UI nunca chama infraestrutura diretamente — sempre via use case
- Domínio não importa CustomTkinter, FFmpeg, nem storage
- Adaptadores de infraestrutura implementam portas (interfaces)
- Platform-specific code isolado em `infrastructure/runtime_paths.py`

---

## 6. Próximos passos

### Fase atual — Consolidação multiplataforma (✅ concluída)

| Item | Status |
|------|--------|
| Infraestrutura portável (paths, runtime) | ✅ |
| Output organization (dest/proj/tipo-timestamp) | ✅ |
| CI/CD nos 3 SOs (lint + test + build) | ✅ |
| Build PyInstaller onefile | ✅ |
| Scripts de instalação (Linux, Windows, macOS) | ✅ |
| Hardcoded `python3` corrigido (Windows) | ✅ |
| UPX condicional por plataforma | ✅ |

### Próximas features

1. **Transcrição** — integrar faster-whisper na interface
2. **Voz sintética** — integrar edge-tts
3. **OCR** — reconhecimento de texto em vídeos
4. **Processamento em lote**
5. **Versão portátil** (zero instalação)

Ver `AudioLabEditor.md` para o plano completo de fases.

---

## 7. LGPD — Checklist rapido

- [x] Nenhum dado pessoal coletado sem consentimento
- [x] Nenhuma telemetria ou envio de dados
- [x] Logs sem caminhos absolutos do usuario
- [x] Cache local com politica de retencao
- [x] Compliance = revisao assistida, nao decisao automatica

---

## 8. ISO 25010 — Criterios de qualidade

| Criterio | Como verificar | Status |
|----------|---------------|--------|
| Compilacao | `python -m compileall -q src/` | ✅ |
| Testes | `pytest tests/ -v` (32 testes) | ✅ |
| Lint | `ruff check src/ tests/` | ✅ |
| Seguranca | `shell=False` em todo subprocess | ✅ |
| Manutencao | Nenhum arquivo > 500 linhas | ✅ |
| Portabilidade | CI roda nos 3 SOs (Linux, Windows, macOS) | ✅ |
| Usabilidade | Interface grafica com feedback visual | ✅ |
