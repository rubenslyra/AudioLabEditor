# Manual do Desenvolvedor — AudioLabEditor

Para continuar o desenvolvimento manualmente sem os agentes.

---

## 1. Ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install customtkinter Pillow yt-dlp demucs torch rich
# Ou instalar perfil completo:
pip install -r rl-media-studio-v1_6/requirements.txt
pip install -r MVP-AudioStemLab/requirements.txt
```

**Dependências externas:** ffmpeg, ffprobe (no PATH ou junto ao executável)

---

## 2. Onde está o quê

```
AudioLabEditor/                    → projeto alvo (será criado pelos agentes)
├── src/
│   ├── presentation/              → GUI (CustomTkinter)
│   ├── application/               → use cases
│   ├── domain/                    → entidades
│   └── infrastructure/            → ffmpeg, storage, demucs

rl-media-studio-v1_6/              → base GUI existente (CustomTkinter)
├── src/rlmedia/
│   ├── ui/tabs/                   → abas da interface
│   │   ├── capture_tab.py         → captura de midia
│   │   ├── stem_tab.py            → separador de stems (JA CRIADO)
│   │   ├── trim_tab.py            → editor de audio
│   │   ├── video_editor_tab.py    → editor de video (~1968 linhas)
│   │   └── credits_tab.py         → creditos
│   ├── core/media/                → servicos de midia
│   │   ├── stem_service.py        → separacao Demucs (JA CRIADO)
│   │   ├── capture_service.py     → captura por URL
│   │   └── ffmpeg_service.py      → comandos ffmpeg
│   ├── core/storage/              → persistencia
│   │   ├── settings_store.py      → JSON settings (thread-safe)
│   │   ├── path_config.py         → config de paths (JA CRIADO)
│   │   └── history_store.py       → historico de operacoes
│   └── config/paths.py            → resolucao de paths

MVP-AudioStemLab/                  → CLI de separacao de stems (Demucs)
├── core/separator.py              → engine Demucs via subprocess
├── core/file_manager.py           → gerenciamento de arquivos
├── app.py                         → entrypoint CLI
└── requirements.txt               → demucs, torch, rich, yt-dlp

docs-pre-req/                      → analises pre-requisito
├── analise-audiolab-mvp.md
├── rl-media-studio-v1_6-analysis-report.md
├── plano-integracao-codex.md      → (sera criado por codex)
└── plano-saida-projeto-tty1.md    → (sera criado por tty1)
```

---

## 3. Comandos essenciais

```bash
# Executar a GUI (rl-media-studio-v1_6)
cd rl-media-studio-v1_6
python -m rlmedia

# Verificar sintaxe de todos os arquivos
python -m compileall -q rl-media-studio-v1_6/

# Rodar testes (se pytest instalado)
cd rl-media-studio-v1_6
python -m pytest -q

# Verificar status dos branches
./scripts/monitor.sh status

# Iniciar monitor de commits
./scripts/monitor.sh start
```

---

## 4. Fluxo de trabalho

```mermaid
git checkout -b feat/minha-feature opencode
# ... desenvolver ...
python -m compileall -q .
git add -A && git commit -m "feat: descricao"
# Tester valida (black box)
# Se aprovado: merge para opencode
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

## 5. Arquitetura alvo (Clean Architecture)

```
presentation/  (CustomTkinter)  →  application/  (use cases)  →  domain/  (entidades)
                                     ↓
                              infrastructure/  (ffmpeg, storage, demucs, yt-dlp)
```

**Regras:**
- UI nunca chama infraestrutura diretamente — sempre via use case
- Domínio não importa CustomTkinter, FFmpeg, nem storage
- Adaptadores de infraestrutura implementam portas (interfaces)

---

## 6. Próximos passos (se agentes não concluírem)

### Fase 0 — Infraestrutura Portável (codex)
```bash
# Se codex nao concluir, fazer manualmente:
git checkout fix/self-contained-deps
# 1. Criar AudioLabEditor/src/infrastructure/
# 2. Embutir yt-dlp, ffmpeg no PyInstaller
# 3. Startup doctor
# 4. Launchers .sh/.bat/.desktop
```

### Fase 1 — Output Organization (tty1)
```bash
# Se tty1 nao concluir, fazer manualmente:
git checkout feat-output-organization
# 1. Portar PathConfig para o novo projeto
# 2. Logica de saida: {dest}/{projeto}/{tipo}-{timestamp}.{ext}
# 3. Integrar nas abas CaptureTab, TrimTab, VideoEditorTab
```

### Fase 2+ — Continuacao
```bash
git checkout -b feat/captura-midia opencode
git checkout -b feat/editor-audio opencode
git checkout -b feat/editor-video opencode
git checkout -b feat/compliance opencode
```

Ver `AudioLabEditor.md` para o plano completo de fases.

---

## 7. LGPD — Checklist rapido

- [ ] Nenhum dado pessoal coletado sem consentimento
- [ ] Nenhuma telemetria ou envio de dados
- [ ] Logs sem caminhos absolutos do usuario
- [ ] Cache local com politica de retencao
- [ ] Compliance = revisao assistida, nao decisao automatica

---

## 8. ISO 25010 — Criterios de qualidade

| Criterio | Como verificar |
|----------|---------------|
| Compilacao | `python -m compileall -q src/` |
| Testes | `pytest -q` |
| Seguranca | `shell=False` em todo subprocess |
| Manutencao | Nenhum arquivo > 500 linhas |
| Portabilidade | Testar Windows, Linux, macOS |
| Usabilidade | Tester valida black box |
