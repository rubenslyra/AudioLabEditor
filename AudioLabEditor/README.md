# AudioLabEditor

Aplicacao desktop alvo para a mescla entre `rl-media-studio-v1_6` e `MVP-AudioStemLab`.

Este scaffold inicial foca a fase 0:

- dependencias portaveis ao lado do executavel;
- resolucao de paths baseada no diretorio do `.exe` ou `sys._MEIPASS`;
- startup doctor com erro amigavel;
- launchers para duplo clique.

## Desenvolvimento

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .[ai]
audiolab-editor
```
