#!/usr/bin/env python3
"""skill_builder.py — LizziAI Skill Builder CLI"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("שגיאה: חבילת anthropic נדרשת. הפעל: pip install anthropic")
    sys.exit(1)

SKILLS_DIR = Path("skills")
MODEL = "claude-opus-4-7"

# Stable system prompt — cached to avoid repeated token costs across batch runs
SYSTEM_PROMPT = """אתה מומחה לבניית skills ל-LizziAI — עורך דין AI המשמש משרדי עורכי דין בישראל.

## עקרונות ספריית ה-Skills (חובה לשלב בכל skill)
1. תמיד לייצר פלט מלא וגמור — אין גרסה מקוצרת
2. להתקדם מקצועית גם עם מידע חלקי; לציין פערים במפורש
3. לעולם לא להמציא עובדות, מקורות, הנחות או מסקנות
4. הפלט חייב להיות מעשי ומוכוון-החלטה, לא אקדמי
5. לשאול רק שאלה ממוקדת אחת אם חסר מידע קריטי באמת
6. לשמור על עקביות פנימית בין כל ה-skills בספרייה

## מבנה מסמך Skill (חובה)
כל skill חייב לכלול את הסעיפים הבאים בדיוק:
- מטרה
- מתי מפעילים (לפחות 3 תנאים)
- קלט חובה
- קלט רצוי
- עקרונות עבודה מחייבים (לפחות 10)
- שלבי ביצוע (לפחות 10)
- פורמט פלט (מפורט)
- כללי זהירות (לפחות 5)
- בדיקות איכות לפני מסירה (לפחות 9)
- נוסח הפעלה אחיד (תבנית fill-in-the-blanks)

## ה-Benchmark: מזכר משפטי
ה-skill "מזכר משפטי" הוא הסטנדרט: ~10 עקרונות מחייבים, ~10 שלבי ביצוע, מפרט פלט מלא, 5 כללי זהירות, 9 בדיקות איכות. כל skill חדש חייב להגיע לאותה רמת פירוט.

## שפה ואיכות
- כל התוכן בעברית מקצועית-משפטית
- עקרונות ספציפיים ל-skill, לא גנריים
- שלבים פרקטיים ומפורטים עם הנחיות ברורות
- כללי זהירות הרלוונטיים לסוג המשימה המשפטית"""


def generate_skill_document(skill_data: dict) -> str:
    """Generate complete skill document using Claude API with streaming and prompt caching."""
    client = anthropic.Anthropic()

    triggers_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(skill_data["triggers"]))
    required_str = "\n".join(f"- {inp}" for inp in skill_data["required_inputs"])
    optional_str = "\n".join(f"- {inp}" for inp in skill_data.get("optional_inputs", []))
    quality_str = "\n".join(f"- {q}" for q in skill_data["quality_checks"])

    # Build activation prompt input fields block
    activation_fields = "\n".join(
        f"[{inp}]: [יש למלא]" for inp in skill_data["required_inputs"]
    )
    if skill_data.get("optional_inputs"):
        activation_fields += "\n" + "\n".join(
            f"[{inp}]: [יש למלא אם רלוונטי]" for inp in skill_data["optional_inputs"]
        )

    user_prompt = f"""צור מסמך skill מלא ומקצועי ל-LizziAI עבור:

**שם:** {skill_data['name_he']} (slug: `{skill_data['slug']}`)
**מטרה:** {skill_data['goal']}

**תנאי הפעלה שסופקו:**
{triggers_str}

**קלטי חובה:**
{required_str}

**קלטים רצויים:**
{optional_str if optional_str else "(לא סופקו)"}

**פורמט פלט:**
{skill_data['output_format']}

**בדיקות איכות ספציפיות לתחום (שסופקו):**
{quality_str}

---

צור את המסמך המלא בפורמט Markdown עם המבנה הבא בדיוק:

# SKILL: {skill_data['name_he']}
**סלאג:** `{skill_data['slug']}`
**תאריך יצירה:** {datetime.now().strftime('%d/%m/%Y')}

---

## מטרה
[הסבר מפורט — מה ה-skill מייצר, למי מיועד, מהי תרומתו המעשית]

## מתי מפעילים
[רשימה ממוספרת, לפחות 3 תנאים — כלול את התנאים שסופקו + הרחב בהתאם לתחום]

## קלט חובה
[רשימה מוקצת מהנתונים שסופקו]

## קלט רצוי
[רשימה מוקצת, או "אין" אם לא סופקו]

## עקרונות עבודה מחייבים
[לפחות 10 עקרונות ממוספרים — ספציפיים ל-skill זה ולתחום המשפטי. שלב את עקרונות הספרייה בצורה ייחודית לתחום]

