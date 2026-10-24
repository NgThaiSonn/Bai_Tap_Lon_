import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders.cart import Cart, StockError

from .compatibility import COMPONENT_GROUPS, check_compatibility, component_kind
from .filters import PRICE_RANGE_OPTIONS, filter_products, price_filter_error
from .forms import ReviewForm
from .models import Category, Product, Review
from .services import user_can_review


def home(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    preferred_order = {
        name: index
        for index, name in enumerate(("Laptop", "PC văn phòng", "PC gaming", "Màn hình", "Phụ kiện PC", "Linh kiện PC"))
    }
    categories = sorted(
        Category.objects.all(),
        key=lambda category: preferred_order.get(category.name, 99),
    )
    category_sections = [
        {"category": category, "products": products.filter(category=category)[:6]}
        for category in categories
    ]
    return render(request, "catalog/home.html", {
        "categories": categories,
        "category_sections": category_sections,
    })


def product_list(request, slug=None):
    category = get_object_or_404(Category, slug=slug) if slug else None
    base = Product.objects.filter(is_active=True).select_related("category")
    if category:
        base = base.filter(category=category)

    filter_params = request.GET.copy()
    if category:
        filter_params["category"] = category.slug
        if category.slug == "linh-kien-pc" and request.GET.get("kind") == "cpu":
            # CPU pages intentionally omit the ready-stock control.
            filter_params.pop("in_stock", None)
    products = filter_products(base, filter_params)
    params = request.GET.copy()
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    def query_for(key, value):
        query = request.GET.copy()
        query.pop("page", None)
        query[key] = value
        return query.urlencode()

    params.pop("page", None)
    kind_options = {
        "linh-kien-pc": [("CPU", "cpu"), ("Mainboard", "mainboard"), ("VGA", "vga"), ("RAM", "ram"), ("SSD", "ssd"), ("Nguồn", "psu")],
        "laptop": [("Laptop văn phòng", "laptop-office"), ("Laptop gaming", "laptop-gaming"), ("Laptop đồ họa", "laptop-creator")],
        "phu-kien-pc": [("Chuột", "mouse"), ("Bàn phím", "keyboard"), ("Camera", "camera"), ("Tai nghe", "headset"), ("Micro", "microphone")],
    }
    spec_filter_groups = {
        "laptop": [],
        "phu-kien-pc": [],
        "man-hinh": [],
        "pc-van-phong": [],
    }
    component_filter_groups = {
        "cpu": [],
        "mainboard": [],
        "vga": [],
        "ram": [],
        "ssd": [],
        "psu": [],
    }

    active_category_slug = category.slug if category else ""
    if active_category_slug == "linh-kien-pc":
        cpu_records = list(
            filter_products(base, {"kind": "cpu"}).values_list("name", "specifications")
        )
        cpu_family_patterns = [
            ("Intel Core i3", re.compile(r"\bcore\s+i3\b", re.IGNORECASE)),
            ("Intel Core i5", re.compile(r"\bcore\s+i5\b", re.IGNORECASE)),
            ("Intel Core i7", re.compile(r"\bcore\s+i7\b", re.IGNORECASE)),
            ("Intel Core i9", re.compile(r"\bcore\s+i9\b", re.IGNORECASE)),
            ("Intel Core Ultra 5", re.compile(r"\bcore\s+ultra\s+5\b", re.IGNORECASE)),
            ("Intel Core Ultra 7", re.compile(r"\bcore\s+ultra\s+7\b", re.IGNORECASE)),
            ("Intel Core Ultra 9", re.compile(r"\bcore\s+ultra\s+9\b", re.IGNORECASE)),
            ("AMD Ryzen 3", re.compile(r"\bryzen\s+(?:ai\s+)?3\b", re.IGNORECASE)),
            ("AMD Ryzen 5", re.compile(r"\bryzen\s+(?:ai\s+)?5\b", re.IGNORECASE)),
            ("AMD Ryzen 7", re.compile(r"\bryzen\s+(?:ai\s+)?7\b", re.IGNORECASE)),
            ("AMD Ryzen 9", re.compile(r"\bryzen\s+(?:ai\s+)?9\b", re.IGNORECASE)),
        ]
        cpu_family_counts = {label: 0 for label, _pattern in cpu_family_patterns}
        cpu_socket_counts = {}
        for cpu_name, cpu_specs in cpu_records:
            cpu_text = f"{cpu_name} {(cpu_specs or {}).get('CPU', '')}"
            for label, pattern in cpu_family_patterns:
                if pattern.search(cpu_text):
                    cpu_family_counts[label] += 1
                    break
            socket = str((cpu_specs or {}).get("Socket", "")).strip()
            if socket:
                cpu_socket_counts[socket] = cpu_socket_counts.get(socket, 0) + 1

        family_options = [
            (f"{label} ({count})", label)
            for label, count in cpu_family_counts.items()
            if count
        ]
        socket_options = [
            (f"{socket} ({count})", socket)
            for socket, count in sorted(cpu_socket_counts.items(), key=lambda item: item[0].casefold())
        ]
        component_filter_groups["cpu"] = [
            {"name": "cpu_family", "label": "Dòng CPU", "options": family_options, "paired_options": True},
            {"name": "socket", "label": "Socket", "options": socket_options, "paired_options": True},
        ]

        def component_text(name, specs, *keys):
            values = [str((specs or {}).get(key, "")) for key in keys]
            values.append(name)
            return " ".join(value for value in values if value).strip()

        def component_options(records, classifier, label_for=None):
            counts = {}
            for name, specs in records:
                for value in classifier(name, specs or {}):
                    if value:
                        counts[value] = counts.get(value, 0) + 1
            label_for = label_for or (lambda value: value)
            return [
                (f"{label_for(value)} ({count})", value)
                for value, count in sorted(counts.items(), key=lambda item: str(item[0]).casefold())
            ]

        def component_group(kind, records, definitions):
            groups = []
            for name, label, classifier, label_for in definitions:
                options = component_options(records, classifier, label_for)
                if options:
                    groups.append({"name": name, "label": label, "options": options, "paired_options": True})
            component_filter_groups[kind] = groups

        mainboard_records = list(
            filter_products(base, {"kind": "mainboard"}).values_list("name", "specifications")
        )

        def mainboard_socket(name, specs):
            match = re.search(r"\b(AM\s*[45]|LGA\s*\d{4})\b", component_text(name, specs, "Socket"), re.IGNORECASE)
            if not match:
                return []
            socket = re.sub(r"\s+", "", match.group(1)).upper()
            return [socket]

        def mainboard_form_factor(name, specs):
            value = component_text(name, specs, "Kích thước", "Form Factor").casefold()
            if re.search(r"micro\s*-?\s*atx|\bmatx\b", value):
                return ["Micro-ATX"]
            if re.search(r"mini\s*-?\s*itx|\bitx\b", value):
                return ["Mini-ITX"]
            if re.search(r"\be\s*-?\s*atx\b", value):
                return ["E-ATX"]
            if re.search(r"\batx\b", value):
                return ["ATX"]
            return []

        def mainboard_chipset(_name, specs):
            value = str((specs or {}).get("Chipset", "")).strip()
            return [value] if value else []

        def mainboard_ram_slots(_name, specs):
            value = component_text("", specs, "Số khe cắm RAM", "Số khe RAM", "Khe RAM", "DIMM")
            match = re.search(r"\b(\d+)\b", value)
            return [match.group(1)] if match else []

        component_group("mainboard", mainboard_records, [
            ("socket", "Socket", mainboard_socket, None),
            ("form_factor", "Form Factor", mainboard_form_factor, None),
            ("chipset", "Chipset", mainboard_chipset, None),
            ("ram_slots", "Số khe cắm RAM", mainboard_ram_slots, lambda value: f"{value} khe"),
        ])

        vga_records = list(filter_products(base, {"kind": "vga"}).values_list("name", "specifications"))

        def vga_purpose(_name, specs):
            value = str((specs or {}).get("Nhu cầu sử dụng") or (specs or {}).get("Mục đích sử dụng") or "").strip()
            return [value] if value else []

        def vga_brand(name, specs):
            value = component_text(name, specs, "GPU", "VGA", "Đồ họa").casefold()
            if any(marker in value for marker in ("nvidia", "geforce", "rtx", "gtx")):
                return ["NVIDIA"]
            if any(marker in value for marker in ("amd", "radeon", "rx ")):
                return ["AMD"]
            if "intel arc" in value:
                return ["Intel"]
            return []

        def vga_memory_type(name, specs):
            value = component_text(name, specs, "VRAM", "Kiểu bộ nhớ", "Loại bộ nhớ", "Memory Type")
            match = re.search(r"\b(GDDR\s*\dX?|HBM\s*\d?)\b", value, re.IGNORECASE)
            return [re.sub(r"\s+", "", match.group(1)).upper()] if match else []

        def vga_memory_size(name, specs):
            value = component_text(name, specs, "VRAM")
            match = re.search(r"\b(\d+)\s*GB\b", value, re.IGNORECASE)
            return [f"{match.group(1)}GB"] if match else []

        def vga_memory_bus(_name, specs):
            value = component_text("", specs, "Giao diện bộ nhớ", "Bus bộ nhớ", "Memory Bus")
            match = re.search(r"\b(\d+)\s*-?\s*bit\b", value, re.IGNORECASE)
            return [f"{match.group(1)}-bit"] if match else []

        component_group("vga", vga_records, [
            ("gpu_purpose", "Nhu cầu sử dụng", vga_purpose, None),
            ("gpu_brand", "Card đồ họa", vga_brand, None),
            ("gpu_memory_type", "Kiểu bộ nhớ", vga_memory_type, None),
            ("vram", "Kích thước bộ nhớ", vga_memory_size, None),
            ("memory_bus_width", "Giao diện bộ nhớ", vga_memory_bus, None),
        ])

        ram_records = list(filter_products(base, {"kind": "ram"}).values_list("name", "specifications"))

        def ram_type(name, specs):
            match = re.search(r"\bDDR\s*[45]\b", component_text(name, specs, "Chuẩn", "Chuẩn RAM", "Loại RAM"), re.IGNORECASE)
            return [re.sub(r"\s+", "", match.group(0)).upper()] if match else []

        def ram_capacity(name, specs):
            value = component_text(name, specs, "Dung lượng", "RAM")
            match = re.search(r"(?<!\d)(\d+)\s*GB\b", value, re.IGNORECASE)
            return [f"{match.group(1)}GB"] if match else []

        def ram_bus(_name, specs):
            value = component_text("", specs, "Bus", "BUS RAM")
            match = re.search(r"\b(\d{3,5})\s*MHz\b", value, re.IGNORECASE)
            return [match.group(1)] if match else []

        def ram_ecc(_name, specs):
            value = component_text("", specs, "Tự sửa lỗi", "ECC", "Error Correction")
            if not value:
                return []
            if re.search(r"non\s*-?\s*ecc|không", value, re.IGNORECASE):
                return ["Non-ECC"]
            if re.search(r"\becc\b|có", value, re.IGNORECASE):
                return ["ECC"]
            return [value]

        def ram_led(name, specs):
            value = component_text(name, specs, "Đèn LED", "Đèn", "Lighting")
            if re.search(r"không\s*(có)?\s*(đèn|led|rgb)|non\s*-?\s*rgb|without\s*rgb", value, re.IGNORECASE):
                return ["Không có LED"]
            if re.search(r"\brgb\b|\bled\b|có đèn", value, re.IGNORECASE):
                return ["Có LED"]
            return []

        component_group("ram", ram_records, [
            ("ram_type", "Loại RAM", ram_type, None),
            ("capacity", "Dung lượng", ram_capacity, None),
            ("memory_bus", "BUS RAM", ram_bus, lambda value: f"{value}MHz"),
            ("ram_ecc", "Tự sửa lỗi", ram_ecc, None),
            ("ram_lighting", "Đèn LED", ram_led, None),
        ])

        ssd_records = list(filter_products(base, {"kind": "ssd"}).values_list("name", "specifications"))

        def ssd_capacity(name, specs):
            value = component_text(name, specs, "Dung lượng", "Ổ cứng")
            match = re.search(r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(TB|GB)\b", value, re.IGNORECASE)
            if not match:
                return []
            amount = match.group(1).replace(",", ".")
            amount = amount.rstrip("0").rstrip(".") if "." in amount else amount
            return [f"{amount}{match.group(2).upper()}"]

        def ssd_type(name, specs):
            value = component_text(name, specs, "Loại ổ cứng", "Giao tiếp", "Chuẩn").casefold()
            if "nvme" in value or re.search(r"\bm\.2\b", value):
                return ["NVMe"]
            if "sata" in value:
                return ["SATA"]
            return []

        def ssd_interface(_name, specs):
            value = component_text("", specs, "Giao diện PCIe", "Giao tiếp", "Chuẩn")
            match = re.search(r"\bPCIe?\s*[- ]?\s*(?:Express\s*)?(?:Gen\s*)?([345])(?:\.0)?\b", value, re.IGNORECASE)
            return [f"PCIe {match.group(1)}.0"] if match else []

        component_group("ssd", ssd_records, [
            ("capacity", "Dung lượng", ssd_capacity, None),
            ("storage_type", "Loại ổ cứng", ssd_type, None),
            ("ssd_interface", "Giao diện PCIe", ssd_interface, None),
        ])

        psu_records = list(filter_products(base, {"kind": "psu"}).values_list("name", "specifications"))

        def psu_wattage(_name, specs):
            value = component_text("", specs, "Công suất")
            match = re.search(r"\b(\d{3,4})\s*W\b", value, re.IGNORECASE)
            return [f"{match.group(1)}W"] if match else []

        def psu_standard(_name, specs):
            value = component_text("", specs, "Hiệu suất", "Chuẩn nguồn", "Chuẩn")
            match = re.search(r"80\s*Plus(?:\s*(White|Bronze|Silver|Gold|Platinum|Titanium))?", value, re.IGNORECASE)
            if not match:
                return []
            grade = f" {match.group(1).title()}" if match.group(1) else ""
            return [f"80 Plus{grade}"]

        def psu_cable(_name, specs):
            value = str((specs or {}).get("Kiểu dây", "")).strip()
            return [value] if value else []

        def psu_size(_name, specs):
            value = component_text("", specs, "Kích cỡ nguồn", "Kích thước nguồn", "Form Factor nguồn")
            match = re.search(r"\b(Flex\s*ATX|ATX|SFX|TFX)\b", value, re.IGNORECASE)
            return [re.sub(r"\s+", "", match.group(1)).upper()] if match else []

        component_group("psu", psu_records, [
            ("wattage", "Công suất", psu_wattage, None),
            ("efficiency", "Chuẩn nguồn", psu_standard, None),
            ("modular", "Kiểu dây nguồn", psu_cable, None),
            ("psu_size", "Kích cỡ nguồn", psu_size, None),
        ])

    if active_category_slug == "pc-gaming":
        gaming_records = list(base.values_list("name", "specifications"))

        def text_for(specs, name, *keys):
            parts = [str((specs or {}).get(key, "")) for key in keys]
            parts.append(name)
            return " ".join(part for part in parts if part).strip()

        def clean_number(value):
            value = value.replace(",", ".")
            return value.rstrip("0").rstrip(".") if "." in value else value

        def build_group_options(definitions, classifier):
            counts = {value: 0 for value, _label in definitions}
            for name, specs in gaming_records:
                value = classifier(name, specs or {})
                if value in counts:
                    counts[value] += 1
            return [
                (f"{label} ({counts[value]})", value)
                for value, label in definitions
                if counts[value]
            ]

        cpu_family_definitions = [
            ("i3", "Intel Core i3"),
            ("i5", "Intel Core i5"),
            ("i7", "Intel Core i7"),
            ("i9", "Intel Core i9"),
            ("Ryzen 3", "AMD Ryzen 3"),
            ("Ryzen 5", "AMD Ryzen 5"),
            ("Ryzen 7", "AMD Ryzen 7"),
            ("Ryzen 9", "AMD Ryzen 9"),
            ("Core Ultra 5", "Intel Core Ultra 5"),
            ("Core Ultra 7", "Intel Core Ultra 7"),
            ("Core Ultra 9", "Intel Core Ultra 9"),
        ]

        def cpu_family(name, specs):
            cpu_value = str((specs or {}).get("CPU") or name).casefold()
            for value, _label in cpu_family_definitions:
                if value.startswith("i") and value[1:].isdigit():
                    if f"core {value}" in cpu_value or ("intel" in cpu_value and value in cpu_value):
                        return value
                elif value.casefold() in cpu_value:
                    return value
            return None

        mainboard_by_chipset = {}
        for name, specs in gaming_records:
            board_value = text_for(specs, name, "Mainboard", "Chipset")
            for chipset in re.findall(r"(?<![A-Z0-9])([HBZAX]\d{3,4}E?)", board_value.upper()):
                mainboard_by_chipset[chipset] = f"Chipset {chipset}"
        mainboard_definitions = sorted(mainboard_by_chipset.items())

        def mainboard_family(name, specs):
            board_value = text_for(specs, name, "Mainboard", "Chipset").upper()
            match = re.search(r"(?<![A-Z0-9])([HBZAX]\d{3,4}E?)", board_value)
            return match.group(1) if match else None

        storage_by_capacity = {}
        for name, specs in gaming_records:
            storage_value = " ".join(
                str((specs or {}).get(key, ""))
                for key in ("Ổ cứng", "Dung lượng")
                if (specs or {}).get(key)
            ) or name
            match = re.search(r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(TB|GB)\b", storage_value, re.IGNORECASE)
            if match:
                amount = clean_number(match.group(1))
                capacity = f"{amount}{match.group(2).upper()}"
                storage_kind = "HDD" if "hdd" in storage_value.casefold() else (
                    "SSD" if any(marker in storage_value.casefold() for marker in ("ssd", "nvme", "sata", "pcie")) else ""
                )
                option_value = f"{capacity}|{storage_kind}" if storage_kind else capacity
                storage_by_capacity[option_value] = f"{storage_kind} {capacity}".strip()
        storage_definitions = sorted(
            storage_by_capacity.items(),
            key=lambda item: float(re.match(r"\d+(?:\.\d+)?", item[0]).group())
            * (1000 if item[0].split("|")[0].endswith("TB") else 1),
        )

        def storage_family(name, specs):
            storage_value = " ".join(
                str((specs or {}).get(key, ""))
                for key in ("Ổ cứng", "Dung lượng")
                if (specs or {}).get(key)
            ) or name
            match = re.search(r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(TB|GB)\b", storage_value, re.IGNORECASE)
            if not match:
                return None
            amount = clean_number(match.group(1))
            capacity = f"{amount}{match.group(2).upper()}"
            storage_kind = "HDD" if "hdd" in storage_value.casefold() else (
                "SSD" if any(marker in storage_value.casefold() for marker in ("ssd", "nvme", "sata", "pcie")) else ""
            )
            return f"{capacity}|{storage_kind}" if storage_kind else capacity

        gpu_family_labels = {}
        for name, specs in gaming_records:
            gpu_value = text_for(specs, name, "VGA", "GPU", "Đồ họa")
            rtx = re.search(r"\bRTX\s*(\d{4})", gpu_value, re.IGNORECASE)
            rx = re.search(r"\bRX\s*(\d{4})", gpu_value, re.IGNORECASE)
            if rtx:
                series = rtx.group(1)[:2]
                gpu_family_labels[f"RTX {series[0]}"] = f"NVIDIA GeForce RTX {series} Series"
            elif rx:
                series = f"{rx.group(1)[0]}000"
                gpu_family_labels[f"RX {rx.group(1)[0]}"] = f"AMD Radeon RX {series} Series"
        gpu_family_definitions = sorted(gpu_family_labels.items(), key=lambda item: item[1])

        def gpu_family(name, specs):
            gpu_value = text_for(specs, name, "VGA", "GPU", "Đồ họa")
            rtx = re.search(r"\bRTX\s*(\d{4})", gpu_value, re.IGNORECASE)
            if rtx:
                return f"RTX {rtx.group(1)[0]}"
            rx = re.search(r"\bRX\s*(\d{4})", gpu_value, re.IGNORECASE)
            if rx:
                return f"RX {rx.group(1)[0]}"
            return None

        ram_family_labels = {}
        for name, specs in gaming_records:
            ram_value = text_for(specs, name, "RAM")
            capacity = re.search(r"(?<!\d)(\d+)\s*GB\b", ram_value, re.IGNORECASE)
            memory_type = re.search(r"DDR\s*(\d)", ram_value, re.IGNORECASE)
            if capacity and memory_type:
                value = f"{capacity.group(1)}GB|DDR{memory_type.group(1)}"
                label = f"{capacity.group(1)}GB DDR{memory_type.group(1)}"
            elif memory_type:
                value = f"DDR{memory_type.group(1)}"
                label = value
            elif capacity:
                value = f"{capacity.group(1)}GB"
                label = value
            else:
                continue
            ram_family_labels[value] = label
        ram_family_definitions = sorted(ram_family_labels.items(), key=lambda item: item[1])

        def ram_family(name, specs):
            ram_value = text_for(specs, name, "RAM")
            capacity = re.search(r"(?<!\d)(\d+)\s*GB\b", ram_value, re.IGNORECASE)
            memory_type = re.search(r"DDR\s*(\d)", ram_value, re.IGNORECASE)
            if capacity and memory_type:
                return f"{capacity.group(1)}GB|DDR{memory_type.group(1)}"
            if memory_type:
                return f"DDR{memory_type.group(1)}"
            if capacity:
                return f"{capacity.group(1)}GB"
            return None

        case_types = [
            ("full-tower", "Full Tower", ("full tower", "full-tower")),
            ("mid-tower", "Mid Tower", ("mid tower", "mid-tower")),
            ("mini-tower", "Mini Tower", ("mini tower", "mini-tower")),
            ("mini-itx", "Mini-ITX / SFF", ("mini-itx", "sff")),
            ("micro-atx", "Micro-ATX", ("micro-atx", "micro atx", "matx")),
            ("atx", "ATX", ("atx",)),
        ]

        def case_type(name, specs):
            case_value = text_for(specs, name, "Loại case", "Vỏ case", "Case").casefold()
            for value, _label, markers in case_types:
                if any(marker in case_value for marker in markers):
                    return value
            return None

        case_definitions = [(value, label) for value, label, _markers in case_types]
        gpu_brands = [(brand, brand) for brand in ("NVIDIA", "AMD", "Intel")]

        def gpu_brand(name, specs):
            gpu_value = text_for(specs, name, "VGA", "GPU", "Đồ họa").casefold()
            if any(marker in gpu_value for marker in ("nvidia", "geforce", "rtx", "gtx")):
                return "NVIDIA"
            if any(marker in gpu_value for marker in ("amd", "radeon", "rx ")):
                return "AMD"
            if "intel arc" in gpu_value:
                return "Intel"
            return None

        cpu_family_options = build_group_options(cpu_family_definitions, cpu_family)
        mainboard_options = build_group_options(mainboard_definitions, mainboard_family)
        storage_options = build_group_options(storage_definitions, storage_family)
        gpu_family_options = build_group_options(gpu_family_definitions, gpu_family)
        ram_family_options = build_group_options(ram_family_definitions, ram_family)
        gpu_brand_options = build_group_options(gpu_brands, gpu_brand)
        case_type_options = build_group_options(case_definitions, case_type)

        gaming_filter_definitions = [
            ("mainboard_family", "Main", mainboard_options),
            ("cpu_family", "CPU", cpu_family_options),
            ("storage_family", "Ổ Cứng", storage_options),
            ("gpu_family", "VGA", gpu_family_options),
            ("ram_family", "RAM", ram_family_options),
            ("gpu_brand", "Hãng VGA", gpu_brand_options),
            ("case_type", "Loại case", case_type_options),
        ]
        spec_filter_groups["pc-gaming"] = [
            {"name": name, "label": label, "options": options, "paired_options": True}
            for name, label, options in gaming_filter_definitions
            if options
        ]

    elif active_category_slug in {"laptop", "phu-kien-pc", "pc-van-phong", "man-hinh"}:
        category_records = list(base.values_list("name", "specifications"))

        def counted_options(definitions, classifier):
            counts = {value: 0 for value, _label in definitions}
            for name, specs in category_records:
                value = classifier(name, specs or {})
                if value in counts:
                    counts[value] += 1
            return [
                (f"{label} ({counts[value]})", value)
                for value, label in definitions
                if counts[value]
            ]

        def text_for_specs(name, specs, *keys):
            parts = [str((specs or {}).get(key, "")) for key in keys]
            parts.append(name)
            return " ".join(part for part in parts if part).strip()

        if active_category_slug == "laptop":
            laptop_groups = []
            selected_laptop_kind = (request.GET.get("kind") or "").strip()
            laptop_kinds = {"laptop-office", "laptop-gaming", "laptop-creator"}
            laptop_base = filter_products(base, {"kind": selected_laptop_kind}) if selected_laptop_kind in laptop_kinds else base
            laptop_records = list(laptop_base.values_list("name", "specifications"))

            def laptop_counted_options(definitions, classifier):
                counts = {value: 0 for value, _label in definitions}
                for name, specs in laptop_records:
                    value = classifier(name, specs or {})
                    if value in counts:
                        counts[value] += 1
                return [
                    (f"{label} ({counts[value]})", value)
                    for value, label in definitions
                    if counts[value]
                ]

            def laptop_text(name, specs, *keys):
                return text_for_specs(name, specs, *keys)

            style_definitions = [("Gaming", "Gaming"), ("Mỏng nhẹ", "Mỏng nhẹ"), ("Sáng tạo", "Sáng tạo")]
            purpose_definitions = [("Văn phòng", "Văn phòng"), ("Gaming", "Gaming"), ("Creator", "Creator")]
            cpu_definitions = [(brand, brand) for brand in ("Intel", "AMD", "Qualcomm", "Apple")]
            gpu_definitions = [(family, family) for family in ("Intel Arc", "Radeon", "GeForce")]
            os_definitions = [(name, name) for name in ("Windows", "Linux", "macOS")]
            touch_definitions = [("yes", "Có cảm ứng"), ("no", "Không cảm ứng")]

            def laptop_style(name, specs):
                value = name.casefold()
                if any(marker in value for marker in ("gaming", "katana", "tuf")):
                    return "Gaming"
                if any(marker in value for marker in ("creator", "proart", "studio")):
                    return "Sáng tạo"
                if any(marker in value for marker in ("slim", "vivobook", "ultrabook", "thin")):
                    return "Mỏng nhẹ"
                return None

            def laptop_purpose(name, specs):
                value = f"{name} {specs or {}}".casefold()
                if any(marker in value for marker in ("gaming", "katana", "tuf")):
                    return "Gaming"
                if any(marker in value for marker in ("creator", "proart", "studio")):
                    return "Creator"
                return "Văn phòng"

            def laptop_cpu(name, specs):
                value = str((specs or {}).get("CPU") or name).casefold()
                for brand in ("Intel", "AMD", "Qualcomm", "Apple"):
                    if brand.casefold() in value:
                        return brand
                return None

            def laptop_ram(name, specs):
                value = laptop_text(name, specs, "RAM")
                match = re.search(r"(?<!\d)(\d+)\s*GB\b", value, re.IGNORECASE)
                return f"{match.group(1)}GB" if match else None

            def laptop_storage(name, specs):
                value = laptop_text(name, specs, "Ổ cứng", "Dung lượng")
                match = re.search(r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(TB|GB)\b", value, re.IGNORECASE)
                if not match:
                    return None
                amount = match.group(1).replace(",", ".")
                amount = amount.rstrip("0").rstrip(".") if "." in amount else amount
                return f"{amount}{match.group(2).upper()}"

            def laptop_display_size(name, specs):
                value = laptop_text(name, specs, "Màn hình", "Kích thước")
                match = re.search(r"(?<!\d)(\d{2}(?:[.,]\d)?)\s*(?:inch(?:es)?|in\b|\")", value, re.IGNORECASE)
                if not match:
                    return None
                amount = match.group(1).replace(",", ".")
                return amount.rstrip("0").rstrip(".") if "." in amount else amount

            def laptop_gpu(name, specs):
                value = laptop_text(name, specs, "VGA", "GPU", "Đồ họa").casefold()
                if any(marker in value for marker in ("geforce", "nvidia", "rtx", "gtx")):
                    return "GeForce"
                if any(marker in value for marker in ("radeon", " amd ", "rx ")):
                    return "Radeon"
                if "intel arc" in value:
                    return "Intel Arc"
                return None

            resolution_definitions = [
                ("Full HD", "Full HD"), ("WUXGA", "WUXGA"), ("2K", "2K / QHD"),
                ("3K", "3K"), ("4K", "4K / UHD"),
            ]

            def laptop_resolution(name, specs):
                value = laptop_text(name, specs, "Độ phân giải", "Màn hình").casefold()
                if any(marker in value for marker in ("3840", "4k", "uhd")):
                    return "4K"
                if any(marker in value for marker in ("3200", "2880", "3k")):
                    return "3K"
                if any(marker in value for marker in ("2560", "1440p", "qhd", "2k")):
                    return "2K"
                if any(marker in value for marker in ("1920 x 1200", "1920x1200", "wuxga")):
                    return "WUXGA"
                if any(marker in value for marker in ("1920", "1080p", "full hd", "fhd")):
                    return "Full HD"
                return None

            refresh_definitions = {}
            for name, specs in laptop_records:
                value = laptop_text(name, specs, "Tần số quét", "Màn hình")
                match = re.search(r"(?<!\d)(\d{2,3})\s*Hz\b", value, re.IGNORECASE)
                if match:
                    refresh_definitions[f"{match.group(1)}Hz"] = f"{match.group(1)}Hz"
            refresh_definitions = sorted(refresh_definitions.items(), key=lambda item: int(item[0][:-2]))

            def laptop_refresh(name, specs):
                value = laptop_text(name, specs, "Tần số quét", "Màn hình")
                match = re.search(r"(?<!\d)(\d{2,3})\s*Hz\b", value, re.IGNORECASE)
                return f"{match.group(1)}Hz" if match else None

            def laptop_os(name, specs):
                value = laptop_text(name, specs, "Hệ điều hành", "OS").casefold()
                if "windows" in value:
                    return "Windows"
                if "linux" in value:
                    return "Linux"
                if "macos" in value or "mac os" in value:
                    return "macOS"
                return None

            def laptop_touch(name, specs):
                screen = str((specs or {}).get("Màn hình", "")).casefold()
                if not screen:
                    return None
                return "yes" if any(marker in screen for marker in ("cảm ứng", "touch")) else "no"

            laptop_filter_definitions = [
                ("style", "Chọn Laptop", style_definitions, laptop_style),
                ("laptop_purpose", "Phong cách", purpose_definitions, laptop_purpose),
                ("cpu", "CPU", cpu_definitions, laptop_cpu),
                ("ram", "RAM", None, laptop_ram),
                ("storage", "SSD", None, laptop_storage),
                ("display_size", "Màn hình (inch)", None, laptop_display_size),
                ("gpu", "VGA", gpu_definitions, laptop_gpu),
                ("resolution", "Độ phân giải màn hình", resolution_definitions, laptop_resolution),
                ("touch", "Cảm ứng màn hình", touch_definitions, laptop_touch),
                ("refresh", "Tần số màn hình", refresh_definitions, laptop_refresh),
                ("os", "Hệ điều hành", os_definitions, laptop_os),
            ]
            for name, label, definitions, classifier in laptop_filter_definitions:
                if definitions is None:
                    values = {}
                    for product_name, specs in laptop_records:
                        value = classifier(product_name, specs or {})
                        if value:
                            values[value] = f"{value} inch" if name == "display_size" else value
                    definitions = sorted(values.items(), key=lambda item: item[1])
                options = laptop_counted_options(definitions, classifier)
                if options:
                    laptop_groups.append({"name": name, "label": label, "options": options, "paired_options": True})
            spec_filter_groups["laptop"] = laptop_groups

        elif active_category_slug == "phu-kien-pc":
            accessory_groups = []
            accessory_kind = (request.GET.get("kind") or "").strip()
            accessory_kinds = {"mouse", "keyboard", "camera", "headset", "microphone"}
            accessory_base = filter_products(base, {"kind": accessory_kind}) if accessory_kind in accessory_kinds else base
            accessory_records = list(accessory_base.values_list("name", "specifications"))

            def accessory_values(keys, parser):
                counts = {}
                for name, specs in accessory_records:
                    options = parser(name, specs or {}, keys)
                    for value in set(options):
                        counts[value] = counts.get(value, 0) + 1
                return counts

            def accessory_dpi(name, specs, keys):
                value = " ".join(str((specs or {}).get(key, "")) for key in keys)
                match = re.search(r"(?<!\d)(\d{1,3}(?:[.,]\d{3})+|\d+)(?![\d.,])", value)
                if not match:
                    return []
                return [match.group(1).replace(",", "").replace(".", "")]

            def accessory_resolution(name, specs, keys):
                value = " ".join(str((specs or {}).get(key, "")) for key in keys)
                match = re.search(r"\b(\d{3,4}\s*p|\d{3,4}\s*[x×]\s*\d{3,4})\b", value, re.IGNORECASE)
                if not match:
                    return []
                return [re.sub(r"\s*([x×])\s*", r"\1", match.group(1)).replace(" ", "").lower()]

            def accessory_exact(name, specs, keys):
                return [
                    str((specs or {}).get(key, "")).strip()
                    for key in keys
                    if (specs or {}).get(key)
                ]

            accessory_filter_definitions = {
                "mouse": [
                    ("dpi", "DPI", ("DPI", "DPI tối đa"), accessory_dpi),
                    ("sensor", "Cảm biến", ("Cảm biến", "Sensor"), accessory_exact),
                    ("lighting", "Đèn", ("Đèn", "Đèn nền", "Lighting"), accessory_exact),
                ],
                "keyboard": [
                    ("switch", "Switch", ("Switch", "Loại switch"), accessory_exact),
                    ("layout", "Layout", ("Layout", "Số phím"), accessory_exact),
                    ("lighting", "Đèn", ("Đèn", "Đèn nền", "Lighting"), accessory_exact),
                ],
                "camera": [
                    ("resolution", "Độ phân giải", ("Độ phân giải", "Resolution"), accessory_resolution),
                    ("micro_support", "Micro", ("Micro", "Microphone"), accessory_exact),
                ],
                "headset": [
                    ("audio", "Âm thanh", ("Âm thanh", "Audio"), accessory_exact),
                    ("micro_support", "Micro", ("Micro", "Microphone"), accessory_exact),
                ],
                "microphone": [
                    ("pickup_pattern", "Hướng thu", ("Hướng thu", "Pickup pattern"), accessory_exact),
                    ("accessory_style", "Kiểu micro", ("Kiểu", "Loại", "Type"), accessory_exact),
                ],
            }
            # Type-specific choices appear after the user selects an accessory group.
            active_accessory_filters = accessory_filter_definitions.get(
                accessory_kind,
                [],
            )
            for name, label, keys, parser in active_accessory_filters:
                counts = accessory_values(keys, parser)
                options = [(f"{value} ({count})", value) for value, count in sorted(counts.items(), key=lambda item: item[0].casefold())]
                if options:
                    accessory_groups.append({"name": name, "label": label, "options": options, "paired_options": True})
            spec_filter_groups["phu-kien-pc"] = accessory_groups

        elif active_category_slug == "pc-van-phong":
            office_groups = []

            cpu_definitions = [
                ("i3", "Intel Core i3"), ("i5", "Intel Core i5"),
                ("i7", "Intel Core i7"), ("i9", "Intel Core i9"),
                ("Core Ultra 5", "Intel Core Ultra 5"),
                ("Core Ultra 7", "Intel Core Ultra 7"),
                ("Core Ultra 9", "Intel Core Ultra 9"),
                ("Ryzen 3", "AMD Ryzen 3"), ("Ryzen 5", "AMD Ryzen 5"),
                ("Ryzen 7", "AMD Ryzen 7"), ("Ryzen 9", "AMD Ryzen 9"),
            ]

            def office_cpu(name, specs):
                cpu_value = str((specs or {}).get("CPU") or name).casefold()
                for value, _label in cpu_definitions:
                    if value == "i3" or value == "i5" or value == "i7" or value == "i9":
                        if re.search(rf"\b{value}\b", cpu_value):
                            return value
                    elif value.casefold() in cpu_value:
                        return value
                return None

            chipset_definitions = {}
            for name, specs in category_records:
                board_value = text_for_specs(name, specs, "Mainboard", "Chipset")
                for chipset in re.findall(r"(?<![A-Z0-9])([HBZAX]\d{3,4}E?)(?![A-Z0-9])", board_value.upper()):
                    chipset_definitions[chipset] = f"Chipset {chipset}"
            chipset_definitions = sorted(chipset_definitions.items())

            def office_chipset(name, specs):
                board_value = text_for_specs(name, specs, "Mainboard", "Chipset").upper()
                match = re.search(r"(?<![A-Z0-9])([HBZAX]\d{3,4}E?)(?![A-Z0-9])", board_value)
                return match.group(1) if match else None

            storage_definitions = {}
            for name, specs in category_records:
                storage_value = text_for_specs(name, specs, "Ổ cứng", "Dung lượng")
                match = re.search(r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(TB|GB)\b", storage_value, re.IGNORECASE)
                if match:
                    amount = match.group(1).replace(",", ".")
                    amount = amount.rstrip("0").rstrip(".") if "." in amount else amount
                    capacity = f"{amount}{match.group(2).upper()}"
                    storage_definitions[capacity] = capacity
            storage_definitions = sorted(
                storage_definitions.items(),
                key=lambda item: float(re.match(r"\d+(?:\.\d+)?", item[0]).group())
                * (1000 if item[0].endswith("TB") else 1),
            )

            def office_storage(name, specs):
                storage_value = text_for_specs(name, specs, "Ổ cứng", "Dung lượng")
                match = re.search(r"(?<!\d)(\d+(?:[.,]\d+)?)\s*(TB|GB)\b", storage_value, re.IGNORECASE)
                if not match:
                    return None
                amount = match.group(1).replace(",", ".")
                amount = amount.rstrip("0").rstrip(".") if "." in amount else amount
                return f"{amount}{match.group(2).upper()}"

            ram_definitions = {}
            for name, specs in category_records:
                ram_value = text_for_specs(name, specs, "RAM")
                capacity = re.search(r"(?<!\d)(\d+)\s*GB\b", ram_value, re.IGNORECASE)
                memory_type = re.search(r"DDR\s*(\d)", ram_value, re.IGNORECASE)
                if capacity and memory_type:
                    value = f"{capacity.group(1)}GB|DDR{memory_type.group(1)}"
                    ram_definitions[value] = f"{capacity.group(1)}GB DDR{memory_type.group(1)}"
                elif memory_type:
                    value = f"DDR{memory_type.group(1)}"
                    ram_definitions[value] = value
                elif capacity:
                    value = f"{capacity.group(1)}GB"
                    ram_definitions[value] = value
            ram_definitions = sorted(ram_definitions.items(), key=lambda item: item[1])

            def office_ram(name, specs):
                ram_value = text_for_specs(name, specs, "RAM")
                capacity = re.search(r"(?<!\d)(\d+)\s*GB\b", ram_value, re.IGNORECASE)
                memory_type = re.search(r"DDR\s*(\d)", ram_value, re.IGNORECASE)
                if capacity and memory_type:
                    return f"{capacity.group(1)}GB|DDR{memory_type.group(1)}"
                if memory_type:
                    return f"DDR{memory_type.group(1)}"
                return f"{capacity.group(1)}GB" if capacity else None

            gpu_definitions = {}
            gpu_brand_definitions = [(brand, brand) for brand in ("NVIDIA", "AMD", "Intel")]
            case_definitions = [
                ("full-tower", "Full Tower", ("full tower", "full-tower")),
                ("mid-tower", "Mid Tower", ("mid tower", "mid-tower")),
                ("mini-tower", "Mini Tower", ("mini tower", "mini-tower")),
                ("mini-itx", "Mini-ITX / SFF", ("mini-itx", "mini itx", "sff")),
                ("micro-atx", "Micro-ATX", ("micro-atx", "micro atx", "matx")),
                ("atx", "ATX", ("atx",)),
            ]

            def office_gpu_text(name, specs):
                graphics_specs = " ".join(
                    str((specs or {}).get(key, ""))
                    for key in ("VGA", "GPU", "Đồ họa")
                    if (specs or {}).get(key)
                )
                if graphics_specs:
                    return graphics_specs
                if re.search(
                    r"\b(?:RTX|GTX|RX)\s*\d{4}\b|\b(?:GeForce|Radeon|Intel UHD|Intel Arc|Intel Iris)\b",
                    name,
                    re.IGNORECASE,
                ):
                    return name
                return ""

            def office_gpu(name, specs):
                value = office_gpu_text(name, specs)
                rtx = re.search(r"\bRTX\s*(\d{4})", value, re.IGNORECASE)
                gtx = re.search(r"\bGTX\s*(\d{4})", value, re.IGNORECASE)
                rx = re.search(r"\bRX\s*(\d{4})", value, re.IGNORECASE)
                if rtx:
                    family = f"RTX {rtx.group(1)[:2]}"
                    gpu_definitions[family] = f"GeForce RTX {rtx.group(1)[:2]} Series"
                    return family
                if gtx:
                    family = f"GTX {gtx.group(1)[:2]}"
                    gpu_definitions[family] = f"GeForce GTX {gtx.group(1)[:2]} Series"
                    return family
                if rx:
                    family = f"RX {rx.group(1)[0]}"
                    gpu_definitions[family] = f"Radeon RX {rx.group(1)[0]} Series"
                    return family
                folded = value.casefold()
                for marker in ("intel arc", "intel iris", "intel uhd", "radeon graphics"):
                    if marker in folded:
                        gpu_definitions[marker] = marker.title()
                        return marker
                return None

            def office_gpu_brand(name, specs):
                value = office_gpu_text(name, specs).casefold()
                if any(marker in value for marker in ("nvidia", "geforce", "rtx", "gtx")):
                    return "NVIDIA"
                if any(marker in value for marker in ("amd", "radeon", "rx ")):
                    return "AMD"
                if "intel" in value:
                    return "Intel"
                return None

            def office_case(name, specs):
                value = text_for_specs(name, specs, "Loại case", "Vỏ case", "Case").casefold()
                for code, _label, markers in case_definitions:
                    if any(marker in value for marker in markers):
                        return code
                return None

            office_filter_definitions = [
                ("cpu_family", "CPU", cpu_definitions, office_cpu),
                ("mainboard_family", "Main", chipset_definitions, office_chipset),
                ("storage_family", "Ổ cứng", storage_definitions, office_storage),
                ("gpu_family", "VGA", None, office_gpu),
                ("ram_family", "RAM", ram_definitions, office_ram),
                ("gpu_brand", "Hãng VGA", gpu_brand_definitions, office_gpu_brand),
                ("case_type", "Loại case", [(value, label) for value, label, _markers in case_definitions], office_case),
            ]
            for name, label, definitions, classifier in office_filter_definitions:
                if name == "gpu_family":
                    # Discover GPU families first so only values found in this category are shown.
                    for record_name, record_specs in category_records:
                        office_gpu(record_name, record_specs or {})
                    definitions = sorted(gpu_definitions.items(), key=lambda item: item[1])
                options = counted_options(definitions or [], classifier)
                if options:
                    office_groups.append({"name": name, "label": label, "options": options, "paired_options": True})
            spec_filter_groups["pc-van-phong"] = office_groups

        else:
            monitor_groups = []

            def monitor_text(name, specs):
                return text_for_specs(name, specs, *((specs or {}).keys())).casefold()

            resolution_definitions = [("4K", "4K / UHD"), ("2K", "2K / QHD"), ("Full HD", "Full HD")]

            def monitor_resolution(name, specs):
                value = monitor_text(name, specs)
                if any(marker in value for marker in ("3840", "4k", "uhd")):
                    return "4K"
                if any(marker in value for marker in ("2560", "1440p", "qhd", "2k")):
                    return "2K"
                if any(marker in value for marker in ("1920", "1080p", "full hd", "fhd")):
                    return "Full HD"
                return None

            refresh_definitions = {}
            size_definitions = {}
            panel_definitions = [(value, value) for value in ("IPS", "VA", "OLED", "TN", "Mini LED", "QLED")]
            purpose_definitions = [(value, label) for value, label in (("gaming", "Gaming"), ("office", "Văn phòng"), ("creator", "Đồ họa"))]

            def monitor_refresh(name, specs):
                value = monitor_text(name, specs)
                match = re.search(r"(?<!\d)(\d{2,3})\s*hz\b", value)
                return f"{match.group(1)}Hz" if match else None

            def monitor_size(name, specs):
                value = monitor_text(name, specs)
                match = re.search(r"(?<!\d)(\d{2}(?:[.,]\d)?)\s*(?:inch(?:es)?|in\b|\")", value)
                if not match:
                    return None
                amount = match.group(1).replace(",", ".")
                amount = amount.rstrip("0").rstrip(".") if "." in amount else amount
                return amount

            def monitor_panel(name, specs):
                value = monitor_text(name, specs)
                for marker, _label in panel_definitions:
                    if marker.casefold() in value:
                        return marker
                return None

            def monitor_purpose(name, specs):
                value = monitor_text(name, specs)
                if "gaming" in value or "ultragear" in value:
                    return "gaming"
                if any(marker in value for marker in ("văn phòng", "office")):
                    return "office"
                if any(marker in value for marker in ("đồ họa", "creator", "proart", "graphic")):
                    return "creator"
                return None

            for name, specs in category_records:
                refresh = monitor_refresh(name, specs or {})
                if refresh:
                    refresh_definitions[refresh] = refresh
                size = monitor_size(name, specs or {})
                if size:
                    size_definitions[size] = f"{size} inch"

            monitor_filter_definitions = [
                ("display_size", "Kích thước", sorted(size_definitions.items(), key=lambda item: float(item[0])), monitor_size),
                ("resolution", "Độ phân giải", resolution_definitions, monitor_resolution),
                ("refresh", "Tần số quét", sorted(refresh_definitions.items(), key=lambda item: int(item[0][:-2])), monitor_refresh),
                ("panel", "Tấm nền", panel_definitions, monitor_panel),
                ("purpose", "Nhu cầu", purpose_definitions, monitor_purpose),
            ]
            for name, label, definitions, classifier in monitor_filter_definitions:
                options = counted_options(definitions, classifier)
                if options:
                    monitor_groups.append({"name": name, "label": label, "options": options, "paired_options": True})
            spec_filter_groups["man-hinh"] = monitor_groups

    kind_options_for_category = kind_options.get(active_category_slug, [])
    selected_kind = (request.GET.get("kind") or "").strip()
    legacy_component_groups = {
        "mainboard-intel": "mainboard",
        "mainboard-amd": "mainboard",
        "vga-nvidia": "vga",
        "vga-amd": "vga",
        "ram-ddr4": "ram",
        "ram-ddr5": "ram",
        "ssd-nvme": "ssd",
        "ssd-sata": "ssd",
        "psu-80plus": "psu",
    }
    active_kind = legacy_component_groups.get(selected_kind, selected_kind)
    kind_filter_options = kind_options_for_category
    if active_category_slug in {"laptop", "phu-kien-pc"}:
        # Only show subcategories that have products and include their counts.
        kind_filter_options = []
        for label, kind in kind_options_for_category:
            count = filter_products(base, {"kind": kind}).count()
            if count:
                kind_filter_options.append((f"{label} ({count})", kind))
    price_range_key = active_kind if active_kind in PRICE_RANGE_OPTIONS else active_category_slug
    # On the PC components page, show only brands that actually sell the
    # selected component type (for example, CPU brands while CPU is selected).
    brand_base = base
    if active_category_slug == "linh-kien-pc" and active_kind in component_filter_groups:
        brand_base = filter_products(base, {"kind": active_kind})
    elif active_category_slug in {"laptop", "phu-kien-pc"} and active_kind in {
        kind for _label, kind in kind_options_for_category
    }:
        brand_base = filter_products(base, {"kind": active_kind})
    brands = brand_base.exclude(brand="").order_by("brand").values_list("brand", flat=True).distinct()
    component_filter_names = (
        "cpu", "ram", "storage", "gpu", "purpose", "resolution", "refresh", "os",
        "display", "touch", "style", "laptop_purpose",
        "socket", "cpu_cores", "cpu_clock", "tdp", "cpu_family", "chipset", "ram_type", "form_factor",
        "vram", "interface", "capacity", "memory_bus", "latency", "storage_type",
        "wattage", "efficiency", "modular", "ram_slots", "gpu_brand", "gpu_purpose",
        "gpu_memory_type", "memory_bus_width", "ram_ecc", "ram_lighting", "ssd_interface", "psu_size",
        "gpu_family", "storage_family", "mainboard_family", "ram_family", "case_type",
    )

    def query_for_kind(kind):
        query = request.GET.copy()
        query.pop("page", None)
        for name in set(component_filter_names) | {
            group["name"]
            for group in spec_filter_groups.get(active_category_slug, [])
        } | {"brand", "price_range", "min_price", "max_price"}:
            query.pop(name, None)
        query["kind"] = kind
        return query.urlencode()

    is_component_category = active_category_slug == "linh-kien-pc"
    if is_component_category:
        selected_spec_filter_groups = component_filter_groups.get(active_kind, [])
    else:
        selected_spec_filter_groups = spec_filter_groups.get(active_category_slug, [])

    # Do not offer values that cannot match any active product in this category.
    # For component pages, scope availability to the selected component group.
    availability_params = (
        {"kind": active_kind}
        if is_component_category or (
            active_category_slug == "laptop" and active_kind in {kind for _label, kind in kind_options_for_category}
        ) or (
            active_category_slug == "phu-kien-pc" and active_kind in {kind for _label, kind in kind_options_for_category}
        )
        else {}
    )
    available_filter_groups = []
    for group in selected_spec_filter_groups:
        available_options = []
        for option in group["options"]:
            value = option[1] if isinstance(option, (tuple, list)) else option
            probe = {**availability_params, group["name"]: value}
            if filter_products(base, probe).exists():
                available_options.append(option)
        if available_options:
            available_filter_groups.append({**group, "options": available_options})
    selected_spec_filter_groups = available_filter_groups

    component_kinds = {kind for _label, kind in kind_options.get("linh-kien-pc", [])}
    active_kind_label = next(
        (label for label, kind in kind_options_for_category if kind == active_kind),
        "",
    )
    show_filter_panel = not is_component_category or active_kind in component_kinds

    context = {
        "category": category,
        "page_obj": page_obj,
        "brands": brands,
        "brand_links": [
            {"name": brand, "query": query_for("brand", brand)}
            for brand in brands
        ],
        "kind_options": kind_options_for_category,
        "kind_filter_options": kind_filter_options,
        "kind_links": [
            {"label": label, "kind": kind, "query": query_for_kind(kind) if is_component_category else query_for("kind", kind)}
            for label, kind in kind_options_for_category
        ],
        "spec_filter_groups": selected_spec_filter_groups,
        "price_range_options": PRICE_RANGE_OPTIONS.get(
            price_range_key,
            PRICE_RANGE_OPTIONS["default"],
        ),
        "active_kind": active_kind,
        "active_kind_label": active_kind_label,
        "is_component_category": is_component_category,
        "hide_brand_select": is_component_category and active_kind == "cpu",
        "hide_stock_filter": is_component_category and active_kind == "cpu",
        "show_filter_panel": show_filter_panel,
        "querystring": params.urlencode(),
        "sort_options": [
            ("newest", "Mới nhất"),
            ("price_asc", "Giá tăng dần"),
            ("price_desc", "Giá giảm dần"),
            ("name", "Tên A-Z"),
        ],
        "filters": request.GET,
        "price_error": price_filter_error(request.GET),
    }
    return render(request, "catalog/product_list.html", context)


def compare_products(request):
    requested_ids = []
    for value in (request.GET.get("ids") or "").split(","):
        try:
            product_id = int(value.strip())
        except (TypeError, ValueError):
            continue
        if product_id > 0 and product_id not in requested_ids:
            requested_ids.append(product_id)
        if len(requested_ids) == 4:
            break

    found = Product.objects.filter(pk__in=requested_ids, is_active=True).select_related("category")
    by_id = {product.pk: product for product in found}
    products = [by_id[product_id] for product_id in requested_ids if product_id in by_id]
    keys = set()
    for product in products:
        for key in (product.specifications or {}):
            if str(key).casefold() not in {"nguồn tham khảo", "source"}:
                keys.add(str(key))
    return render(request, "catalog/compare.html", {
        "products": products,
        "specification_keys": sorted(keys),
        "compare_ids": ",".join(str(product.pk) for product in products),
    })


def pc_builder(request):
    groups = {key: [] for key, _label in COMPONENT_GROUPS}
    available_products = Product.objects.filter(
        is_active=True,
        stock__gt=0,
        category__slug="linh-kien-pc",
    ).select_related("category")
    for product in available_products:
        key = component_kind(product)
        if key in groups:
            groups[key].append(product)

    products_by_id = {
        str(product.pk): product
        for items in groups.values()
        for product in items
    }
    selected = {}
    if request.method == "POST":
        for key, _label in COMPONENT_GROUPS:
            product = products_by_id.get(request.POST.get(key, ""))
            if product:
                selected[key] = product

    diagnostics = []
    has_conflict = False
    checked = request.method == "POST"
    if checked:
        diagnostics, has_conflict = check_compatibility(selected)
        if request.POST.get("action") == "add":
            if not selected:
                messages.error(request, "Hãy chọn ít nhất một linh kiện.")
            elif has_conflict:
                messages.error(request, "Cấu hình có linh kiện không tương thích. Hãy sửa cảnh báo trước khi thêm vào giỏ.")
            else:
                cart = Cart(request)
                current = cart.raw()
                shortages = [
                    product for product in selected.values()
                    if current.get(product.pk, 0) + 1 > product.stock
                ]
                if shortages:
                    messages.error(request, "Số lượng một linh kiện không còn đủ trong kho.")
                else:
                    try:
                        for product in selected.values():
                            cart.add(product.pk, 1)
                    except StockError as error:
                        messages.error(request, error.message)
                    else:
                        messages.success(request, "Đã thêm cấu hình vào giỏ hàng.")
                        return redirect("orders:cart")

    component_groups = [
        {
            "key": key,
            "label": label,
            "products": groups[key],
            "selected_id": selected[key].pk if key in selected else "",
        }
        for key, label in COMPONENT_GROUPS
    ]
    return render(request, "catalog/pc_builder.html", {
        "component_groups": component_groups,
        "selected": list(selected.values()),
        "total": sum((product.price for product in selected.values()), start=0),
        "diagnostics": diagnostics,
        "has_conflict": has_conflict,
        "checked": checked,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    can_review = user_can_review(request.user, product)
    review_form = None
    if can_review:
        existing = Review.objects.filter(product=product, user=request.user).first()
        review_form = ReviewForm(instance=existing)
    context = {
        "product": product,
        "reviews": product.reviews.select_related("user"),
        "can_review": can_review,
        "review_form": review_form,
        "related": Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)[:4],
    }
    return render(request, "catalog/product_detail.html", context)


@login_required
@require_POST
def review_submit(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if not user_can_review(request.user, product):
        messages.error(request, "Bạn chỉ có thể đánh giá sản phẩm sau khi đơn hàng đã hoàn thành.")
        return redirect(product)
    existing = Review.objects.filter(product=product, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
    else:
        messages.error(request, "Đánh giá không hợp lệ, vui lòng kiểm tra lại.")
    return redirect(product)



