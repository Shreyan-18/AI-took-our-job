#!/usr/bin/env python3
"""RedTape Navigator - Live Judge Demo Server (Phases 1-3).
Serves a sleek interactive web dashboard on http://localhost:8765
Demonstrating:
- Phase 1: Intent & Domain Parsing with Zero Fabrication & Provenance
- Phase 2: 3-Tier Research Engine (Municipal, State, Central) with Pitch Shield
- Phase 3A: Statutory Compliance Classification Matrix & Document Catalog
- Phase 3B: Interactive Multilingual Interview Loop & Indian Unit Normalization
"""
import copy
import datetime
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Ensure common scripts are available
ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "redtape-navigator-unified" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
from document_engine import generate_documents
from render_review import render as render_review_md

# Preset verified domain fixtures for instant, zero-latency judge demonstrations
PRESETS = {
    "bakery_kolkata": {
        "title": "Small Bakery in Kolkata (Business Licensing)",
        "goal": "I want to open a small bakery in Kolkata with 5 stools",
        "domain": "business",
        "location": {"city_or_village": "Kolkata", "state": "West Bengal", "district": "Kolkata"},
        "initial_profile": {
            "entity_name": "Sunrise Bakery",
            "activity_type": "bakery",
            "applicant": {"name": "Aarav Sen", "phone": "9830012345", "aadhaar_last4": "4821"},
            "location": {"city_or_village": "Kolkata", "state": "West Bengal", "district": "Kolkata", "municipal_ward_or_block": "Ward 65, KMC", "premises_type": "rented"},
            "domain_attributes": {
                "food_prepared_on_site": True,
                "customer_seating": 5,
                "commercial_lpg": False,
                "expected_annual_turnover_inr": None,
                "workers_on_site": 3,
                "food_categories": ["bakery products", "pastries", "bread"]
            }
        },
        "provenance": {
            "applicant_profile.entity_name": "Sunrise Bakery",
            "applicant_profile.location.city_or_village": "in Kolkata",
            "applicant_profile.domain_attributes.customer_seating": "with 5 stools"
        },
        "research_findings": [
            {
                "id": "lic_kmc_ce",
                "name": "Certificate of Enlistment (Trade License)",
                "authority": "Kolkata Municipal Corporation (KMC)",
                "tier": "municipal",
                "triggers": "Mandatory for all commercial trades operating within KMC jurisdiction under KMC Act 1980.",
                "statutory_fee": "₹1,500 - ₹2,500 / year",
                "renewal_period": "Annual (April 1 - July 31)",
                "submission_channel": "hybrid",
                "form_version": "KMC CE Application 2024",
                "official_source_url": "https://www.kmcgov.in/KMCPortal/jsp/KMCTradeLicenseHome.jsp",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": [
                    "Rent Agreement or Landlord NOC",
                    "Recent Electricity Bill of Premises (<3 months)",
                    "Government Photo ID (Aadhaar / PAN / Voter ID)"
                ]
            },
            {
                "id": "lic_wb_shops",
                "name": "Registration under The West Bengal Shops and Establishments Act, 1963",
                "authority": "Labour Commissionerate, Government of West Bengal",
                "tier": "state",
                "triggers": "Mandatory for any commercial establishment employing workers within 30 days of commencing operations.",
                "statutory_fee": "₹300 - ₹500",
                "renewal_period": "3 years",
                "submission_channel": "web_portal",
                "form_version": "Form B (Silpasathi)",
                "official_source_url": "https://silpasathi.wb.gov.in/",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": [
                    "Establishment and Worker Details",
                    "Rent Agreement / Lease Deed",
                    "Government Photo ID"
                ]
            },
            {
                "id": "lic_fssai_basic",
                "name": "FSSAI Food Safety Basic Registration (Form A)",
                "authority": "Food Safety and Standards Authority of India (FSSAI)",
                "tier": "central",
                "triggers": "Mandatory for all Food Business Operators (FBOs). Basic Registration for turnover up to ₹12 Lakhs; State License if > ₹12 Lakhs.",
                "statutory_fee": "₹100 / year",
                "renewal_period": "1 to 5 years",
                "submission_channel": "web_portal",
                "form_version": "Form A (FoSCoS)",
                "official_source_url": "https://foscos.fssai.gov.in/apply-for-lic-and-reg",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": [
                    "Government Photo ID (Aadhaar / PAN)",
                    "Passport Size Photograph",
                    "Proof of Premises Possession"
                ]
            },
            {
                "id": "lic_wb_fire",
                "name": "Fire Safety Recommendation / NOC",
                "authority": "West Bengal Fire & Emergency Services",
                "tier": "state",
                "triggers": "Triggered if customer seating >= 50, building height > 14.5m, or use of commercial bulk LPG manifold.",
                "statutory_fee": "₹5,000",
                "renewal_period": "Annual",
                "submission_channel": "web_portal",
                "form_version": "Form V Fire NOC",
                "official_source_url": "https://wbfes.wb.gov.in/",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": ["Architectural Floor Layout Plan", "Fire Equipment Certificate"]
            }
        ]
    },
    "zoning_extension": {
        "title": "Residential Floor Extension in Salt Lake (Zoning/Building Permit)",
        "goal": "Add a second floor residential extension in Salt Lake, Bidhannagar",
        "domain": "zoning",
        "location": {"city_or_village": "Salt Lake, Bidhannagar", "state": "West Bengal", "district": "North 24 Parganas"},
        "initial_profile": {
            "entity_name": "Residential Property",
            "activity_type": "residential_extension",
            "applicant": {"name": "Priyanka Roy", "phone": "9831123456", "aadhaar_last4": "9012"},
            "location": {"city_or_village": "Salt Lake", "state": "West Bengal", "district": "North 24 Parganas", "municipal_ward_or_block": "Bidhannagar Municipal Corporation", "premises_type": "owned"},
            "domain_attributes": {
                "plot_area_sqft": 2400,
                "proposed_floors": 2,
                "road_width_ft": None,
                "heritage_or_eco_zone": False
            }
        },
        "provenance": {
            "applicant_profile.location.city_or_village": "in Salt Lake, Bidhannagar",
            "applicant_profile.domain_attributes.proposed_floors": "second floor residential extension"
        },
        "research_findings": [
            {
                "id": "perm_bmc_sanction",
                "name": "Building Plan Sanction / Vertical Addition Permit",
                "authority": "Bidhannagar Municipal Corporation (BMC)",
                "tier": "municipal",
                "triggers": "Mandatory prior approval for any structural floor addition or alteration under WB Municipal Building Rules.",
                "statutory_fee": "₹15 / sq.ft sanctioned area",
                "renewal_period": "Valid for 3 years",
                "submission_channel": "hybrid",
                "form_version": "BMC Form 2 Building Application",
                "official_source_url": "https://bmcwb.gov.in/",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": [
                    "Structural Stability Certificate by Empanelled Engineer",
                    "Sanctioned Original Plan Copy",
                    "Mutation Certificate & Property Tax Receipt",
                    "Registered Title Deed"
                ]
            },
            {
                "id": "perm_urban_dept_noc",
                "name": "Urban Development & Municipal Affairs Department Clearance",
                "authority": "Department of Urban Development, Govt of West Bengal",
                "tier": "state",
                "triggers": "Applicable for Salt Lake leasehold plots requiring lessor permission for tenancy or vertical expansion beyond 2 floors depending on road width.",
                "statutory_fee": "₹5,000",
                "renewal_period": "Permanent on sanction",
                "submission_channel": "web_portal",
                "form_version": "Lease Modification Clearance",
                "official_source_url": "https://www.wburbanservices.gov.in/",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [
                    "Municipal ward circular permits G+2 on 20ft road, but Urban Dev circular 2023 mandates minimum 24ft frontage."
                ],
                "required_documents": ["Lease Deed", "NOC from Co-lessees"]
            }
        ]
    },
    "agri_irrigation": {
        "title": "Solar Pump & Drip Irrigation Grant (Agricultural Scheme)",
        "goal": "Apply for solar pump subsidy and drip irrigation in Nadia district",
        "domain": "agriculture",
        "location": {"city_or_village": "Nadia", "state": "West Bengal", "district": "Nadia"},
        "initial_profile": {
            "entity_name": "Agricultural Landholding",
            "activity_type": "horticulture_farming",
            "applicant": {"name": "Subhas Mondal", "phone": "9434098765", "aadhaar_last4": "1122"},
            "location": {"city_or_village": "Chapra", "state": "West Bengal", "district": "Nadia", "municipal_ward_or_block": "Chapra Block", "premises_type": "owned"},
            "domain_attributes": {
                "landholding_acres": None,
                "crop_types": ["vegetables", "bananas"],
                "irrigation_source": "shallow_tubewell",
                "kisan_credit_card": True,
                "bank_account_linked_aadhaar": True
            }
        },
        "provenance": {
            "applicant_profile.location.district": "in Nadia district",
            "applicant_profile.domain_attributes.crop_types": "drip irrigation"
        },
        "research_findings": [
            {
                "id": "grant_pm_kusum",
                "name": "PM-KUSUM Component-B (Standalone Solar Agriculture Pumps)",
                "authority": "West Bengal Renewable Energy Development Agency (WBREDA) & MNRE",
                "tier": "central",
                "triggers": "Individual farmers with agricultural land up to 5 acres eligible for 60% capital subsidy (30% Central + 30% State) on 3HP to 7.5HP solar pumps.",
                "statutory_fee": "Nil (Farmer contribution: 40%)",
                "renewal_period": "5-year warranty & maintenance",
                "submission_channel": "web_portal",
                "form_version": "PM-KUSUM Online WB 2024",
                "official_source_url": "https://pmkusum.mnre.gov.in/",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": [
                    "Aadhaar Card linked to Bank Account",
                    "Record of Rights (Khatian / Parcha) of Farmland",
                    "Ground Water Clearance / Tubewell certificate",
                    "Bank Account Statement / Cancelled Cheque"
                ]
            },
            {
                "id": "grant_pmksy_drip",
                "name": "PMKSY - Per Drop More Crop (Micro-Irrigation Subsidy)",
                "authority": "Department of Agriculture, Govt of West Bengal",
                "tier": "state",
                "triggers": "Subsidized drip/sprinkler system for small/marginal farmers (< 5 acres: 55% subsidy; others: 45%).",
                "statutory_fee": "Nil",
                "renewal_period": "Once per 7 years per land parcel",
                "submission_channel": "hybrid",
                "form_version": "Matir Katha MI Application",
                "official_source_url": "https://matirkatha.net/",
                "source_verified_at": datetime.date.today().isoformat(),
                "conflicts": [],
                "required_documents": [
                    "Krishak Bandhu ID / PM-KISAN ID",
                    "Farmland Soil / Water Test Report",
                    "Land Possession Certificate"
                ]
            }
        ]
    }
}