## שלבי ביצוע
[לפחות 10 שלבים ממוספרים ומפורטים. כל שלב: מה עושים + איך + על מה לשים לב]

## פורמט פלט
[תיאור מפורט: סעיפים חובה, סדר הצגה, אורך משוער לכל חלק, רמת פירוט נדרשת]

## כללי זהירות
[לפחות 5 כללים — אי-ודאות, מגבלות AI, מקרים שדורשים בדיקה אנושית, אזהרות לתחום]

## בדיקות איכות לפני מסירה
[לפחות 9 בדיקות. כלול את הבדיקות שסופקו + הוסף בדיקות ספציפיות ל-skill. פורמט: "[ ] תיאור הבדיקה"]

## נוסח הפעלה אחיד
```
הפעילי את skill {skill_data['name_he']}.
[תיאור המשימה] ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.
{activation_fields}
דגשים מיוחדים: [יש למלא אם קיימים]
אם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.
```

הנחיות:
- עברית מקצועית-משפטית לאורך כל המסמך
- כל סעיף — עמוק וספציפי, לא גנרי
- עקרונות ושלבים חייבים להתאים בדיוק לסוג ה-skill
- הגע לרמת פירוט benchmark "מזכר משפטי"
"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        message = stream.get_final_message()

    text_blocks = [b.text for b in message.content if b.type == "text"]
    return "\n".join(text_blocks)


def validate_skill_data(data: dict) -> list[str]:
    """Validate skill data, return list of errors."""
    errors = []

    required_fields = ["name_he", "slug", "goal", "triggers", "required_inputs", "output_format", "quality_checks"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"חסר שדה חובה: '{field}'")

    if len(data.get("triggers", [])) < 3:
        errors.append(f"נדרשים לפחות 3 תנאי הפעלה (סופקו: {len(data.get('triggers', []))})")

    if len(data.get("required_inputs", [])) < 2:
        errors.append(f"נדרשים לפחות 2 קלטי חובה (סופקו: {len(data.get('required_inputs', []))})")

    if not data.get("quality_checks"):
        errors.append("נדרשת לפחות בדיקת איכות אחת")

    slug = data.get("slug", "")
    if slug and not re.match(r"^[a-z][a-z0-9_]*$", slug):
        errors.append("הסלאג חייב להכיל רק a-z, 0-9, _ ולהתחיל באות לטינית קטנה")

    return errors


def collect_list_input(prompt: str, min_items: int = 1) -> list[str]:
    """Collect multiple items interactively, one per line."""
    print(f"\n{prompt} (שורה ריקה לסיום):")
    items = []
    while True:
        item = input("  > ").strip()
        if not item:
            if len(items) >= min_items:
                break
            print(f"  נדרש לפחות {min_items} פריט/ים. המשך להזין:")
        else:
            items.append(item)
    return items


def interactive_mode():
    """Run interactive skill creation wizard."""
    print("\n" + "=" * 52)
    print("   LizziAI Skill Builder — מצב אינטראקטיבי")
    print("=" * 52 + "\n")

    skill_data: dict = {}

    # Hebrew name
    while True:
        name_he = input("שם ה-skill בעברית (לדוגמה: חוות דעת משפטית): ").strip()
        if name_he:
            skill_data["name_he"] = name_he
            break
        print("  שגיאה: נדרש שם")

    # English slug — suggest ASCII-only default
    ascii_slug = re.sub(r"[^a-zA-Z0-9\s]", "", name_he).lower().strip()
    default_slug = re.sub(r"\s+", "_", ascii_slug)[:30].strip("_") or "skill"

    while True:
        raw = input(f"סלאג באנגלית [{default_slug}]: ").strip()
        slug = raw or default_slug
        if re.match(r"^[a-z][a-z0-9_]*$", slug):
            skill_data["slug"] = slug
            break
        print("  שגיאה: הסלאג חייב להכיל רק a-z, 0-9, _ ולהתחיל באות")

    # Goal
    while True:
        print("\nתיאור המטרה (1–3 משפטים):")
        goal = input("  > ").strip()
        if goal:
            skill_data["goal"] = goal
            break
        print("  שגיאה: נדרש תיאור")

    # Trigger conditions
    skill_data["triggers"] = collect_list_input(
        "תנאי הפעלה — מתי משתמשים ב-skill? (לפחות 3)", min_items=3
    )

    # Required inputs
    skill_data["required_inputs"] = collect_list_input(
        "קלטי חובה — מה חייבים לספק? (לפחות 2)", min_items=2
    )

    # Optional inputs
    opt = input("\nהאם יש קלטים רצויים? (כן/לא) [לא]: ").strip().lower()
    if opt in ("כן", "yes", "y"):
        skill_data["optional_inputs"] = collect_list_input("קלטים רצויים", min_items=1)
    else:
        skill_data["optional_inputs"] = []

    # Output format
    while True:
        print("\nתיאור פורמט הפלט:")
        output_format = input("  > ").strip()
        if output_format:
            skill_data["output_format"] = output_format
            break
        print("  שגיאה: נדרש תיאור")

    # Quality checks
    skill_data["quality_checks"] = collect_list_input(
        "בדיקות איכות ספציפיות לתחום", min_items=1
    )

    # Validate before calling API
    errors = validate_skill_data(skill_data)
    if errors:
        print("\n⚠  שגיאות אימות:")
        for e in errors:
            print(f"  - {e}")
        print("\nאנא תקן ונסה שוב.")
        sys.exit(1)

    print(f"\n... מייצר skill '{skill_data['name_he']}' — אנא המתן ...")
    document = generate_skill_document(skill_data)

    SKILLS_DIR.mkdir(exist_ok=True)
    out_path = SKILLS_DIR / f"SKILL_{skill_data['slug']}.md"
    out_path.write_text(document, encoding="utf-8")
    print(f"\nנשמר בהצלחה: {out_path}")
    return out_path


