import io
import json
from datetime import date

from django.contrib import messages
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Allocation, Period, SchoolClass, Subject, Teacher

MODELS = {
    "teacher": Teacher,
    "class": SchoolClass,
    "period": Period,
    "subject": Subject,
}


def dashboard(request):
    context = {
        "teachers": Teacher.objects.all(),
        "classes": SchoolClass.objects.all(),
        "periods": Period.objects.all(),
        "subjects": Subject.objects.all(),
    }
    return render(request, "dashboard.html", context)


@require_POST
def add_item(request, kind):
    model = MODELS.get(kind)
    if not model:
        return redirect("dashboard")

    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Name is required.")
        return redirect(request.POST.get("next") or "dashboard")

    if kind == "teacher":
        Teacher.objects.create(
            name=name,
            designation=request.POST.get("designation", "").strip(),
            contact_no=request.POST.get("contact_no", "").strip(),
            is_active=request.POST.get("is_active") == "on",
        )
    elif model.objects.filter(name__iexact=name).exists():
        messages.error(request, f'"{name}" already exists.')
        return redirect(request.POST.get("next") or "dashboard")
    elif kind in ("class", "period"):
        last = model.objects.aggregate(m=Max("order"))["m"] or 0
        model.objects.create(name=name, order=last + 1)
    else:
        model.objects.create(name=name)

    messages.success(request, f'{kind.title()} "{name}" added successfully.')
    return redirect(request.POST.get("next") or "dashboard")


@require_POST
def delete_item(request, kind, pk):
    model = MODELS.get(kind)
    if model:
        obj = get_object_or_404(model, pk=pk)
        name = str(obj)
        obj.delete()
        messages.success(request, f'{kind.title()} "{name}" deleted.')
    return redirect(request.POST.get("next") or "dashboard")


@require_POST
def edit_item(request, kind, pk):
    model = MODELS.get(kind)
    nxt = request.POST.get("next") or "dashboard"
    if not model:
        return redirect("dashboard")
    obj = get_object_or_404(model, pk=pk)
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Name is required.")
        return redirect(nxt)
    if kind != "teacher" and model.objects.filter(name__iexact=name).exclude(pk=pk).exists():
        messages.error(request, f'"{name}" already exists.')
        return redirect(nxt)

    obj.name = name
    if kind == "teacher":
        obj.designation = request.POST.get("designation", "").strip()
        obj.contact_no = request.POST.get("contact_no", "").strip()
        obj.is_active = request.POST.get("is_active") == "on"
    obj.save()
    messages.success(request, f'{kind.title()} "{name}" updated.')
    return redirect(nxt)


@require_POST
def toggle_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.is_active = not teacher.is_active
    teacher.save(update_fields=["is_active"])
    return redirect(request.POST.get("next") or "dashboard")


def class_wise(request):
    periods = list(Period.objects.all())
    teachers = list(Teacher.objects.all())
    subjects = list(Subject.objects.all())
    allocs = {(a.school_class_id, a.period_id): a for a in Allocation.objects.all()}

    rows = []
    for c in SchoolClass.objects.all():
        cells = []
        for p in periods:
            a = allocs.get((c.id, p.id))
            cells.append({
                "period": p,
                "teacher_id": a.teacher_id if a else None,
                "subject_id": a.subject_id if a else None,
            })
        rows.append({"cls": c, "cells": cells})

    context = {
        "periods": periods,
        "rows": rows,
        "teachers": teachers,
        "subjects": subjects,
    }
    return render(request, "class_wise.html", context)


def teacher_wise(request):
    periods = list(Period.objects.all())
    allocs = Allocation.objects.select_related("school_class", "subject").filter(teacher__isnull=False)
    lookup = {(a.teacher_id, a.period_id): a for a in allocs}

    rows = []
    for t in Teacher.objects.all():
        cells, total = [], 0
        for p in periods:
            a = lookup.get((t.id, p.id))
            if a:
                total += 1
            cells.append(a)
        rows.append({"teacher": t, "cells": cells, "total": total})

    return render(request, "teacher_wise.html", {"periods": periods, "rows": rows})


