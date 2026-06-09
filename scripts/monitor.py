#!/usr/bin/env python3
"""
Monitor de Ciclo — AudioLabEditor
Roda em background, verifica commits, alerta gates de teste.

ISO 25010 / IEC / LGPD — Rastreabilidade contínua.
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RLMS_REPO = REPO_ROOT / "rl-media-studio-v1_6"

TRACKED = {
    "tty0 (codex)": {
        "repo": REPO_ROOT,
        "branch": "fix/self-contained-deps",
        "phase": "0",
    },
    "tty1 (opencode)": {
        "repo": RLMS_REPO,
        "branch": "feat-output-organization",
        "phase": "1",
    },
    "tty2 (opencode)": {
        "repo": RLMS_REPO,
        "branch": "feat/path-config-ui",
        "phase": "1-2",
    },
}

PHASES = {
    "0": "Fase 0 — Infraestrutura Portável (deps empacotadas, launchers, doctor)",
    "1": "Fase 1 — Núcleo (path config, output organization)",
    "2": "Fase 2 — Stem Separation GUI",
    "3": "Fase 3 — Captura de Mídia",
    "4": "Fase 4 — Editor de Áudio",
    "5": "Fase 5 — Editor de Vídeo",
    "6": "Fase 6 — Compliance e LGPD",
    "7": "Fase 7 — Transcrição, OCR, Voz Guia",
}


def git_log(repo: Path, branch: str, count: int = 5):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "log", f"--max-count={count}", "--oneline", branch, "--"],
            capture_output=True, text=True, check=False, timeout=15,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []


def git_last_commit_date(repo: Path, branch: str):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", branch, "--format=%ct"],
            capture_output=True, text=True, check=False, timeout=15,
        )
        if result.stdout.strip():
            return int(result.stdout.strip())
    except Exception:
        pass
    return None


def check_testing_gate_ready(repo: Path, branch: str, phase: str) -> bool:
    """Retorna True se a branch tem commits recentes (última hora) indicando gate pronto."""
    ts = git_last_commit_date(repo, branch)
    if ts is None:
        return False
    now = int(time.time())
    return (now - ts) < 3600  # commits na última hora


def print_alert(agent: str, phase: str, repos: list[str]):
    border = "━" * 60
    print()
    print(border)
    print(f"  🧪 GATE DE TESTE PRONTO — {agent}")
    print(f"  Fase: {phase} — {PHASES.get(phase, '—')}")
    print(f"  Branch{'s' if len(repos) > 1 else ''}: {', '.join(repos)}")
    print()
    print("  Ação requerida:")
    print("    1. White box: compile, lint, testes (opencode)")
    print("    2. Black box: tester executa e valida")
    print("    3. Gate: relatório → aprovado/recusado → merge")
    print(border)
    print()


def run_once(snapshot: dict[str, int]) -> dict[str, int]:
    for agent, cfg in TRACKED.items():
        repo = cfg["repo"]
        branch = cfg["branch"]
        phase = cfg["phase"]
        key = f"{agent}@{branch}"

        ts = git_last_commit_date(repo, branch)

        if ts is None:
            continue

        prev = snapshot.get(key)
        if prev is not None and ts > prev:
            print_alert(agent, phase, [str(repo.name or repo)])

        if prev is None:
            snapshot[key] = ts
        elif ts > prev:
            snapshot[key] = ts

    return snapshot


def daemon(interval: int = 300):
    print(f"🧪 Monitor de Ciclo AudioLabEditor iniciado em {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"   Polling a cada {interval}s. Pressione Ctrl+C para parar.")
    print(f"   Branches monitoradas:")
    for agent, cfg in TRACKED.items():
        print(f"     • {agent}: {cfg['repo'].name}/{cfg['branch']} (Fase {cfg['phase']})")
    print()

    snapshot: dict[str, int] = {}

    while True:
        try:
            snapshot = run_once(snapshot)
        except Exception as exc:
            print(f"[{datetime.now():%H:%M:%S}] Erro no ciclo: {exc}", file=sys.stderr)
        time.sleep(interval)


def status():
    print(f"📊 Status das branches — {datetime.now():%Y-%m-%d %H:%M:%S}")
    print()
    for agent, cfg in TRACKED.items():
        repo = cfg["repo"]
        branch = cfg["branch"]
        phase = cfg["phase"]
        commits = git_log(repo, branch, count=3)
        ts = git_last_commit_date(repo, branch)

        repo_name = repo.name or "."
        if ts:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        else:
            dt = "—"

        print(f"  {agent}")
        print(f"    Repo:     {repo_name}")
        print(f"    Branch:   {branch}")
        print(f"    Fase:     {phase} — {PHASES.get(phase, '—')}")
        print(f"    Ultimo:   {dt}")
        if commits:
            print(f"    Commits:")
            for c in commits:
                print(f"      • {c}")
        else:
            print(f"    Commits:  (sem commits ou branch nao encontrada)")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de Ciclo AudioLabEditor")
    parser.add_argument("mode", nargs="?", default="daemon", choices=["daemon", "status"],
                        help="daemon (padrao, polling eterno) ou status (print unico)")
    parser.add_argument("--interval", "-i", type=int, default=300,
                        help="Intervalo de polling em segundos (padrao: 300)")
    args = parser.parse_args()

    if args.mode == "status":
        status()
    else:
        daemon(interval=args.interval)
