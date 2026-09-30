# Procedura Onboarding Tecnico Nuovi Ingegneri

Data ultimo aggiornamento: 2026-02-01  
Responsabile: Team Lead Platform Engineering  

## Benvenuto nel Team Tecnico
Questa guida contiene tutti i passaggi necessari per rendere operativo il proprio ambiente di sviluppo locale entro le prime 48 ore dall'ingresso in azienda.

## Step 1: Configurazione Chiavi e VPN
1. Generare una coppia di chiavi ED25519 con il comando:
   `ssh-keygen -t ed25519 -C "nome.cognome@internal.corp"`
2. Caricare la chiave pubblica sul portale aziendale Identity Access Manager.
3. Installare il client OpenVPN e scaricare il profilo `.ovpn` dedicato alla propria sede.

## Step 2: Accesso ai Repository Git
- Server GitLab interno: `https://gitlab.internal.corp`
- Verificare la corretta configurazione del commit signing con GPG.
- Clonare il repository template per i microservizi:
  `git clone git@gitlab.internal.corp:platform/service-template.git`

## Step 3: Ambiente Docker e Kubernetes
Tutti gli sviluppatori utilizzano Docker Desktop o Podman con cluster locale k3d / Minikube.
Eseguire il comando di bootstrap:
`make setup-dev-cluster`

## Contatti di Supporto
Per qualsiasi problema con credenziali e token, aprire un ticket interno sul canale Slack `#help-it-support`.
