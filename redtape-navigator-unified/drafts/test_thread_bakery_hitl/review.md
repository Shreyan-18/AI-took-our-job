# Application Review Package: small bakery

- **Goal:** I want to open a small bakery in Park Circus, Kolkata with 5 counter seats
- **Domain:** `business` | **Location:** Park Circus, Kolkata

> **Preparation Aid Only:** Verify all fees, rules, and form versions with the issuing authority before paying or submitting. This assistant never submits on your behalf.

## 1. Compliance Matrix

| Requirement | Tier | Authority | Status | Channel | Fee | Source | Verified |
|---|---|---|---|---|---|---|---|
| Certificate of Enlistment (Trade License) | municipal | Kolkata Municipal Corporation (KMC) | **Required** | web_portal | Varies based on trade category and area; issued real-time on payment. | https://www.kmcgov.in | 2026-11-21 |
| Registration under The Shops and Establishment Act, 1963 | state | Labour Department, Government of West Bengal | **Required** | web_portal | Slab-based based on number of employees (null for specific small units) | https://silpasathi.wb.gov.in/ | 2026-11-21 |
| FSSAI Food Safety Registration | central | Food Safety and Standards Authority of India (FSSAI) | **Required** | web_portal | ₹100 per year | https://foscos.fssai.gov.in/ | 2026-11-21 |
| GST Registration | central | Goods and Services Tax Network (GSTN) | **Needs Verification** | web_portal | null | https://www.gst.gov.in/ | 2026-11-21 |
| Udyam Registration | central | Ministry of Micro, Small and Medium Enterprises | **Needs Verification** | web_portal | null | https://udyamregistration.gov.in/ | 2026-11-21 |
| Fire Safety Recommendation / Fire NOC | state | West Bengal Fire & Emergency Services (WBFES) | **Not Applicable** | hybrid | None | https://wbfes.gov.in/ | 2026-11-21 |

## 2. Audit Trail & Rule Reasoning

- **Certificate of Enlistment (Trade License)** (`Required`): Mandatory for operating any trade or commercial business within Park Circus jurisdiction.
- **Registration under The Shops and Establishment Act, 1963** (`Required`): Required for commercial establishment operating with 3 worker(s) on site.
  - status change: 2026-11-21: Conditional -> Required (Mandatory for all commercial units in Kolkata. The applicant has 3 workers on si)
- **FSSAI Food Safety Registration** (`Required`): Required: expected annual turnover of Rs 800,000 is within the Basic Registration threshold of <= Rs 12 Lakhs.
  - status change: 2026-11-21: Needs Verification -> Required (Required: expected annual turnover of Rs 800,000 is within the Basic Registratio)
- **GST Registration** (`Needs Verification`): Requires verification with issuing authority.
  - status change: 2026-11-21: Conditional -> Needs Verification (Requires verification with issuing authority.)
- **Udyam Registration** (`Needs Verification`): Requires verification with issuing authority.
  - status change: 2026-11-21: Not Applicable -> Needs Verification (Requires verification with issuing authority.)
- **Fire Safety Recommendation / Fire NOC** (`Not Applicable`): Not Applicable: customer seating (5) is below the mandatory Fire NOC threshold.
  - status change: 2026-11-21: Conditional -> Not Applicable (Not Applicable: customer seating (5) is below the mandatory Fire NOC threshold.)

## 3. Conflicts & System Notices

- **FSSAI Food Safety Registration** (conflicting official sources):
  - Snippet 10 claims turnover limit for Basic Registration is revised to ₹1.5 Crore from April 2026, while traditional limit is ₹12 Lakh.
  - Snippet 11 states there is 'no expiry' for new licenses in 2026, contradicting the traditional 1-5 year renewal cycle.
- **GST Registration** (conflicting official sources):
  - Thresholds vary between ₹20 Lakh and ₹40 Lakh depending on whether the bakery is classified as a supplier of goods or a service provider (restaurant service).
- _Agent notice:_ Notice: Live Gemini compliance evaluation was unavailable (HTTP 503/429); evaluated using verified deterministic statutory rule engine.

## 4. Filled PDF Drafts & Digital Portal Packs

