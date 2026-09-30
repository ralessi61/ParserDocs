# Scheda Tecnica e Architettura Storage SAN Enterprise

Data: 2026-03-25  
Classificazione: Documento Interno Riservato  
Modello Apparato: Dell EMC PowerStore 5000T  

## 1. Caratteristiche Hardware
Lo storage array installato presso il Datacenter Primario adotta un'architettura dual-controller Active/Active (Node A e Node B) collegata tramite fabric Fibre Channel ridondata a 32 Gbps.

- **Capacità Lorda**: 184 TB NVMe All-Flash
- **Capacità Netta (con deduplica 4:1 media)**: ~550 TB utilizzabili
- **IOPS Massimi Dichiarati**: fino a 350.000 IOPS su blocchi 8KB random read
- **Latenza Media**: < 0.45 ms

## 2. Suddivisione LUN e Volumi Logici

### Volume Group A: Cluster Virtualizzazione VMware ESXi
- `LUN-ESXI-PROD-01`: 45 TB, formattato VMFS 6, multi-pathing Round-Robin attivo.
- `LUN-ESXI-PROD-02`: 45 TB, formattato VMFS 6.

### Volume Group B: Database Relazionali Bare-Metal
- `LUN-ORA-DATA-01`: 20 TB, dedicato a tabelle Oracle EBS.
- `LUN-ORA-REDO-01`: 2 TB, volumi a latenza ultrabassa per log di transazione.
- `LUN-PG-DATA-01`: 30 TB, dedicato all'istanza primaria PostgreSQL.

## 3. Politiche di Snapshot e Replica Asincrona
Le snapshot locali vengono acquisite ogni 4 ore con retention di 7 giorni.
La replica verso il Datacenter Secondario (Disaster Recovery) è attiva in modalità asincrona con intervallo RPO target di 15 minuti.
