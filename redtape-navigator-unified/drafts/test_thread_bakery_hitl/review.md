# Application Review Package: I want to open a small bakery in Park Circus, Kolkata with 5 counter seats

- **Goal:** I want to open a small bakery in Park Circus, Kolkata with 5 counter seats
- **Domain:** `business` | **Location:** Kolkata, West Bengal

> **Preparation Aid Only:** Verify all fees, rules, and form versions with the issuing authority before paying or submitting. This assistant never submits on your behalf.

> **Snapshot Warning:** One or more live government portals were unreachable; unverified fallback leads were used. Verify all `NOT VERIFIED` items below before paying fees.

## 1. Compliance Matrix

| Requirement | Tier | Authority | Status | Channel | Fee | Source | Verified |
|---|---|---|---|---|---|---|---|
| Certificate of Enlistment (Trade License) | municipal | Kolkata Municipal Corporation | **Required** | web_portal | None | https://www.kmcgov.in/KMCPortal/jsp/KMCTradeLicenseHome.jsp | NOT VERIFIED |
| Registration under The Shops and Establishments Act | state | Labour Commissionerate, Government of West Bengal | **Required** | web_portal | None | https://silpasathi.wb.gov.in/ | NOT VERIFIED |
| FSSAI Basic Food Safety Registration | central | Food Safety and Standards Authority of India | **Required** | web_portal | ₹100 | https://foscos.fssai.gov.in | NOT VERIFIED |

## 2. Audit Trail & Rule Reasoning

- **Certificate of Enlistment (Trade License)** (`Required`): Mandatory for operating any trade or commercial business within Kolkata jurisdiction.
- **Registration under The Shops and Establishments Act** (`Required`): Required for commercial establishment operating with 3 worker(s) on site.
  - status change: 2026-11-20: Conditional -> Required (Required for commercial establishment operating with 3 worker(s) on site.)
- **FSSAI Basic Food Safety Registration** (`Required`): Required: expected annual turnover of Rs 800,000 is within the Basic Registration threshold of <= Rs 1.5 Crore.
  - status change: 2026-11-20: Conditional -> Required (Required: expected annual turnover of Rs 800,000 is within the Basic Registratio)

## 3. Conflicts & System Notices

- _Agent notice:_ Notice: Live Gemini interview parser was unavailable; parsed via deterministic regex slot-filler.
- _Agent notice:_ Notice: Live Gemini compliance evaluation was unavailable (HTTP 503/429); evaluated using verified deterministic statutory rule engine.

## 4. Filled PDF Drafts & Digital Portal Packs

- **PDF Draft — WB_Shops_Establishment_Form_B.pdf**: 33% complete (`Draft_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/draft_WB_Shops_Establishment_Form_B.pdf`
  - needs your input: `applicant_profile.entity_name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.applicant.phone`
- **PDF Draft — FSSAI_Registration_Form_A.pdf**: 12% complete (`Draft_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/draft_FSSAI_Registration_Form_A.pdf`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.entity_name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.phone`
  - needs your input: `applicant_profile.applicant.pan`
- **Web Portal Pack — KMC Certificate of Enlistment (Trade License)**: 44% ready (`Pack_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/kmc_trade_license_pack.md` (https://www.kmcgov.in/KMCPortal/jsp/KMCTradeLicenseHome.jsp)
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.location.premises_type`
  - needs your input: `applicant_profile.entity_name`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.applicant.phone`
- **Web Portal Pack — SilpaSathi West Bengal Shops & Establishments (Form B)**: 43% ready (`Pack_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/silpasathi_pack.md` (https://silpasathi.wb.gov.in/)
  - needs your input: `applicant_profile.entity_name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.applicant.phone`
- **Web Portal Pack — FoSCoS FSSAI Basic Food Registration (Form A)**: 33% ready (`Pack_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/foscos_pack.md` (https://foscos.fssai.gov.in)
  - needs your input: `applicant_profile.entity_name`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.location.pin`
  - needs your input: `applicant_profile.applicant.phone`
  - needs your input: `applicant_profile.applicant.pan`

## 5. Supporting Document Checklist

- [ ] Rent Agreement or Landlord NOC _(for: lic_kmc_certificate_of_enlistment, lic_fssai_basic_registration)_ [Template_Available]
- [ ] Government Photo ID (Aadhaar / PAN / Voter ID) _(for: lic_kmc_certificate_of_enlistment, lic_fssai_basic_registration)_ [Action_Required]
- [ ] Assessee Number details _(for: lic_kmc_certificate_of_enlistment)_ [Action_Required]
- [ ] Establishment address proof _(for: lic_wb_shops_and_establishments)_ [Action_Required]
- [ ] Details of workers on site _(for: lic_wb_shops_and_establishments)_ [Action_Required]
- [ ] Property Tax or Trade License data linkage _(for: lic_wb_shops_and_establishments)_ [Action_Required]
- [ ] List of food category desired to be manufactured/processed _(for: lic_fssai_basic_registration)_ [Template_Available]

## 6. Submission Readiness

**Action needed before submission.** Resolve the items below:
- **Note:** lic_kmc_certificate_of_enlistment: not live-verified (source_verified_at empty); flag snapshot warning to user
- **Note:** lic_wb_shops_and_establishments: not live-verified (source_verified_at empty); flag snapshot warning to user
- **Note:** lic_fssai_basic_registration: not live-verified (source_verified_at empty); flag snapshot warning to user
- **Note:** WB_Shops_Establishment_Form_B.pdf: 4 pending mandatory field(s): applicant_profile.entity_name, applicant_profile.location.address, applicant_profile.applicant.name, applicant_profile.applicant.phone
- **Note:** FSSAI_Registration_Form_A.pdf: 5 pending mandatory field(s): applicant_profile.applicant.name, applicant_profile.entity_name, applicant_profile.location.address, applicant_profile.applicant.phone, applicant_profile.applicant.pan
- **Note:** KMC Certificate of Enlistment (Trade License) (portal): 5 pending mandatory field(s): applicant_profile.location.address, applicant_profile.location.premises_type, applicant_profile.entity_name, applicant_profile.applicant.name, applicant_profile.applicant.phone
- **Note:** SilpaSathi West Bengal Shops & Establishments (Form B) (portal): 4 pending mandatory field(s): applicant_profile.entity_name, applicant_profile.location.address, applicant_profile.applicant.name, applicant_profile.applicant.phone
- **Note:** FoSCoS FSSAI Basic Food Registration (Form A) (portal): 6 pending mandatory field(s): applicant_profile.entity_name, applicant_profile.applicant.name, applicant_profile.location.address, applicant_profile.location.pin, applicant_profile.applicant.phone, applicant_profile.applicant.pan

_To correct any field, add it to `state.overrides` and re-run Document + Review._
