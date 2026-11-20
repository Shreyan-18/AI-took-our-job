# LangGraph + FastAPI + React Implementation Mapping

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

class RedTapeState(TypedDict, total=False):
    project_id: str; goal: str; domain: str; applicant_profile: dict
    provenance: dict; research_findings: list; compliance_matrix: list
    open_questions: list; form_artifacts: list; portal_artifacts: list
    required_supporting_documents: list; overrides: dict
    validation: dict; workflow_flags: dict; errors: list

g = StateGraph(RedTapeState)
for name, fn in [("research", research), ("compliance", compliance),
                 ("interview", interview), ("document", document),
                 ("validate", validate), ("review", review)]:
    g.add_node(name, fn)
g.set_entry_point("research")
g.add_edge("research", "compliance")
g.add_conditional_edges("compliance", lambda s: "interview" if s.get("open_questions") and s.get("workflow_flags", {}).get("interview_rounds", 0) < 4 else "document")
g.add_edge("interview", "compliance")
g.add_edge("document", "validate")
g.add_conditional_edges("validate", lambda s: "review" if s.get("validation", {}).get("passed") else "interview")
g.add_edge("review", END)
app = g.compile(checkpointer=SqliteSaver.from_conn_string("redtape.db"), interrupt_before=["interview", "review"])
```

- **Script Reuse:** `fill_pdf.py`, `generate_portal_pack.py`, `validate_state.py`, and `render_review.py` expose pure Python functions (`fill`, `build_portal_pack`, `validate`, `render`) directly importable by LangGraph nodes.
- **FastAPI Endpoints:** `POST /projects`, `POST /projects/{id}/messages`, `GET /projects/{id}/state`, `GET /projects/{id}/forms/{name}.pdf`, `POST /projects/{id}/overrides`, `GET /projects/{id}/stream` (SSE).
