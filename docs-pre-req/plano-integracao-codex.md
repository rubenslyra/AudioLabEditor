# Plano de Integracao Codex — Distribuicao Profissional

Data: 2026-06-10 | Responsavel: codex / tty0 | Branch: feat/path-config-ui

## Decisao Tecnica

O AudioLabEditor nao deve depender de um executavel monolitico com todas as
dependencias de IA, multimidia e modelos embarcados. PyInstaller/Nuitka entram
apenas como etapa de build do aplicativo principal.

A distribuicao alvo passa a ser:

```text
app leve
bootstrap/runtime doctor
dependency manager
assets versionados por plataforma
instalador nativo
```

## Objetivo de Curto Prazo

Disponibilizar uma versao de teste base para validar UI, captura, corte, editor
e organizacao de saida. Stems/Demucs continuam no fluxo funcional do projeto,
mas a distribuicao completa de IA sera tratada como runtime externo versionado.

## Estrutura de Runtime

Os assets instalados/baixados ficam fora do binario principal:

```text
AudioLabEditor runtime
├── runtime/
│   └── tools/
│       └── ffmpeg/
│           └── bin/
├── models/
├── cache/
└── plugins/
```

Diretorios por sistema:

- Linux: `$XDG_DATA_HOME/audiolabeditor` ou `~/.local/share/audiolabeditor`
- Windows: `%LOCALAPPDATA%/AudioLabEditor`
- macOS: `~/Library/Application Support/AudioLabEditor`

## Resolucao de Dependencias

Ordem de busca para binarios:

1. Ao lado do executavel/app bundle
2. Bundle temporario do empacotador, quando existir
3. Runtime gerenciado do usuario
4. `PATH` do sistema somente em modo desenvolvimento

Em modo congelado, o app nao deve depender do `PATH` global do sistema.

## Assets Versionados

Publicar no GitHub Releases ou storage equivalente:

```text
linux-x64/
├── ffmpeg.tar.gz
├── demucs-cpu.tar.gz
└── models-v4.tar.gz

windows-x64/
├── ffmpeg.zip
├── demucs-cpu.zip
└── models-v4.zip

macos-arm64/
├── ffmpeg.tar.gz
├── demucs-cpu.tar.gz
└── models-v4.tar.gz
```

CUDA/GPU deve ser um pacote separado, nunca requisito do instalador base.

## Roadmap

### Fase A — Teste Base

- [x] Binario Linux base em `dist/AudioLabEditor`
- [x] Testes automatizados verdes
- [x] Paths centralizados para data/cache/models/tools
- [ ] Black box em sessao grafica normal

### Fase B — Runtime Manager

- [ ] Manifesto de runtime (`runtime-manifest.json`)
- [ ] Verificacao de versao/hash dos assets
- [ ] Download/extracao de ffmpeg no runtime gerenciado
- [ ] Startup Doctor com acao reparavel: baixar dependencia ausente
- [ ] Testes de resolucao sem internet usando fixtures locais

### Fase C — IA Externa

- [ ] Pacote Demucs CPU versionado por plataforma
- [ ] Cache/modelos em `models/`
- [ ] Politica de fallback quando IA nao estiver instalada
- [ ] Download sob demanda ao abrir a aba Stems ou ao executar separacao

### Fase D — Distribuicao Nativa

- [ ] Linux: AppImage do app base + runtime fetcher
- [ ] Windows: Inno Setup/NSIS + runtime fetcher
- [ ] macOS: `.app`/DMG + assinatura/notarizacao quando aplicavel
- [ ] CI/CD por plataforma

## Criterios de Aceite

- App base abre sem Demucs instalado
- Dependencias ausentes mostram mensagem clara e reparavel
- `ffmpeg` congelado e IA nao dependem de `PATH` global
- Assets pesados nao entram no executavel principal
- Testes automatizados cobrem paths e isolamento de configuracao local
