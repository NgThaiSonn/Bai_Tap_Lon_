/* Xử lý bất đồng bộ với Fetch API: /api/check-stock/, /api/cart/update/ */
(function () {
  const meta = document.querySelector('meta[name="csrf-token"]');
  const csrf = meta ? meta.content : "";
  const fmt = (v) => new Intl.NumberFormat("vi-VN").format(v) + " ₫";
  const cartRows = () => Array.from(document.querySelectorAll(".cart-item-row[data-product-id]"));

  async function postJSON(url, data) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify(data),
    });
    return { ok: res.ok, data: await res.json() };
  }

  function updateBadge(count) {
    const badge = document.getElementById("cart-badge");
    if (badge) badge.textContent = count;
  }

  function showAlert(msg) {
    const box = document.getElementById("cart-alert");
    if (!box) return;
    box.textContent = msg;
    box.classList.remove("d-none");
    setTimeout(() => box.classList.add("d-none"), 4000);
  }

  function refreshSelection() {
    const rows = cartRows();
    if (!rows.length) return;
    const checked = rows.filter((row) => row.querySelector(".cart-select-item")?.checked);
    const all = document.getElementById("cart-select-all");
    const count = document.getElementById("cart-selected-count");
    const lineCount = document.getElementById("cart-line-count");
    const total = checked.reduce((sum, row) => sum + Number(row.dataset.subtotal || 0), 0);
    const hasUnavailable = checked.some((row) => row.dataset.available === "false");

    if (all) {
      all.checked = checked.length === rows.length;
      all.indeterminate = checked.length > 0 && checked.length < rows.length;
    }
    if (count) count.textContent = checked.length;
    if (lineCount) lineCount.textContent = rows.length;
    ["cart-total", "cart-payable"].forEach((id) => {
      const node = document.getElementById(id);
      if (node) node.textContent = fmt(total);
    });

    const checkout = document.getElementById("cart-checkout-btn");
    if (checkout) {
      const ids = checked.map((row) => row.dataset.productId);
      checkout.href = ids.length
        ? checkout.dataset.checkoutUrl + "?product_ids=" + encodeURIComponent(ids.join(","))
        : "#";
      checkout.classList.toggle("is-disabled", ids.length === 0 || hasUnavailable);
      checkout.setAttribute("aria-disabled", ids.length === 0 || hasUnavailable ? "true" : "false");
      checkout.title = hasUnavailable ? "Hãy điều chỉnh số lượng sản phẩm vượt tồn kho." : "";
    }
  }

  // ---- Trang giỏ hàng ----
  function applyCart(cart) {
    updateBadge(cart.count);
    const present = new Set(cart.lines.map((line) => String(line.product_id)));
    cartRows().forEach((row) => {
      const id = row.dataset.productId;
      if (!present.has(id)) { row.remove(); return; }
      const line = cart.lines.find((item) => String(item.product_id) === id);
      const subtotal = row.querySelector(".line-subtotal");
      if (subtotal) subtotal.textContent = fmt(line.subtotal);
      row.dataset.subtotal = line.subtotal;
      const available = line.stock >= line.quantity;
      row.dataset.available = available ? "true" : "false";
      row.classList.toggle("is-unavailable", !available);
      let warning = row.querySelector(".cart-stock-warning");
      if (!available) {
        if (!warning) {
          warning = document.createElement("div");
          warning.className = "cart-stock-warning";
          row.querySelector(".cart-product-info")?.appendChild(warning);
        }
        warning.textContent = "Chỉ còn " + line.stock + " sản phẩm trong kho. Vui lòng điều chỉnh số lượng.";
      } else if (warning) {
        warning.remove();
      }
      const input = row.querySelector(".cart-qty");
      if (input) {
        input.value = line.quantity;
        input.dataset.prev = line.quantity;
        input.max = line.stock;
      }
    });
    if (cart.lines.length === 0) {
      window.location.reload();
      return;
    }
    refreshSelection();
  }

  async function updateQty(productId, quantity, input) {
    const result = await postJSON("/api/cart/update/", { product_id: Number(productId), quantity: Number(quantity) });
    if (!result.ok) {
      showAlert(result.data.message || "Không cập nhật được giỏ hàng.");
      if (input) input.value = input.dataset.prev;
      if (result.data.cart) updateBadge(result.data.cart.count);
      return;
    }
    applyCart(result.data.cart);
  }

  document.querySelectorAll(".cart-qty").forEach((input) => {
    input.dataset.prev = input.value;
    input.addEventListener("change", () => updateQty(input.dataset.productId, input.value, input));
  });

  document.querySelectorAll(".cart-qty-step").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.closest(".cart-quantity-stepper")?.querySelector(".cart-qty");
      if (!input) return;
      const current = Number.parseInt(input.value || "1", 10);
      const next = Math.max(1, Math.min(Number(input.max || 999), current + Number(button.dataset.step)));
      if (next === current) return;
      input.value = next;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });

  document.querySelectorAll(".cart-remove-btn").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      updateQty(button.dataset.productId, 0, null);
    });
  });

  const selectAll = document.getElementById("cart-select-all");
  if (selectAll) {
    selectAll.addEventListener("change", () => {
      document.querySelectorAll(".cart-select-item").forEach((input) => { input.checked = selectAll.checked; });
      refreshSelection();
    });
  }
  document.querySelectorAll(".cart-select-item").forEach((input) => {
    input.addEventListener("change", refreshSelection);
  });
  refreshSelection();

  const voucherButton = document.querySelector("[data-voucher-toggle]");
  if (voucherButton) {
    voucherButton.addEventListener("click", () => {
      const note = document.getElementById("cart-voucher-note");
      const expanded = voucherButton.getAttribute("aria-expanded") === "true";
      voucherButton.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (note) note.hidden = expanded;
    });
  }

  // ---- Trang chi tiết sản phẩm: kiểm tra tồn kho theo thời gian thực ----
  const stockInput = document.getElementById("detail-qty");
  if (stockInput) {
    const msg = document.getElementById("stock-msg");
    const btn = document.getElementById("add-btn");
    const check = async () => {
      const q = Math.max(1, parseInt(stockInput.value || "1", 10));
      const res = await fetch("/api/check-stock/?product_id=" + stockInput.dataset.productId + "&quantity=" + q);
      const data = await res.json();
      msg.textContent = data.message;
      msg.className = "small " + (data.available ? "text-success" : "text-danger");
      btn.disabled = !data.available;
    };
    stockInput.addEventListener("input", check);
  }
})();
