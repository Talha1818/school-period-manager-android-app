# Period Manager

A Django web app for GHS Jalhan to manage teacher period distribution:
add teachers, classes, periods and subjects, then assign them on a
Class Wise and Teacher Wise grid — with clash protection, drag-and-drop
reordering, and a PDF export.

## Features

- **Dashboard** — 4 tables (Teachers, Classes, Periods, Subjects) with
  counts, add/edit/delete for each, and a toggle for a teacher's
  Active/Inactive status.
- **Add/Edit modals**
  - Teacher: name, designation, contact no, Active
  - Class: name (e.g. 10th, 9th B)
  - Period: name (e.g. P1, P2...)
  - Subject: name
- **Drag-and-drop reordering** on all 4 dashboard tables and on the
  Class Wise rows — order is saved automatically as you drag.
- **Class Wise** — one row per class, one column per period; each cell
  has a Teacher and a Subject dropdown that saves on change. A teacher
  already assigned to a period in one class can't be assigned to a
  *different* class in that *same* period (a different period is fine)
  — the site blocks it with an on-screen error.
- **Teacher Wise** — one row per teacher, showing the class + subject
  assigned in each period, plus a Total Periods column. Read-only;
  edit from Class Wise.
- **PDF export** — Teacher Wise → Save PDF, titled "BEST TIME TABLE
  GHS JALHAN / DESIGNED BY TARIQ JAVEED SST" with the current date.
- **Current date** shown in the header on every page.
- **Django admin** at `/admin` for direct data access if ever needed.
- Seed data seeds itself: teachers, periods, subjects, classes, and
  the actual Class Wise assignments already in GHS Jalhan's timetable
  are loaded automatically the first time you run migrations.

## Tech stack

Django 4.2+, SQLite, Bootstrap 5 (CDN), vanilla JS (no build step),
ReportLab for PDF export, WhiteNoise for static files, Waitress as the
production server when packaged as a desktop app.

## Project layout

```
period_manager/
├── config/              Django project settings, URLs, WSGI
├── timetable/           The app: models, views, admin, migrations
│   └── migrations/      0001 schema, 0002-0006 seed data from the Excel
├── templates/           dashboard.html, class_wise.html, teacher_wise.html, base.html
├── static/               css/style.css, js/app.js
├── manage.py
├── run_app.py            Entry point for the packaged .exe (see below)
├── build_exe.py           Builds the .exe with PyInstaller
├── installer.iss           Inno Setup script for a Windows installer
├── requirements.txt
└── requirements-build.txt
```

## Running locally (development)

1. `python -m venv venv && venv\Scripts\activate`
   (Linux/Mac: `source venv/bin/activate`)
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
   (creates `db.sqlite3` and loads teachers/classes/periods/subjects
   and the Class Wise assignments from the Excel — safe to re-run,
   never overwrites anything you've since changed)
4. `python manage.py createsuperuser` (optional, for `/admin`)
5. `python manage.py runserver`
6. Open http://127.0.0.1:8000

## Building the Windows .exe

1. `pip install -r requirements-build.txt`
2. `python build_exe.py`
   - If `db.sqlite3` doesn't exist yet in the project folder, this runs
     `migrate` first to create it (with everything pre-loaded) — that
     file is shipped inside the exe as the seed database. It's
     git-ignored, so each machine builds its own.
3. Output: `dist\PeriodManager\PeriodManager.exe` — runs standalone.
4. Optional installer: open `installer.iss` in Inno Setup (or run
   `iscc installer.iss`) to produce `Output\PeriodManager_Setup.exe`.

**Where user data lives:** once installed, the live database is stored
at `%LOCALAPPDATA%\PeriodManager\db.sqlite3` — separate from the
Program Files install, so it survives reinstalls/updates and needs no
admin rights to write to. Nothing is uploaded or synced anywhere.

## Notes

- `db.sqlite3` is git-ignored on purpose — each environment (dev
  machine, build machine) creates its own via `migrate`.
- Re-running `migrate` never overwrites a class/period cell you've
  already filled in through the website; the seed migrations only
  fill in what's still empty.
