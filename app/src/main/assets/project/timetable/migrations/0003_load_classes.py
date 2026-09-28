"""Loads the classes listed in the Excel timetable (CLASS WISE sheet).
Safe to re-run: classes that already exist (any letter case) are skipped."""
from django.db import migrations
from django.db.models import Max

CLASSES = [
    "10th", "10th B", "9th", "9th B",
    "8th A", "8th B", "7th A", "7th B", "6th A", "6th B",
]


def load(apps, schema_editor):
    SchoolClass = apps.get_model("timetable", "SchoolClass")
    order = SchoolClass.objects.aggregate(m=Max("order"))["m"] or 0
    for name in CLASSES:
        if SchoolClass.objects.filter(name__iexact=name).exists():
            continue
        order += 1
        SchoolClass.objects.create(name=name, order=order)


class Migration(migrations.Migration):
    dependencies = [("timetable", "0002_load_school_data")]
    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