def list_mode():
    """List all skills in the skills directory."""
    skill_files = sorted(SKILLS_DIR.glob("SKILL_*.md")) if SKILLS_DIR.exists() else []

    if not skill_files:
        print("\nאין skills בספרייה.")
        return

    print("\n" + "=" * 52)
    print("   Skills בספרייה")
    print("=" * 52)
    for skill_file in skill_files:
        slug = skill_file.stem.replace("SKILL_", "")
        content = skill_file.read_text(encoding="utf-8")
        match = re.search(r"^# SKILL: (.+)$", content, re.MULTILINE)
        name_he = match.group(1).strip() if match else "—"
        print(f"  {slug:<32} {name_he}")
    print()


def batch_mode(input_file: str) -> None:
    """Process a JSON batch file of skill definitions."""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"שגיאה: קובץ '{input_file}' לא נמצא.")
        sys.exit(1)

    try:
        skills = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"שגיאה בפרסור JSON: {e}")
        sys.exit(1)

    if not isinstance(skills, list):
        print("שגיאה: קובץ ה-JSON חייב להכיל מערך של skill objects.")
        sys.exit(1)

    print(f"\n{'='*52}")
    print(f"   עיבוד אצווה: {len(skills)} skills")
    print(f"{'='*52}\n")

    SKILLS_DIR.mkdir(exist_ok=True)
    success_count = fail_count = 0

    for i, skill_data in enumerate(skills, 1):
        name = skill_data.get("name_he", f"skill #{i}")
        slug = skill_data.get("slug", f"skill_{i}")
        print(f"[{i}/{len(skills)}] {name} ({slug}) ...", end=" ", flush=True)

        errors = validate_skill_data(skill_data)
        if errors:
            print("נכשל — שגיאות אימות:")
            for e in errors:
                print(f"          - {e}")
            fail_count += 1
            continue

        try:
            document = generate_skill_document(skill_data)
            out_path = SKILLS_DIR / f"SKILL_{slug}.md"
            out_path.write_text(document, encoding="utf-8")
            print(f"נשמר: {out_path}")
            success_count += 1
        except Exception as e:
            print(f"נכשל — {e}")
            fail_count += 1

    print(f"\nסיכום: {success_count} הצליחו, {fail_count} נכשלו.")


def print_usage() -> None:
    print("""
LizziAI Skill Builder

שימוש:
  python skill_builder.py new                   מצב אינטראקטיבי
  python skill_builder.py list                  הצגת כל ה-skills
  python skill_builder.py batch <file.json>     עיבוד אצווה מ-JSON

פורמט JSON לעיבוד אצווה:
  [
    {
      "name_he": "חוות דעת משפטית",
      "slug": "legal_opinion",
      "goal": "...",
      "triggers": ["...", "...", "..."],
      "required_inputs": ["...", "..."],
      "optional_inputs": ["..."],
      "output_format": "...",
      "quality_checks": ["...", "..."]
    }
  ]

משתנה סביבה נדרש:
  ANTHROPIC_API_KEY
""")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "new":
        interactive_mode()
    elif command == "list":
        list_mode()
    elif command == "batch":
        if len(sys.argv) < 3:
            print("שגיאה: נדרש נתיב לקובץ JSON")
            print("שימוש: python skill_builder.py batch <file.json>")
            sys.exit(1)
        batch_mode(sys.argv[2])
    else:
        print(f"פקודה לא מוכרת: '{command}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
