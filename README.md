# Investment Intelligence public data transport

Public projections from the private Stock and Crypto producers. No custom workflow, scanner, calculation engine or report renderer.

| Path | Purpose |
| --- | --- |
| stocks/latest_scan.json, stocks/report_core.json, stocks/full_universe_technical_snapshot.json | Stocks scanner and report inputs |
| stocks/calibration_ledger.json | Public Stocks calibration |
| bvb/vumanchu_orange_latest.json | Isolated BVB output |
| crypto/latest_scan.json, crypto/current_4h_scan.json, crypto/previous_4h_scan.json | Crypto latest and 4H continuity |
| crypto/calibration_ledger* | Public ledger, manifest and referenced segments |

These public RAW paths remain required by Business while both source engines are private. Historical Pages runs are not a data dependency. Do not archive this transport, replace public projections with private history or make private engines public to remove it.

[Canonical operating architecture](https://github.com/catalin6100/crypto-trend-engine/blob/main/docs/architecture.md) defines ownership and recovery. RAW URLs and formats are unchanged.
