# Stock & Crypto Signal Bridge

A lightweight **public JSON distribution bridge** for the private stock and crypto signal engines.

Despite the historical repository name `stock-daily-signal-bridge`, this repository now publishes **both STOCKS and CRYPTO machine-readable snapshots** for downstream ChatGPT investment workflows.

The bridge contains **published outputs only**. It does not calculate indicators, scan markets, rank opportunities, or make investment decisions.

---

## Repository role

```text
PRIVATE COMPUTE REPOS
        |
        | generate + validate deterministic artifacts
        |
        +-------------------------------+
        |                               |
        v                               v
stock-daily-signal-engine       crypto-trend-engine
        |                               |
        | publish latest JSON           | publish latest JSON
        |                               |
        +---------------+---------------+
                        |
                        v
          stock-daily-signal-bridge
                  PUBLIC
                        |
              +---------+---------+
              |                   |
              v                   v
 stocks/latest_scan.json   crypto/latest_scan.json
              |                   |
              +---------+---------+
                        |
                        v
          downstream ChatGPT workflows
```

This repository is therefore a **transport / publication layer**, not an analytics engine.

---

# Public endpoints

## Stocks

Repository path:

```text
stocks/latest_scan.json
```

Raw public URL:

```text
https://raw.githubusercontent.com/catalin6100/stock-daily-signal-bridge/main/stocks/latest_scan.json
```

The artifact is produced by the private:

```text
stock-daily-signal-engine
```

It is consumed by:

```text
Daily Stocks — Action Now
```

---

## Crypto

Repository path:

```text
crypto/latest_scan.json
```

Raw public URL:

```text
https://raw.githubusercontent.com/catalin6100/stock-daily-signal-bridge/main/crypto/latest_scan.json
```

The artifact is produced by the private:

```text
crypto-trend-engine
```

It is consumed by the crypto reporting stack, including:

```text
Daily Crypto Signals — Adaptive 20-Layer
Crypto 4H Report Check
```

---

# Current repository structure

```text
.
├── README.md
├── stocks/
│   └── latest_scan.json
└── crypto/
    └── latest_scan.json
```

No analytics code is required in this repository.

---

# Design principles

## 1. Public read, private compute

The calculation engines remain separate from this repository.

This bridge exposes only the machine-readable result that downstream consumers need.

That separation keeps:

- computation code private;
- API keys and repository tokens private;
- collector implementation details isolated;
- public consumption simple;
- ChatGPT access independent from a GitHub connector/plugin.

---

## 2. No GitHub authentication required for consumers

Downstream readers should use the public RAW URLs directly.

For normal consumption:

```text
GitHub account connection = NOT REQUIRED
GitHub plugin/connector    = NOT REQUIRED
```

The JSON can be fetched with ordinary HTTPS.

---

## 3. `latest_scan.json` means latest published snapshot

Both folders expose a stable filename:

```text
latest_scan.json
```

The file is overwritten by the corresponding upstream producer when a newer validated snapshot is published.

Consumers must **not assume freshness from the filename alone**.

Always validate the metadata inside the JSON.

---

# Freshness contract

Every downstream consumer must inspect the artifact before using it.

At minimum, validate:

```text
generated_at_utc
generated_at_europe_bucharest
pipeline_version
```

Then apply the asset-specific freshness contract.

---

## Stocks freshness

Important stock fields include:

```text
timeframe
latest_closed_session
signal_lookback_sessions
data_quality
universe
```

The stock artifact is designed around:

```text
1D_CLOSED_BARS_ONLY
```

The consumer must verify that `latest_closed_session` corresponds to the latest fully completed NYSE session expected before the report.

Do not treat an unfinished current NYSE session as a completed Daily signal.

The artifact also contains explicit provider / freshness diagnostics under:

```text
data_quality
```

A downstream report must surface a limitation rather than silently treating stale or incomplete scanner data as current.

---

## Crypto freshness

Important crypto fields include:

```text
schema_version
report_mode
reference_timezone
current_hour_cycle
universe
status
provider_policy
```

Production crypto snapshots are designed around:

```text
FULL_HOURLY
```

The critical freshness object is:

```text
current_hour_cycle
```

Consumers should verify:

```text
complete = true
current_cycle_coverage_count = analysis_ready_assets
missing_current_1h_assets = []
```

and confirm that:

```text
expected_latest_1h_close_utc
```

matches the expected latest fully completed 1H cycle.

---

# Producer schedules

This repository itself does **not** schedule scans.

Publication is initiated by the upstream private repositories.

## Stocks producer

Current upstream schedule:

```text
Monday–Friday
16:15 Europe/Bucharest
```

The stock engine publishes its validated CLOSED-1D artifact to:

```text
stocks/latest_scan.json
```

The downstream `Daily Stocks — Action Now` report currently runs later at:

```text
17:40 Europe/Bucharest
```

The timing separation is intentional:

```text
collector = deterministic completed-1D snapshot
report    = completed-1D snapshot + current-session execution context
```

---

## Crypto producer

Current primary upstream schedule:

```text
HH:12 every hour, 24/7
Europe/Bucharest
```

