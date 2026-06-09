# Relatório de Análise — MVP-AudioStemLab v0.3.8

## 1. Funcionalidades Principais

| Funcionalidade | Status | Tecnologia |
|---|---|---|
| Separação de stems por IA | ✅ Implementado | Demucs 4.0.1 (Hybrid Transformer) |
| 3 modos de separação | ✅ Implementado | vocals, full4, extended6 |
| 3 formatos de saída | ✅ Implementado | WAV, MP3 320kbps, FLAC |
| Seletor nativo de arquivo | ✅ Implementado | tkinter filedialog |
| Seletor nativo de pasta | ✅ Implementado | tkinter askdirectory |
| Download de áudio (yt-dlp) | ✅ Implementado | yt-dlp via subprocess |
| Interface de terminal estilizada | ✅ Implementado | Rich (painéis, tabelas, prompts) |
| Build portável (PyInstaller) | ✅ Implementado | Linux, Windows, macOS |
| Pipeline CI/CD (GitHub Actions) | ✅ Implementado | testes + build + release |
| Pacotes CPU e CUDA separados | ✅ Implementado | requisitos distintos por aceleração |
| Progresso com % e tempo decorrido | ✅ Implementado | parsing de stdout do Demucs |
| Testes unitários (7 testes) | ✅ Implementado | pytest |
| Logs de execução | ❌ Ausente | — |
| Organização por job/música | ❌ Ausente | — |
| Interface gráfica desktop | ❌ Ausente | — |
| Player multistem | ❌ Ausente | — |
| Detecção de BPM/tom | ❌ Ausente | — |

## 2. Estrutura e Estado Atual

### 2.1 Arquitetura

```
MVP-AudioStemLab/
├── app.py                      # Entrypoint — loop CLI principal
├── core/
│   ├── __init__.py             # Package marker
│   ├── paths.py                # AppPaths — resolução portável de diretórios
│   ├── separator.py            # AudioSeparator — subprocess Demucs + parsing
│   ├── file_manager.py         # FileManager — FS + download yt-dlp
│   ├── file_dialogs.py         # FileDialog + fallback — tkinter dialogs
│   ├── terminal_ui.py          # TerminalUI — interface com Rich
│   ├── terminal_launcher.py    # Detecção de terminal/sistema
│   └── version.py              # APP_NAME, APP_VERSION, SUPPORTED_PLATFORMS
├── scripts/
│   ├── package_release.py      # Empacotamento ZIP de release
│   └── generate_snapshots.py   # Geração de SVGs para docs
├── tests/
│   └── test_core.py            # 7 testes (paths, UI, comandos, versão)
├── packaging/
│   └── AudioStemLab.spec       # Spec PyInstaller
├── launchers/                  # Scripts de inicialização por SO
├── assets/                     # Banner, fontes Fira Code, licenças
├── docs/                       # Roadmap, changelog, releases, screenshots
├── .github/workflows/
│   ├── ci.yml                  # Testa Python 3.10 e 3.11
│   └── release.yml             # Build + publish em 5 variantes
└── requirements*.txt           # runtime, dev, cpu, cuda, build
```

**Padrão arquitetural**: CLI monolítico com separação por responsabilidade em módulos `core/`. Não há inversão de dependência — todos os módulos importam diretamente. O `app.py` coordena o fluxo.

### 2.2 Fluxo da Aplicação

```
app.py:main()
  ├─ TerminalUI() — header + menu
  ├─ FileManager.ensure_directories()
  ├─ Loop principal
  │   ├─ [1] Separar áudio
  │   │   ├─ choose_audio_source_method() → file dialog | manual
  │   │   ├─ choose_separation_mode() → vocals | full4 | extended6
  │   │   ├─ choose_output_format() → wav | mp3 | flac
  │   │   ├─ choose_destination_method() → default | custom folder
  │   │   └─ AudioSeparator.separate() → subprocess demucs
  │   ├─ [2] Baixar áudio
  │   │   └─ FileManager.download_audio() → subprocess yt-dlp
  │   ├─ [3] Sobre
  │   └─ [0] Sair
```

### 2.3 Dependências Core

| Dependência | Versão | Função |
|---|---|---|
| demucs | 4.0.1 | Modelo de separação de fontes musicais |
| torch / torchaudio | (transitiva) | Runtime PyTorch para Demucs |
| torchcodec | 0.14.0 | Codec de áudio para torchaudio |
| rich | 14.2.0 | Interface de terminal estilizada |
| yt-dlp | 2026.3.17 | Download de áudio de URLs |
| tkinter | (stdlib) | Diálogos nativos de arquivo |

### 2.4 Estado Atual — Pontos Fortes

- **Código limpo e enxuto**: ~960 linhas de Python, bem organizado em módulos.
- **Portabilidade real**: caminhos adaptáveis por SO (XDG, APPDATA, ~/Library), launchers para 3 sistemas.
- **Pipeline de release maduro**: CI testa, builda 5 variantes (linux-cpu, linux-cuda, windows-cpu, windows-cuda, macos-cpu), publica release com assets divididos se >2GB.
- **Documentação técnica**: changelog, roadmap, planos iniciais, notas de release — tudo registrado.
- **UX de terminal boa**: Rich com tabelas, painéis, prompts, progresso legível.
- **Tratamento de fallbacks**: seletor nativo indisponível → entrada manual.

### 2.5 Estado Atual — Pontos Fracos

