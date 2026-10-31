# 🦠 Simulated Ransomware & Keylogger in Python — Educational Lab

> Project for the [DIO](https://www.dio.me) **Cybersecurity** challenge:
> simulating malware (ransomware and keylogger) in a 100% controlled environment, focused on **understanding in order to defend**.

🌎 **Versão em português:** [README.md](README.md)

---

## ⚠️ Ethical disclaimer — read before running

This project exists **for educational purposes only**, in the context of the DIO challenge:

- The "ransomware" operates **exclusively inside the `lab/` folder** of this repository — the scripts have a **safety guard** and refuse to touch any other path;
- The encrypted files are **fake**, created by `gerar_arquivos_teste.py`;
- The keylogger was written **to run on YOUR own machine**, capturing test keystrokes; **no persistence, no process hiding, no antivirus evasion**;
- The "email delivery" is demonstrated against a **local capture SMTP server** (MailHog in Docker) — no real server, no credentials in the code;
- **Using these techniques against third-party systems or data without authorization is a CRIME** (Brazil: art. 154-A of the Penal Code and Law 12.737/2012). The goal is to understand the mechanics of these threats in order to build better defenses.

## 📑 Table of contents

1. [How the ransomware works](#-how-the-ransomware-works)
2. [Part 1 — Simulated ransomware](#-part-1--simulated-ransomware)
3. [How the keylogger works](#-how-the-keylogger-works)
4. [Part 2 — Simulated keylogger](#-part-2--simulated-keylogger)
5. [How to run the lab](#-how-to-run-the-lab)
6. [🛡️ Defense and prevention](#️-defense-and-prevention)
7. [Critical reflection](#-critical-reflection)
8. [Evidence](#-evidence)
9. [Repository structure](#-repository-structure)
10. [References](#-references)

---

## 🔐 How the ransomware works

Ransomware is malware that **makes data inaccessible** (encryption with a key only the attacker has) and demands a ransom for the "return". The essential mechanics, reproduced in miniature by this lab:

1. **Generates a symmetric key** — here we use `Fernet` from the `cryptography` library (AES-128-CBC + HMAC-SHA256: confidentiality **and** integrity);
2. **Encrypts the victim's files in place** — the content becomes a meaningless blob (`gAAAAA...`);
3. **Drops a ransom note** — psychological pressure (deadline, threat, crypto payment instructions);
4. **In the real world**: the key never stays on the victim's machine (the simulation keeps it in `lab/.chave.key` precisely so the lab can be reversed) and the malware tries to wipe shadow copies, spread through the network and persist — **none of that is implemented here on purpose**.

> 💡 The structural lesson: encryption is a **good** technology — the crime lies in the use (encrypting other people's data + extortion). The same Fernet in this lab protects legitimate files.

## 🧪 Part 1 — Simulated ransomware

```bash
python ransomware/gerar_arquivos_teste.py   # creates 3 fake files in lab/
python ransomware/ransomware_sim.py         # encrypts, drops ransom note
python ransomware/decrypt_sim.py            # decrypts and checks SHA-256
```

What each script does:

| Script | Action | Built-in protection |
|---|---|---|
| `gerar_arquivos_teste.py` | creates fake CSV, TXT and MD in `lab/` | nothing sensitive |
| `ransomware_sim.py` | generates `lab/.chave.key`, SHA-256 manifest, encrypts the files, writes `LEIA_ME_RESGATE.txt` | **operates only inside `lab/`** |
| `decrypt_sim.py` | decrypts with the key, **compares each file's SHA-256 against the manifest**, removes key/note | refuses to run without key/manifest |

Decryption output (real lab evidence):

```
[*] DECIFRADO: funcionarios.csv    | sha256 conferido: OK
[*] DECIFRADO: relatorio.md        | sha256 conferido: OK
[*] DECIFRADO: senhas_antigas.txt  | sha256 conferido: OK
[DONE] 3/3 arquivo(s) restaurado(s) e verificado(s).
```

> 🧠 **Professional detail:** the hash manifest mirrors the logic defenders use when responding to real incidents — proving the restoration is faithful to the original.

## ⌨️ How the keylogger works

A keylogger records **everything typed** on the keyboard and exfiltrates the log. In this lab:

1. **Capture** — `pynput.keyboard.Listener` registers every key (printable as character, special as `[ENTER]`, `[ESC]`...);
2. **Logging** — accumulates into a hidden log file (`lab/.keylog.txt`);
3. **Didactic "stealth"** — console-less execution via `pythonw.exe keylogger/keylogger_sim.py --hidden` (output goes to `nul`); without a window, the user doesn't notice. *REAL stealth (registry persistence, misleadingly named processes, antivirus bypass) is NOT part of this lab*;
4. **Exfiltration** — every `KEYLOG_SEND_EVERY` keystrokes, the log goes out via **email** (`smtplib`): credentials come **exclusively from environment variables** (`SMTP_HOST/PORT/USER/PASS`, `MAIL_FROM/TO`) — **nothing hardcoded**.

## 🧪 Part 2 — Simulated keylogger

The lab ran against a **local capture SMTP server** (MailHog in Docker) — zero real credentials:

```bash
# disposable capture server
docker run -d --name keylogger-smtp -p 127.0.0.1:51025:1025 -p 127.0.0.1:58025:8025 mailhog/mailhog

# keylogger (sends every 8 keystrokes to MailHog)
$env:KEYLOG_SEND_EVERY='8'; $env:SMTP_HOST='127.0.0.1'; $env:SMTP_PORT='51025'
python keylogger/keylogger_sim.py
```

Keylogger console during the lab (real evidence):

```
[*] keylogger simulado gravando em ...\lab\.keylog.txt
[*] envio automático a cada 8 teclas -> 127.0.0.1:51025
[+] envio #1: log (8 chars) -> 127.0.0.1:51025
[+] envio #2: log (8 chars) -> 127.0.0.1:51025
[*] ESC — encerrando keylogger (simulação).
```

And two messages arrived in MailHog, from `keylogger@lab.local` to `vitima@lab.local`, with the captured fragments in the body (`senha-do`, `lab-123-`). That is exactly how credentials stolen by a real keylogger reach the attacker.

> 💡 **Gmail variant (documented, not executed):** a real attacker's destination would be an external SMTP. Just set `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER`/`SMTP_PASS` (**app password**, never the normal password) — the code already supports STARTTLS + login. MailHog was used in this lab for safety and reproducibility.

## 🔁 How to run the lab

```bash
git clone https://github.com/kaiquetheo-star/dio-ransomware-keylogger-sim.git
cd dio-ransomware-keylogger-sim

python -m venv .venv
.venv\Scripts\pip install -r requirements.txt        # Linux/Mac: .venv/bin/pip
.venv\Scripts\python ransomware/gerar_arquivos_teste.py
.venv\Scripts\python ransomware/ransomware_sim.py
.venv\Scripts\python ransomware/decrypt_sim.py
# keylogger: see Part 2 (requires a graphical environment; local SMTP via Docker)
```

`lab/`, keys and logs stay out of git (`.gitignore`).

## 🛡️ Defense and prevention

Against ransomware:

| Layer | Measure | Why it works |
|---|---|---|
| Backup | **3-2-1** (3 copies, 2 media, 1 offline/immutable) | ransom becomes pointless: restore **without paying** |
| Antivirus/EDR | behavioral protection (mass-encryption blocking) | detects the *behavior*, not the signature |
| Least privilege | user without admin; services with minimal accounts | limits encryption reach and lateral movement |
| Updates | OS, browser, Office, firmware | ransomware enters through known vulnerabilities |
| Office rules | block macros from email/internet | top corporate entry point |
| Segmentation | restricted SMB, no broad shares | prevents the network "domino effect" |
| Response | **do NOT pay**; isolate the machine; trigger the incident plan | paying funds crime and doesn't guarantee restoration |

Against keyloggers:

| Layer | Measure | Why it works |
|---|---|---|
| MFA | second factor everywhere | a captured password alone becomes useless |
| Password manager | automatic typing/credential injection | reduces what "goes through the keyboard" |
| Antivirus/EDR | detects keyboard hooks and suspicious processes | a keylogger must hook into the system |
| Firewall (egress!) | control outbound connections per process | exfiltration must leave to the internet |
| Sandboxing | dubious apps isolated | blocks global keyboard access |
| Awareness | phishing is the main delivery channel for both | **the weakest link is human** |

**Indicators of compromise** this lab illustrates: mass file renaming/corruption + odd text note (ransomware); unsigned process reading the keyboard + unusual SMTP traffic (keylogger).

## 🤔 Critical reflection

1. **AI lowered the barrier** — generating convincing phishing and simple malicious code became trivial; the answer is not a single technical control, it is **defense in depth + trained people**.
2. **Encryption is not the villain** — the same Fernet that "kidnaps" in the lab encrypts backups and legitimate messages. Security is a question of **who controls the key**.
3. **The ransomware antidote is boring** — an offline backup, tested regularly, beats any magic tool.
4. **The keylogger antidote is architectural** — MFA kills most of the value of a stolen password.
5. **Understanding the attack is a prerequisite of defense** — exactly what this lab exercised: reproduce the mechanics in miniature to recognize the indicators in the real world.

## 📸 Evidence

| # | File | What it shows |
|---|---|---|
| 01 | `01-gerar-arquivos.png` | 3 fake files created in `lab/` |
| 02 | `02-ransomware-exec.png` | key generated, SHA-256 manifest, 3 files encrypted, ransom note |
| 03 | `03-resgate-cifrado.png` | note content + file becomes a `gAAAAA...` blob |
| 04 | `04-decrypt-integridade.png` | decryption with SHA-256 verified 3/3 |
| 05 | `05-keylogger-envios.png` | keylogger console with 2 automatic sends |
| 06 | `06-email-mailhog.png` | emails captured in MailHog (API v2) |

> 📸 The PNGs are **renders of the real output** captured in this lab (authentic content; visual formatting for readability). Environment: Windows 11 + Python 3.11 (venv) + MailHog in Docker. Raw logs in `results/` (not committed).

## 📁 Repository structure

```
dio-ransomware-keylogger-sim/
├── README.md / README.en.md
├── requirements.txt            # cryptography, pynput, aiosmtpd
├── ransomware/
│   ├── gerar_arquivos_teste.py # creates lab/ with fake files
│   ├── ransomware_sim.py       # encrypts + ransom note (locked to lab/)
│   └── decrypt_sim.py          # decrypts + integrity check
├── keylogger/
│   └── keylogger_sim.py        # capture + log + automatic SMTP sending
├── images/                     # evidence
└── lab/                        # lab working area (out of git)
```

## 📚 References

- [cryptography (Fernet) — documentation](https://cryptography.io/en/latest/fernet/)
- [pynput — documentation](https://pynput.readthedocs.io/en/latest/)
- [smtplib — Python docs](https://docs.python.org/3/library/smtplib.html)
- [aiosmtpd — debug SMTP server](https://aiosmtpd.readthedocs.io/)
- [MailHog — email capture](https://github.com/mailhog/MailHog)
- [CERT.br — Security Handbook (PT)](https://cartilha.cert.br/)
- [IBM — Cost of a Data Breach / X-Force Threat Report](https://www.ibm.com/reports/data-breach)

---

⭐ If this material helped you, consider starring the repository!
