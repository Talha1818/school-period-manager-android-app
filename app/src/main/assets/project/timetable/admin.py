from django.contrib import admin
from .models import Teacher, SchoolClass, Period, Subject, Allocation

admin.site.register(Teacher)
admin.site.register(SchoolClass)
admin.site.register(Period)
admin.site.register(Subject)
admin.site.register(Allocation)
