# Offline Test Report

**Date:** 2026-09-12
**Method:** run the main academic demo (S1, seed 20260805, 720 h, target
10,000) with all external network access blocked, after installation was
complete.

---

## 1. Network-dependency audit (static)

The Lab code was scanned for any network client:

| Check | Result |
|---|---|
| `requests` / `urllib` / `http.client` / `aiohttp` / `httpx` / websocket | none |
| `socket` usage | only `scripts/launcher.py`, loopback `127.0.0.1` bind to find a free local port |
| `http://` / `https://` strings in code | only `http://localhost` (the app's own local server) |

The Lab performs no API call, no cloud call, no external database access, and
no download at run time.

## 2. Offline run (network blocked)

The demo was executed in the clean-machine environment with all proxy
environment variables forced to a dead local address
(`HTTP_PROXY/HTTPS_PROXY/ALL_PROXY=http://127.0.0.1:9`, `NO_PROXY=""`), so any
outbound request would fail immediately.

| Measurement | Value |
|---|---|
| Scenario | S1, seed 20260805, 720 h |
| Target | 10,000 patients |
| Patients generated | 10,622 |
| Events generated | 31,653 |
| Validation status | VALIDATED |
| Wall time | 34.25 s |
| Configuration hash | `e460cf54…` (identity match) |

**Result: OFFLINE DEMO: PASS** — the full generation → validation pipeline
completes with zero network access.

## 3. Conclusion

The demonstration requires no API, no cloud service, no external database,
and no internet service. After installation, it is fully self-contained on the
local machine.
