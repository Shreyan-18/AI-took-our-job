#!/usr/bin/env python3
"""Integration Test for LangGraph Human-In-The-Loop (HITL) Checkpoints & Interrupts."""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from _common import load_json, save_json
from langgraph.checkpoint.memory import MemorySaver
from workflow import RedTapeState, build_workflow


def main():
    print("--- [TEST] Starting LangGraph Human-In-The-Loop Flow ---")
    memory = MemorySaver()
    app = build_workflow(checkpointer=memory, interrupt_interview=True, interrupt_review=False)

    # Initial state with bakery goal in demo mode (uses cached research for 10ms speed)
    thread_id = "test_thread_bakery_hitl"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "project_id": thread_id,
        "goal": "I want to open a small bakery in Park Circus, Kolkata with 5 counter seats",
        "created_at": "2026-11-20T22:00:00+00:00",
        "preferred_language": "en",
        "applicant_profile": {},
        "provenance": {},
        "research_findings": [],
        "compliance_matrix": [],
        "open_questions": [],
        "form_artifacts": [],
        "portal_artifacts": [],
        "required_supporting_documents": [],
        "overrides": {},
        "workflow_flags": {"research_mode": "cached_live"},
        "errors": [],
    }

    # Step 1: Run graph until first interrupt
    print("\n[Step 1] Invoking graph from start...")
    app.invoke(initial_state, config=config)

    # Inspect state at interrupt
    snapshot = app.get_state(config)
    print(f"Graph paused at next node: {snapshot.next}")
    assert "interview" in snapshot.next, f"Expected graph to pause before 'interview', but got {snapshot.next}"
    print(f"Open questions awaiting citizen input: {snapshot.values.get('open_questions')}")

    # Step 2: Resume with citizen conversational answer
    user_answer = "We expect about 8 lakh rupees annual turnover, and there will be 3 workers on site assisting with baking and counter sales."
    print(f"\n[Step 2] Resuming graph with citizen response:\n\"{user_answer}\"")

    app.update_state(config, {"user_answer": user_answer})
    app.invoke(None, config=config)

    # Handle follow-up interview rounds if any open questions remain
    round_count = 1
    while round_count < 4:
        cur_snap = app.get_state(config)
        if not cur_snap.next or "interview" not in cur_snap.next:
            break
        round_count += 1
        follow_up = "The shop area is 250 sq ft and we use electric baking equipment without commercial gas cylinders."
        print(f"\n[Step 2.{round_count}] Providing follow-up answers:\n\"{follow_up}\"")
        app.update_state(config, {"user_answer": follow_up})
        app.invoke(None, config=config)

    # Step 3: Verify completion
    final_snapshot = app.get_state(config)
    print(f"Graph final next node: {final_snapshot.next} (empty means END reached)")
    assert not final_snapshot.next, "Expected graph to have completed all nodes to END"

    values = final_snapshot.values
    print("\n[Verification Summary]:")
    turnover_val = values.get('applicant_profile', {}).get('domain_attributes', {}).get('expected_annual_turnover_inr')
    workers_val = values.get('applicant_profile', {}).get('domain_attributes', {}).get('workers_on_site')
    print(f"- Annual Turnover: {turnover_val}")
    print(f"- Workers on Site: {workers_val}")
    if turnover_val:
        print(f"- Provenance for turnover: \"{values['provenance'].get('applicant_profile.domain_attributes.expected_annual_turnover_inr')}\"")
    print(f"- Form Artifacts Generated: {len(values.get('form_artifacts', []))}")
    print(f"- Portal Artifacts Generated: {len(values.get('portal_artifacts', []))}")
    print(f"- Validation Passed: {values.get('validation', {}).get('passed')}")
    print(f"- Review Package Path: {values.get('review_path')}")

    assert values.get('validation', {}).get('passed') is True
    assert len(values.get('form_artifacts', [])) > 0 or len(values.get('portal_artifacts', [])) > 0
    print("\nALL HITL INTEGRATION CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
