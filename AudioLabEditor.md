# AudioLabEditor — Plano Base

Aplicação desktop multimídia unificada.
Stack: Python ≥3.11, CustomTkinter (GUI), Demucs (stems), FFmpeg, yt-dlp.

---

## Fases

### Fase 0 — Infraestrutura Portável
| # | Tarefa | Resp. |
|---|--------|-------|
| 0.1 | Empacotar yt-dlp, ffmpeg, Demucs dentro do executável | codex |
| 0.2 | Path resolution relocatable (sys._MEIPASS / dir do .exe) | codex |
| 0.3 | Startup doctor: valida deps antes de abrir janela | codex |
| 0.4 | Corrigir launchers .sh/.bat/.desktop para duplo clique | codex |
| 0.5 | **Gate:** tester executa com duplo clique sem erro | tester |

### Fase 1 — Núcleo da Aplicação
| # | Tarefa | Resp. |
|---|--------|-------|
| 1.1 | Seletor de pasta origem (Browse + path, sem default) | opencode |
| 1.2 | Seletor de pasta destino (Browse + path, sem default) | opencode |
| 1.3 | Campo nome do projeto (default "ALE") | opencode |
| 1.4 | Output: `{dest}/{projeto}/audio-stem-{modo}-{timestamp}/` | opencode |
| 1.5 | **Gate:** tester abre app, configura paths, gera stem | tester |

### Fase 2 — Separação de Stems (GUI)
| # | Tarefa | Resp. |
|---|--------|-------|
| 2.1 | Aba "Separador de Stems" com modo/ formato / iniciar | ✅ feito |
| 2.2 | Serviço Demucs com progresso (subprocess) | ✅ feito |
| 2.3 | Modal de progresso + resultado + abrir pasta | ✅ feito |
| 2.4 | Histórico de stems persistido | ✅ feito |
| 2.5 | **Gate:** tester gera stems de um arquivo .mp3/.wav | tester |

### Fase 3 — Captura de Mídia
| # | Tarefa | Resp. |
|---|--------|-------|
| 3.1 | Unificar CaptureTab com paths configuráveis (sem default) | — |
| 3.2 | Download original, comprimido e áudio-only | — |
| 3.3 | Validação de URL (apenas https?) | — |
| 3.4 | **Gate:** tester baixa áudio de URL e extrai stems | tester |

### Fase 4 — Editor de Áudio
| # | Tarefa | Resp. |
|---|--------|-------|
| 4.1 | Waveform sob demanda com zoom e marcadores | — |
| 4.2 | Corte e exportação em múltiplos formatos | — |
| 4.3 | Cache de waveform | — |
| 4.4 | **Gate:** tester corta áudio e exporta | tester |

### Fase 5 — Editor de Vídeo
| # | Tarefa | Resp. |
|---|--------|-------|
| 5.1 | Extrair VideoEditorState, TimelineController da UI (~1968 linhas) | — |
| 5.2 | Preview, timeline, cortes, fade, velocidade | — |
| 5.3 | Render com presets de resolução + metadados | — |
| 5.4 | **Gate:** tester edita e renderiza vídeo | tester |

### Fase 6 — Compliance e LGPD
| # | Tarefa | Resp. |
|---|--------|-------|
| 6.1 | Revisão assistida (não decisão automática) | — |
| 6.2 | Evidências com timestamp + fonte oficial | — |
| 6.3 | Política de retenção de transcrições e histórico | — |
| 6.4 | Relatório exportável (HTML/JSON/PDF) | — |
| 6.5 | Modo offline com aviso de limitação | — |
| 6.6 | **Gate:** tester gera relatório de compliance | tester |

### Fase 7 — Transcrição, OCR, Voz Guia
| # | Tarefa | Resp. |
|---|--------|-------|
| 7.1 | Transcrição via faster-whisper (.srt) | — |
| 7.2 | OCR de frames via PaddleOCR | — |
| 7.3 | Voz guia via edge-tts | — |
| 7.4 | **Gate:** tester transcreve vídeo e gera SRT | tester |

---

## Critérios de Aceite (ISO 25010)

- [x] **Funcionalidade:** cada feature faz o que promete
- [x] **Portabilidade:** Windows, Linux, macOS (duplo clique)
- [x] **Usabilidade:** feedback visual, mensagens claras, sem default paths
- [x] **Confiabilidade:** sem crashes, erros tratados, doctor na inicialização
- [x] **Segurança:** shell=False, sem credenciais, path validation, LGPD
- [x] **Manutenibilidade:** <500 linhas por arquivo, sem except Exception silencioso
- [x] **Eficiência:** operações longas com progresso e cancelamento

---

## LGPD — Compliance por Design

1. Não coletar dados pessoais sem consentimento explícito
2. Não enviar telemetria
3. Logs sem exposição de caminhos absolutos do usuário
4. Cache local com política de retenção documentada
5. Compliance = revisão assistida, nunca decisão automatizada final
6. Relatório de compliance inclui: timestamp, fonte, método, confiança
