# Memória de trabalho — letras e cifras

Data de registro: 2026-06-20  
Objetivo: retomar o planejamento e a implementação do recurso de letra/cifra no AudioLab Editor.

## Pedido do usuário

Criar formas de:

- extrair o texto cantado de uma música;
- organizar a transcrição como canção ou poesia;
- gerar uma cifra preliminar;
- usar CLIs quando disponíveis;
- manter o fluxo educativo e complementar a plataformas como Moises, sem prometer substituição.

## Decisões confirmadas

1. O fluxo de letra recomendado é `Demucs vocals → WhisperX/Faster-Whisper → formatação → revisão humana`.
2. WhisperX é a preferência para alinhamento por palavra; Faster-Whisper continua útil como backend/base existente.
3. Formatação em verso, estrofe, refrão e ponte será heurística e editável.
4. O fluxo de cifra recomendado é `Demucs no_vocals/other → Chordino → CSV com tempos → alinhamento à letra`.
5. Basic Pitch é opção para MIDI/eventos de notas, não para cifra pronta.
6. Cifra e letra devem ser apresentadas como estimativas; revisão humana é obrigatória.
7. Prioridade de produto: primeiro “Letra assistida”; depois “Cifra beta”.
8. Saídas desejadas para letra: TXT, Markdown, LRC, SRT e JSON.
9. A abordagem CLI é complementar, não substituta de Moises ou outras plataformas gerenciadas.

## Estado atual do código observado

- `TranscriptionTab` já oferece transcrição com Faster-Whisper e anuncia TXT/SRT.
- `TranscriptionRequest` ainda possui apenas origem, idioma, modelo, destino e projeto.
- `WhisperSubprocessAdapter` trabalha com segmentos, não ativa `word_timestamps=True` e não produz estrutura de letra.
- `DemucsSubprocessAdapter` já suporta vocals, quatro stems e seis stems em WAV/MP3/FLAC.
- O adaptador Demucs atual executa `python -m demucs`; a documentação CLI passou a preferir `demucs` global. Uma decisão de arquitetura será necessária antes de alterar o aplicativo.

## Defeitos/riscos encontrados durante a leitura

Antes de ampliar a transcrição, validar e corrigir `src/infrastructure/whisper_adapter.py`:

- o script gerado importa `json, sys`, mas usa `os`;
- usa `output_dir` sem defini-lo dentro do script;
- chama `_fmt_srt` antes de declarar a função;
- interpola caminhos diretamente em código Python, o que é frágil para barras, aspas e caracteres especiais;
- o processamento atual não possui teste de integração que execute o script gerado.

Esses pontos foram apenas registrados; nenhuma correção foi implementada nesta sessão.

## Escopo proposto para o MVP de letra

### História

Como músico ou compositor, quero obter uma letra preliminar organizada a partir de uma música para revisar e editar sem transcrever tudo manualmente.

### Incluído

- opção de usar a mix ou isolar vocal;
- idioma português;
- modelo selecionável;
- timestamps por palavra;
- sugestão de linhas e estrofes por pausas;
- detecção simples de trechos repetidos como possíveis refrões;
- editor de texto antes da exportação;
- TXT, Markdown, LRC, SRT e JSON;
- mensagens claras para falha de modelo, memória, formato e alinhamento.

### Fora do MVP

- garantia de letra oficial;
- identificação perfeita de verso/refrão/ponte;
- publicação automática;
- tradução poética;
- cifra automática no mesmo incremento;
- substituição de plataformas comerciais.

## Critérios de aceite preliminares

1. Dado um áudio válido, o usuário obtém texto e timestamps sem bloquear a UI.
2. O usuário pode revisar todo o conteúdo antes de exportar.
3. O sistema diferencia claramente transcrição bruta de letra revisada.
4. Linhas e estrofes sugeridas podem ser editadas ou removidas.
5. Falhas não deixam arquivos finais apresentados como concluídos.
6. Caminhos com espaços e caracteres Unicode são tratados sem interpolação insegura.
7. O fluxo funciona em CPU; GPU é aceleração opcional.
8. O aplicativo informa download de modelo, consumo de armazenamento e uso de rede.
9. Testes automatizados simulam modelos e processos externos.
10. Uma validação manual usa ao menos fala limpa, canto solo e música com backing vocals.

## Próximos passos para amanhã

1. Reproduzir e corrigir os problemas do `WhisperSubprocessAdapter` com testes.
2. Decidir entre:
   - ampliar o adapter Faster-Whisper com timestamps por palavra; ou
   - criar um `WhisperXCliAdapter` separado.
3. Definir tipos de domínio `LyricsRequest`, `LyricsResult`, `LyricsLine` e `LyricsWord`.
4. Criar um formatador puro de linhas/estrofes, sem dependência de UI ou modelo.
5. Escrever testes para pausas, repetição, Unicode e ausência de timestamps.
6. Prototipar uma tela “Letra assistida” com revisão antes da exportação.
7. Só depois iniciar o spike do Chordino/Sonic Annotator para “Cifra beta”.

## Questões abertas

- WhisperX será dependência embarcada, opcional ou CLI externo?
- Quais modelos de alinhamento em português serão suportados e armazenados?
- LRC terá timestamp por linha ou por palavra?
- Como o usuário confirma refrões sugeridos?
- A cifra será simplificada para tríades por padrão?
- Haverá transposição e escolha entre sustenidos/bemóis?
- Licenças e distribuição de Chordino/Sonic Annotator permitem o empacotamento desejado?
- O modo offline completo é requisito de lançamento?

## Arquivo de referência criado

- `docs/GUIA_LETRAS_E_CIFRAS.md`

## Fontes consultadas

- https://github.com/SYSTRAN/faster-whisper
- https://github.com/m-bain/whisperX
- https://github.com/spotify/basic-pitch
- https://code.soundsoftware.ac.uk/projects/nnls-chroma
- https://vamp-plugins.org/sonic-annotator/
- https://github.com/facebookresearch/demucs

## Frase para retomar

“Retome `docs/LETRAS_CIFRAS_HANDOFF.md` e comece pelo passo 1: testar e corrigir o WhisperSubprocessAdapter antes de implementar Letra assistida.”

