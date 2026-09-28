"""Gives existing teachers and subjects a sequential order value
(alphabetical, matching how they were shown before) so drag-and-drop
reordering starts from their current position."""
from django.db import migrations


def seed(apps, schema_editor):
    Teacher = apps.get_model("timetable", "Teacher")
    Subject = apps.get_model("timetable", "Subject")
    for i, t in enumerate(Teacher.objects.order_by("name"), start=1):
        Teacher.objects.filter(pk=t.pk).update(order=i)
    for i, s in enumerate(Subject.objects.order_by("name"), start=1):
        Subject.objects.filter(pk=s.pk).update(order=i)


class Migration(migrations.Migration):
    dependencies = [("timetable", "0004_alter_subject_options_alter_teacher_options_and_more")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
