# BigQuery and Cloud SQL: Service and Cost Notes

Pricing checked against official Google Cloud pages on August 18, 2026. Prices
vary by region, edition, billing model, and future Google changes, so use the
pricing calculator for a production estimate.

## They are separate services

Cloud SQL and BigQuery both understand SQL, but they solve different problems:

| Service | Primary workload | Runtime model | Typical application |
| --- | --- | --- | --- |
| Cloud SQL | Transactional reads and writes | Managed MySQL, PostgreSQL, or SQL Server instance | Application system of record |
| BigQuery | Large analytical scans and aggregations | Serverless data warehouse with separate storage and compute | Reporting, analytics, ML, and BI |

Creating a Cloud SQL database does not automatically create or populate
BigQuery. To use both, choose an explicit integration:

- [BigQuery Cloud SQL federation](https://cloud.google.com/bigquery/docs/cloud-sql-federated-queries)
  queries supported Cloud SQL data in place with `EXTERNAL_QUERY`.
- [Datastream for BigQuery](https://cloud.google.com/datastream-for-bigquery)
  can backfill and continuously replicate operational changes into BigQuery.

This demo needs analytics only, so it uses BigQuery directly and does not create
a Cloud SQL instance.

## BigQuery pricing and this demo

Google's [BigQuery pricing page](https://cloud.google.com/bigquery/pricing)
currently lists:

- First 10 GiB of storage per month free.
- First 1 TiB of on-demand query processing per month free.
- On-demand analysis starting at $6.25 per TiB scanned.
- US active logical storage at $0.000031507 per GiB-hour, about $0.023 per
  GiB-month.

The current demo table is about 0.0053 GiB. Outside the free tier, that is about
$0.00012 per month at the listed active logical-storage rate. Each agent query
is capped at 100 MiB, which is at most about $0.00060 at $6.25 per TiB before
the free tier. With the current table and light testing, the BigQuery portion
should remain inside the free tier if that billing account's monthly allowance
has not already been consumed. Vertex AI model calls are billed separately.

BigQuery is serverless, so there is no database instance to stop. The practical
lifecycle is:

1. `./scripts/provision.sh` creates the dataset and seeds the table.
2. The table automatically expires 30 days after its latest seed.
3. `./scripts/cleanup.sh` previews destruction without deleting anything.
4. `./scripts/cleanup.sh --execute` deletes the demo dataset and its tables.

Google documents the `google_bigquery_dataset` Terraform resource in
[Create datasets](https://cloud.google.com/bigquery/docs/datasets#terraform).

## Cloud SQL pricing for comparison

Google's [Cloud SQL pricing page](https://cloud.google.com/sql/pricing) lists a
shared-core `db-f1-micro` example at $0.0105 per hour, or about $7.67 for a
730-hour month. Cloud SQL storage starts around $0.17 per GB-month, and the
minimum data disk is 10 GB, adding roughly $1.70. That gives an illustrative
floor of about $9.37 per month before regional differences, IP addresses,
network transfer, backup storage, or higher availability.

Cloud SQL can be stopped without deleting its data. Google states in
[Start, stop, and restart instances](https://cloud.google.com/sql/docs/mysql/start-stop-restart-instance)
that stopping suspends instance charges, but storage and IP-address charges
continue. Terraform can also create and destroy a disposable Cloud SQL
instance, but destroying it deletes the database unless it is separately
backed up or protected.
