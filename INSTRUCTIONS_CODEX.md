# Instruções para codex (tty0)

## Contexto

Você é o Agente codex no terminal tty0, alocado para trabalhar na mescla dos projetos
`rl-media-studio-v1_6/` (GUI desktop) e `MVP-AudioStemLab/` (separação de stems por IA).

O objetivo é garantir que o executável de produção funcione com **duplo clique**,
sem depender de variáveis de ambiente para encontrar dependências.

## Sua Branch

**`fix/self-contained-deps`** — criada a partir de `opencode`.

Trabalhe dentro de `rl-media-studio-v1_6/` (e também no que for necessário
em `MVP-AudioStemLab/`).

## Tarefas Prioritárias

### 1. Empacotar TODAS as dependências no executável

O PyInstaller não pode deixar de fora:
- `yt-dlp` (embarcado, sem chamada externa)
- `ffmpeg` / `ffprobe` (binários devem vir junto ao executável)
- Modelos do Demucs (ou download sob demanda com cache local ao lado do .exe)
- `faster-whisper`, `paddleocr` (se incluídos no perfil)

### 2. Path resolution relocatable

- O executável deve encontrar suas dependências na **própria pasta** onde está
  (ou em `_internal/`, `lib/` relativo ao .exe)
- **NÃO** usar `PATH`, `APPDATA`, `XDG_*` ou `~` para lookup de binários
- Usar `sys.executable` ou `sys._MEIPASS` como âncora

### 3. Corrigir launchers (.sh / .bat / .desktop)

- Testar duplo clique: o programa precisa abrir a janela GUI diretamente
- Se houver `.sh` ou `.bat`, garantir que resolvem o caminho relativo
  ao diretório do script (`"$(dirname "$0")"` no Linux, `%~dp0` no Windows)
- Remover dependência de terminal — se houver erro, mostrar messagebox, não print

### 4. Startup doctor

Adicionar verificação na inicialização:
- Se falta yt-dlp, ffmpeg, ou modelo Demucs → mostrar dialog claro
- Se algo não for encontrado, abortar com mensagem amigável
- **Nunca** crashar silenciosamente

### 5. Cross-platform

- Windows: `.exe` com duplo clique
- Linux: `.desktop` + binário portátil
- macOS: `.app` bundle

---

## Observações Finais

- Já tivemos problemas com executáveis que não abriam com duplo clique
  e não encontravam dependências. **Não repetir esses erros.**
- Se precisar de alterações no `MVP-AudioStemLab/`, faça.
- Commite na branch `fix/self-contained-deps`.