Additional backup publication cycles used to protect the 4H report windows run at:

```text
00:27
04:27
08:27
12:27
16:27
20:27
Europe/Bucharest
```

The downstream 4H report currently runs at:

```text
00:50
04:50
08:50
12:50
16:50
20:50
Europe/Bucharest
```

The bridge must therefore expose the newest validated current-hour crypto cycle before the report consumes it.

---

# Stocks artifact

The stock JSON is a deterministic **closed-1D technical snapshot** across the current S&P 500 universe.

Representative top-level fields include:

```json
{
  "generated_at_utc": "...",
  "generated_at_europe_bucharest": "...",
  "pipeline_version": "...",
  "engine": "...",
  "timeframe": "1D_CLOSED_BARS_ONLY",
  "signal_lookback_sessions": 3,
  "latest_closed_session": "...",
  "vumanchu_gold": {},
  "vumanchu_top": {},
  "universe": {},
  "scoring": {},
  "performance": {},
  "data_quality": {},
  "top10": [],
  "all_candidates": []
}
```

The exact schema can evolve with the producer pipeline.

Consumers should use `pipeline_version` and required-field validation rather than assuming an old static schema.

---

## Stocks — JOAT + Sniper

The published stock snapshot can include:

- Sniper BUY / SELL state;
- D0 / D1 / D2 signal age;
- JOAT confirmation;
- technical scoring;
- GICS niche direction;
- stock-vs-niche relative strength;
- Entry / SL / TP1;
- remaining R:R;
- setup/actionability metadata.

The bridge does not reinterpret these values.

It transports exactly what the upstream collector publishes.

---

## Stocks — VuManChu RAW Gold

The stock artifact includes the dedicated:

```text
vumanchu_gold
```

block.

Key governance:

```text
FULL S&P500
CLOSED 1D only
no lookahead
scoring impact = NONE
```

The rolling one-calendar-month discovery history is published through:

```text
vumanchu_gold.rolling_1_calendar_month_hits
```

Membership is based on **First Detection / detection bar**, not the visually back-plotted pivot date.

The artifact can also include:

- pivot;
- detection bar;
- detection-bar high;
- RAW trigger diagnostics;
- 1D lifecycle;
- completeness;
- missing / failed coverage.

---

## Stocks — VuManChu TOP

Newer stock producer versions can also export:

```text
vumanchu_top
```

This is a separate bearish / exhaustion evidence layer.

Important ownership rule:

```text
VuManChu TOP evidence alone does NOT create
SELL / REDUCE / SHORT / HIGH-CONVICTION TOP.
```

RAW Red Circle evidence is informational.

Overbought alone is never a SELL decision.

Any final high-conviction TOP interpretation belongs to the downstream Daily Stocks decision layer where independent evidence can be combined.

---

# Crypto artifact

The crypto JSON is a current-cycle technical snapshot built around:

```text
SNIPER_1H
```

Representative top-level fields include:

```json
{
  "schema_version": "LATEST_SCAN_V1",
  "generated_at_utc": "...",
  "generated_at_europe_bucharest": "...",
  "pipeline_version": "...",
  "report_mode": "FULL_HOURLY",
  "reference_timezone": "Europe/Bucharest",
  "current_hour_cycle": {},
  "universe": {},
  "status": {},
  "provider_policy": {},
  "capability_note": {},
  "action_report": {},
  "vumanchu_gold": {},
  "trend_engine_summary": {},
  "assets": []
}
```

Again, `pipeline_version` in the artifact is authoritative for the producer version actually published.

---

## Crypto — current-hour coverage

The bridge exposes the producer's exact current-cycle contract:

```text
expected_latest_1h_start_utc
expected_latest_1h_close_utc
analysis_ready_assets
current_cycle_coverage_count
missing_current_1h_assets
complete
```

This allows downstream reports to distinguish:

```text
CURRENT
STALE
INCOMPLETE
UNUSABLE
```

without guessing from repository commit time.

---

## Crypto — Sniper / JOAT / 4H context

The crypto artifact can include:

- NEW Sniper 1H BUY / SELL;
- RETEST LONG / SHORT;
- ACTIVE setup lifecycle;
- Entry;
- Stop Loss;
- TP1–TP5;
- TP hit progression;
- signal age;
- JOAT at Sniper signal;
- current JOAT;
- recent strong JOAT triggers;
- 4H trend;
- trend alignment;
- Top BUY / SELL technical candidate arrays;
- counter-trend exceptions.

The bridge performs no ranking changes and no recalculation.

---

## Crypto — VuManChu RAW Gold

Crypto also contains a separate:

```text
vumanchu_gold
```

block.

Its role is distinct from Sniper / JOAT:

```text
CLOSED 1D only
no lookahead
scoring impact = NONE
```

The VuManChu crypto discovery universe is independent from the perpetual-only execution universe.

The bridge may therefore contain valid VuManChu events for assets that are not part of the standard Sniper / JOAT execution set.

The downstream Daily Crypto workflow owns the visible interpretation of those events.

---

# Raw access examples

## curl — Stocks

