import httpx

BASE = "http://localhost:8000/api/documents"

docs = [
    {
        "type": "ruling",
        "title": 'ע"א 5123/15 פלוני נ\u2019 מדינת ישראל',
        "summary": "הכרה בזכות העובד לפיצויי בגין פיטורים שלא כדין מחברה פרטית",
        "case_number": 'ע"א 5123/15',
        "court": "בית המשפט העליון",
        "judge": "כב' השופטת א. חיות",
        "law_area": "עבודה",
        "urgency": "high",
        "pub_date": "15/12/2024",
        "source_url": "https://supreme.court.gov.il",
        "scraped_from": "manual",
    },
    {
        "type": "ruling",
        "title": 'ת"א 34567/23 כהן נ\u2019 לוי',
        "summary": "חיוב בפיצוי בגין הפרת חוזה שכירות דירה על ידי המשכיר",
        "case_number": 'ת"א 34567/23',
        "court": "בית משפט מחוזי",
        "judge": "כב' השופט ד. מינץ",
        "law_area": "מקרקעין",
        "urgency": "medium",
        "pub_date": "20/01/2025",
        "scraped_from": "manual",
    },
    {
        "type": "ruling",
        "title": 'ע"פ 8910/24 מדינת ישראל נ\u2019 אלמוני',
        "summary": "הרשעה בעבירות הונאה – פסק דין תקדימי בנושא הונאת השקעות",
        "case_number": 'ע"פ 8910/24',
        "court": "בית משפט מחוזי",
        "judge": "כב' השופט י. עמית",
        "law_area": "פלילי",
        "urgency": "high",
        "pub_date": "05/02/2025",
        "scraped_from": "manual",
    },
    {
        "type": "ruling",
        "title": 'ת"צ 12345/24 ישראלי נ\u2019 חברת ביטוח הראל',
        "summary": "אישור תובענה ייצוגית בגין גביית יתר בפוליסות ביטוח חיים",
        "case_number": 'ת"צ 12345/24',
        "court": "בית משפט שלום",
        "judge": "כב' השופטת מ. רובינשטיין",
        "law_area": "חוזים",
        "urgency": "medium",
        "pub_date": "10/03/2025",
        "scraped_from": "manual",
    },
    {
        "type": "bill",
        "title": 'הצעת חוק הגנת הפרטיות (תיקון מספר 14) התשפ"ה-2025',
        "summary": "הצעת חוק ממשלתית – עדכון הוראות הגנת מידע אישי בעידן הבינה המלאכותית",
        "case_number": "פ/1234",
        "court": "כנסת ישראל",
        "law_area": "טכנולוגיה,פרטיות",
        "urgency": "high",
        "pub_date": "01/01/2025",
        "scraped_from": "manual",
    },
    {
        "type": "legislation",
        "title": 'חוק שכר מינימום (תיקון) התשפ"ד-2024',
        "summary": "העלאת שכר המינימום ל-6,000 שקלים החל מינואר 2025",
        "case_number": 'ס"ח 3120',
        "court": "כנסת ישראל",
        "law_area": "עבודה",
        "urgency": "medium",
        "pub_date": "30/12/2024",
        "scraped_from": "manual",
    },
    {
        "type": "legislation",
        "title": 'חוק התכנון והבנייה (תיקון מספר 80) התשפ"ה-2025',
        "summary": "רפורמה בדיני התכנון – הפשטת הליכי הרישוי לבנייה למגורים",
        "case_number": 'ס"ח 3145',
        "court": "כנסת ישראל",
        "law_area": "מקרקעין,תכנון",
        "urgency": "low",
        "pub_date": "15/02/2025",
        "scraped_from": "manual",
    },
]

for d in docs:
    r = httpx.post(BASE, json=d)
    if r.status_code == 201:
        print(f"  ✓ {d['title'][:55]}")
    else:
        print(f"  ✗ {r.status_code} {r.text[:80]}")
