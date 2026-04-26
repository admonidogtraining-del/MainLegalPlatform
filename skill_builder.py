#!/usr/bin/env python3
"""skill_builder.py — LizzyAI Skill Builder CLI"""

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
SYSTEM_PROMPT = """אתה מומחה לבניית skills ל-LizzyAI — עורכת דין AI המשמשת משרדי עורכי דין בישראל.

## עקרונות ספריית ה-Skills (14 עקרונות מחייבים — חייבים לבוא לידי ביטוי בכל skill)
1. כל skill מתבצע ברמת העבודה הטובה, המלאה והמדויקת ביותר שניתן להפיק מן החומר שנמסר.
2. אין גרסה קצרה וגרסה מורחבת — ברירת המחדל תמיד ביצוע מלא ומיטבי.
3. אם ניתן להתקדם מקצועית על בסיס מידע חלקי — להתקדם, תוך ציון ברור של מגבלות ופערים.
4. אם חסר מידע מהותי שאי אפשר בלעדיו — לשאול שאלה קצרה, ממוקדת והכרחית בלבד.
5. אין להמציא עובדות, מקורות, אסמכתאות, מסמכים, הנחות או מסקנות שלא נתמכים בחומר שנמסר.
6. כאשר המשימה משפטית, להפיק תוצר עבודה משרדי, פרקטי ומכוון-החלטה — לא תשובה כללית, אקדמית או מופשטת.
7. לשמור על אחידות פנימית בין כל ה-skills בספרייה וליישם כל אחד לפי מבנה ולכללים שיוגדרו בו.
8. אם משתמש מפעיל skill מסוים — לפעול לפיו כברירת מחדל בלי לבקש לנסח מחדש את המתודולוגיה.
9. אם משימה דורשת שילוב בין כמה skills — ליישמם באופן משולב, עקבי וברור.
10. לראות בכל skill שנמסר כספריית העבודה הפעילה של המשתמש.
11. לשמור על אותו היגיון עבודה, רמת איכות ומבנה תוצרים בין משתמשים שונים.
12. אם משימה נשענת על מסמכים — לעבוד קודם כל על בסיסם, ולאחר מכן על ההנחיות הכלליות.
13. אם קיים פער בין הנחיית skill לבין מידע חסר — לציין, להמשיך ככל שניתן, ולשאול רק אם הכרחי.
14. מטרת-על: לאפשר לכל משתמש לקבל אותה סביבת עבודה מקצועית עם אותם skills ואותה מתודולוגיה.

## מבנה מסמך Skill — הסעיפים בדיוק (לפי תבנית הספרייה הקיימת)
כל skill חייב לכלול את הסעיפים הבאים בסדר הזה בדיוק:

1. **מטרה** — תיאור מפורט של מה ה-skill מייצר, למי, ומהי תרומתו המעשית
2. **מתי מפעילים** — רשימת נקודות (•), לפחות 5 תנאים ממוקדים
3. **קלט חובה** — רשימת נקודות (•) — מה חייב להיות זמין כדי לבצע את ה-skill
4. **קלט רצוי** — רשימת נקודות (•) — מה מועיל אך לא הכרחי
5. **עקרונות עבודה מחייבים** — רשימה ממוספרת, לפחות 10 עקרונות ספציפיים ל-skill זה (לא גנריים)
6. **שלבי ביצוע** — רשימה ממוספרת, לפחות 10 שלבים פרקטיים ומפורטים
7. **פורמט פלט** — רשימת נקודות (•) — הסעיפים שחייבים להופיע בפלט, בסדר
8. **כללי זהירות / אי-ודאות / מידע חסר** — רשימה ממוספרת, לפחות 5 כללים הנוגעים לאי-ודאות, מגבלות ומידע חסר
9. **בדיקות איכות לפני מסירה** — רשימת נקודות (•) עם שאלות בינאריות, לפחות 9 בדיקות

## נוסח הפעלה אחיד — תבנית מחייבת
הסעיף האחרון (לאחר שורת הפרדה) הוא נוסח ההפעלה. הפורמט המחייב:

```
הפעילי את skill [שם ה-skill בעברית].
[תיאור קצר וספציפי של המשימה — שורה אחת] ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.
[שדה קלט חובה 1]: [יש למלא]
[שדה קלט חובה 2]: [יש למלא]
[שדה קלט רצוי]: [יש למלא אם קיים/רלוונטי]
דגשים מיוחדים: [יש למלא אם קיימים]
אם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.
```

## ה-Benchmark: מזכר משפטי
מזכר משפטי הוא הסטנדרט של הספרייה: 9 עקרונות עבודה מחייבים (חלקם עם תת-נקודות), 10 שלבי ביצוע, פורמט פלט עם 5 סעיפי חובה + הנחיות מבנה לפי סוגים, 6 כללי זהירות, 9 בדיקות איכות. כל skill חדש חייב להגיע לאותה רמת פירוט.

## שפה ואיכות
- כל התוכן בעברית מקצועית-משפטית
- עקרונות ושלבים ספציפיים ל-skill, לא גנריים
- שלבים פרקטיים עם הנחיות ברורות מה עושים + איך + על מה לשים לב
- כללי זהירות הרלוונטיים לתחום המשפטי הספציפי של ה-skill"""


