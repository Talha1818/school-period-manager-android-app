function csrfToken() {
  var el = document.querySelector("[name=csrfmiddlewaretoken]");
  return el ? el.value : "";
}

function showToast(message, type) {
  var toastEl = document.getElementById("appToast");
  document.getElementById("appToastBody").textContent = message;
  toastEl.className = "toast align-items-center border-0 text-bg-" + (type || "success");
  bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 2200 }).show();
}

document.addEventListener("DOMContentLoaded", function () {
  // Delete confirmation
  document.querySelectorAll("[data-delete-url]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.getElementById("deleteForm").action = btn.dataset.deleteUrl;
      document.getElementById("deleteName").textContent = btn.dataset.deleteName;
      bootstrap.Modal.getOrCreateInstance(document.getElementById("deleteModal")).show();
    });
  });

  // Edit buttons
  document.querySelectorAll("[data-edit-url]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var d = btn.dataset;
      if (d.kind) {
        document.getElementById("editSimpleForm").action = d.editUrl;
        document.getElementById("esKind").textContent = d.kind;
        document.getElementById("esName").value = d.name;
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editSimpleModal")).show();
      } else {
        document.getElementById("editTeacherForm").action = d.editUrl;
        document.getElementById("etName").value = d.name;
        document.getElementById("etDesig").value = d.designation || "";
        document.getElementById("etContact").value = d.contact || "";
        document.getElementById("etActive").checked = d.active === "1";
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editTeacherModal")).show();
      }
    });
  });

  // Mobile sidebar (with backdrop, closes on outside tap / quick-add)
  var sidebar = document.getElementById("sidebar");
  function setSidebar(open) {
    sidebar.classList.toggle("open", open);
    document.body.classList.toggle("sidebar-open", open);
  }
  var menuBtn = document.getElementById("menuBtn");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      setSidebar(!sidebar.classList.contains("open"));
    });
  }
  var backdrop = document.getElementById("sidebarBackdrop");
  if (backdrop) backdrop.addEventListener("click", function () { setSidebar(false); });
  sidebar.querySelectorAll(".btn-side").forEach(function (b) {
    b.addEventListener("click", function () { setSidebar(false); });
  });

  // Touch reordering via drag handle (HTML5 drag & drop doesn't fire on touch)
  document.querySelectorAll(".drag-handle").forEach(function (h) {
    var row = null, tbody = null, moved = false;
    h.addEventListener("touchstart", function () {
      row = h.closest("tr.drag-row");
      if (!row) return;
      tbody = row.parentNode;
      moved = false;
      row.draggable = false;
      row.classList.add("dragging");
    }, { passive: true });
    h.addEventListener("touchmove", function (e) {
      if (!row) return;
      e.preventDefault();
      var y = e.touches[0].clientY, after = null, best = -Infinity;
      [].slice.call(tbody.querySelectorAll("tr.drag-row:not(.dragging)")).forEach(function (r) {
        var b = r.getBoundingClientRect();
        var off = y - b.top - b.height / 2;
        if (off < 0 && off > best) { best = off; after = r; }
      });
      if (after) { if (row.nextElementSibling !== after) { tbody.insertBefore(row, after); moved = true; } }
      else if (tbody.lastElementChild !== row) { tbody.appendChild(row); moved = true; }
    }, { passive: false });
    function end() {
      if (!row) return;
      row.classList.remove("dragging");
      row.draggable = true;
      var t = tbody, m = moved;
      row = null;
      if (m) t.dispatchEvent(new Event("dragend", { bubbles: true }));
    }
    h.addEventListener("touchend", end);
    h.addEventListener("touchcancel", end);
  });

  // Focus first input when a modal opens
  document.querySelectorAll(".modal").forEach(function (m) {
    m.addEventListener("shown.bs.modal", function () {
      var i = m.querySelector("input[type=text]");
      if (i) i.focus();
    });
  });
});
