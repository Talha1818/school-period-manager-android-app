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

  // Mobile sidebar
  var menuBtn = document.getElementById("menuBtn");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      document.getElementById("sidebar").classList.toggle("open");
    });
  }

  // Focus first input when a modal opens
  document.querySelectorAll(".modal").forEach(function (m) {
    m.addEventListener("shown.bs.modal", function () {
      var i = m.querySelector("input[type=text]");
      if (i) i.focus();
    });
  });
});
