# Compliance Taxonomy & Tier Sweeps

| Status | Use When | Required Fields |
|---|---|---|
| `Required` | Mandatory per official source; all triggers met | `official_source_url`, `rationale` |
| `Conditional` | Depends on unknown profile field(s) | `depends_on[]`, `official_source_url`, `rationale` quoting threshold |
| `Not Applicable` | Source states an exemption/threshold profile falls outside | `official_source_url`, `rationale` quoting threshold + user value |
| `Needs Verification` | Sources conflict, are outdated (>30d or superseded form), or missing | `conflicts[]` or gap `note` |

## Mandatory 3-Tier Sweep
Always check **Municipal/Local** (trade licence, building/zoning, health, gram panchayat), **State** (shops & establishments, fire NOC, pollution PCB, state agriculture/land dept), and **Central** (FSSAI, GST, Udyam, PM-KISAN, PM-FME).

## Audit Trail Rule
Whenever a profile update changes a status, append `"YYYY-MM-DD: Old -> New (reason)"` to `history[]`.
