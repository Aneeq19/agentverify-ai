"""Versioned, section-level keyword retrieval with visible evidence."""
import hashlib
import re
from pathlib import Path
from schemas import Guidance

KB = Path(__file__).with_name("knowledge_base.md")
STOP = {"what", "with", "from", "should", "the", "and", "for", "this",
        "that", "does", "have", "about", "information", "help", "tell",
        "case", "patient", "verification", "dental"}


def retrieve_workflow_guidance(query: str, limit: int = 3) -> list[Guidance]:
    content = KB.read_text(encoding="utf-8")
    version = hashlib.sha256(content.encode()).hexdigest()[:12]
    terms = set(re.findall(r"[a-z]{3,}", query.lower())) - STOP
    scored = []
    for section in content.split("\n---\n"):
        title_match = re.search(r"^## (.+)$", section, re.M)
        if not title_match:
            continue
        title = title_match.group(1)
        if title in {"Purpose", "Mandatory Verification Rule"}:
            continue
        words = set(re.findall(r"[a-z]{3,}", section.lower()))
        score = len(terms & words)
        if score:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            scored.append((score, Guidance(
                source_id=f"knowledge_base.md#{slug}", title=title,
                text=section.strip(), version=version,
            )))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:limit]]