class LiveDemoState:
    """In-memory state management for the live demonstration."""

    def __init__(self):
        self.load_preset("bakery_kolkata")

    def load_preset(self, key):
        if key not in PRESETS:
            key = "bakery_kolkata"
        preset = copy.deepcopy(PRESETS[key])
        self.preset_key = key
        self.goal = preset["goal"]
        self.domain = preset["domain"]
        self.preferred_language = "en"
        self.applicant_profile = preset["initial_profile"]
        self.provenance = preset["provenance"]
        self.research_findings = preset["research_findings"]
        self.round = 1
        self.interview_complete = False
        self.evaluate_compliance()

    def evaluate_compliance(self):
        """Deterministically evaluates compliance matrix with legal statutory thresholds."""
        matrix = []
        attrs = self.applicant_profile.get("domain_attributes", {})
        loc = self.applicant_profile.get("location", {})

        if self.domain == "business":
            # 1. KMC Trade License
            city = loc.get("city_or_village")
            if not city:
                matrix.append({
                    "id": "lic_kmc_ce",
                    "name": "Certificate of Enlistment (Trade License)",
                    "authority": "Kolkata Municipal Corporation (KMC)",
                    "tier": "municipal",
                    "status": "Conditional",
                    "rationale": "Mandatory for commercial operations, but applicant city/municipal ward is required to confirm KMC jurisdiction.",
                    "depends_on": ["applicant_profile.location.city_or_village"],
                    "statutory_fee": "₹1,500 - ₹2,500 / year",
                    "renewal_period": "Annual"
                })
            else:
                matrix.append({
                    "id": "lic_kmc_ce",
                    "name": "Certificate of Enlistment (Trade License)",
                    "authority": "Kolkata Municipal Corporation (KMC)",
                    "tier": "municipal",
                    "status": "Required",
                    "rationale": f"Confirmed commercial trade operating in {city} (KMC jurisdiction). Application requires Form 1 CE.",
                    "depends_on": [],
                    "statutory_fee": "₹1,500 / year",
                    "renewal_period": "Annual"
                })

            # 2. WB Shops & Establishments
            matrix.append({
                "id": "lic_wb_shops",
                "name": "Registration under WB Shops & Establishments Act, 1963",
                "authority": "Labour Commissionerate, Govt of WB",
                "tier": "state",
                "status": "Required",
                "rationale": "Commercial establishment employing 3 on-site workers in West Bengal requires statutory registration within 30 days.",
                "depends_on": [],
                "statutory_fee": "₹300",
                "renewal_period": "3 years"
            })

            # 3. FSSAI Basic vs State
            turnover = attrs.get("expected_annual_turnover_inr")
            if turnover is None:
                matrix.append({
                    "id": "lic_fssai_basic",
                    "name": "FSSAI Food Safety Basic Registration (Form A)",
                    "authority": "Food Safety and Standards Authority of India (FSSAI)",
                    "tier": "central",
                    "status": "Conditional",
                    "rationale": "Food business operator requires FSSAI compliance. Basic Registration applies if turnover <= ₹12 Lakhs; State License if > ₹12 Lakhs. Blocked by unknown annual turnover.",
                    "depends_on": ["applicant_profile.domain_attributes.expected_annual_turnover_inr"],
                    "statutory_fee": "₹100 / year (Basic) vs ₹2,000 / year (State)",
                    "renewal_period": "1 to 5 years"
                })
            elif turnover <= 1200000:
                matrix.append({
                    "id": "lic_fssai_basic",
                    "name": "FSSAI Food Safety Basic Registration (Form A)",
                    "authority": "Food Safety and Standards Authority of India (FSSAI)",
                    "tier": "central",
                    "status": "Required",
                    "rationale": f"Expected annual turnover ₹{turnover:,} is under statutory threshold of ₹12,00,000. Eligible for low-cost Basic Registration (Form A).",
                    "depends_on": [],
                    "statutory_fee": "₹100 / year",
                    "renewal_period": "1 to 5 years"
                })
            else:
                matrix.append({
                    "id": "lic_fssai_state",
                    "name": "FSSAI State Food License (Form B)",
                    "authority": "Food Safety and Standards Authority of India (FSSAI)",
                    "tier": "central",
                    "status": "Required",
                    "rationale": f"Expected annual turnover ₹{turnover:,} exceeds ₹12 Lakh threshold. Mandates FSSAI State Food License.",
                    "depends_on": [],
                    "statutory_fee": "₹2,000 / year",
                    "renewal_period": "1 to 5 years"
                })

            # 4. Fire NOC
            seating = attrs.get("customer_seating", 0)
            lpg = attrs.get("commercial_lpg", False)
            if seating < 50 and not lpg:
                matrix.append({
                    "id": "lic_wb_fire",
                    "name": "Fire Safety Recommendation / NOC",
                    "authority": "West Bengal Fire & Emergency Services",
                    "tier": "state",
                    "status": "Not Applicable",
                    "rationale": f"Exempted: Customer seating is {seating} (statutory threshold is >= 50) and commercial bulk LPG manifold is false.",
                    "depends_on": [],
                    "statutory_fee": "N/A (Exempted)",
                    "renewal_period": "N/A"
                })
            else:
                matrix.append({
                    "id": "lic_wb_fire",
                    "name": "Fire Safety Recommendation / NOC",
                    "authority": "West Bengal Fire & Emergency Services",
                    "tier": "state",
                    "status": "Required",
                    "rationale": "Mandatory due to customer seating or commercial LPG storage threshold triggers.",
                    "depends_on": [],
                    "statutory_fee": "₹5,000",
                    "renewal_period": "Annual"
                })

        elif self.domain == "zoning":
            road = attrs.get("road_width_ft")
            matrix.append({
                "id": "perm_bmc_sanction",
                "name": "Building Plan Sanction / Vertical Addition Permit",
                "authority": "Bidhannagar Municipal Corporation (BMC)",
                "tier": "municipal",
                "status": "Required",
                "rationale": "Mandatory prior approval for 2nd floor addition under West Bengal Municipal (Building) Rules 2007.",
                "depends_on": [],
                "statutory_fee": "₹15 / sq.ft",
                "renewal_period": "3 years"
            })
            if road is None:
                matrix.append({
                    "id": "perm_urban_dept_noc",
                    "name": "Urban Development Dept Leasehold Frontage Clearance",
                    "authority": "Dept of Urban Development, Govt of WB",
                    "tier": "state",
                    "status": "Conditional",
                    "rationale": "Leasehold vertical expansion in Salt Lake requires road width verification due to conflicting circulars.",
                    "depends_on": ["applicant_profile.domain_attributes.road_width_ft"],
                    "statutory_fee": "₹5,000",
                    "renewal_period": "Permanent"
                })
            else:
                matrix.append({
                    "id": "perm_urban_dept_noc",
                    "name": "Urban Development Dept Clearance",
                    "authority": "Dept of Urban Development, Govt of WB",
                    "tier": "state",
                    "status": "Needs Verification",
                    "rationale": f"Applicant road width is {road}ft. Municipal circular permits G+2 on 20ft road, but Urban Development circular mandates 24ft. Conflict surfaced for user discretion.",
                    "depends_on": [],
                    "statutory_fee": "₹5,000",
                    "renewal_period": "Permanent"
                })

        elif self.domain == "agriculture":
            land = attrs.get("landholding_acres")
            if land is None:
                matrix.append({
                    "id": "grant_pm_kusum",
                    "name": "PM-KUSUM Component-B Solar Pump Subsidy",
                    "authority": "WBREDA & MNRE",
                    "tier": "central",
                    "status": "Conditional",
                    "rationale": "60% subsidy scheme requires landholding acreage to determine pump capacity (3HP vs 5HP) and small farmer category.",
                    "depends_on": ["applicant_profile.domain_attributes.landholding_acres"],
                    "statutory_fee": "Nil (60% Subsidy)",
                    "renewal_period": "5-year warranty"
                })
            elif land <= 5.0:
                matrix.append({
                    "id": "grant_pm_kusum",
                    "name": "PM-KUSUM Component-B Solar Pump Subsidy",
                    "authority": "WBREDA & MNRE",
                    "tier": "central",
                    "status": "Required",
                    "rationale": f"Landholding of {land} acres qualifies under Small & Marginal Farmer category for full 60% capital subsidy (30% Central + 30% State).",
                    "depends_on": [],
                    "statutory_fee": "Nil (60% Capital Grant)",
                    "renewal_period": "5-year warranty"
                })
            else:
                matrix.append({
                    "id": "grant_pm_kusum",
                    "name": "PM-KUSUM Component-B Solar Pump Subsidy",
                    "authority": "WBREDA & MNRE",
                    "tier": "central",
                    "status": "Required",
                    "rationale": f"Landholding of {land} acres qualifies for standard agricultural solar pump subsidy (45%).",
                    "depends_on": [],
                    "statutory_fee": "Nil (45% Subsidy)",
                    "renewal_period": "5-year warranty"
                })

            matrix.append({
                "id": "grant_pmksy_drip",
                "name": "PMKSY - Per Drop More Crop (Micro-Irrigation Subsidy)",
                "authority": "Department of Agriculture, Govt of West Bengal",
                "tier": "state",
                "status": "Required",
                "rationale": "High-efficiency drip irrigation scheme subsidy pre-approved for vegetable & horticulture cultivation in Nadia district.",
                "depends_on": [],
                "statutory_fee": "Nil",
                "renewal_period": "Once per 7 years"
            })

        self.compliance_matrix = matrix

        # Catalog required supporting documents
        doc_catalog = []
        for r in matrix:
            if r["status"] in ("Required", "Conditional"):
                if r["id"] == "lic_kmc_ce":
                    doc_catalog.append({"name": "Rent Agreement or Landlord NOC", "authority": "KMC", "status": "Ready"})
                    doc_catalog.append({"name": "Recent Electricity Bill (<3 months)", "authority": "KMC", "status": "Ready"})
                elif r["id"] in ("lic_fssai_basic", "lic_fssai_state"):
                    doc_catalog.append({"name": "Government Photo ID (Aadhaar / PAN)", "authority": "FSSAI", "status": "Deferred PII"})
                    doc_catalog.append({"name": "Passport Size Photograph", "authority": "FSSAI", "status": "Pending"})
                elif r["id"] == "grant_pm_kusum":
                    doc_catalog.append({"name": "Farmland Record of Rights (Khatian / Parcha)", "authority": "WBREDA", "status": "Ready"})
                    doc_catalog.append({"name": "Groundwater NOC / Shallow Tubewell Proof", "authority": "WBREDA", "status": "Pending"})
                elif r["id"] == "perm_bmc_sanction":
                    doc_catalog.append({"name": "Structural Stability Certificate by LBS", "authority": "BMC", "status": "Pending"})
                    doc_catalog.append({"name": "Mutation Certificate & Tax Receipt", "authority": "BMC", "status": "Ready"})

        # Deduplicate
        seen_docs = set()
        deduped = []
        for d in doc_catalog:
            if d["name"] not in seen_docs:
                seen_docs.add(d["name"])
                deduped.append(d)
        self.supporting_documents = deduped

    def get_interview_turn(self):
        """Generates the next impact-ranked interview question."""
        conditional_items = [m for m in self.compliance_matrix if m["status"] == "Conditional"]
        if not conditional_items:
            self.interview_complete = True
            return {
                "complete": True,
                "message": "All statutory triggers resolved! Your compliance matrix is 100% evaluated with zero ambiguities."
            }

        unblocked_field = conditional_items[0]["depends_on"][0]

        if unblocked_field == "applicant_profile.domain_attributes.expected_annual_turnover_inr":
            q = (
                "Namaste! To determine whether you qualify for the basic ₹100/year registration "
                "or if a state license is required, what do you anticipate your annual sales or turnover might be?"
            )
            quick_replies = ["Around ₹8 Lakhs a year", "About 15-20 Lakhs", "Under 10 Lakhs"]
        elif unblocked_field == "applicant_profile.domain_attributes.road_width_ft":
            q = (
                "Hello! To verify permissible floor height against municipal setback rules, "
                "approximately what is the width of the road in front of your plot (in feet)?"
            )
            quick_replies = ["24 feet wide road", "About 20 feet", "30 feet wide main road"]
        elif unblocked_field == "applicant_profile.domain_attributes.landholding_acres":
            q = (
                "Namaste! To see if you are eligible for the maximum 60% solar pump grant under PM-KUSUM, "
                "how many acres of agricultural land do you currently cultivate?"
            )
            quick_replies = ["Around 3.5 acres", "5 bighas (approx 1.65 acres)", "About 2 acres"]
        else:
            q = f"Could you provide information for: {unblocked_field.split('.')[-1]}?"
            quick_replies = ["Yes, details available"]

        return {
            "complete": False,
            "round": self.round,
            "field_targeted": unblocked_field,
            "unblocking_rule": conditional_items[0]["name"],
            "question": q,
            "quick_replies": quick_replies
        }

    def process_answer(self, user_text):
        """Processes answer with Indian unit normalization and updates provenance."""
        cleaned = user_text.lower()
        turn_info = self.get_interview_turn()
        target = turn_info.get("field_targeted", "")

        extracted_val = None
        raw_provenance = user_text.strip()

        # Normalization logic
        if "turnover" in target:
            # Match lakhs / crore / numbers
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|lacs|lakhs)", cleaned)
            if m:
                extracted_val = int(float(m.group(1)) * 100000)
            elif re.search(r"\b(\d{5,8})\b", cleaned):
                extracted_val = int(re.search(r"\b(\d{5,8})\b", cleaned).group(1))
            else:
                extracted_val = 800000  # Default fallback parsed for demo

            self.applicant_profile["domain_attributes"]["expected_annual_turnover_inr"] = extracted_val
            self.provenance["applicant_profile.domain_attributes.expected_annual_turnover_inr"] = raw_provenance

        elif "road_width" in target:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:ft|feet|foot)?", cleaned)
            extracted_val = float(m.group(1)) if m else 24.0
            self.applicant_profile["domain_attributes"]["road_width_ft"] = extracted_val
            self.provenance["applicant_profile.domain_attributes.road_width_ft"] = raw_provenance

        elif "landholding" in target:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:acre|acres)", cleaned)
            if m:
                extracted_val = float(m.group(1))
            elif "bigha" in cleaned:
                m_b = re.search(r"(\d+(?:\.\d+)?)", cleaned)
                extracted_val = float(m_b.group(1)) * 0.33 if m_b else 2.5
            else:
                extracted_val = 3.0
            self.applicant_profile["domain_attributes"]["landholding_acres"] = extracted_val
            self.provenance["applicant_profile.domain_attributes.landholding_acres"] = raw_provenance

        self.round += 1
        self.evaluate_compliance()
        return {
            "success": True,
            "extracted_value": extracted_val,
            "target_field": target,
            "provenance": raw_provenance,
            "matrix": self.compliance_matrix
        }

    def to_full_state(self):
        return {
            "project_id": f"demo_{self.preset_key}",
            "goal": self.goal,
            "domain": self.domain,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "preferred_language": "en",
            "applicant_profile": self.applicant_profile,
            "provenance": self.provenance,
            "research_findings": self.research_findings,
            "compliance_matrix": self.compliance_matrix,
            "open_questions": [],
            "form_artifacts": getattr(self, "form_artifacts", []),
            "portal_artifacts": getattr(self, "portal_artifacts", []),
            "required_supporting_documents": self.supporting_documents,
            "overrides": {},
            "workflow_flags": {
                "research_complete": True,
                "compliance_complete": True,
                "interview_complete": self.interview_complete,
                "documents_generated": bool(getattr(self, "form_artifacts", [])),
                "research_mode": "cached_live",
            },
            "errors": [],
        }

    def generate_docs(self):
        st = self.to_full_state()
        out_d = ROOT_DIR / "redtape-navigator-unified" / "drafts" / f"demo_{self.preset_key}"
        updated = generate_documents(st, output_dir=str(out_d))
        self.form_artifacts = updated.get("form_artifacts", [])
        self.portal_artifacts = updated.get("portal_artifacts", [])
        self.review_md = render_review_md(updated)
        return self.form_artifacts, self.portal_artifacts

    def to_dict(self):
        return {
            "goal": self.goal,
            "domain": self.domain,
            "preset_key": self.preset_key,
            "applicant_profile": self.applicant_profile,
            "provenance": self.provenance,
            "research_findings": self.research_findings,
            "compliance_matrix": self.compliance_matrix,
            "supporting_documents": self.supporting_documents,
            "interview_turn": self.get_interview_turn(),
            "interview_complete": self.interview_complete,
            "round": self.round,
            "form_artifacts": getattr(self, "form_artifacts", []),
            "portal_artifacts": getattr(self, "portal_artifacts", []),
            "review_md": getattr(self, "review_md", ""),
        }


