# Protocolo de Testes — AudioLabEditor

## ISO 25010 / IEC / LGPD

---

## 1. Papéis

| Papel | Agente | Responsabilidade |
|-------|--------|------------------|
| **White Box** | opencode (tty1) | Teste estrutural, compilação, lint, cobertura, segurança |
| **Black Box** | tester (usuário) | Teste funcional, UX, casos de borda, plataforma |
| **Coordenador** | opencode (tty0→tty1) | Gate de qualidade, rastreabilidade, merge |

---

## 2. Ciclo por Feature Task

```
[Task Concluída]
       │
       ▼
┌──────────────────────────────┐
│  1. WHITE BOX GATE (opencode) │
│  • compileall                │
│  • lint / types              │
│  • testes unitários          │
│  • análise de segurança      │
│  • checklist ISO 25010       │
└──────────────┬───────────────┘
       │ (passou?)
       ▼
┌──────────────────────────────┐
│  2. BLACK BOX GATE (tester)  │
│  • executar aplicação        │
│  • testar funcionalidade     │
│  • testar casos de borda     │
│  • validar LGPD              │
│  • relatar falhas            │
└──────────────┬───────────────┘
       │ (passou?)
       ▼
┌──────────────────────────────┐
│  3. GATE DE QUALIDADE        │
│  • relatório de teste        │
│  • não conformidades         │
│  • decisão: aprovado/recusado│
└──────────────┬───────────────┘
       │
       ▼
   Merge / Próxima task
```

---

## 3. White Box Checklist (opencode)

### 3.1 Compilação e Estática

- [ ] `python3 -m compileall -q src/` — zero erros
- [ ] `ruff check src/` — zero violações de estilo (se disponível)
- [ ] `mypy src/` — type checks (se disponível)

### 3.2 Testes Unitários

- [ ] `pytest -q` — todos verdes
- [ ] Nenhum teste ignorado sem justificativa
- [ ] Cobertura mínima da nova funcionalidade: 60%

### 3.3 Segurança (IEC 62443 / LGPD)

- [ ] Nenhuma senha, token ou chave em texto plano no código
- [ ] `subprocess.run` com `shell=False` (nunca `shell=True`)
- [ ] Caminhos de arquivo validados contra path traversal (`../`, `~`, symlinks)
- [ ] URLs validadas antes de passar ao yt-dlp (apenas `https?://`)
- [ ] Logs sem exposição de caminhos absolutos do usuário
- [ ] Dados de compliance/transcrição não armazenados sem política de retenção

### 3.4 Arquitetura (ISO 25010 — Maintainability)

- [ ] Nenhum arquivo novo > 500 linhas (exceto se justificado)
- [ ] Nenhum `except Exception` silencioso
- [ ] Separação UI / domínio / infraestrutura respeitada
- [ ] Imports seguem a hierarquia de camadas

---

## 4. Black Box Checklist (tester)

### 4.1 Funcionalidade (ISO 25010 — Functional Suitability)

- [ ] A funcionalidade executa o que foi especificado
- [ ] O resultado é correto e completo
- [ ] Mensagens de erro são claras e acionáveis

### 4.2 Usabilidade (ISO 25010 — Usability)

- [ ] A interface é compreensível sem instruções
- [ ] Botões e campos têm rótulos descritivos
- [ ] Feedbacks visuais para operações longas (progress bar, modal)
- [ ] Cancelamento de operação é possível (quando aplicável)

### 4.3 Casos de Borda

- [ ] Campo vazio → mensagem de erro amigável
- [ ] Arquivo inexistente → erro tratado
- [ ] Caminho inválido → erro tratado
- [ ] Rede indisponível → erro tratado (não crash)
- [ ] Permissão negada → erro tratado

### 4.4 Privacidade (LGPD)

- [ ] Nenhum dado pessoal é coletado sem consentimento explícito
- [ ] Caminhos de arquivo do usuário não são expostos em logs
- [ ] Não há telemetria ou envio de dados sem autorização
- [ ] Cache local tem política de retenção clara

---

## 5. Gate de Qualidade

### 5.1 Critérios de Aprovação

| Critério | Obrigatório? |
|----------|-------------|
| White Box — compilação OK | ✅ Sim |
| White Box — testes verdes | ✅ Sim |
| White Box — sem falhas de segurança | ✅ Sim |
| Black Box — funcionalidade OK | ✅ Sim |
| Black Box — sem crashes | ✅ Sim |
| Black Box — LGPD respeitada | ✅ Sim |

### 5.2 Registro

Cada feature task gera um relatório em `docs/testing/`:

```yaml
task: "Descrição curta"
branch: "nome-da-branch"
white_box:
  date: 2026-06-09
  result: pass/fail
  notes: ""
black_box:
  tester: "usuário"
  date: 2026-06-09
  result: pass/fail
  notes: ""
gate:
  decision: approved/rejected
  reviewer: "coordenador"
```

---

## 6. Regras de Release

1. Toda task só é considerada **completa** após passar pelos 3 gates
2. Testes rodam **limpos** (sem `skip`, sem `xfail` não justificado)
3. A branch só pode mergear após aprovação do black box
4. O coordenador mantém a rastreabilidade no `CHANGELOG.md`
