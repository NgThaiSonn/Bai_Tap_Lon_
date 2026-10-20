import re


COMPONENT_GROUPS = (
    ("cpu", "CPU"),
    ("mainboard", "Mainboard"),
    ("ram", "RAM"),
    ("vga", "Card màn hình"),
    ("psu", "Nguồn"),
    ("storage", "Ổ cứng"),
)


def _spec(product, *keys):
    specifications = product.specifications or {}
    for key in keys:
        value = specifications.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def component_kind(product):
    """Identify desktop PC components from the specifications stored on a product."""
    if product.category.slug != "linh-kien-pc":
        return None

    specs = product.specifications or {}
    lowered = {str(key).casefold() for key in specs}
    name = product.name.casefold()

    if "chipset" in lowered or "mainboard" in name or "bo mạch chủ" in name:
        return "mainboard"
    if "socket" in lowered:
        return "cpu"
    if "gpu" in lowered or "vram" in lowered or "card màn hình" in name or "geforce" in name or "radeon" in name:
        return "vga"
    if "công suất" in lowered or name.startswith("nguồn "):
        return "psu"
    memory_details = " ".join(str(value) for value in specs.values()) + " " + product.name
    if "bus" in lowered and "dung lượng" in lowered and (
        "ram" in name or re.search(r"DDR[345]", memory_details, re.IGNORECASE)
    ):
        return "ram"
    if any(word in name for word in ("ssd", "nvme", "hdd")) or (
        "dung lượng" in lowered and ("chuẩn" in lowered or "loại ổ cứng" in lowered)
    ):
        return "storage"
    return None


def _socket(value):
    match = re.search(r"\b(AM\d+|LGA\s*\d+)\b", (value or "").upper())
    return re.sub(r"\s+", "", match.group(1)) if match else ""


def _memory_types(value):
    return set(re.findall(r"DDR[345]", (value or "").upper()))


def _watts(value):
    match = re.search(r"(\d{2,4})\s*W\b", (value or "").upper())
    return int(match.group(1)) if match else None


def check_compatibility(selected):
    """Return user-facing compatibility notes and whether any hard conflict exists."""
    notes = []
    has_conflict = False

    def add(level, text):
        nonlocal has_conflict
        notes.append({"level": level, "text": text})
        has_conflict = has_conflict or level == "danger"

    cpu = selected.get("cpu")
    board = selected.get("mainboard")
    ram = selected.get("ram")
    gpu = selected.get("vga")
    psu = selected.get("psu")

    if cpu and board:
        cpu_socket = _socket(_spec(cpu, "Socket"))
        board_socket = _socket(_spec(board, "Socket"))
        if cpu_socket and board_socket:
            if cpu_socket == board_socket:
                add("success", f"CPU và mainboard cùng socket {cpu_socket}.")
            else:
                add("danger", f"CPU dùng socket {cpu_socket}, còn mainboard dùng {board_socket}.")
        else:
            add("warning", "Chưa đủ thông tin socket để xác nhận CPU và mainboard tương thích.")
    else:
        add("info", "Chọn cả CPU và mainboard để kiểm tra socket.")

    if ram and board:
        ram_type = _memory_types(_spec(ram, "Chuẩn", "Loại RAM", "RAM") + " " + ram.name)
        board_types = _memory_types(_spec(board, "RAM hỗ trợ", "Chuẩn RAM"))
        if ram_type and board_types:
            if ram_type & board_types:
                add("success", f"RAM {sorted(ram_type & board_types)[0]} phù hợp với mainboard.")
            else:
                add("danger", f"RAM {', '.join(sorted(ram_type))} không khớp chuẩn RAM mainboard hỗ trợ.")
        else:
            add("warning", "Chưa đủ thông tin chuẩn RAM để xác nhận tương thích với mainboard.")
    elif ram or board:
        add("info", "Chọn cả RAM và mainboard để kiểm tra chuẩn bộ nhớ.")

    if gpu and psu:
        required_watts = _watts(_spec(gpu, "Nguồn đề nghị", "Công suất nguồn đề nghị", "Nguồn khuyến nghị"))
        psu_watts = _watts(_spec(psu, "Công suất", "Công suất định danh"))
        if required_watts and psu_watts:
            if psu_watts >= required_watts:
                add("success", f"Nguồn {psu_watts}W đáp ứng mức đề nghị {required_watts}W cho card màn hình.")
            else:
                add("danger", f"Card màn hình đề nghị nguồn {required_watts}W nhưng nguồn đã chọn chỉ có {psu_watts}W.")
        else:
            add("warning", "Chưa đủ thông tin công suất để xác nhận card màn hình và nguồn.")
    elif gpu or psu:
        add("info", "Chọn cả card màn hình và nguồn để kiểm tra công suất.")

    if not selected:
        add("info", "Chọn linh kiện để bắt đầu kiểm tra cấu hình.")
    return notes, has_conflict
