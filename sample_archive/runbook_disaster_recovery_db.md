# Runbook di Disaster Recovery Database

Data di revisione: 2026-03-15  
Autore: Team Infrastruttura e Database  
Stato: Approvato  

## 1. Obiettivo e Perimetro
Il presente documento descrive le azioni operative obbligatorie per il ripristino dei cluster database PostgreSQL in caso di avaria irreversibile del nodo primario o corruzione dei dati sul datacenter primario.

## 2. Metriche di Riferimento (SLA)
- **RPO (Recovery Point Objective)**: massimo 15 minuti tramite shipping continuo dei WAL verso bucket S3 protetto.
- **RTO (Recovery Time Objective)**: massimo 60 minuti per il reindirizzamento dei carichi applicativi.

## 3. Procedura Operativa di Failover

### Fase A: Accertamento dell'isolamento
1. Verificare l'effettiva non raggiungibilità del nodo `pg-prod-01.internal.corp`.
2. Eseguire comando di verifica heartbeat:
   `crm_mon -1`
3. Assicurarsi che il fencing STONITH sia stato attivato per prevenire condizioni di split-brain.

### Fase B: Promozione della Replica Standby
1. Collegarsi in console sicura sul nodo di replica `pg-prod-02.internal.corp`.
2. Interrompere il replay dei WAL:
   `pg_ctl promote -D /var/lib/postgresql/16/main`
3. Verificare lo stato del log di PostgreSQL per confermare che l'istanza accetta connessioni in scrittura:
   `tail -f /var/log/postgresql/postgresql-16-main.log`

### Fase C: Switch del Virtual IP
Aggiornare il target del bilanciatore HAProxy tramite script di automazione `/opt/scripts/switch_db_vip.sh standby`.
Effettuare test di connessione da un nodo applicativo `app-core-01`.

## 4. Contatti di Reperibilità
In caso di anomalie bloccanti contattare il Lead DBA reperibile al numero interno 4022.
