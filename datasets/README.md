# AFRACANet data packs

Prepared 26 October 2026. These files are not automatically loaded into either
application. They do not replace the current runtime seeds or connect the modules.

For the larger, configurable packs with a populated isolated relational database
and matching graph exports, see [scalable synthetic scenarios](SYNTHETIC.md).
The small replay below remains useful for a quick manual allocation-import demo.

| Pack                                | Contents                                                                                                                | What may be claimed                                                                                                          |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `public/weather/`                   | Actual Open-Meteo/ERA5 API responses for September 2026 at two representative county reference points; 60 daily records | Public gridded weather reanalysis with source, retrieval time, units, and hashes; not on-farm measurements                   |
| `replay/scenario.json`              | 30 fictional farmers, 522 synthetic ledger events, 12 fictional loan histories, and 54 membership links                 | Deterministic workflow replay only; not customer records, validated credit training data, or evidence of predictive accuracy |
| `replay/input-finance-usd-demo.csv` | Thirty illustrative USD allocations in the current approval-import format                                               | Anonymous non-live sandbox scenarios; independent of the fictional KES ledger, with no implied exchange-rate conversion      |

All farmer-region assignments in the replay are synthetic. Joining a fictional
farmer to a real weather reference point does not establish that a real farmer
experienced those conditions. The two reference points are not cadastral locations
or verified farm coordinates. The weather manifest records the requested point;
the raw response records the provider's grid-cell coordinates.

## Reproduce the packs

```powershell
.\.venv\Scripts\python.exe scripts/build_replay_dataset.py
.\.venv\Scripts\python.exe scripts/fetch_public_weather.py --start 2026-09-01 --end 2026-09-30
.\.venv\Scripts\python.exe -m pytest -q tests/test_data_pack.py
```

The replay generator is deterministic for its declared seed and as-of date.
Existing public snapshots are not overwritten unless `--force` is explicitly
provided. Refreshing can change provider data and hashes; retain the version used
for a recorded demonstration. Failed/missing public data is not filled with
synthetic weather. The initial ERA5-Land request lacked precipitation values;
the committed snapshot explicitly requests ERA5, which returned the required fields.

## Import and integration boundaries

The CSV may be previewed in the lender's **Credit allocations** tab for a clearly
labelled replay. It creates imported demo participants; it is not a genuine lender
decision. The JSON catalogue is a synthetic fixture, not a dealer quotation, and
is not automatically imported. The graph/ledger JSON has not yet been adapted
to the AI module's Neo4j schema. That adapter and safe incremental ingestion remain
implementation work. Do not run the existing upstream destructive seeder on a
database containing real records.

The CSV expires on the fixture's explicit date. Regenerate/update a dated replay
intentionally when that scenario expires; do not silently renew actual approvals.
KES ledger amounts and USD test allocations must remain distinct.

## Attribution and permitted use

Public weather: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api),
with ERA5 data via the Copernicus Climate Change Service. Data attribution is
required under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Retain the manifest and show attribution wherever these values are displayed.
Review the [API usage terms](https://open-meteo.com/en/pricing) before commercial
deployment; data licensing and hosted API access are separate questions.

The replay is newly generated fictional material within this repository's MIT
license. It is not calibrated to an actual farmer population and supplies no real
consent, repayment outcome, demand, or underwriting validation evidence.

PayPal's [Developer Testing Agreement](https://www.paypal.com/us/legalhub/paypal/devtest-agreement)
requires anonymous, non-live data for sandbox testing. Keep any future private
partner dataset separate from provider sandbox fixtures and from public Git.
