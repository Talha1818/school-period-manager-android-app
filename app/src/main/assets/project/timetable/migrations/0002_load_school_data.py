"""Loads teachers, periods and subjects taken from
BEST_TIME_TABLE_BY_TARIQ_JAVEED_2025_TO_2026.xlsx (GHS Jalhan).
Safe to re-run: existing names are never duplicated."""
from django.db import migrations

# (name, designation code as written in the Excel sheet)
TEACHERS = [
    ("Tariq Javeed", "SST"),
    ("Zia Ullah", "EST"),
    ("Mubashir Khalid", "STI"),
    ("Ismat Ullah", "EST"),
    ("Javed Younis", "EST"),
    ("M. Umer Farooq", "EST"),
    ("Zulifqar Ali", "EST"),
    ("Babar Shahzad", "EST"),
    ("Nasir Mehmood", "PST"),
    ("Usama", "STI"),
    ("Abdul Malik", "EST"),
    ("Khalid Hassan", "EST"),
    ("M. Arif", "EST"),
    ("M. Ramzan", "EST"),
    ("Talib H.", "EST"),
    ("Ulfet P.", "EST"),
    ("Aisaha M.", "PST"),
    ("M. Sohail", "PST"),
    ("Mubashir (PST)", "PST"),
]

PERIODS = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]

SUBJECTS = [
    "The Quran", "Tarjuma Quran", "Islamyat", "Urdu", "English", "Math",
    "General Science", "Physics", "Chemistry", "Biology", "Computer",
    "Social Studies", "Pak Studies",
]


def load(apps, schema_editor):
    Teacher = apps.get_model("timetable", "Teacher")
    Period = apps.get_model("timetable", "Period")
    Subject = apps.get_model("timetable", "Subject")

    for name, desig in TEACHERS:
        Teacher.objects.get_or_create(name=name, defaults={"designation": desig, "is_active": True})

    for i, name in enumerate(PERIODS, start=1):
        Period.objects.get_or_create(name=name, defaults={"order": i})

    for name in SUBJECTS:
        Subject.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [("timetable", "0001_initial")]
    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
