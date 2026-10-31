#!/usr/bin/env python3
"""
decrypt_sim.py — "paga o resgate" sem pagar nada: usa a chave Fernet
gerada em lab/.chave.key para restaurar os arquivos e CONFERE o SHA-256
de cada um contra o manifesto original (integridade).

⚠️ EDUCACIONAL — desafio DIO. Só opera dentro de lab/ deste repositório.
"""
import json
import sys
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

REPO_ROOT = Path(__file__).resolve().parent.parent
LAB_DIR = REPO_ROOT / "lab"
KEY_NAME = ".chave.key"
MANIFEST_NAME = ".manifesto.json"
NOTE_NAME = "LEIA_ME_RESGATE.txt"


def falha(msg: str) -> None:
    print(f"[X] RECUSADO: {msg}")
    sys.exit(2)


def main() -> int:
    if not LAB_DIR.exists():
        falha("pasta lab/ não existe.")
    key_path = LAB_DIR / KEY_NAME
    if not key_path.exists():
        falha(f"sem {KEY_NAME} em lab/ — sem chave não há 'resgate' que pague.")
    if not (LAB_DIR / MANIFEST_NAME).exists():
        falha(f"sem {MANIFEST_NAME} — rode o ransomware_sim.py primeiro.")

    chave = key_path.read_bytes()
    fernet = Fernet(chave)
    manifesto = json.loads((LAB_DIR / MANIFEST_NAME).read_text(encoding="utf-8"))

    ok = 0
    for nome, hash_original in manifesto.items():
        alvo = LAB_DIR / nome
        if not alvo.exists():
            print(f"[!] faltando: {nome}")
            continue
        try:
            restaurado = fernet.decrypt(alvo.read_bytes())
        except InvalidToken:
            print(f"[X] chave errada para {nome} (HMAC falhou)")
            continue
        alvo.write_bytes(restaurado)
        conferido = "OK" if json_hash(restaurado) == hash_original else "DIVERGE!"
        print(f"[*] DECIFRADO: {nome}  | sha256 conferido: {conferido}")
        ok += 1 if conferido == "OK" else 0

    # limpeza: chave, manifesto e nota saem da pasta ao final
    for extra in (KEY_NAME, MANIFEST_NAME, NOTE_NAME):
        f = LAB_DIR / extra
        if f.exists():
            f.unlink()

    print(f"\n[DONE] {ok}/{len(manifesto)} arquivo(s) restaurado(s) e verificado(s).")
    print("       Lição real: backup offline restaura tudo SEM pagar resgate.")
    return 0


def json_hash(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
