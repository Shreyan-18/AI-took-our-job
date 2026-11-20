#!/usr/bin/env python3
"""LangGraph StateGraph Orchestration Engine for RedTape Navigator.
Implements the unified autonomous legal-administrative pipeline:
  [User Goal]
       |
  (orchestrator) -> (research) -> (compliance) <---+
                                       |            | (interview answers loop)
                           [has open Qs?] -> (interview)
                                       |
                                  (documents)
                                       |
                                  (validate)
                                       |
                                   (review) -> [END]

Preserves human checkpoints via interrupts before interview turns and review packaging.
"""
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from _common import effective_value, is_blank, load_json, save_json
from compliance_engine import compliance as run_compliance
from document_engine import generate_documents
from interview_engine import generate_question_batch, process_user_answer, rank_open_questions
from orchestrator_parser import parse_intent
from render_review import render as render_review_md
from research_engine import research as run_research
from validate_state import validate as run_validate


class RedTapeState(TypedDict, total=False):
    project_id: str
    goal: str
    domain: str
    preferred_language: str
    created_at: str
    applicant_profile: dict[str, Any]
    provenance: dict[str, str]
    research_findings: list[dict[str, Any]]
    compliance_matrix: list[dict[str, Any]]
    open_questions: list[str]
    form_artifacts: list[dict[str, Any]]
    portal_artifacts: list[dict[str, Any]]
    required_supporting_documents: list[dict[str, Any]]
    overrides: dict[str, Any]
    validation: dict[str, Any]
    workflow_flags: dict[str, Any]
    errors: list[str]

    # Graph coordination fields
    user_answer: Optional[str]
    latest_interview_turn: Optional[dict[str, Any]]
    review_markdown: Optional[str]
    review_path: Optional[str]


# ---------------- Node Implementations ---------------- #

def node_orchestrator(state: RedTapeState) -> dict[str, Any]:
    """Extract location, domain, and pre-stated facts from user goal."""
    print("\n--- [LangGraph Node: Orchestrator] ---")
    goal = state.get("goal", "")
    if not goal:
        raise ValueError("State 'goal' is required.")

    # Only parse if profile is missing activity_type
    profile = state.get("applicant_profile", {})
    if not profile.get("activity_type"):
        print(f"Parsing goal: \"{goal}\"")
        parsed = parse_intent(goal)
        state_update = {
            "domain": parsed.get("domain", state.get("domain", "general")),
            "applicant_profile": parsed.get("applicant_profile", {}),
            "provenance": parsed.get("provenance", {}),
        }
        return state_update
    print("Applicant profile already present; skipping initial parse.")
    return {}


def node_research(state: RedTapeState) -> dict[str, Any]:
    """Execute 3-tier live regulatory search across Municipal, State, and Central tiers."""
    print("\n--- [LangGraph Node: Research Engine (3-Tier & Pitch Shield)] ---")
    findings = state.get("research_findings", [])
    if not findings:
        is_demo = state.get("workflow_flags", {}).get("research_mode") in ("cached_live", "demo")
        updated = run_research(state, demo_mode=is_demo)
        return {
            "research_findings": updated.get("research_findings", []),
            "workflow_flags": updated.get("workflow_flags", {}),
        }
    print(f"Research findings already present ({len(findings)} items).")
    return {}


def node_compliance(state: RedTapeState) -> dict[str, Any]:
    """Evaluate research findings against profile and update audit trail."""
    print("\n--- [LangGraph Node: Compliance Matrix & Audit Trail] ---")
    updated = run_compliance(state)
    return {
        "compliance_matrix": updated.get("compliance_matrix", []),
        "open_questions": updated.get("open_questions", []),
        "required_supporting_documents": updated.get("required_supporting_documents", []),
        "workflow_flags": updated.get("workflow_flags", {}),
    }


def node_interview(state: RedTapeState) -> dict[str, Any]:
    """Handle conversational slot-filling and question batching."""
    print("\n--- [LangGraph Node: Multilingual Interview Engine] ---")
    user_ans = state.get("user_answer")
    state_updates: dict[str, Any] = {}

    # If the user supplied an answer, parse it first
    if user_ans:
        print(f"Processing incoming citizen response: \"{user_ans}\"")
        active_targets = rank_open_questions(state)[:3]
        parse_res = process_user_answer(state, user_ans, active_targets)
        print(f"Extracted: {json.dumps(parse_res.get('extracted'))}")
        state_updates["applicant_profile"] = state.get("applicant_profile")
        state_updates["provenance"] = state.get("provenance")
        state_updates["workflow_flags"] = state.get("workflow_flags")
        state_updates["open_questions"] = state.get("open_questions")
        state_updates["user_answer"] = None  # Clear consumed answer

    # Generate next question batch
    batch = generate_question_batch(state)
    state_updates["latest_interview_turn"] = batch
    if batch.get("complete"):
        print(f"Interview Complete: {batch.get('question')}")
    else:
        print(f"[Round {batch.get('round')}] Generated Question for Citizen:\n{batch.get('question')}")

    return state_updates


