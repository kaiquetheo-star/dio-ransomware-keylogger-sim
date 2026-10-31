# 🦠 Ransomware & Keylogger Simulados em Python — Lab Educacional

> Projeto do desafio de **Cibersegurança** da [DIO](https://www.dio.me):
> simulação de malwares (ransomware e keylogger) em ambiente 100% controlado, com foco em **entender para defender**.

🌎 **English version:** [README.en.md](README.en.md)

---

## ⚠️ Aviso ético — leia antes de rodar

Este projeto existe **apenas para fins educacionais**, no contexto do desafio da DIO:

- O "ransomware" opera **exclusivamente dentro da pasta `lab/`** deste repositório — os scripts possuem **trava de segurança** e se recusam a tocar qualquer outro caminho;
- Os arquivos cifrados são **fictícios**, criados por `gerar_arquivos_teste.py`;
- O keylogger foi escrito **para rodar na SUA própria máquina**, capturando teclas de teste; **sem persistência, sem ocultação de processo, sem evasão de antivírus**;
- O "envio por e-mail" é demonstrado contra um **servidor SMTP de captura local** (MailHog) — nenhum servidor real, nenhuma credencial no código;
- **Usar técnicas deste projeto contra sistemas ou dados de terceiros sem autorização é CRIME** (Brasil: art. 154-A do Código Penal e Lei 12.737/2012). O objetivo é entender a mecânica das ameaças para construir defesas melhores.

## 📑 Índice

1. [Como o ransomware funciona](#-como-o-ransomware-funciona)
2. [Parte 1 — Ransomware simulado](#-parte-1--ransomware-simulado)
3. [Como o keylogger funciona](#-como-o-keylogger-funciona)
4. [Parte 2 — Keylogger simulado](#-parte-2--keylogger-simulado)
5. [Como rodar o laboratório](#-como-rodar-o-laboratório)
6. [🛡️ Defesa e prevenção](#️-defesa-e-prevenção)
7. [Reflexão crítica](#-reflexão-crítica)
8. [Evidências](#-evidências)
9. [Estrutura do repositório](#-estrutura-do-repositório)
10. [Referências](#-referências)

---

## 🔐 Como o ransomware funciona

Ransomware é um malware que **torna dados inacessíveis** (criptografia com chave que só o atacante tem) e cobra resgate pela "devolução". A mecânica essencial, que este lab reproduz em miniatura:

1. **Gera uma chave simétrica** — aqui usamos `Fernet` da biblioteca `cryptography` (AES-128-CBC + HMAC-SHA256: confidencialidade **e** integridade);
2. **Cifra os arquivos da vítima no próprio lugar** — o conteúdo vira um blob sem sentido (`gAAAAA...`);
3. **Deixa uma nota de resgate** — pressão psicológica (prazo, ameaça, instrução de pagamento em cripto);
4. **No mundo real**: a chave nunca fica na máquina da vítima (o simulado guarda em `lab/.chave.key` justamente para reverter o lab) e o malware tenta apagar shadow copies, espalhar-se pela rede e persistir — **isso NÃO está implementado aqui de propósito**.

> 💡 A lição estrutural: criptografia é uma tecnologia **boa** — o crime está no uso (cifrar dados alheios + extorsão). O mesmo Fernet deste lab protege arquivos legítimos.

## 🧪 Parte 1 — Ransomware simulado

```bash
python ransomware/gerar_arquivos_teste.py   # cria 3 arquivos fictícios em lab/
python ransomware/ransomware_sim.py         # cifra, cria nota de resgate
python ransomware/decrypt_sim.py            # decifra e confere SHA-256
```

O que cada script faz:

| Script | Ação | Proteção embutida |
|---|---|---|
| `gerar_arquivos_teste.py` | cria CSV, TXT e MD fictícios em `lab/` | nada sensível |
| `ransomware_sim.py` | gera `lab/.chave.key`, manifesto SHA-256, cifra os arquivos, escreve `LEIA_ME_RESGATE.txt` | **só opera dentro de `lab/`** |
| `decrypt_sim.py` | decifra com a chave, **compara SHA-256 de cada arquivo com o manifesto**, remove chave/nota | recusa rodar sem chave/manifesto |

Saída da descriptografia (evidência real do lab):

```
[*] DECIFRADO: funcionarios.csv    | sha256 conferido: OK
[*] DECIFRADO: relatorio.md        | sha256 conferido: OK
[*] DECIFRADO: senhas_antigas.txt  | sha256 conferido: OK
[DONE] 3/3 arquivo(s) restaurado(s) e verificado(s).
```

> 🧠 **Detalhe profissional:** o manifesto de hash reproduz a lógica que defensores usam ao responder incidentes reais — provar que a restauração é fiel ao original.

## ⌨️ Como o keylogger funciona

Keylogger registra **tudo que é digitado** no teclado e exfiltra o registro. Neste lab:

1. **Captura** — `pynput.keyboard.Listener` registra cada tecla (imprimíveis como caractere, especiais como `[ENTER]`, `[ESC]`...);
2. **Registro** — acumula em arquivo de log oculto (`lab/.keylog.txt`);
3. **"Furtividade" didática** — execução sem console via `pythonw.exe keylogger/keylogger_sim.py --hidden` (a saída vai para `nul`); sem janela, o usuário não percebe. *Furtividade REAL (persistência em registry, processos com nomes enganosos, bypass de antivírus) NÃO faz parte deste lab*;
4. **Exfiltração** — a cada `KEYLOG_SEND_EVERY` teclas, o log sai por **e-mail** (`smtplib`): credenciais vêm **exclusivamente de variáveis de ambiente** (`SMTP_HOST/PORT/USER/PASS`, `MAIL_FROM/TO`) — **nada hardcoded**.

## 🧪 Parte 2 — Keylogger simulado

Laboratório executado com **SMTP de captura local** (MailHog em Docker) — zero credenciais reais:

```bash
# servidor de captura (descartável)
docker run -d --name keylogger-smtp -p 127.0.0.1:51025:1025 -p 127.0.0.1:58025:8025 mailhog/mailhog

# keylogger (envia a cada 8 teclas para o MailHog)
$env:KEYLOG_SEND_EVERY='8'; $env:SMTP_HOST='127.0.0.1'; $env:SMTP_PORT='51025'
python keylogger/keylogger_sim.py
```

Console do keylogger no lab (evidência real):

```
[*] keylogger simulado gravando em ...\lab\.keylog.txt
[*] envio automático a cada 8 teclas -> 127.0.0.1:51025
[+] envio #1: log (8 chars) -> 127.0.0.1:51025
[+] envio #2: log (8 chars) -> 127.0.0.1:51025
[*] ESC — encerrando keylogger (simulação).
```

E no MailHog chegaram duas mensagens, de `keylogger@lab.local` para `vitima@lab.local`, com os trechos capturados no corpo (`senha-do`, `lab-123-`). É exatamente assim que credenciais roubadas por keylogger real chegam ao atacante.

> 💡 **Variante Gmail (documento, não executada):** em produção de um atacante real o destino seria um SMTP externo. Basta definir `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER`/`SMTP_PASS` (**app password**, nunca a senha normal) — o código já suporta STARTTLS + login. Neste lab usamos MailHog por segurança e reprodutibilidade.

## 🔁 Como rodar o laboratório

```bash
git clone https://github.com/kaiquetheo-star/dio-ransomware-keylogger-sim.git
cd dio-ransomware-keylogger-sim

python -m venv .venv
.venv\Scripts\pip install -r requirements.txt        # Linux/Mac: .venv/bin/pip
.venv\Scripts\python ransomware/gerar_arquivos_teste.py
.venv\Scripts\python ransomware/ransomware_sim.py
.venv\Scripts\python ransomware/decrypt_sim.py
# keylogger: veja Parte 2 (requer ambiente gráfico; SMTP local via Docker)
```

`lab/`, chaves e logs ficam fora do git (`.gitignore`).

## 🛡️ Defesa e prevenção

Contra ransomware:

| Camada | Medida | Por que funciona |
|---|---|---|
| Backup | **3-2-1** (3 cópias, 2 mídias, 1 offline/imutável) | resgate fica inútil: restaura **sem pagar** |
| Antivírus/EDR | proteção comportamental (bloqueio de criptografia em massa) | detecta o *comportamento*, não a assinatura |
| Menor privilégio | usuário sem admin; serviços com conta de mínimo acesso | limita o alcance da cifra e a movimentação lateral |
| Atualizações | SO, browser, Office, firmware | ransomware entra por vulnerabilidade conhecida |
| Regras de Office | bloquear macros de e-mail/internet | principal porta de entrada corporativa |
| Segmentação | SMB restrito, sem compartilhamentos amplos | impede o "efeito dominó" na rede |
| Resposta | **NÃO pagar**; isolar máquina; acionar plano de incidentes | pagar financia o crime e não garante restauração |

Contra keylogger:

| Camada | Medida | Por que funciona |
|---|---|---|
| MFA | segundo fator em tudo | senha capturada vira inútil sozinha |
| Password manager | digitação automática/injeção de credenciais | reduz o que "passa pelo teclado" |
| Antivírus/EDR | detecta hooks de teclado e processos suspeitos | keylogger precisa se prender ao sistema |
| Firewall (saída!) | controlar conexões de saída de processos | exfiltração precisa sair para a internet |
| Sandboxing | apps duvidosos isolados | impede acesso ao teclado global |
| Conscientização | phishing = principal entrega de ambos | **o elo mais fraco é humano** |

**Indicadores de comprometimento** que este lab ilustra: arquivos renomeados/corrompidos em massa + nota de texto estranha (ransomware); processo sem assinatura lendo teclado + tráfego SMTP incomum (keylogger).

## 🤔 Reflexão crítica

1. **IA baixou a barreira** — gerar phishing crível e código malicioso simples ficou trivial; a resposta não é técnica isolada, é **defesa em profundidade + pessoas treinadas**.
2. **Criptografia não é vilã** — a mesma Fernet que "sequestra" no lab cifra backups e mensagens legítimas. Segurança é questão de **quem controla a chave**.
3. **O antídoto do ransomware é chato** — backup offline testado regularmente vale mais que qualquer ferramenta mágica.
4. **O antídoto do keylogger é arquitetural** — MFA mata a maior parte do valor do roubo de senha.
5. **Entender o ataque é pré-requisito da defesa** — foi exatamente o que este lab exercitou: reproduzir a mecânica em miniatura para reconhecer os indicadores no mundo real.

## 📸 Evidências

| # | Arquivo | O que mostra |
|---|---|---|
| 01 | `01-gerar-arquivos.png` | 3 arquivos fictícios criados em `lab/` |
| 02 | `02-ransomware-exec.png` | chave gerada, manifesto SHA-256, 3 arquivos cifrados, nota de resgate |
| 03 | `03-resgate-cifrado.png` | conteúdo da nota + arquivo vira blob `gAAAAA...` |
| 04 | `04-decrypt-integridade.png` | decifragem com SHA-256 conferido 3/3 |
| 05 | `05-keylogger-envios.png` | console do keylogger com 2 envios automáticos |
| 06 | `06-email-mailhog.png` | e-mails capturados no MailHog (API v2) |

> 📸 Os PNGs são **renders das saídas reais** capturadas neste lab (conteúdo autêntico; formatação visual para leitura). Ambiente: Windows 11 + Python 3.11 (venv) + MailHog em Docker. Logs brutos em `results/` (não versionados).

## 📁 Estrutura do repositório

```
dio-ransomware-keylogger-sim/
├── README.md / README.en.md
├── requirements.txt            # cryptography, pynput, aiosmtpd
├── ransomware/
│   ├── gerar_arquivos_teste.py # cria lab/ com arquivos fictícios
│   ├── ransomware_sim.py       # cifra + nota de resgate (travado em lab/)
│   └── decrypt_sim.py          # decifra + confere integridade
├── keylogger/
│   └── keylogger_sim.py        # captura + log + envio SMTP automático
├── images/                     # evidências
└── lab/                        # área de trabalho do lab (fora do git)
```

## 📚 Referências

- [cryptography (Fernet) — documentação](https://cryptography.io/en/latest/fernet/)
- [pynput — documentação](https://pynput.readthedocs.io/en/latest/)
- [smtplib — Python docs](https://docs.python.org/3/library/smtplib.html)
- [aiosmtpd — servidor SMTP de debug](https://aiosmtpd.readthedocs.io/)
- [MailHog — captura de e-mails](https://github.com/mailhog/MailHog)
- [CERT.br — Cartilha de Segurança](https://cartilha.cert.br/)
- [IBM — Cost of a Data Breach / X-Force Threat Report](https://www.ibm.com/reports/data-breach)

---

⭐ Se este material te ajudou, considere dar uma estrela no repositório!
