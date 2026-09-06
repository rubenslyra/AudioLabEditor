# Guia prático — extração de letra e criação de cifra assistida

Este guia apresenta fluxos locais para obter uma letra preliminar, organizar o texto como canção/poesia e estimar acordes. Os resultados exigem revisão humana: canto, efeitos, backing vocals, modulações e arranjos densos reduzem a precisão.

## O que cada ferramenta faz

| Ferramenta | Função | Resultado principal |
|---|---|---|
| Demucs | Isola vocal ou acompanhamento | WAV/FLAC/MP3 por stem |
| Faster-Whisper | Transcreve voz | Segmentos e timestamps |
| WhisperX | Transcreve e alinha palavras | TXT, SRT, VTT, TSV e JSON |
| Chordino + Sonic Annotator | Estima acordes ao longo do tempo | CSV com timestamps e acordes |
| Basic Pitch | Transcreve notas | MIDI e eventos de notas |

Basic Pitch não produz uma cifra pronta. Ele é útil quando se deseja extrair MIDI de um instrumento isolado e inferir os acordes em uma etapa posterior.

## Pré-requisitos

Confirme os CLIs disponíveis no PowerShell:

```powershell
Get-Command demucs,whisperx,sonic-annotator,basic-pitch -ErrorAction SilentlyContinue
demucs --help
whisperx --help
sonic-annotator -l
basic-pitch --help
```

Não é obrigatório instalar todas as ferramentas para começar. Para letra, bastam Demucs e WhisperX/Faster-Whisper. Para cifra direta, acrescente Sonic Annotator e o plugin Chordino.

## Fluxo A — gerar uma letra preliminar

### 1. Isolar o vocal

```powershell
demucs -n htdemucs --two-stems vocals --flac -o ".\stems" ".\musica.flac"
```

Saída esperada:

```text
stems/htdemucs/musica/vocals.flac
stems/htdemucs/musica/no_vocals.flac
```

### 2. Transcrever e alinhar em português

CPU:

```powershell
whisperx ".\stems\htdemucs\musica\vocals.flac" --model large-v3 --language pt --device cpu --compute_type int8 --output_dir ".\letra" --output_format all
```

GPU NVIDIA compatível:

```powershell
whisperx ".\stems\htdemucs\musica\vocals.flac" --model large-v3 --language pt --device cuda --compute_type float16 --batch_size 4 --output_dir ".\letra" --output_format all
```

Reduza `--batch_size` se faltar memória de GPU. O alinhamento de palavras depende de um modelo fonético compatível com o idioma.

### 3. Revisar a transcrição

Antes de formatar:

- escute o vocal junto com o texto;
- corrija nomes próprios, contrações e repetições;
- marque palavras incertas em vez de inventá-las;
- remova alucinações geradas em silêncios;
- confira backing vocals e frases sobrepostas separadamente.

### 4. Organizar como canção ou poesia

Use os timestamps como apoio:

- pausa curta: possível quebra de verso;
- pausa longa: possível nova estrofe;
- trecho textual repetido: possível refrão;
- trecho sem vocal: possível introdução, ponte instrumental ou solo;
- mudança clara de conteúdo: possível ponte ou pré-refrão.

Modelo de saída:

```text
[Verso 1]

Primeira linha da canção
Segunda linha da canção

[Pré-refrão]

Linha de preparação

[Refrão]

Trecho que se repete
Trecho que se repete
```

Esses rótulos são hipóteses editoriais. WhisperX não identifica automaticamente a estrutura musical com confiabilidade suficiente para dispensar revisão.

## Fluxo B — gerar uma cifra preliminar com Chordino

### 1. Preparar o acompanhamento

O comando do fluxo anterior já cria `no_vocals.flac`. Para arranjos densos, teste também o stem `other` ou stems harmônicos isolados pelo modelo de seis fontes.

```powershell
demucs -n htdemucs_6s --flac -o ".\stems-6" ".\musica.flac"
```

### 2. Localizar o identificador do Chordino

```powershell
sonic-annotator -l | Select-String "chordino"
```

Use o identificador retornado pela sua instalação. Um identificador comum é `vamp:nnls-chroma:chordino:simplechord`, mas ele deve ser confirmado localmente.

### 3. Extrair acordes para CSV