def node_documents(state: RedTapeState) -> dict[str, Any]:
    """Generate official AcroForm PDF drafts and Digital Portal submission packs."""
    print("\n--- [LangGraph Node: Document & Web Portal Engine] ---")
    updated = generate_documents(state)
    return {
        "form_artifacts": updated.get("form_artifacts", []),
        "portal_artifacts": updated.get("portal_artifacts", []),
        "required_supporting_documents": updated.get("required_supporting_documents", []),
        "workflow_flags": updated.get("workflow_flags", {}),
    }


def node_validate(state: RedTapeState) -> dict[str, Any]:
    """Validate canonical invariants and zero fabrication."""
    print("\n--- [LangGraph Node: Invariant Validation] ---")
    val_res = run_validate(state)
    return {"validation": val_res}


def node_review(state: RedTapeState) -> dict[str, Any]:
    """Render comprehensive 6-part markdown review package."""
    print("\n--- [LangGraph Node: Human Review Checkpoint] ---")
    review_text = render_review_md(state)
    proj_id = state.get("project_id", "default_project")
    out_dir = ROOT_DIR / "drafts" / proj_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "review.md"
    out_file.write_text(review_text, encoding="utf-8")
    print(f"Rendered Human Review Package -> {out_file}")
    return {
        "review_markdown": review_text,
        "review_path": str(out_file),
    }


# ---------------- Conditional Routing ---------------- #

def route_after_compliance(state: RedTapeState) -> str:
    """Route to interview if open questions exist and round limit not reached."""
    flags = state.get("workflow_flags", {})
    open_q = state.get("open_questions", [])
    rounds = flags.get("interview_rounds", 0)

    if open_q and rounds < 4 and not flags.get("interview_complete"):
        return "interview"
    return "documents"


def route_after_interview(state: RedTapeState) -> str:
    """Route back to compliance to re-evaluate rules if an answer was parsed."""
    flags = state.get("workflow_flags", {})
    if flags.get("compliance_needs_reeval"):
        flags["compliance_needs_reeval"] = False
        return "compliance"
    return "documents"


# ---------------- StateGraph Builder ---------------- #

def build_workflow(checkpointer=None, interrupt_interview: bool = True, interrupt_review: bool = True):
    """Compile the LangGraph workflow."""
    workflow = StateGraph(RedTapeState)

    workflow.add_node("orchestrator", node_orchestrator)
    workflow.add_node("research", node_research)
    workflow.add_node("compliance", node_compliance)
    workflow.add_node("interview", node_interview)
    workflow.add_node("documents", node_documents)
    workflow.add_node("validate", node_validate)
    workflow.add_node("review", node_review)

    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "research")
    workflow.add_edge("research", "compliance")

    workflow.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {
            "interview": "interview",
            "documents": "documents",
        },
    )

    workflow.add_conditional_edges(
        "interview",
        route_after_interview,
        {
            "compliance": "compliance",
            "documents": "documents",
        },
    )

    workflow.add_edge("documents", "validate")
    workflow.add_edge("validate", "review")
    workflow.add_edge("review", END)

    interrupts = []
    if interrupt_interview:
        interrupts.append("interview")
    if interrupt_review:
        interrupts.append("review")

    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupts if interrupts else None,
    )
    return app


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Run RedTape Navigator LangGraph Orchestration.")
    ap.add_argument("--goal", help="Initial user goal text")
    ap.add_argument("--state", help="Path to initial or resumed state.json")
    ap.add_argument("--answer", help="Citizen answer to resume graph from interview interrupt")
    ap.add_argument("--no-interrupts", action="store_true", help="Run straight through with simulated answer")
    ap.add_argument("--out", help="Path to save resulting state.json")
    args = ap.parse_args()

    initial_state = {}
    if args.state:
        initial_state = load_json(args.state)
    elif args.goal:
        initial_state = {
            "project_id": f"proj_run_{int(os.getpid())}",
            "goal": args.goal,
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
            "workflow_flags": {},
            "errors": [],
        }
    else:
        ap.error("Must provide either --goal or --state.")

    if args.answer:
        initial_state["user_answer"] = args.answer

    memory = MemorySaver()
    app = build_workflow(checkpointer=memory, interrupt_interview=not args.no_interrupts, interrupt_review=not args.no_interrupts)

    thread_config = {"configurable": {"thread_id": initial_state.get("project_id", "demo_thread")}}

    print("\nExecuting RedTape Navigator StateGraph...")
    result = app.invoke(initial_state, config=thread_config)
    print("\nGraph Execution Finished (or paused at interrupt checkpoint).")

    out_file = args.out or f"drafts/{initial_state.get('project_id', 'demo_thread')}/state.json"
    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    save_json(out_file, result)
    print(f"Saved state to {out_file}.")


if __name__ == "__main__":
    main()