@require_POST
def reorder_items(request, kind):
    model = MODELS.get(kind)
    if not model or not hasattr(model, "order"):
        return JsonResponse({"ok": False, "message": "Not reorderable."}, status=400)
    try:
        data = json.loads(request.body)
        order = [int(x) for x in data.get("order", [])]
    except (ValueError, TypeError):
        return JsonResponse({"ok": False, "message": "Invalid data."}, status=400)

    for i, pk in enumerate(order, start=1):
        model.objects.filter(pk=pk).update(order=i)
    return JsonResponse({"ok": True})


@require_POST
def save_allocation(request):
    try:
        data = json.loads(request.body)
        class_id = int(data["class_id"])
        period_id = int(data["period_id"])
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"ok": False, "message": "Invalid data."}, status=400)

    teacher_id = int(data["teacher_id"]) if data.get("teacher_id") else None
    subject_id = int(data["subject_id"]) if data.get("subject_id") else None

    # A teacher cannot teach two classes in the same period.
    if teacher_id:
        clash = (
            Allocation.objects.filter(period_id=period_id, teacher_id=teacher_id)
            .exclude(school_class_id=class_id)
            .select_related("school_class", "teacher", "period")
            .first()
        )
        if clash:
            return JsonResponse({
                "ok": False,
                "message": f"{clash.teacher.name} is already assigned to class "
                           f"{clash.school_class.name} in {clash.period.name}.",
            }, status=409)

    if not teacher_id and not subject_id:
        Allocation.objects.filter(school_class_id=class_id, period_id=period_id).delete()
    else:
        Allocation.objects.update_or_create(
            school_class_id=class_id,
            period_id=period_id,
            defaults={"teacher_id": teacher_id, "subject_id": subject_id},
        )
    return JsonResponse({"ok": True, "message": "Saved"})


def teacher_wise_pdf(request):
    """Download the Teacher Wise table as a landscape A4 PDF."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    periods = list(Period.objects.all())
    allocs = Allocation.objects.select_related("school_class", "subject").filter(teacher__isnull=False)
    lookup = {(a.teacher_id, a.period_id): a for a in allocs}

    cell = ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5, leading=9, alignment=1)
    head = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=8, leading=10, alignment=1, textColor=colors.white)
    name_st = ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=8, leading=10)

    data = [[Paragraph("Teacher Name", head)] + [Paragraph(p.name, head) for p in periods] + [Paragraph("Total", head)]]
    for t in Teacher.objects.all():
        row, total = [], 0
        label = f"<b>{t.name}</b>" + (f"<br/><font size=6.5 color='#64748b'>{t.designation}</font>" if t.designation else "")
        row.append(Paragraph(label, name_st))
        for p in periods:
            a = lookup.get((t.id, p.id))
            if a:
                total += 1
                sub = a.subject.name if a.subject else "-"
                row.append(Paragraph(f"<b>{a.school_class.name}</b><br/>{sub}", cell))
            else:
                row.append(Paragraph("-", cell))
        row.append(Paragraph(f"<b>{total}</b>", cell))
        data.append(row)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=10 * mm, rightMargin=10 * mm,
                            topMargin=12 * mm, bottomMargin=10 * mm, title="Teacher Wise Distribution")
    usable = landscape(A4)[0] - 20 * mm
    name_w, total_w = 38 * mm, 14 * mm
    period_w = (usable - name_w - total_w) / max(len(periods), 1)

    table = Table(data, colWidths=[name_w] + [period_w] * len(periods) + [total_w], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7ff")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontSize=15, alignment=0, spaceAfter=2)
    subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#4f46e5"),
                              fontName="Helvetica-Bold", spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=8.5, textColor=colors.HexColor("#64748b"))
    doc.build([
        Paragraph("BEST TIME TABLE GHS JALHAN", title),
        Paragraph("DESIGNED BY TARIQ JAVEED SST", subtitle),
        Paragraph(f"Teacher Wise Period Distribution &nbsp;&bull;&nbsp; Generated on {date.today():%d %B, %Y}", sub),
        Spacer(1, 6 * mm),
        table,
    ])

    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="teacher_wise_{date.today():%Y-%m-%d}.pdf"'
    return response