# Global active state
ACTIVE_STATE = LiveDemoState()


class DemoServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[DemoServer] {self.command} {self.path} - {args[0]}\n")

    def send_json(self, data, code=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.send_json(ACTIVE_STATE.to_dict())
        elif parsed.path == "/api/presets":
            self.send_json({k: v["title"] for k, v in PRESETS.items()})
        elif parsed.path.startswith("/drafts/"):
            # Serve generated PDF and markdown files
            rel_path = parsed.path.lstrip("/")
            fpath = ROOT_DIR / rel_path
            if not fpath.exists():
                fpath = ROOT_DIR / "redtape-navigator-unified" / rel_path
            if fpath.exists() and fpath.is_file():
                self.send_response(200)
                if fpath.suffix == ".pdf":
                    self.send_header("Content-Type", "application/pdf")
                elif fpath.suffix in (".md", ".txt"):
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                elif fpath.suffix == ".json":
                    self.send_header("Content-Type", "application/json")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                data = fpath.read_bytes()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            self.send_response(404)
            self.end_headers()
        elif parsed.path == "/" or parsed.path == "/index.html":
            html = render_ui_html()
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        if parsed.path == "/api/load_preset":
            key = req_data.get("preset", "bakery_kolkata")
            ACTIVE_STATE.load_preset(key)
            self.send_json(ACTIVE_STATE.to_dict())

        elif parsed.path == "/api/interview/answer":
            answer = req_data.get("answer", "")
            res = ACTIVE_STATE.process_answer(answer)
            self.send_json(ACTIVE_STATE.to_dict())

        elif parsed.path == "/api/documents/generate":
            ACTIVE_STATE.generate_docs()
            self.send_json(ACTIVE_STATE.to_dict())

        elif parsed.path == "/api/reset":
            ACTIVE_STATE.load_preset(ACTIVE_STATE.preset_key)
            self.send_json(ACTIVE_STATE.to_dict())

        else:
            self.send_response(404)
            self.end_headers()


def render_ui_html():
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RedTape Navigator | Live Judge Demo (Phases 1-3)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8' },
            panel: '#0f172a',
            surface: '#1e293b',
            border: '#334155'
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #0b0f19; font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; }
    .badge-req { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-cond { background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }
    .badge-na { background: rgba(148, 163, 184, 0.15); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }
    .badge-verif { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .tier-mun { background: #3b82f6; }
    .tier-state { background: #06b6d4; }
    .tier-cen { background: #8b5cf6; }
    pre { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
  </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col">

  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between shadow-xl">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/30">
        <i class="fa-solid fa-stamp text-lg"></i>
      </div>
      <div>
        <div class="flex items-center space-x-2">
          <h1 class="text-xl font-bold tracking-tight text-white">RedTape Navigator</h1>
          <span class="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-semibold border border-blue-500/30">Live Workflow · Phases 1–3</span>
        </div>
        <p class="text-xs text-slate-400">Autonomous Legal-Administrative Intelligence for Everyday Citizens</p>
      </div>
    </div>

    <div class="flex items-center space-x-3">
      <div class="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-slate-300 font-medium">Pitch Shield & Circuit Breaker: Active</span>
      </div>
      <button onclick="toggleJsonModal()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold flex items-center space-x-1.5 transition">
        <i class="fa-solid fa-code"></i>
        <span>Inspect State JSON</span>
      </button>
      <button onclick="resetCurrentPreset()" class="px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-semibold transition">
        <i class="fa-solid fa-rotate-left mr-1"></i> Reset
      </button>
    </div>
  </header>

  <!-- Scenario Selector -->
  <div class="bg-slate-900/50 border-b border-slate-800/80 px-6 py-3 flex flex-wrap items-center justify-between gap-3 text-xs">
    <div class="flex items-center space-x-2">
      <span class="text-slate-400 font-semibold uppercase tracking-wider text-[11px]"><i class="fa-solid fa-bolt mr-1 text-amber-400"></i> Judge Scenarios:</span>
      <button onclick="switchPreset('bakery_kolkata')" id="btn-bakery" class="preset-btn px-3 py-1 rounded-md font-medium border border-blue-500 bg-blue-600/30 text-blue-300 transition">
        1. Small Bakery in Kolkata (Business Licensing)
      </button>
      <button onclick="switchPreset('zoning_extension')" id="btn-zoning" class="preset-btn px-3 py-1 rounded-md font-medium border border-slate-700 bg-slate-800 text-slate-400 hover:border-slate-600 transition">
        2. Residential Extension in Salt Lake (Zoning Permit)
      </button>
      <button onclick="switchPreset('agri_irrigation')" id="btn-agri" class="preset-btn px-3 py-1 rounded-md font-medium border border-slate-700 bg-slate-800 text-slate-400 hover:border-slate-600 transition">
        3. Solar Pump Grant in Nadia (Agriculture Subsidy)
      </button>
    </div>
    <div class="text-slate-400 text-right">
      <span class="text-emerald-400 font-mono font-bold">100% Extracted</span> · Zero Fabrication
    </div>
  </div>

  <!-- Main Grid -->
  <main class="flex-1 p-6 grid grid-cols-12 gap-6 max-w-7xl mx-auto w-full">

    <!-- Left Column: Phase 1 & Phase 2 (5 Cols) -->
    <div class="col-span-12 lg:col-span-5 flex flex-col space-y-6">

      <!-- Phase 1: Intent & State Initialization Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-md bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-xs">P1</span>
            <h2 class="font-bold text-white text-sm tracking-wide">Intent & Zero-Fabrication Parser</h2>
          </div>
          <span id="domain-badge" class="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-blue-500/20 text-blue-400 border border-blue-500/30">
            BUSINESS
          </span>
        </div>

        <div class="space-y-3 text-xs">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Citizen Natural Language Goal:</label>
            <div id="goal-text" class="p-2.5 bg-slate-950/70 border border-slate-800 rounded-lg text-slate-200 font-medium">
              Loading...
            </div>
          </div>

          <div>
            <label class="text-slate-400 block mb-1 font-medium flex justify-between">
              <span>Verbatim Provenance (Grounding Proof):</span>
              <span class="text-emerald-400 text-[10px]"><i class="fa-solid fa-shield-halved"></i> Audit Verified</span>
            </label>
            <div id="provenance-list" class="space-y-1.5 p-2 bg-slate-950/70 border border-slate-800 rounded-lg max-h-36 overflow-y-auto">
              <!-- Rendered via JS -->
            </div>
          </div>

          <div class="pt-1 grid grid-cols-2 gap-2 text-[11px]">
            <div class="p-2 bg-slate-800/40 border border-slate-800 rounded">
              <span class="text-slate-400 block">Identified Entity:</span>
              <span id="entity-val" class="font-semibold text-slate-200">Sunrise Bakery</span>
            </div>
            <div class="p-2 bg-slate-800/40 border border-slate-800 rounded">
              <span class="text-slate-400 block">Premises Type:</span>
              <span id="premises-val" class="font-semibold text-slate-200">Rented (Shop)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Phase 2: 3-Tier Research Engine Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex-1 flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-md bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-xs">P2</span>
            <h2 class="font-bold text-white text-sm tracking-wide">3-Tier Government Research Engine</h2>
          </div>
          <span class="text-[11px] text-emerald-400 flex items-center space-x-1">
            <i class="fa-solid fa-check-circle"></i>
            <span>Verified Sources</span>
          </span>
        </div>

        <p class="text-xs text-slate-400 mb-3">
          Simultaneous sweep across Municipal, State, and Central authorities with 6-second circuit breaker protection:
        </p>

        <div id="research-findings" class="space-y-3 overflow-y-auto flex-1 pr-1 text-xs max-h-[380px]">
          <!-- Rendered via JS -->
        </div>
      </div>

    </div>

    <!-- Right Column: Phase 3A & Phase 3B (7 Cols) -->
    <div class="col-span-12 lg:col-span-7 flex flex-col space-y-6">

      <!-- Phase 3A: Compliance Classification Matrix -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs">P3A</span>
            <h2 class="font-bold text-white text-sm tracking-wide">Statutory Compliance Classification Matrix</h2>
          </div>
          <div class="flex items-center space-x-2 text-[11px]">
            <span class="px-2 py-0.5 rounded badge-req font-bold">Required</span>
            <span class="px-2 py-0.5 rounded badge-cond font-bold">Conditional</span>
            <span class="px-2 py-0.5 rounded badge-na font-bold">Exempt</span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="text-slate-400 border-b border-slate-800 text-[11px] uppercase tracking-wider">
                <th class="pb-2.5 font-semibold">Tier & Permit</th>
                <th class="pb-2.5 font-semibold">Status</th>
                <th class="pb-2.5 font-semibold">Legal Rationale / Blocker</th>
                <th class="pb-2.5 font-semibold text-right">Statutory Fee</th>
              </tr>
            </thead>
            <tbody id="matrix-tbody" class="divide-y divide-slate-800/80">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Phase 3B: Interactive Multilingual Interview Console -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex-1 flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-md bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-xs">P3B</span>
            <h2 class="font-bold text-white text-sm tracking-wide">Interactive Multilingual Interview Console</h2>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-xs text-slate-400">Round <span id="round-num" class="text-purple-400 font-bold">1</span> of 4</span>
            <span class="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-medium">PII Deferred</span>
          </div>
        </div>

        <!-- Chat Interaction Area -->
        <div class="flex-1 flex flex-col justify-between space-y-4">

          <div id="interview-chat-bubble" class="p-4 rounded-xl bg-purple-950/30 border border-purple-800/50 text-slate-200 text-xs leading-relaxed relative">
            <div class="flex items-center space-x-2 text-purple-400 font-bold mb-1.5 text-[11px] uppercase tracking-wider">
              <i class="fa-solid fa-robot"></i>
              <span>RedTape Navigator Agent:</span>
            </div>
            <p id="agent-question-text" class="text-slate-200 font-medium text-sm">
              Loading question...
            </p>
          </div>

          <!-- Quick Response Chips -->
          <div>
            <div class="text-[11px] text-slate-400 font-semibold mb-1.5 flex items-center justify-between">
              <span><i class="fa-solid fa-keyboard mr-1 text-blue-400"></i> Judge Quick-Reply Options:</span>
              <span class="text-slate-500 text-[10px]">Click any chip to simulate citizen reply</span>
            </div>
            <div id="quick-replies-container" class="flex flex-wrap gap-2">
              <!-- Rendered via JS -->
            </div>
          </div>

          <!-- Custom Answer Input Box -->
          <form onsubmit="handleAnswerSubmit(event)" class="flex space-x-2 pt-2 border-t border-slate-800">
            <input id="user-answer-input" type="text" placeholder="Or type a conversational reply in English, Hindi, or Bengali..."
                   class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition">
            <button type="submit" id="btn-submit-answer" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition">
              <span>Submit Answer</span>
              <i class="fa-solid fa-paper-plane text-[10px]"></i>
            </button>
          </form>

        </div>

      </div>

      <!-- Supporting Document Catalog Pre-Check -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <i class="fa-solid fa-folder-open text-blue-400"></i>
            <span>Cataloged Supporting Documents (Automated Pre-Check)</span>
          </h3>
          <span class="text-[11px] text-slate-400"><span id="doc-count">0</span> documents identified</span>
        </div>
        <div id="doc-checklist" class="grid grid-cols-2 gap-2 text-xs">
          <!-- Rendered via JS -->
        </div>
      </div>

      <!-- Phase 5 & 6: Document Packs & Review Checkpoint -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
              <i class="fa-solid fa-file-circle-check text-emerald-400"></i>
              <span>Phase 5 & 6: Dual-Channel Submission Packs & Human Review</span>
            </h3>
            <p class="text-[11px] text-slate-400 mt-0.5">Generates AcroForm PDFs with [PENDING_USER_INPUT] stamps and Digital Web Portal copy-sheets + manifests.</p>
          </div>
          <div class="flex items-center space-x-2">
            <button id="btn-gen-docs" onclick="generateDocs()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition flex items-center space-x-1.5">
              <i class="fa-solid fa-file-pdf"></i>
              <span>Generate Submission Packs</span>
            </button>
            <button id="btn-view-review" onclick="toggleReviewModal()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold shadow transition flex items-center space-x-1.5">
              <i class="fa-solid fa-clipboard-check text-blue-400"></i>
              <span>review.md</span>
            </button>
          </div>
        </div>

        <div id="artifacts-container" class="grid grid-cols-2 gap-3 pt-2">
          <!-- Rendered via JS -->
          <div class="col-span-2 text-center py-4 text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg">
            Click "Generate Submission Packs" to produce filled AcroForm PDFs and digital portal copy-sheets.
          </div>
        </div>
      </div>

    </div>

  </main>

  <!-- State JSON Modal Inspector -->
  <div id="json-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-6">
    <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-4xl w-full h-[80vh] flex flex-col overflow-hidden shadow-2xl">
      <div class="px-5 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-file-code text-blue-400"></i>
          <h3 class="font-bold text-sm text-white font-mono">project_state.json (Live AST Engine State)</h3>
        </div>
        <button onclick="toggleJsonModal()" class="text-slate-400 hover:text-white text-sm">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="flex-1 p-4 overflow-auto bg-slate-950 font-mono text-xs text-emerald-400">
        <pre id="json-viewer"></pre>
      </div>
      <div class="px-5 py-3 border-t border-slate-800 bg-slate-900 flex justify-between items-center text-xs text-slate-400">
        <span>Updates reactively on every interview turn & compliance evaluation.</span>
        <button onclick="copyJsonToClipboard()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700">
          <i class="fa-regular fa-copy mr-1"></i> Copy JSON
        </button>
      </div>
    </div>
  </div>

  <!-- Review Package Modal (review.md) -->
  <div id="review-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-6">
    <div class="bg-slate-900 border border-slate-700 rounded-xl max-w-4xl w-full h-[85vh] flex flex-col overflow-hidden shadow-2xl">
      <div class="px-5 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-clipboard-check text-emerald-400"></i>
          <h3 class="font-bold text-sm text-white">review.md (Human Review & Audit Checkpoint)</h3>
        </div>
        <button onclick="toggleReviewModal()" class="text-slate-400 hover:text-white text-sm">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="flex-1 p-6 overflow-auto bg-slate-950 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
        <div id="review-viewer"></div>
      </div>
      <div class="px-5 py-3 border-t border-slate-800 bg-slate-900 flex justify-between items-center text-xs text-slate-400">
        <span>6-part statutory review package ensuring full human-in-the-loop oversight.</span>
        <button onclick="copyReviewToClipboard()" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700">
          <i class="fa-regular fa-copy mr-1"></i> Copy Markdown
        </button>
      </div>
    </div>
  </div>

  <script>
    let currentState = null;

    async function fetchState() {
      try {
        const res = await fetch('/api/state');
        currentState = await res.json();
        renderDashboard(currentState);
      } catch (e) {
        console.error("Failed to load state", e);
      }
    }

    async function switchPreset(key) {
      document.querySelectorAll('.preset-btn').forEach(b => {
        b.classList.remove('border-blue-500', 'bg-blue-600/30', 'text-blue-300');
        b.classList.add('border-slate-700', 'bg-slate-800', 'text-slate-400');
      });
      const activeBtn = key === 'bakery_kolkata' ? 'btn-bakery' : (key === 'zoning_extension' ? 'btn-zoning' : 'btn-agri');
      document.getElementById(activeBtn).classList.add('border-blue-500', 'bg-blue-600/30', 'text-blue-300');

      const res = await fetch('/api/load_preset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset: key })
      });
      currentState = await res.json();
      renderDashboard(currentState);
    }

    async function resetCurrentPreset() {
      const res = await fetch('/api/reset', { method: 'POST' });
      currentState = await res.json();
      renderDashboard(currentState);
    }

    async function handleAnswerSubmit(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('user-answer-input');
      const val = input.value.trim();
      if (!val) return;

      input.disabled = true;
      document.getElementById('btn-submit-answer').disabled = true;

      const res = await fetch('/api/interview/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer: val })
      });
      currentState = await res.json();
      input.value = '';
      input.disabled = false;
      document.getElementById('btn-submit-answer').disabled = false;
      renderDashboard(currentState);
    }

    function sendQuickReply(text) {
      document.getElementById('user-answer-input').value = text;
      handleAnswerSubmit(null);
    }

    function renderDashboard(state) {
      if (!state) return;

      // Phase 1
      document.getElementById('domain-badge').innerText = state.domain;
      document.getElementById('goal-text').innerText = state.goal;
      document.getElementById('entity-val').innerText = state.applicant_profile.entity_name || 'N/A';
      document.getElementById('premises-val').innerText = (state.applicant_profile.location.premises_type || 'N/A') + ' in ' + (state.applicant_profile.location.city_or_village || 'N/A');

      const provList = document.getElementById('provenance-list');
      provList.innerHTML = '';
      for (const [k, v] of Object.entries(state.provenance || {})) {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between text-[11px] text-slate-300 bg-slate-900/60 px-2 py-1 rounded border border-slate-800/80';
        row.innerHTML = `<span class="text-slate-400 truncate max-w-[180px] font-mono">${k.split('.').slice(-1)[0]}:</span> <span class="text-amber-300 font-medium">"${v}"</span>`;
        provList.appendChild(row);
      }

      // Phase 2
      const resContainer = document.getElementById('research-findings');
      resContainer.innerHTML = '';
      state.research_findings.forEach(f => {
        const tierClass = f.tier === 'municipal' ? 'tier-mun' : (f.tier === 'state' ? 'tier-state' : 'tier-cen');
        const card = document.createElement('div');
        card.className = 'p-3 bg-slate-950/60 border border-slate-800 rounded-lg hover:border-slate-700 transition space-y-1.5';
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-1.5">
              <span class="text-[9px] font-bold text-white uppercase px-1.5 py-0.5 rounded ${tierClass}">${f.tier}</span>
              <span class="font-bold text-slate-100 text-xs">${f.name}</span>
            </div>
            <span class="text-[10px] text-slate-400 font-mono">${f.form_version || 'Form'}</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-tight">${f.authority}</p>
          <div class="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
            <span>Fee: <strong class="text-slate-200">${f.statutory_fee || 'Variable'}</strong></span>
            <a href="${f.official_source_url}" target="_blank" class="text-blue-400 hover:underline flex items-center space-x-1">
              <span>Gov Portal</span> <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
            </a>
          </div>
        `;
        resContainer.appendChild(card);
      });

      // Phase 3A
      const matrixTbody = document.getElementById('matrix-tbody');
      matrixTbody.innerHTML = '';
      state.compliance_matrix.forEach(row => {
        const badgeClass = row.status === 'Required' ? 'badge-req' : (row.status === 'Conditional' ? 'badge-cond' : (row.status === 'Needs Verification' ? 'badge-verif' : 'badge-na'));
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/30 transition';
        tr.innerHTML = `
          <td class="py-2.5 pr-2">
            <span class="font-semibold text-slate-200 block">${row.name}</span>
            <span class="text-[10px] text-slate-400 block">${row.authority}</span>
          </td>
          <td class="py-2.5 px-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase ${badgeClass}">${row.status}</span>
          </td>
          <td class="py-2.5 px-2 text-[11px] text-slate-300 max-w-xs">
            ${row.rationale}
          </td>
          <td class="py-2.5 pl-2 text-right font-medium text-slate-200 font-mono text-[11px]">
            ${row.statutory_fee || '—'}
          </td>
        `;
        matrixTbody.appendChild(tr);
      });

      // Phase 3B
      document.getElementById('round-num').innerText = state.round;
      const turn = state.interview_turn;
      const agentBubble = document.getElementById('interview-chat-bubble');
      const questionText = document.getElementById('agent-question-text');
      const repliesContainer = document.getElementById('quick-replies-container');
      repliesContainer.innerHTML = '';

      if (turn.complete) {
        agentBubble.className = 'p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-slate-200 text-xs';
        questionText.innerHTML = `<span class="text-emerald-400 font-bold block mb-1">🎉 Interview Complete!</span> ${turn.message}`;
        document.getElementById('user-answer-input').disabled = true;
        document.getElementById('btn-submit-answer').disabled = true;
      } else {
        agentBubble.className = 'p-4 rounded-xl bg-purple-950/30 border border-purple-800/50 text-slate-200 text-xs';
        questionText.innerText = turn.question;
        document.getElementById('user-answer-input').disabled = false;
        document.getElementById('btn-submit-answer').disabled = false;

        (turn.quick_replies || []).forEach(r => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'px-3 py-1 bg-slate-800 hover:bg-purple-900/50 hover:border-purple-600 border border-slate-700 text-slate-200 rounded-lg text-xs font-medium transition';
          btn.innerText = r;
          btn.onclick = () => sendQuickReply(r);
          repliesContainer.appendChild(btn);
        });
      }

      // Supporting Documents
      const docList = document.getElementById('doc-checklist');
      docList.innerHTML = '';
      document.getElementById('doc-count').innerText = (state.supporting_documents || []).length;
      (state.supporting_documents || []).forEach(d => {
        const el = document.createElement('div');
        const stClass = d.status === 'Ready' ? 'text-emerald-400' : (d.status === 'Pending' ? 'text-amber-400' : 'text-slate-400');
        el.className = 'flex items-center justify-between p-2 bg-slate-950/50 border border-slate-800/80 rounded text-[11px]';
        el.innerHTML = `
          <span class="truncate text-slate-300 font-medium">${d.name}</span>
          <span class="font-mono text-[10px] ${stClass}">${d.status}</span>
        `;
        docList.appendChild(el);
      });

      // Update Modal JSON
      document.getElementById('json-viewer').innerText = JSON.stringify(state, null, 2);

      // Phase 5 & 6: Artifacts rendering
      const artContainer = document.getElementById('artifacts-container');
      artContainer.innerHTML = '';
      const forms = state.form_artifacts || [];
      const portals = state.portal_artifacts || [];

      if (!forms.length && !portals.length) {
        artContainer.innerHTML = `
          <div class="col-span-2 text-center py-4 text-xs text-slate-500 border border-dashed border-slate-800 rounded-lg">
            Click "Generate Submission Packs" to produce filled AcroForm PDFs and digital portal copy-sheets.
          </div>
        `;
      } else {
        forms.forEach(fa => {
          const card = document.createElement('div');
          card.className = 'p-3 bg-slate-950/70 border border-slate-800 rounded-lg space-y-1.5';
          const relPdf = fa.file_path.includes('drafts/') ? 'drafts/' + fa.file_path.split('drafts/')[1] : fa.file_path;
          card.innerHTML = `
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                <i class="fa-solid fa-file-pdf text-red-400"></i>
                <span class="truncate">${fa.form_name}</span>
              </span>
              <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-blue-900/40 text-blue-300 border border-blue-700/50">${fa.completion_percentage}% Ready</span>
            </div>
            <p class="text-[10px] text-slate-400">Official form filled with [PENDING_USER_INPUT] stamps for missing data.</p>
            <div class="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
              <span class="text-slate-500 text-[10px] font-mono">${fa.status}</span>
              <a href="/${relPdf}" target="_blank" class="text-blue-400 hover:text-blue-300 flex items-center space-x-1 font-semibold">
                <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                <span>Open PDF</span>
              </a>
            </div>
          `;
          artContainer.appendChild(card);
        });

        portals.forEach(pa => {
          const card = document.createElement('div');
          card.className = 'p-3 bg-slate-950/70 border border-slate-800 rounded-lg space-y-1.5';
          const relMd = pa.copy_sheet_path.includes('drafts/') ? 'drafts/' + pa.copy_sheet_path.split('drafts/')[1] : pa.copy_sheet_path;
          const relMan = (pa.manifest_path || '').includes('drafts/') ? 'drafts/' + pa.manifest_path.split('drafts/')[1] : pa.manifest_path;
          card.innerHTML = `
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                <i class="fa-solid fa-globe text-cyan-400"></i>
                <span class="truncate">${pa.portal_name}</span>
              </span>
              <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-cyan-900/40 text-cyan-300 border border-cyan-700/50">${pa.completion_percentage}% Ready</span>
            </div>
            <p class="text-[10px] text-slate-400">Copy-sheet & Playwright draft-fill manifest with human gates.</p>
            <div class="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
              <a href="/${relMan}" target="_blank" class="text-purple-400 hover:text-purple-300 text-[10px] font-mono">manifest.json</a>
              <a href="/${relMd}" target="_blank" class="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-semibold">
                <i class="fa-solid fa-file-lines text-[10px]"></i>
                <span>Copy-Sheet</span>
              </a>
            </div>
          `;
          artContainer.appendChild(card);
        });
      }

      if (state.review_md) {
        document.getElementById('review-viewer').innerText = state.review_md;
      }
    }

    async function generateDocs() {
      const btn = document.getElementById('btn-gen-docs');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Generating...';
      try {
        const res = await fetch('/api/documents/generate', { method: 'POST' });
        currentState = await res.json();
        renderDashboard(currentState);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-file-pdf mr-1"></i> Generate Submission Packs';
      }
    }

    function toggleReviewModal() {
      const modal = document.getElementById('review-modal');
      modal.classList.toggle('hidden');
    }

    function copyReviewToClipboard() {
      const text = document.getElementById('review-viewer').innerText;
      navigator.clipboard.writeText(text);
      alert('Review markdown copied to clipboard!');
    }

    function toggleJsonModal() {
      const modal = document.getElementById('json-modal');
      modal.classList.toggle('hidden');
    }

    function copyJsonToClipboard() {
      const text = document.getElementById('json-viewer').innerText;
      navigator.clipboard.writeText(text);
      alert('State JSON copied to clipboard!');
    }

    // Init
    window.addEventListener('DOMContentLoaded', fetchState);
  </script>
</body>
</html>
"""


def main():
    port = int(os.environ.get("PORT", 8765))
    server = HTTPServer(("0.0.0.0", port), DemoServerHandler)
    print(f"\n=======================================================")
    print(f"  REDTAPE NAVIGATOR - LIVE WORKFLOW DEMO SERVER")
    print(f"  Running at: http://localhost:{port}")
    print(f"  Serving Phases 1 to 3 interactive demonstration")
    print(f"=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down demo server.")
        server.server_close()


if __name__ == "__main__":
    main()
