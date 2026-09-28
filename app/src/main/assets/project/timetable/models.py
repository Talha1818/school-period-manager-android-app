from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=120, blank=True)
    contact_no = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "classes"

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Allocation(models.Model):
    """One cell of the timetable: class + period -> teacher + subject."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="allocations")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name="allocations")
    teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.CASCADE, related_name="allocations")
    subject = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.CASCADE, related_name="allocations")

    class Meta:
        unique_together = ("school_class", "period")

    def __str__(self):
        return f"{self.school_class} / {self.period}"