- **PDF Draft — KMC_Section199_Trade_Enlistment.pdf**: 44% complete (`Draft_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/draft_KMC_Section199_Trade_Enlistment.pdf`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.location.municipal_ward_or_block`
  - needs your input: `applicant_profile.applicant.phone`
  - needs your input: `applicant_profile.applicant.pan`
- **PDF Draft — WB_Shops_Establishment_Form_B.pdf**: 50% complete (`Draft_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/draft_WB_Shops_Establishment_Form_B.pdf`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.applicant.phone`
- **PDF Draft — FSSAI_Registration_Form_A.pdf**: 38% complete (`Draft_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/draft_FSSAI_Registration_Form_A.pdf`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.phone`
  - needs your input: `applicant_profile.applicant.pan`
- **Web Portal Pack — KMC Certificate of Enlistment (Trade License)**: 56% ready (`Pack_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/kmc_trade_license_pack.md` (https://www.kmcgov.in/KMCPortal/jsp/KMCTradeLicenseHome.jsp)
  - needs your input: `applicant_profile.location.municipal_ward_or_block`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.applicant.phone`
- **Web Portal Pack — SilpaSathi West Bengal Shops & Establishments (Form B)**: 57% ready (`Pack_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/silpasathi_pack.md` (https://silpasathi.wb.gov.in/)
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.applicant.phone`
- **Web Portal Pack — FoSCoS FSSAI Basic Food Registration (Form A)**: 44% ready (`Pack_Generated`) → `/Users/tamajitghosh/Desktop/red-tape/redtape-navigator-unified/drafts/test_thread_bakery_hitl/foscos_pack.md` (https://foscos.fssai.gov.in)
  - needs your input: `applicant_profile.applicant.name`
  - needs your input: `applicant_profile.location.address`
  - needs your input: `applicant_profile.location.pin`
  - needs your input: `applicant_profile.applicant.phone`
  - needs your input: `applicant_profile.applicant.pan`

## 5. Supporting Document Checklist

- [ ] Rent Agreement or Landlord NOC _(for: kmc_trade_license)_ [Template_Available]
- [ ] Government Photo ID (Aadhaar / PAN / Voter ID) _(for: kmc_trade_license, wb_shops_establishments, fssai_basic_registration)_ [Action_Required]
- [ ] Previous year's CE (for renewals) _(for: kmc_trade_license)_ [Action_Required]
- [ ] Aadhaar Card _(for: kmc_trade_license)_ [Action_Required]
- [ ] Trade License _(for: wb_shops_establishments)_ [Action_Required]
- [ ] Address Proof of Establishment _(for: wb_shops_establishments)_ [Action_Required]
- [ ] Appointment letters of employees (if any) _(for: wb_shops_establishments)_ [Action_Required]
- [ ] Proof of Address of Business Premises _(for: fssai_basic_registration)_ [Action_Required]
- [ ] List of Food Categories _(for: fssai_basic_registration)_ [Action_Required]

## 6. Submission Readiness

**Action needed before submission.** Resolve the items below:
- **Note:** msme_udyam: Needs Verification should document conflicts[] or a gap note
- **Note:** KMC_Section199_Trade_Enlistment.pdf: 5 pending mandatory field(s): applicant_profile.applicant.name, applicant_profile.location.address, applicant_profile.location.municipal_ward_or_block, applicant_profile.applicant.phone, applicant_profile.applicant.pan
- **Note:** WB_Shops_Establishment_Form_B.pdf: 3 pending mandatory field(s): applicant_profile.location.address, applicant_profile.applicant.name, applicant_profile.applicant.phone
- **Note:** FSSAI_Registration_Form_A.pdf: 4 pending mandatory field(s): applicant_profile.applicant.name, applicant_profile.location.address, applicant_profile.applicant.phone, applicant_profile.applicant.pan
- **Note:** KMC Certificate of Enlistment (Trade License) (portal): 4 pending mandatory field(s): applicant_profile.location.municipal_ward_or_block, applicant_profile.location.address, applicant_profile.applicant.name, applicant_profile.applicant.phone
- **Note:** SilpaSathi West Bengal Shops & Establishments (Form B) (portal): 3 pending mandatory field(s): applicant_profile.location.address, applicant_profile.applicant.name, applicant_profile.applicant.phone
- **Note:** FoSCoS FSSAI Basic Food Registration (Form A) (portal): 5 pending mandatory field(s): applicant_profile.applicant.name, applicant_profile.location.address, applicant_profile.location.pin, applicant_profile.applicant.phone, applicant_profile.applicant.pan

_To correct any field, add it to `state.overrides` and re-run Document + Review._
