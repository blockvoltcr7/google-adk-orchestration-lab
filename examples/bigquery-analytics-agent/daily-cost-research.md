# BigQuery Demo Daily Cost Research

Checked: 2026-08-18. Prices are USD and use Google Cloud's listed US
multi-region rates. Taxes, negotiated discounts, credits, currency conversion,
and other workloads on the same billing account are excluded.

## Bottom line

Leaving this demo dataset and table in BigQuery while nobody uses the agent has
an estimated **$0.00/day bill under the BigQuery free tier**. BigQuery is
serverless, so there is no continuously running database instance and no idle
compute charge. Google describes BigQuery as requiring no infrastructure to
provision or manually scale; on-demand compute is charged for bytes processed
by queries. Merely retaining a dataset/table does not run analysis compute.
[BigQuery overview](https://cloud.google.com/bigquery/docs/introduction),
[BigQuery pricing](https://cloud.google.com/bigquery/pricing)

Storage is the only ongoing BigQuery cost for the inactive demo. The observed
table footprint is 5,648,632 active logical bytes, approximately **0.00526
GiB**. Google's free tier includes the first **10 GiB of storage per month per
billing account**, so this table consumes about 0.053% of that allowance and
costs $0 while the account remains within it.
[BigQuery free usage tier](https://cloud.google.com/bigquery/pricing#free-tier)

## Rates and calculations

| Item | Official US rate | Demo estimate |
| --- | ---: | ---: |
| Active logical storage | $0.000031507/GiB-hour; first 10 GiB/month free | $0/day within free tier |
| Idle storage if the free tier is already exhausted | Same rate | about $0.00000398/day; about $0.000121/month using 730 hours |
| On-demand analysis | $6.25/TiB processed; first 1 TiB/month free | $0 with available free-tier allowance |
| One agent query at the configured 100 MiB safety ceiling | $6.25/TiB beyond free tier | at most about $0.000596/query |

The storage calculation is:

```text
5,648,632 / 1,073,741,824 GiB * $0.000031507/GiB-hour * 24 hours
= $0.000003978/day
```

The maximum-query calculation is:

```text
100 MiB / 1,048,576 MiB per TiB * $6.25/TiB
= $0.000596046 per query
```

Actual analytical queries over this 5.39 MiB table will generally process less
than the 100 MiB safety ceiling, especially when they select only needed
columns. Google bills on-demand queries according to bytes processed in the
selected columns; cached results and queries that return an error are not
charged.
[BigQuery on-demand pricing details](https://cloud.google.com/bigquery/pricing#on_demand_pricing)

Google lists active logical storage in the US at
**$0.000031507/GiB-hour** and prorates it per MiB per second. The dataset uses
the default logical storage billing model; Google documents that datasets
default to logical billing when no model is specified.
[BigQuery storage pricing](https://cloud.google.com/bigquery/pricing#storage),
[BigQuery storage billing models](https://cloud.google.com/bigquery/docs/storage_overview#storage_billing_models)

## Interpretation

- **Inactive day:** $0 under the free tier; approximately $0.000004/day in the
  conservative scenario where the billing account's 10 GiB allowance has
  already been consumed elsewhere.
- **Active testing day:** storage remains effectively zero, plus query charges.
  With unused query free tier, those queries are $0. If the 1 TiB allowance is
  already exhausted, every 100 MiB-capped query is at most about $0.000596.
- **Dataset/table existence:** an empty dataset or table metadata does not
  create an idle compute meter. Stored table data is billed as storage, and
  query jobs are billed as analysis. A separately purchased BigQuery capacity
  reservation would be different, but this demo uses on-demand pricing and has
  no reservation.

Free-tier limits and rates apply at the billing-account level, not as a fresh
allowance exclusive to this demo. Other BigQuery storage and queries attached
to the same billing account can therefore consume the allowances first.
[BigQuery pricing account scope](https://cloud.google.com/bigquery/pricing)