def generate_skill_document(skill_data: dict) -> str:
    """Generate complete skill document using Claude API with streaming and prompt caching."""
    client = anthropic.Anthropic()

    triggers_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(skill_data["triggers"]))
    required_str = "\n".join(f"- {inp}" for inp in skill_data["required_inputs"])
    optional_str = "\n".join(f"- {inp}" for inp in skill_data.get("optional_inputs", []))
    quality_str = "\n".join(f"- {q}" for q in skill_data["quality_checks"])

    # Build activation prompt input fields block (matching real format)
    activation_fields = "\n".join(
        f"{inp}: [יש למלא]" for inp in skill_data["required_inputs"]
    )
    if skill_data.get("optional_inputs"):
        activation_fields += "\n" + "\n".join(
            f"{inp}: [יש למלא אם קיים/רלוונטי]" for inp in skill_data["optional_inputs"]
        )

    user_prompt = f"""צור מסמך skill מלא ומקצועי ל-LizzyAI עבור:

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

צור את המסמך המלא בפורמט Markdown עם המבנה הבא בדיוק. שים לב: הסעיפים השתמש בנקודות (•) עבור רשימות, ובמספור (1. 2. 3.) עבור עקרונות ושלבים.

# SKILL: {skill_data['name_he']}
**סלאג:** `{skill_data['slug']}`
**תאריך יצירה:** {datetime.now().strftime('%d/%m/%Y')}

---

## מטרה
[פסקה אחת עד שתיים — מה ה-skill מייצר, למי מיועד, באילו הקשרים משרדיים הוא שימושי, מהי תרומתו המעשית]

## מתי מפעילים
• [תנאי הפעלה שסופקו + הרחב לפחות ל-5 תנאים ממוקדים ספציפיים ל-skill]

## קלט חובה
• [קלטי החובה שסופקו — כל פריט בשורה נפרדת עם •]

## קלט רצוי
• [קלטים רצויים שסופקו — או "אין" אם לא סופקו]

## עקרונות עבודה מחייבים
1. [לפחות 10 עקרונות ממוספרים — ספציפיים לחלוטין ל-skill זה ולתחום המשפטי שלו. אין עקרונות גנריים. כל עיקרון מציין מה עושים ולמה]

## שלבי ביצוע
1. [לפחות 10 שלבים ממוספרים ופרקטיים — כל שלב מציין מה עושים, איך עושים, ועל מה לשים לב]

## פורמט פלט
• [כותרת התוצר]
• [כל סעיף חובה שחייב להופיע בפלט, לפי הסדר]
• [אם יש פורמט מיוחד כגון טבלת סיכונים — פרט את עמודות הטבלה]

## כללי זהירות / אי-ודאות / מידע חסר
1. [לפחות 5 כללים ממוספרים — כיצד לטפל בחוסרי מידע, בסיכוני ניסוח, ובמצבי אי-ודאות ספציפיים ל-skill זה]

## בדיקות איכות לפני מסירה
• האם [בדיקה 1 בניסוח שאלה ישירה — כלול את הבדיקות שסופקו + הוסף ספציפיות ל-skill]
• האם [בדיקה 2]
[לפחות 9 בדיקות. ניסוח: "האם ..." לכל בדיקה]


למשתמש – נוסח הפעלה אחיד:
הפעילי את skill {skill_data['name_he']}.
[נסח תיאור קצר וספציפי של המשימה — שורה אחת, פועל ספציפי כגון "הכיני מזכר", "בדקי את ההסכם", "נסחי מייל"] ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.
{activation_fields}
דגשים מיוחדים: [יש למלא אם קיימים]
אם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.

---

הנחיות לדרגת פירוט:
- עברית מקצועית-משפטית לאורך כל המסמך
- כל עיקרון ושלב — ספציפי לחלוטין ל-skill זה, לא גנרי
- הגע לרמת הפירוט של מזכר משפטי (benchmark): 9+ עקרונות, 10+ שלבים, 5+ סעיפי פלט, 6+ כללי זהירות, 9+ בדיקות
- נוסח ההפעלה: שורה שנייה היא תיאור ספציפי ופועל מדויק (לא "[תיאור המשימה]")
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
    print("   LizzyAI Skill Builder — מצב אינטראקטיבי")
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
LizzyAI Skill Builder

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