```powershell
sonic-annotator -d vamp:nnls-chroma:chordino:simplechord ".\stems\htdemucs\musica\no_vocals.flac" -w csv --csv-force
```

O CSV contém acordes associados a tempos. Revise:

- tonalidade provável;
- acordes curtos ou espúrios;
- inversões;
- acordes estendidos simplificados;
- modulações;
- trechos sem harmonia definida.

### 4. Alinhar acordes e letra

Compare o tempo de cada acorde com os timestamps das palavras. A cifra final pode usar acordes antes das sílabas correspondentes:

```text
[Verso 1]

[C] Primeira linha da canção
[G] Segunda linha da canção

[Refrão]

[Am] Trecho que se repete
[F] Trecho que se repete
```

Esse alinhamento ainda é uma etapa manual ou uma futura função do AudioLab Editor.

## Fluxo C — transcrever instrumento para MIDI

Basic Pitch funciona melhor com um instrumento por vez. Use um stem de guitarra, piano ou outro material pouco denso.

```powershell
basic-pitch ".\midi" ".\stems-6\htdemucs_6s\musica\guitar.flac" --save-note-events
```

Saídas úteis:

- MIDI para edição em DAW;
- CSV de eventos de notas;
- WAV de conferência quando usado `--sonify-midi`.

Para obter nomes de acordes, o MIDI precisa passar por um analisador harmônico. Não trate a saída do Basic Pitch como cifra final.

## Estratégia recomendada no AudioLab Editor

### MVP 1 — Letra assistida

1. selecionar áudio ou vídeo;
2. opcionalmente isolar vocal com Demucs;
3. transcrever com alinhamento por palavra;
4. sugerir quebras de verso e estrofe;
5. permitir edição humana;
6. exportar TXT, Markdown, LRC, SRT e JSON.

### MVP 2 — Cifra beta

1. selecionar mix ou acompanhamento;
2. detectar acordes com timestamps;
3. normalizar grafia dos acordes;
4. alinhar acordes à letra revisada;
5. permitir edição e transposição;
6. exportar TXT/Markdown e, posteriormente, formatos especializados.

## Cuidados de qualidade

- Transcrição de fala não é igual à transcrição de canto.
- Melismas, vibrato, reverb e distorção podem produzir palavras incorretas.
- Backing vocals e vozes sobrepostas confundem alinhamento e separação.
- Chordino estima a harmonia; não conhece a intenção do compositor.
- Basic Pitch detecta notas, não função harmônica nem cifra editorial.
- Sempre preserve o áudio original e registre modelo, opções e versão usados.
- Não publique letra ou cifra sem conferir direitos de uso e autoria.

## Tratamento de erros

| Problema | Ação útil |
|---|---|
| Vocal com muito vazamento | Testar áudio de melhor qualidade, outro modelo Demucs ou trecho menor |
| Whisper inventa texto no silêncio | Revisar VAD, remover silêncio e conferir manualmente |
| Palavra sem timestamp | Confirmar modelo de alinhamento para o idioma e revisar o JSON |
| GPU sem memória | Reduzir batch, usar `int8` ou executar em CPU |
| Chordino não aparece | Confirmar instalação do plugin Vamp e listar plugins com `sonic-annotator -l` |
| Muitos acordes falsos | Usar acompanhamento mais limpo e simplificar eventos muito curtos |
| Basic Pitch mistura instrumentos | Isolar um stem antes da transcrição MIDI |
| Resultado parece correto, mas soa errado | Priorizar a audição e correção musical humana |

## Limites e posicionamento

Essas técnicas ensinam controle local, automação e análise. Elas não substituem plataformas gerenciadas, como Moises, que podem oferecer modelos próprios, fluxo integrado, aplicativos, armazenamento, edição e suporte. A escolha depende do objetivo, qualidade necessária, hardware, privacidade, custo e tempo disponível.

## Referências

- Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
- WhisperX: https://github.com/m-bain/whisperX
- Basic Pitch: https://github.com/spotify/basic-pitch
- NNLS Chroma/Chordino: https://code.soundsoftware.ac.uk/projects/nnls-chroma
- Sonic Annotator: https://vamp-plugins.org/sonic-annotator/
- Demucs: https://github.com/facebookresearch/demucs

