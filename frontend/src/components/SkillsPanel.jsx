import { useState, useEffect } from "react";
import { getSkills } from "../services/api";

// The firm's 7 built-in skills — shown when no generated .md files exist yet
const DEFAULT_SKILLS = [
  {
    name_he: "מזכר משפטי",
    slug: "legal_memo",
    activation_prompt:
      "הפעילי את skill מזכר משפטי.\nהכיני מזכר משפטי בעברית ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.\nהשאלה המשפטית: [יש למלא]\nהעובדות הידועות: [יש למלא]\nמטרת המזכר: [יש למלא]\nהצד המיוצג / ההקשר: [יש למלא אם רלוונטי]\nהמסמכים הרלוונטיים: [יש למלא אם קיימים]\nדגשים מיוחדים: [יש למלא אם קיימים]\nאם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.",
  },
  {
    name_he: "בדיקת NDA",
    slug: "nda_review",
    activation_prompt:
      "הפעילי את skill בדיקת NDA.\nבדקי את הסכם הסודיות ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.\nההסכם: [יש למלא]\nהצד המיוצג: [יש למלא]\nמטרת הבדיקה: [יש למלא]\nדגשים מסחריים או משפטיים: [יש למלא אם קיימים]\nאם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.",
  },
  {
    name_he: "בדיקת חוזה",
    slug: "contract_review",
    activation_prompt:
      "הפעילי את skill בדיקת חוזה.\nבדקי את ההסכם ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.\nההסכם: [יש למלא]\nהצד המיוצג: [יש למלא]\nמטרת הבדיקה: [יש למלא]\nסוג העסקה / הרקע המסחרי: [יש למלא אם קיים]\nדגשים מסחריים או משפטיים: [יש למלא אם קיימים]\nאם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.",
  },
  {
    name_he: "יצירת פרומפט לנבו AI",
    slug: "nevo_prompt",
    activation_prompt:
      "הפעילי את skill יצירת פרומפט לנבו AI.\nנסחי פרומפט למחקר משפטי ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.\nהשאלה המשפטית: [יש למלא]\nתחום הדין: [יש למלא]\nמטרת המחקר: [יש למלא]\nהעובדות הידועות: [יש למלא אם קיימות]\nדגשים מיוחדים: [יש למלא אם קיימים]\nאם חסר מידע מהותי לדיוק המחקר - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.",
  },
  {
    name_he: "כתיבת מייל ללקוח",
    slug: "client_email",
    activation_prompt:
      "הפעילי את skill כתיבת מייל ללקוח.\nנסחי מייל ללקוח ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.\nמטרת המייל: [יש למלא]\nהנמען: [יש למלא]\nהרקע העובדתי: [יש למלא]\nהמסר שצריך להיאמר: [יש למלא]\nשפת המייל: [יש למלא אם רלוונטי]\nדגשים מיוחדים: [יש למלא אם קיימים]\nאם חסר מידע מהותי לניסוח מדויק - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.",
  },
  {
    name_he: "סקירה מקיפה של הדין",
    slug: "law_review",
    activation_prompt:
      "הפעילי את skill סקירה מקיפה של הדין.\nהכיני סקירה משפטית ברמת העבודה הטובה והמלאה ביותר שניתן להפיק מן החומר שנמסר.\nהנושא או הסוגייה: [יש למלא]\nתחום הדין: [יש למלא]\nמטרת הסקירה: [יש למלא]\nרמת העומק המבוקשת: [יש למלא]\nתשתית עובדתית: [יש למלא אם קיימת]\nדגשים מיוחדים: [יש למלא אם קיימים]\nאם חסר מידע מהותי להכרעה - צייני זאת במפורש, המשיכי ככל שניתן באופן מקצועי, ושאלי רק אם אי אפשר להתקדם בלעדיו.",
  },
  {
    name_he: "נרמול שמות קבצים לתיק חברה",
    slug: "file_normalization",
    activation_prompt:
      "הפעילי את skill נרמול שמות קבצים לתיק חברה.\nאם אני מעלה קבצים בשיחה זו, יש לעבד את הקבצים שהועלו וזמינים כאן ולהפיק עבורם את כלל התוצרים שסוכמו, בלי לבקש ממני פעולות נוספות, אלא אם חסר מידע מהותי שאי אפשר להתקדם בלעדיו.\nאם אני מציין שזו אצווה נוספת או המשך של אותו פרויקט, יש לראות בשיחה זו המשך ישיר של אותו פרויקט ולהחיל אוטומטית את כל אותם כללים.\nאם כבר יש לי קובץ Rename_Files.bat קבוע ועובד, אין לשנות את המנוע שלו, אין להחזיר קובץ חדש במנוע אחר ואין להחליף ארכיטקטורה.\nברירת המחדל: טבלה עם ארבע עמודות (שם קובץ מקורי | סוג מסמך | תאריך YYYY-MM-DD | שם קובץ מנורמל מוצע) + הסבר קצר + קובץ Rename_Files.bat מלא מוכן להעתקה-הדבקה.",
  },
];

function CopyIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  );
}

function SkillCard({ skill }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(skill.activation_prompt);
    } catch {
      // fallback for non-secure contexts
      const el = document.createElement("textarea");
      el.value = skill.activation_prompt;
      el.style.position = "fixed";
      el.style.opacity = "0";
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="bg-slate-800 rounded-xl p-4 border-r-4 border-teal-500 flex flex-col gap-3">
      {/* Name + slug */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-white font-semibold text-base leading-snug">{skill.name_he}</h3>
        <span className="flex-shrink-0 text-xs bg-slate-700 text-slate-400 px-2 py-0.5 rounded font-mono leading-5">
          {skill.slug}
        </span>
      </div>

      {/* Prompt preview — first line only */}
      {skill.activation_prompt && (
        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
          {skill.activation_prompt}
        </p>
      )}

      {/* Copy button */}
      <button
        onClick={handleCopy}
        className={`mt-auto flex items-center justify-center gap-1.5 w-full py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
          copied
            ? "bg-teal-900 text-teal-300"
            : "bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white"
        }`}
      >
        {copied ? <CheckIcon /> : <CopyIcon />}
        {copied ? "הועתק!" : "העתק נוסח הפעלה"}
      </button>
    </div>
  );
}

export default function SkillsPanel() {
  const [open, setOpen] = useState(true);
  const [skills, setSkills] = useState(DEFAULT_SKILLS);

  useEffect(() => {
    getSkills()
      .then((res) => {
        if (res.data?.length) setSkills(res.data);
      })
      .catch(() => {
        // backend unavailable — defaults stay in place
      });
  }, []);

  return (
    <section className="px-6 py-4 max-w-7xl mx-auto w-full">
      {/* Collapsible header */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between mb-4 group"
      >
        <div className="flex items-center gap-2">
          {/* lightning bolt icon */}
          <svg
            className="w-4 h-4 text-teal-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <h2 className="text-sm font-semibold text-white tracking-wide">LizziAI Skills</h2>
          <span className="text-xs bg-slate-700 text-slate-400 px-2 py-0.5 rounded-full">
            {skills.length}
          </span>
        </div>
        {/* chevron */}
        <svg
          className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${
            open ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {skills.map((skill) => (
            <SkillCard key={skill.slug} skill={skill} />
          ))}
        </div>
      )}
    </section>
  );
}
