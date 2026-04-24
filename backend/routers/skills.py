from fastapi import APIRouter
from pathlib import Path
import re

router = APIRouter(prefix="/api/skills", tags=["skills"])

# skills/ lives at the project root, one level above backend/
SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


def _parse_md(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    name_m = re.search(r"^# SKILL: (.+)$", text, re.MULTILINE)
    name_he = name_m.group(1).strip() if name_m else path.stem.replace("SKILL_", "")

    slug_m = re.search(r"\*\*סלאג:\*\*\s*`([^`]+)`", text)
    slug = slug_m.group(1).strip() if slug_m else path.stem.replace("SKILL_", "")

    date_m = re.search(r"\*\*תאריך יצירה:\*\*\s*(.+)$", text, re.MULTILINE)
    created_at = date_m.group(1).strip() if date_m else ""

    # Extract the fill-in-the-blanks block under ## נוסח הפעלה אחיד
    act_m = re.search(
        r"## נוסח הפעלה אחיד\s*```[^\n]*\n(.*?)```",
        text,
        re.DOTALL,
    )
    activation_prompt = act_m.group(1).strip() if act_m else ""

    return {
        "name_he": name_he,
        "slug": slug,
        "created_at": created_at,
        "activation_prompt": activation_prompt,
    }


@router.get("")
def list_skills():
    if not SKILLS_DIR.exists():
        return []
    return [
        parsed
        for path in sorted(SKILLS_DIR.glob("SKILL_*.md"))
        if (parsed := _parse_md(path)) is not None
    ]
