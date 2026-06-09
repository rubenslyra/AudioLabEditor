# Plano de Saida por Projeto

Data: 2026-06-09 | Branch: feat-output-organization

## Objetivo
Organizar saida dos stems/arquivos no formato {dest}/{projeto}/audio-stem-{modo}-{timestamp}/.

## Formato de Saida
- Captura: {dest}/{projeto}/capture-{timestamp}.{ext}
- Stems: {dest}/{projeto}/audio-stem-{modo}-{timestamp}/
- Corte: {dest}/{projeto}/trim-{timestamp}.{ext}
- Video: {dest}/{projeto}/edit-{timestamp}.{ext}

## PathConfig
- Browse source/dest sem paths default
- Projeto: padrao "ALE" se vazio
- PathConfig como fonte unica para todas as abas

## OutputOrganizer
- build_output_path() com prefixo/sufixo/timestamp
- build_output_dir() para stems
- Criar diretorio se nao existir

## Criterios de Aceite
compileall, 4 abas com PathConfig, output folder criado, sem default paths.