- **Acoplamento forte**: `separator.py` chama Demucs via subprocess hardcoded; `file_manager.py` chama yt-dlp via subprocess. Sem abstração de portas.
- **Sem logs**: nenhum registro de execução é persistido.
- **Sem organização por job**: stems são sobrescritos se o mesmo arquivo for reprocessado.
- **Sem tratamento de erro granular**: exceções genéricas capturadas com `except Exception`.
- **Sem injeção de dependência**: `AppPaths.default()` é chamado diretamente nos construtores.
- **Sem tipagem estática**: sem type hints em quase todo o código.
- **Cobertura de testes baixa**: 7 testes, nenhum para o fluxo de download ou paths reais.
- **Demucs não é mais mantido ativamente**: o repo original do Meta não recebe updates significativos.
- **Modelos pesados**: download dos pesos na primeira execução (~1-2GB).

## 3. Proposta de Melhorias

Organizadas por camada de maturidade.

### 3.1 Camada Arquitetural (Clean Architecture)

| Problema | Solução Proposta |
|---|---|
| Acoplamento a Demucs via subprocess | Criar interface `ISeparatorEngine` (porta) com adaptadores: `DemucsSubprocessAdapter`, `DemucsPythonAdapter`. `AudioSeparator` vira um `SeparationUseCase` que depende da abstração, não da implementação. |
| Acoplamento a yt-dlp | Criar interface `IDownloader` com adaptador `YtDlpAdapter`. Isolar regras de download da infraestrutura. |
| `AppPaths.default()` espalhado | Inversão de dependência: receber `AppPaths` por parâmetro (já parcialmente feito, mas construtores têm fallback). Remover fallbacks e usar DI explícita. |
| Lógica de UI misturada com fluxo | Extrair `app.py` para casos de uso: `SeparateAudioUseCase`, `DownloadAudioUseCase`. A UI (terminal) é um adaptador de entrada; o caso de uso não deve saber se é terminal ou GUI. |

### 3.2 Camada de Engenharia de Software

| Problema | Solução Proposta |
|---|---|
| Sem type hints | Adicionar typing completo em todos os módulos. |
| `except Exception` genérico | Criar hierarquia de exceções: `SeparationError`, `DownloadError`, `FileNotFound`, `ModelNotFound`. Cada camada captura o que sabe tratar. |
| Sem logs | Adicionar módulo `core/logger.py` com logging estruturado (JSON ou formato padronizado). Rotação de logs, nível configurável. |
| Sem organização por job | Criar `JobManager` que gera pastas `output_stems/<musica_timestamp>/` e salva metadados (modelo, formato, duração, data). |
| Testes frágeis | Testar com `tmp_path` (já faz) mas expandir para testar o parsing de progresso, validação de entradas, e fluxos de erro. Adicionar mocks para subprocess. |
| Sem CI em múltiplos SOs | Workflow atual só testa em Linux. Adicionar matrix com Windows e macOS para testes. |

### 3.3 Camada de Segurança (Cybersecurity)

| Problema | Solução Proposta |
|---|---|
| `subprocess.run` com shell=False (ok) mas sem validação de entrada | Validar caminhos de arquivo contra path traversal (`../`, `~`, symlinks). |
| URL de download sem validação | Validar URL antes de passar ao yt-dlp. Permitir apenas esquemas `https?://`. Bloquear `file://`, `ftp://`, etc. |
| Dependências com CVEs conhecidos | Adicionar scan de dependências no CI (Trivy, pip-audit, ou Dependabot). |
| Log sem sanitização | Garantir que logs nunca contenham caminhos absolutos do usuário ou metadados sensíveis. |
| Sem SBOM | Gerar SBOM (CycloneDX) no pipeline de release. |

### 3.4 Funcionalidades para a Nova Aplicação (Merge com rl-media-studio)

Baseado no que está sendo analisado pelo Codex no outro projeto, sugiro que a nova aplicação mesclada considere:

| Funcionalidade | Origem AudioLab | Origem rl-media-studio |
|---|---|---|
| Separação Demucs | ✅ maduro | ❌ |
| Interface de terminal | ✅ maduro | ❌ |
| Build portátil cross-platform | ✅ maduro | ❌ |
| Pipeline CI/CD release | ✅ maduro | ❌ |
| Interface gráfica desktop | ❌ | ✅ (customtkinter) |
| Webapp Flask | ❌ | ✅ |
| Captura de tela/área | ❌ | ✅ |
| Legendas (OCR/ASR) | ❌ | ✅ |
| Conformidade/LGPD | ❌ | ✅ |
| Módulos C++ nativos | ❌ | ✅ |
| SDK .NET | ❌ | ✅ |
| Organização por projeto | ❌ | ✅ |
| Estrutura modular com injeção | ❌ | ✅ (parcial) |

### 3.5 Roadmap Recomendado para a Nova Aplicação

1. **Fase 0 — Análise e design**: ADR sobre arquitetura alvo (clean/hexagonal), mapeamento de bounded contexts, definição de portas.
2. **Fase 1 — Núcleo cross-platform**: portar `core/` do AudioLab com abstrações de engine de separação, download, paths.
3. **Fase 2 — Interface desktop**: absorver customtkinter do rl-media-studio como adaptador de entrada primário.
4. **Fase 3 — Jobs, logs, metadados**: sistema de jobs com histórico, persistência, re-processamento.
5. **Fase 4 — Player multistem**: player com mute/solo, volume, waveform, BPM/tom detection.
6. **Fase 5 — Webapp**: expor funcionalidades via Flask (do rl-media-studio) para acesso remoto/local.
7. **Fase 6 — Conformidade e segurança**: LGPD/GDPR, SBOM, dependency scanning, audit trail.

---

**Resumo**: MVP-AudioStemLab é um CLI maduro (~960 LOC) com excelente pipeline de release e portabilidade, mas precisa de refatoração arquitetural (clean architecture, DI, ports & adapters), logs, organização por jobs, e validações de segurança. A nova aplicação deve manter o pipeline de build e a simplicidade do AudioLab, absorvendo a GUI, webapp e módulos nativos do rl-media-studio.
