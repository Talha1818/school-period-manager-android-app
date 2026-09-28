"""Loads the actual class-wise period assignments from
BEST_TIME_TABLE_BY_TARIQ_JAVEED_2025_TO_2026.xlsx (CLASS WISE sheet).
Only fills a class/period slot if it is still empty, so it never
overwrites anything already set through the website."""
from django.db import migrations

TEACHER_MAP = {
    "M.UMER EST": "M. Umer Farooq",
    "MUBASHIR STI": "Mubashir Khalid",
    "ISMAT U.EST": "Ismat Ullah",
    "NASIR MEH.PST": "Nasir Mehmood",
    "M.ARIF": "M. Arif",
    "USAMA STI": "Usama",
    "ZIA ULLAH EST": "Zia Ullah",
    "ZULIFQAR A.EST": "Zulifqar Ali",
    "KHALID.H.EST": "Khalid Hassan",
    "A.MALIK EST": "Abdul Malik",
    "JAVED YOU. EST": "Javed Younis",
    "BABAR SHA.EST": "Babar Shahzad",
}

SUBJECT_MAP = {
    "THE QURAN": "The Quran",
    "TARJUMA QUR": "Tarjuma Quran",
    "ISLAMYAT": "Islamyat",
    "URDU": "Urdu",
    "ENGLISH": "English",
    "MATH": "Math",
    "G.SCIENCE": "General Science",
    "PHYSICS": "Physics",
    "CHEMISTRY": "Chemistry",
    "BIO": "Biology",
    "COMPUTER": "Computer",
    "SOCIAL STUDIES": "Social Studies",
    "PAK STUDIES": "Pak Studies",
}

# class name -> {period_number: (subject_raw, teacher_raw)}
DATA = {
    "10th": {1: ("THE QURAN", "M.UMER EST"), 2: ("COMPUTER", "MUBASHIR STI"), 3: ("MATH", "ISMAT U.EST"),
             4: ("ENGLISH", "ISMAT U.EST"), 5: ("PHYSICS", "NASIR MEH.PST"), 6: ("CHEMISTRY", "M.ARIF"),
             7: ("PAK STUDIES", "USAMA STI"), 8: ("URDU", "USAMA STI")},
    "9th": {1: ("ENGLISH", "ZIA ULLAH EST"), 2: ("URDU", "USAMA STI"), 3: ("CHEMISTRY", "ZIA ULLAH EST"),
            4: ("COMPUTER", "MUBASHIR STI"), 5: ("PHYSICS", "ZIA ULLAH EST"), 6: ("MATH", "ZIA ULLAH EST"),
            7: ("ISLAMYAT", "M.UMER EST"), 8: ("THE QURAN", "M.UMER EST")},
    "9th B": {4: ("BIO", "M.ARIF")},
    "8th A": {1: ("ENGLISH", "ISMAT U.EST"), 2: ("G.SCIENCE", "M.ARIF"), 3: ("COMPUTER", "MUBASHIR STI"),
              4: ("THE QURAN", "M.UMER EST"), 5: ("URDU", "ZULIFQAR A.EST"), 6: ("MATH", "ISMAT U.EST"),
              7: ("SOCIAL STUDIES", "KHALID.H.EST"), 8: ("ISLAMYAT", "A.MALIK EST")},
    "7th A": {1: ("MATH", "KHALID.H.EST"), 2: ("ENGLISH", "JAVED YOU. EST"), 3: ("SOCIAL STUDIES", "ZULIFQAR A.EST"),
              4: ("URDU", "BABAR SHA.EST"), 5: ("ISLAMYAT", "JAVED YOU. EST"), 6: ("G.SCIENCE", "ZULIFQAR A.EST"),
              7: ("TARJUMA QUR", "A.MALIK EST"), 8: ("COMPUTER", "JAVED YOU. EST")},
    "6th A": {1: ("ENGLISH", "A.MALIK EST"), 2: ("URDU", "BABAR SHA.EST"), 3: ("COMPUTER", "A.MALIK EST"),
              4: ("THE QURAN", "JAVED YOU. EST"), 5: ("MATH", "KHALID.H.EST"), 6: ("SOCIAL STUDIES", "KHALID.H.EST"),
              7: ("G.SCIENCE", "ZULIFQAR A.EST"), 8: ("ISLAMYAT", "BABAR SHA.EST")},
}


def load(apps, schema_editor):
    SchoolClass = apps.get_model("timetable", "SchoolClass")
    Period = apps.get_model("timetable", "Period")
    Teacher = apps.get_model("timetable", "Teacher")
    Subject = apps.get_model("timetable", "Subject")
    Allocation = apps.get_model("timetable", "Allocation")

    for class_name, periods in DATA.items():
        try:
            school_class = SchoolClass.objects.get(name__iexact=class_name)
        except SchoolClass.DoesNotExist:
            continue
        for period_no, (subject_raw, teacher_raw) in periods.items():
            try:
                period = Period.objects.get(name__iexact=f"P{period_no}")
            except Period.DoesNotExist:
                continue
            if Allocation.objects.filter(school_class=school_class, period=period).exists():
                continue  # don't overwrite anything already set via the site

            teacher = Teacher.objects.filter(name__iexact=TEACHER_MAP.get(teacher_raw, teacher_raw)).first()
            subject = Subject.objects.filter(name__iexact=SUBJECT_MAP.get(subject_raw, subject_raw)).first()
            if not teacher and not subject:
                continue
            Allocation.objects.create(school_class=school_class, period=period, teacher=teacher, subject=subject)


class Migration(migrations.Migration):
    dependencies = [("timetable", "0005_seed_teacher_subject_order")]
    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
