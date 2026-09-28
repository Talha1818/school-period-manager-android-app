import os
import sys
import threading

_started = False


def start(project_dir, data_dir, port=8000):
    """Run migrations (which also seed the data) and start waitress in a background thread."""
    global _started
    if _started:
        return
    os.makedirs(data_dir, exist_ok=True)
    os.environ["PM_DATA_DIR"] = data_dir
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)

    from waitress import serve
    from config.wsgi import application

    t = threading.Thread(
        target=lambda: serve(application, host="127.0.0.1", port=port, threads=4),
        daemon=True,
    )
    t.start()
    _started = True