```bash
curl -fsSL \
  https://raw.githubusercontent.com/catalin6100/stock-daily-signal-bridge/main/stocks/latest_scan.json
```

## curl — Crypto

```bash
curl -fsSL \
  https://raw.githubusercontent.com/catalin6100/stock-daily-signal-bridge/main/crypto/latest_scan.json
```

---

## Python — Stocks

```python
import requests

url = (
    "https://raw.githubusercontent.com/"
    "catalin6100/stock-daily-signal-bridge/"
    "main/stocks/latest_scan.json"
)

data = requests.get(url, timeout=20).json()

print(data["pipeline_version"])
print(data["latest_closed_session"])
print(data["data_quality"]["freshness_status"])
```

---

## Python — Crypto

```python
import requests

url = (
    "https://raw.githubusercontent.com/"
    "catalin6100/stock-daily-signal-bridge/"
    "main/crypto/latest_scan.json"
)

data = requests.get(url, timeout=20).json()

cycle = data["current_hour_cycle"]

print(data["pipeline_version"])
print(cycle["expected_latest_1h_close_utc"])
print(cycle["complete"])
```

---

## jq — quick metadata check

Stocks:

```bash
curl -fsSL \
  https://raw.githubusercontent.com/catalin6100/stock-daily-signal-bridge/main/stocks/latest_scan.json \
  | jq '{
      generated_at_utc,
      pipeline_version,
      latest_closed_session,
      timeframe,
      freshness: .data_quality.freshness_status
    }'
```

Crypto:

```bash
curl -fsSL \
  https://raw.githubusercontent.com/catalin6100/stock-daily-signal-bridge/main/crypto/latest_scan.json \
  | jq '{
      generated_at_utc,
      pipeline_version,
      report_mode,
      expected_close: .current_hour_cycle.expected_latest_1h_close_utc,
      complete: .current_hour_cycle.complete
    }'
```

---

# Cache / propagation note

GitHub's RAW endpoint can briefly lag immediately after a new commit becomes visible in the repository.

Consumers that require the newest cycle should:

1. validate timestamps inside the JSON;
2. retry when the artifact is older than expected;
3. optionally use a harmless cache-busting query parameter;
4. never silently accept an older cycle merely because the HTTP request succeeded.

Example:

```text
.../crypto/latest_scan.json?run=<unique-value>
```

The crypto producer already verifies post-publication bridge freshness as part of its upstream workflow.

---

# Machine-generated files

These files are generated artifacts:

```text
stocks/latest_scan.json
crypto/latest_scan.json
```

They should normally be changed only by the upstream publisher workflows.

Do not manually edit indicator values, timestamps, scores, lifecycle states, coverage, or signal arrays in this repository.

If a value is wrong, fix the **producer** and republish.

---

# Source-of-truth hierarchy

For **calculation logic**:

```text
upstream private collector code
```

For **what was actually published**:

```text
the JSON currently present in this bridge
```

For **producer version**:

```text
latest_scan.json -> pipeline_version
```

For **freshness**:

```text
artifact timestamps + domain-specific freshness fields
```

For **final investment interpretation**:

```text
downstream Daily Stocks / Daily Crypto reporting workflow
```

The README must never override contradictory machine-readable artifact metadata.

---

# What this repository does NOT do

This repository does not:

- scan the S&P 500;
- query CoinGecko;
- query OKX / Bitget / Yahoo / Stooq;
- calculate Sniper;
- calculate JOAT;
- calculate VuManChu;
- calculate 4H trend;
- decide BUY / SELL / REDUCE;
- run portfolio allocation;
- perform market-regime analysis;
- run calibration;
- store API secrets;
- require a GitHub connector for public reads.

It only publishes upstream output.

---

# Security / secret policy

This repository is public.

Never commit:

- API keys;
- `COINGECKO_API_KEY`;
- `BRIDGE_TOKEN`;
- GitHub PATs;
- private-repository credentials;
- private workflow configuration containing secrets;
- account information.

All authentication belongs in the private producer repositories and GitHub Actions secrets.

Only public machine-readable artifacts should be copied here.

---

# Operational ownership

## Stocks

```text
Producer:
stock-daily-signal-engine

Public artifact:
stocks/latest_scan.json

Primary downstream consumer:
Daily Stocks — Action Now
```

## Crypto

```text
Producer:
crypto-trend-engine

Public artifact:
crypto/latest_scan.json

Primary downstream consumers:
Daily Crypto Signals — Adaptive 20-Layer
Crypto 4H Report Check
```

---

# Documentation maintenance rule

Update this README when any of the following changes structurally:

- public folder/path;
- producer repository ownership;
- publication cadence;
- downstream consumption contract;
- freshness validation;
- top-level JSON schema;
- bridge verification behavior;
- authentication/public-access model;
- artifact ownership.

Do **not** hardcode a producer version here as the permanent current version.

The authoritative current version is always:

```text
latest_scan.json -> pipeline_version
```

This prevents README drift when the stock or crypto engine is upgraded independently.

---

# Repository role in one sentence

> **Expose the newest validated stock and crypto signal artifacts through stable public RAW URLs, without moving private computation or secrets into the public repository.**
