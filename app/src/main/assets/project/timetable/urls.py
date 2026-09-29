from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("class-wise/", views.class_wise, name="class_wise"),
    path("class-wise/pdf/", views.class_wise_pdf, name="class_wise_pdf"),
    path("teacher-wise/", views.teacher_wise, name="teacher_wise"),
    path("teacher-wise/pdf/", views.teacher_wise_pdf, name="teacher_wise_pdf"),
    path("add/<str:kind>/", views.add_item, name="add_item"),
    path("edit/<str:kind>/<int:pk>/", views.edit_item, name="edit_item"),
    path("delete/<str:kind>/<int:pk>/", views.delete_item, name="delete_item"),
    path("teacher/<int:pk>/toggle/", views.toggle_teacher, name="toggle_teacher"),
    path("reorder/<str:kind>/", views.reorder_items, name="reorder_items"),
    path("allocation/save/", views.save_allocation, name="save_allocation"),
]
