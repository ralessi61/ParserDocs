---
title: Incident Postmortem - Disservizio Servizio Autenticazione SSO
date: 2026-05-02
severity: P1
service: Identity-Provider-Keycloak
---

# Incident Postmortem - Disservizio Servizio Autenticazione SSO

## Sintesi dell'Incidente
In data 2026-05-02 dalle ore 08:42 alle ore 09:25 CEST si è verificata una temporanea indisponibilità del cluster di autenticazione OpenID Connect / Keycloak, con impossibilità di accesso per circa 1.400 dipendenti e collaboratori aziendali alle applicazioni interne.

## Timeline degli Eventi
- **08:40**: Il task notturno di pulizia delle sessioni scadute ha acquisito un lock di tabella esclusivo sul database primario.
- **08:42**: Le connessioni al pool HikarusCP hanno raggiunto la saturazione (max_connections = 200).
- **08:45**: L'healthcheck HTTP di Kubernetes ha iniziato a restituire 503 Service Unavailable sui pod Keycloak.
- **08:50**: Allarme PagerDuty inoltrato all'ingegnere reperibile.
- **09:10**: Esecuzione del comando di kill della query bloccante su PostgreSQL e riavvio graduale del deployment Kubernetes.
- **09:25**: Tutti i pod ritornati in stato `Ready`. Traffico di autenticazione completamente ristabilito.

## Causa Radice (Root Cause)
Una migrazione schema eseguita il giorno precedente non conteneva l'indice composito su `user_session(created_timestamp, realm_id)`. La query pianificata di cleanup ha pertanto effettuato un Sequential Scan bloccante sull'intera tabella contenente 8 milioni di record.

## Azioni Correttive Preventive
1. Aggiunta dell'indice mancante con flag `CONCURRENTLY`.
2. Segmentazione del cleanup in batch da 5.000 righe con sleep di 200ms per non stressare il locking.
3. Riconfigurazione delle soglie di alert Prometheus per saturazione pool connessioni al 75%.
