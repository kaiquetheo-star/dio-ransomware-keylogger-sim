#!/usr/bin/env python3
"""
gerar_arquivos_teste.py — cria arquivos falsos na pasta lab/ para o
desafio de ransomware simulado (DIO).

⚠️ EDUCACIONAL: os arquivos são 100% fictícios e ficam dentro de lab/.
"""
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent / "lab"

FILES = {
    "funcionarios.csv": (
        "id,nome,cargo,salario\n"
        "1,Fulano de Tal,Analista,5000\n"
        "2,Beltrana Silva,Dev,8000\n"
        "3,Cicrano Souza,QA,6000\n"
    ),
    "senhas_antigas.txt": (
        "# lembretes antigos (fictícios!)\n"
        "email: exemplo@exemplo.com -> senha: NAO-E-SENHA-REAL-123\n"
        "wifi-lab: rede-do-laboratorio-2GHz\n"
    ),
    "relatorio.md": (
        "# Relatório trimestral (fake)\n\n"
        "- Meta Q1: 100% atingida\n"
        "- Meta Q2: 87%\n"
        "- Observação: arquivo criado só para o lab de criptografia.\n"
    ),
}


def main() -> int:
    LAB.mkdir(parents=True, exist_ok=True)
    for name, content in FILES.items():
        (LAB / name).write_text(content, encoding="utf-8")
        print(f"[+] criado: lab/{name} ({len(content)} bytes)")
    print(f"\n[+] {len(FILES)} arquivos de teste em {LAB}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
