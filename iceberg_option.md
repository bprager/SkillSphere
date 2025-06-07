# Should UCLA Radiation Oncology Add **Apache Iceberg** to the Pipeline?
*(Assessment of options, pros/cons, risks, and a 6-month decision timeline)*

---

## 1 | Where Iceberg Fits in the Current Design
| Layer            | Today (proposed)                             | Iceberg-Enabled Variant                       | What Changes? |
|------------------|----------------------------------------------|----------------------------------------------|---------------|
| Curated store    | **Delta Lake** tables on Ceph-NVMe           | **Iceberg** tables on the same Parquet files | Swap table format & catalog; files stay put. |
| Analytics query  | Trino / Spark SQL                            | _unchanged_ — both engines speak Iceberg     | No refactor. |
| Cloud share-out  | De-ID Parquet pushed → GCP BigQuery external | **Native Iceberg in BigQuery & Snowflake** :contentReference[oaicite:0]{index=0} | Removes copy/convert step. |
| Catalog          | Hive Metastore (Delta)                       | **REST/Iceberg Catalog** (AWS Glue, Nessie)  | Extra micro-service; supports multi-cluster. |

---

## 2 | Advantages of Iceberg for UCLA

| Benefit | Why It Helps Radiation Oncology |
|---------|----------------------------------|
| **Open & Vendor-Neutral** | Works with Spark, Flink, Snowflake, BigQuery, Trino, Athena. Lowers lock-in vs Databricks-centric Delta. :contentReference[oaicite:1]{index=1} |
| **Hidden & Evolving Partitions** | Iceberg rewrites partition layouts without data copy—ideal when dose-grid or study-date columns change mid-trial. :contentReference[oaicite:2]{index=2} |
| **Snapshot Isolation & Time-Travel** | Every model can reproduce the *exact* patient cohort used in a previous snapshot—critical for FDA reproducibility. :contentReference[oaicite:3]{index=3} |
| **Merge-On-Read Deletes** | Soft-deletes PHI rows without rewriting whole files; simplifies “right-to-be-forgotten” requests. |
| **Incremental Streaming Reads** | Spark/Flink can subscribe to table change logs—reduces Kafka topic sprawl for downstream ML feature pipelines. |
| **Column-Level Statistics** | Faster “…WHERE tumor_site='H&N'” queries; smaller scan windows on 100 TB Parquet stores. |

---

## 3 | Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Migration Complexity** | Rewrite jobs, QA → delay go-live | Incremental dual-format period (Delta **&** Iceberg) via `spark.read.format("delta/iceberg")`. |
| **Catalog Sprawl** | New REST catalog adds infra overhead | Use managed Glue or open-source **Project Nessie**; deploy HA behind UCLA DMZ. |
| **Staff Ramp-Up** | Iceberg concepts (manifest, snapshot) unfamiliar | 2-week enablement workshop + pair-programming; Iceberg SQL is ANSI-compliant, easing adoption. |
| **Feature Parity Gaps** | Delta has native Change-Data-Feed & OPTIMIZE Z-ORDER | Iceberg’s v2 spec adds equality deletes and merge; Trino provides `ALTER TABLE REWRITE`. |
| **Large Binary Objects** | Raw DICOM (JPEG2K) not columnar | Keep images in object storage (Ceph RGW); store *metadata* rows in Iceberg for joinability. |
| **HIPAA Logging** | Need PHI access audit at row level | Enable Iceberg’s `scan.report-metrics` + Trino session logging to tie query → user. |

---

## 4 | Decision Options

| Option | Description | When to Choose |
|--------|-------------|----------------|
| **A. Stay Delta-Only** | Maintain Delta in Ceph; export Parquet for cloud | Minimum change; acceptable if most analytics stay on-prem. |
| **B. Dual-Write (Delta + Iceberg)** | Ingest stream → write both formats (Spark 3.5) | 6-month evaluation; switch off Delta once Iceberg stable. |
| **C. Iceberg-First** | Convert curated Delta tables to Iceberg; new ingest writes Iceberg only | Choose if multi-cloud analytics / Snowflake tie-in is top priority. |

---

## 5 | Suggested Timeline (Fast-Track: 6 Months)

| Month | Milestone | Success Gate |
|-------|-----------|--------------|
| **0-1** | Lab PoC: Spin up Trino + Iceberg catalog on dev Ceph | Query latency within 10 % of Delta |
| **1-2** | Dual-write branch from Spark ETL; convert **1 TB** pilot cohort | All Great Expectations tests pass |
| **2-3** | Enable BigQuery Iceberg external table for de-ID data share | Cross-cloud query succeeds < 30 s |
| **3-4** | Migrate ML feature store (Feast) to Iceberg offline store | Training pipeline unchanged |
| **4-5** | Security & PHI audit: snapshot access logs, row deletes | Zero critical findings |
| **5-6** | Cut-over decision: retain dual or deprecate Delta | GPU model retrain reproducible via snapshot rollback |

---

## 6 | Recommendation

**Adopt Option B (Dual-Write for 6 months).**
It preserves momentum toward go-live, lets teams benchmark side-by-side, and positions UCLA for **open lakehouse interoperability** (Snowflake, BigQuery, Athena) without forcing a big-bang migration. If KPIs on performance, security, and team adoption clear by Month 5, deprecate Delta and standardise on Iceberg v2.

This phased approach upgrades robustness (snapshot isolation, hidden partitions) and elevates maturity at the application layer (federated analytics, easier PHI delete workflows) while containing risk.

