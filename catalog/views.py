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
        "man-hinh": [("Màn hình Gaming", "monitor-gaming"), ("Màn hình văn phòng", "monitor-office"), ("Màn hình đồ họa", "monitor-creator")],
        "phu-kien-pc": [("Chuột", "mouse"), ("Bàn phím", "keyboard"), ("Camera", "camera"), ("Tai nghe", "headset"), ("Micro", "microphone")],
    }
    spec_filter_groups = {
        "laptop": [
            {"name": "style", "label": "Chọn Laptop", "options": ["Gaming", "Mỏng nhẹ", "Sáng tạo"]},
            {"name": "laptop_purpose", "label": "Phong cách", "options": ["Văn phòng", "Gaming", "Creator"]},
            {"name": "cpu", "label": "CPU", "options": ["Intel", "AMD", "Qualcomm"]},
            {"name": "ram", "label": "RAM", "options": ["8GB", "16GB", "32GB", "64GB", "128GB"]},
            {"name": "storage", "label": "SSD", "options": ["256GB", "512GB", "1TB", "2TB","4TB","8TB"]},
            {"name": "display", "label": "Màn hình", "options": ["13 inch", "14 inch", "15.6 inch", "16 inch", "18 inch", "Kích thước khác"]},
            {"name": "gpu", "label": "VGA", "options": ["Intel Arc", "Radeon", "GeForce"]},
            {"name": "resolution", "label": "Độ phân giải màn hình", "options": ["Full HD", "WUXGA", "2K", "3K","4K"]},
            {"name": "touch", "label": "Cảm ứng màn hình", "options": [("Có cảm ứng", "yes"), ("Không cảm ứng", "no")]},
            {"name": "refresh", "label": "Tần số màn hình", "options": ["60Hz", "120Hz", "144Hz", "165Hz", "240Hz","180Hz"]},
            {"name": "os", "label": "Hệ điều hành", "options": ["Windows", "Linux", "Mac OS"]},
        ],
        "man-hinh": [
            {"name": "purpose", "label": "Nhu cầu", "options": ["Gaming", "Văn phòng", "Đồ họa"]},
            {"name": "resolution", "label": "Độ phân giải", "options": ["Full HD", "2K"]},
            {"name": "refresh", "label": "Tần số quét", "options": ["144Hz", "180Hz"]},
        ],
    }
    component_filter_groups = {
        "cpu": [
            {"name": "socket", "label": "Socket", "options": ["AMD AM5", "LGA1700","LGA 1200","AMD AM4","LGA 1851"]},
            {"name": "Dòng CPU", "label": "Dòng CPU", "options": ["Intel Core i3","Intel Core i5","Intel Core i7","Intel Core i9","AMD Ryzen 3","AMD Ryzen 5","AMD Ryzen 7","AMD Ryzen 9"]},
        ],
        "mainboard": [
            {"name": "socket", "label": "Socket", "options": ["AM5", "LGA1700"]},
            {"name": "chipset", "label": "Chipset", "options": ["A520", "B650", "B760"]},
            {"name": "ram_type", "label": "Chuẩn RAM hỗ trợ", "options": ["DDR4", "DDR5"]},
            {"name": "form_factor", "label": "Kích thước", "options": ["ATX", "micro-ATX"]},
        ],
        "vga": [
            {"name": "gpu", "label": "Hãng / dòng GPU", "options": ["NVIDIA", "AMD", "RTX", "Radeon"]},
            {"name": "vram", "label": "Dung lượng VRAM", "options": ["8GB", "12GB", "16GB"]},
            {"name": "interface", "label": "Giao tiếp", "options": ["PCI Express 4.0", "PCI Express 5.0"]},
        ],
        "ram": [
            {"name": "ram_type", "label": "Chuẩn RAM", "options": ["DDR4", "DDR5"]},
            {"name": "capacity", "label": "Dung lượng", "options": ["8GB", "16GB", "32GB", "64GB"]},
            {"name": "memory_bus", "label": "Bus RAM", "options": ["3200MHz", "5600MHz", "6000MHz"]},
            {"name": "latency", "label": "Độ trễ", "options": ["CL16", "CL36"]},
        ],
        "ssd": [
            {"name": "storage_type", "label": "Loại SSD", "options": ["NVMe", "SATA"]},
            {"name": "capacity", "label": "Dung lượng", "options": ["256GB", "500GB", "512GB", "1TB", "2TB"]},
            {"name": "interface", "label": "Chuẩn kết nối", "options": ["PCIe Gen 3", "PCIe Gen 4", "SATA III"]},
        ],
        "psu": [
            {"name": "wattage", "label": "Công suất", "options": ["550W", "650W", "750W", "850W"]},
            {"name": "efficiency", "label": "Hiệu suất", "options": ["80 Plus", "80 Plus Bronze", "80 Plus Gold", "80 Plus Platinum"]},
            {"name": "modular", "label": "Kiểu dây", "options": ["Full modular", "Semi modular", "Non-modular"]},
        ],
    }

    active_category_slug = category.slug if category else ""
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
            for chipset in re.findall(r"(?<![A-Z0-9])([HBZAX]\d{3})", board_value.upper()):
                mainboard_by_chipset[chipset] = f"Chipset {chipset}"
        mainboard_definitions = sorted(mainboard_by_chipset.items())

        def mainboard_family(name, specs):
            board_value = text_for(specs, name, "Mainboard", "Chipset").upper()
            match = re.search(r"(?<![A-Z0-9])([HBZAX]\d{3})", board_value)
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
    price_range_key = active_kind if active_kind in PRICE_RANGE_OPTIONS else active_category_slug
    # On the PC components page, show only brands that actually sell the
    # selected component type (for example, CPU brands while CPU is selected).
    brand_base = base
    if active_category_slug == "linh-kien-pc" and active_kind in component_filter_groups:
        brand_base = filter_products(base, {"kind": active_kind})
    brands = brand_base.exclude(brand="").order_by("brand").values_list("brand", flat=True).distinct()
    component_filter_names = (
        "cpu", "ram", "storage", "gpu", "purpose", "resolution", "refresh", "os",
        "display", "touch", "style", "laptop_purpose",
        "socket", "cpu_cores", "cpu_clock", "tdp", "chipset", "ram_type", "form_factor",
        "vram", "interface", "capacity", "memory_bus", "latency", "storage_type",
        "wattage", "efficiency", "modular",
    )

    def query_for_kind(kind):
        query = request.GET.copy()
        query.pop("page", None)
        if active_category_slug == "linh-kien-pc":
            for name in (*component_filter_names, "brand", "price_range", "min_price", "max_price"):
                query.pop(name, None)
        query["kind"] = kind
        return query.urlencode()

    is_component_category = active_category_slug == "linh-kien-pc"
    if is_component_category:
        selected_spec_filter_groups = component_filter_groups.get(active_kind, [])
    else:
        selected_spec_filter_groups = spec_filter_groups.get(active_category_slug, [])

    component_kinds = {kind for _label, kind in kind_options.get("linh-kien-pc", [])}
    active_kind_label = dict(kind_options_for_category).get(active_kind, "")
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



