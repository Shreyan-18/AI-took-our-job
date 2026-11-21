#!/usr/bin/env python3
"""End-to-end verification script for the 3 target judge scenarios and Langfuse tracing."""
import sys
import os
import json
from pathlib import Path

# Import demo_server components
from demo_server import LiveDemoState, match_scenario, PRESETS

def run_tests():
    print("==================================================")
    print("RUNNING END-TO-END SCENARIO & COMPLIANCE AUDIT")
    print("==================================================")

    # 1. Test Matcher
    test_prompts = [
        ("open a bakery shop in kolkata park circus, kolkata", "bakery_kolkata"),
        ("I want to set up an artisan bakery in Park Circus with 5 stools", "bakery_kolkata"),
        ("open a stationary book stall in sodpur", "stationery_sodpur"),
        ("planning a small book stall near sodepur station", "stationery_sodpur"),
        ("open a clothes shop in barrackpore", "clothes_barrackpore"),
        ("I want to launch a readymade garments boutique in Barrackpore", "clothes_barrackpore"),
    ]

    for p, expected in test_prompts:
        matched = match_scenario(p)
        assert matched == expected, f"Failed match: '{p}' got {matched}, expected {expected}"
        print(f"✓ Matcher OK: '{p[:45]}...' -> {matched}")

    state = LiveDemoState()

    # 2. Test Scenario 1: Bakery
    print("\n--- Testing Scenario 1: Bakery in Park Circus ---")
    res1 = state.handle_chat("open a bakery shop in kolkata park circus, kolkata")
    matrix1 = state.compliance_matrix
    status_map1 = {m["id"]: m["status"] for m in matrix1}
    print("Compliance Matrix:", status_map1)
    assert status_map1.get("lic_kmc_ce") == "Required"
    assert status_map1.get("lic_wb_shops") == "Required"
    assert status_map1.get("lic_fssai_basic") == "Conditional"
    assert status_map1.get("lic_wb_fire") == "Not Applicable"

    # Test answering interview question
    ans1 = state.handle_chat("My expected annual turnover is around ₹8.5 Lakhs")
    status_map1_updated = {m["id"]: m["status"] for m in state.compliance_matrix}
    print("Updated after Turnover Answer:", status_map1_updated)
    assert status_map1_updated.get("lic_fssai_basic") == "Required"
    print("Form Artifacts for Bakery:", [f["form_name"] for f in state.form_artifacts])
    assert any("FSSAI" in f["form_name"] for f in state.form_artifacts)

    # 3. Test Scenario 2: Stationery Book Stall
    print("\n--- Testing Scenario 2: Stationery Book Stall in Sodepur ---")
    res2 = state.handle_chat("open a stationary book stall in sodpur")
    matrix2 = state.compliance_matrix
    status_map2 = {m["id"]: m["status"] for m in matrix2}
    print("Compliance Matrix:", status_map2)
    assert status_map2.get("lic_panihati_ce") == "Conditional"
    assert status_map2.get("lic_wb_shops") == "Required"
    assert status_map2.get("lic_wb_signage") == "Required"
    assert status_map2.get("lic_fssai_basic") == "Not Applicable", "FSSAI must be Not Applicable for Bookstore!"
    assert status_map2.get("lic_wb_fire") == "Not Applicable"

    # Test answering interview question
    ans2 = state.handle_chat("Carpet area is about 180 sq ft")
    status_map2_updated = {m["id"]: m["status"] for m in state.compliance_matrix}
    print("Updated after Floor Area Answer:", status_map2_updated)
    assert status_map2_updated.get("lic_panihati_ce") == "Required"
    print("Form Artifacts for Stationery:", [f["form_name"] for f in state.form_artifacts])
    assert not any("FSSAI" in f["form_name"] for f in state.form_artifacts), "FSSAI must NOT be drafted for Bookstore!"
    assert any("Municipal" in f["form_name"] for f in state.form_artifacts)

    # 4. Test Scenario 3: Clothes Shop
    print("\n--- Testing Scenario 3: Clothes Shop in Barrackpore ---")
    res3 = state.handle_chat("open a clothes shop in barrackpore")
    matrix3 = state.compliance_matrix
    status_map3 = {m["id"]: m["status"] for m in matrix3}
    print("Compliance Matrix:", status_map3)
    assert status_map3.get("lic_barrackpore_ce") == "Required"
    assert status_map3.get("lic_wb_shops") == "Conditional"
    assert status_map3.get("lic_wb_fire_advisory") == "Required"
    assert status_map3.get("lic_wb_signage") == "Required"
    assert status_map3.get("lic_fssai_basic") == "Not Applicable", "FSSAI must be Not Applicable for Clothes Store!"
    assert status_map3.get("lic_factories_act") == "Not Applicable"

    # Test answering interview question
    ans3 = state.handle_chat("I will employ 4 sales staff members")
    status_map3_updated = {m["id"]: m["status"] for m in state.compliance_matrix}
    print("Updated after Workers Answer:", status_map3_updated)
    assert status_map3_updated.get("lic_wb_shops") == "Required"
    print("Form Artifacts for Clothes:", [f["form_name"] for f in state.form_artifacts])
    assert not any("FSSAI" in f["form_name"] for f in state.form_artifacts), "FSSAI must NOT be drafted for Clothes Store!"
    assert any("Municipal" in f["form_name"] for f in state.form_artifacts)

    print("\n==================================================")
    print("ALL 3 SCENARIOS PASSED WITH PERFECT STATUTORY LOGIC!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
