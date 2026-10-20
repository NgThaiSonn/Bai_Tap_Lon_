(function () {
  const key = "pcshop.compare.v1";
  const dock = document.getElementById("compare-dock");
  const comparePage = document.querySelector(".compare-page");

  function readIds() {
    try {
      const value = JSON.parse(localStorage.getItem(key) || "[]");
      return Array.isArray(value) ? value.map(String).filter((id, index, all) => id && all.indexOf(id) === index).slice(0, 4) : [];
    } catch (_) {
      return [];
    }
  }

  function writeIds(ids) {
    try { localStorage.setItem(key, JSON.stringify(ids.slice(0, 4))); } catch (_) {}
  }

  if (comparePage && new URLSearchParams(window.location.search).has("ids")) {
    writeIds((comparePage.dataset.compareIds || "").split(",").filter(Boolean));
  }

  function render() {
    const ids = readIds();
    if (dock) {
      dock.hidden = ids.length === 0;
      const count = document.getElementById("compare-count");
      const open = document.getElementById("compare-open");
      if (count) count.textContent = ids.length;
      if (open) {
        open.href = ids.length ? dock.dataset.compareUrl + "?ids=" + encodeURIComponent(ids.join(",")) : "#";
        open.textContent = "So sánh (" + ids.length + ")";
      }
    }
    document.querySelectorAll("[data-compare-toggle]").forEach((button) => {
      const selected = ids.includes(String(button.dataset.productId));
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", selected ? "true" : "false");
      button.innerHTML = selected ? '<span aria-hidden="true">✓</span> Đã chọn' : '<span aria-hidden="true">⇄</span> So sánh';
    });
  }

  function showNotice(message) {
    const notice = document.getElementById("compare-feedback");
    if (!notice) return;
    notice.textContent = message;
    window.setTimeout(() => { if (notice.textContent === message) notice.textContent = ""; }, 2800);
  }

  function updateComparePage(ids) {
    writeIds(ids);
    if (!comparePage) { render(); return; }
    const target = comparePage.dataset.compareUrl || window.location.pathname;
    window.location.href = ids.length ? target + "?ids=" + encodeURIComponent(ids.join(",")) : target;
  }

  document.addEventListener("click", (event) => {
    const addButton = event.target.closest("[data-compare-toggle]");
    if (addButton) {
      const ids = readIds();
      const id = String(addButton.dataset.productId);
      if (ids.includes(id)) {
        writeIds(ids.filter((item) => item !== id));
        render();
      } else if (ids.length >= 4) {
        showNotice("Bạn chỉ có thể so sánh tối đa 4 sản phẩm.");
      } else {
        writeIds(ids.concat(id));
        render();
        showNotice("Đã thêm sản phẩm vào danh sách so sánh.");
      }
      return;
    }

    const removeButton = event.target.closest("[data-compare-remove]");
    if (removeButton) {
      const id = String(removeButton.dataset.compareRemove);
      updateComparePage(readIds().filter((item) => item !== id));
      return;
    }

    if (event.target.closest("[data-compare-clear]")) {
      writeIds([]);
      updateComparePage([]);
    }
  });

  render();
})();
