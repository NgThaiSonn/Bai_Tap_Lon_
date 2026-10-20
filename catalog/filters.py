"""Logic lọc/sắp xếp sản phẩm dùng chung cho trang web và REST API."""
from decimal import Decimal, InvalidOperation

from django.db.models import Q

SORT_OPTIONS = {
    "newest": ("-created_at", "-id"),
    "price_asc": ("price", "id"),
    "price_desc": ("-price", "-id"),
    "name": ("name",),
}

# (query value, display label, minimum price, exclusive maximum price), in VND.
# Update these entries to change the price bands for each component group.
PRICE_RANGE_OPTIONS = {
    "default": [
        ("under-10m", "Dưới 10 triệu", None, 10_000_000),
        ("10m-20m", "10–20 triệu", 10_000_000, 20_000_000),
        ("20m-45m", "20–45 triệu", 20_000_000, 45_000_000),
        ("over-45m", "Trên 45 triệu", 45_000_000, None),
    ],
    "pc-van-phong": [
        ("office-under-5m", "Dưới 5 triệu", None, 5_000_000),
        ("office-5m-7m", "5 triệu - 7 triệu", 5_000_000, 7_000_000),
        ("office-7m-10m", "7 triệu - 10 triệu", 7_000_000, 10_000_000),
        ("office-10m-12m", "10 triệu - 12 triệu", 10_000_000, 12_000_000),
        ("office-12m-15m", "12 triệu - 15 triệu", 12_000_000, 15_000_000),
        ("office-15m-18m", "15 triệu - 18 triệu", 15_000_000, 18_000_000),
        ("office-over-18m", "Trên 18 triệu", 18_000_000, None),
    ],
    "pc-gaming": [
        ("gaming-under-10m", "Dưới 10 triệu", None, 10_000_000),
        ("gaming-10m-15m", "10 triệu - 15 triệu", 10_000_000, 15_000_000),
        ("gaming-15m-20m", "15 triệu - 20 triệu", 15_000_000, 20_000_000),
        ("gaming-20m-25m", "20 triệu - 25 triệu", 20_000_000, 25_000_000),
        ("gaming-25m-30m", "25 triệu - 30 triệu", 25_000_000, 30_000_000),
        ("gaming-30m-35m", "30 triệu - 35 triệu", 30_000_000, 35_000_000),
        ("gaming-35m-40m", "35 triệu - 40 triệu", 35_000_000, 40_000_000),
        ("gaming-40m-45m", "40 triệu - 45 triệu", 40_000_000, 45_000_000),
        ("gaming-45m-50m", "45 triệu - 50 triệu", 45_000_000, 50_000_000),
        ("gaming-50m-60m", "50 triệu - 60 triệu", 50_000_000, 60_000_000),
        ("gaming-over-60m", "Trên 60 triệu", 60_000_000, None),
    ],
    "cpu": [
        ("cpu-under-3m", "Dưới 3 triệu", None, 3_000_000),
        ("cpu-3m-7m", "3–7 triệu", 3_000_000, 7_000_000),
        ("cpu-over-7m", "Từ 7 triệu", 7_000_000, None),
    ],
    "mainboard": [
        ("board-under-2m", "Dưới 2 triệu", None, 2_000_000),
        ("board-2m-5m", "2–5 triệu", 2_000_000, 5_000_000),
        ("board-over-5m", "Từ 5 triệu", 5_000_000, None),
    ],
    "vga": [
        ("vga-under-5m", "Dưới 5 triệu", None, 5_000_000),
        ("vga-5m-15m", "5–15 triệu", 5_000_000, 15_000_000),
        ("vga-over-15m", "Từ 15 triệu", 15_000_000, None),
    ],
    "ram": [
        ("ram-under-1m", "Dưới 1 triệu", None, 1_000_000),
        ("ram-1m-3m", "1–3 triệu", 1_000_000, 3_000_000),
        ("ram-over-3m", "Từ 3 triệu", 3_000_000, None),
    ],
    "ssd": [
        ("ssd-under-1m", "Dưới 1 triệu", None, 1_000_000),
        ("ssd-1m-2m", "1–2 triệu", 1_000_000, 2_000_000),
        ("ssd-over-2m", "Từ 2 triệu", 2_000_000, None),
    ],
    "psu": [
        ("psu-under-1m", "Dưới 1 triệu", None, 1_000_000),
        ("psu-1m-2m5", "1–2,5 triệu", 1_000_000, 2_500_000),
        ("psu-over-2m5", "Từ 2,5 triệu", 2_500_000, None),
    ],
}

PRICE_RANGE_KIND_ALIASES = {
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


def _to_decimal(value):
    try:
        d = Decimal(str(value).strip())
        return d if d.is_finite() and d >= 0 else None
    except (InvalidOperation, ValueError, AttributeError):
        return None


def price_filter_error(params):
    raw_min = (params.get("min_price") or "").strip()
    raw_max = (params.get("max_price") or "").strip()
    min_price = _to_decimal(raw_min) if raw_min else None
    max_price = _to_decimal(raw_max) if raw_max else None
    if raw_min and min_price is None:
        return "Giá tối thiểu không hợp lệ; bộ lọc này sẽ được bỏ qua."
    if raw_max and max_price is None:
        return "Giá tối đa không hợp lệ; bộ lọc này sẽ được bỏ qua."
    if min_price is not None and max_price is not None and min_price > max_price:
        return "Giá từ phải nhỏ hơn hoặc bằng giá đến."
    return ""


def filter_products(qs, params):
    """params: dict-like (request.GET hoặc request.query_params)."""
    q = (params.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(specifications__icontains=q))

    category = (params.get("category") or "").strip()
    if category:
        qs = qs.filter(category__slug=category)

    kind = (params.get("kind") or "").strip()
    kind_filters = {
        "cpu": Q(specifications__has_key="Socket") & ~Q(specifications__has_key="Chipset"),
        "mainboard": Q(specifications__has_key="Chipset"),
        "mainboard-intel": Q(specifications__has_key="Chipset") & Q(specifications__icontains="LGA1700"),
        "mainboard-amd": Q(specifications__has_key="Chipset") & Q(specifications__icontains="AM5"),
        "psu": Q(specifications__has_key="Công suất"),
        "psu-80plus": Q(specifications__icontains="80 Plus"),
        "ram": (
            Q(specifications__has_key="Bus")
            | Q(name__icontains="RAM")
            | (Q(specifications__has_key="Dung lượng") & Q(specifications__has_key="Chuẩn"))
        ),
        "ram-ddr4": Q(specifications__has_key="Bus") & (Q(name__icontains="DDR4") | Q(specifications__icontains="DDR4")),
        "ram-ddr5": Q(specifications__has_key="Bus") & (Q(name__icontains="DDR5") | Q(specifications__icontains="DDR5")),
        "ssd": Q(name__icontains="SSD") | Q(name__icontains="NVMe") | (Q(specifications__has_key="Dung lượng") & ~Q(specifications__has_key="Bus")),
        "ssd-nvme": (Q(specifications__has_key="Dung lượng") & ~Q(specifications__has_key="Bus")) & (Q(name__icontains="NVMe") | Q(specifications__icontains="NVMe")),
        "ssd-sata": (Q(specifications__has_key="Dung lượng") & ~Q(specifications__has_key="Bus")) & (Q(name__icontains="SATA") | Q(specifications__icontains="SATA")),
        "vga": Q(specifications__has_key="GPU") | Q(specifications__has_key="VRAM"),
        "vga-nvidia": Q(name__icontains="GeForce") | Q(name__icontains="RTX"),
        "vga-amd": Q(name__icontains="Radeon") | Q(name__icontains="RX"),
        "mouse": Q(name__icontains="Chuột"),
        "keyboard": Q(name__icontains="Bàn phím"),
        "camera": Q(name__icontains="Webcam") | Q(name__icontains="Camera"),
        "headset": Q(name__icontains="Tai nghe"),
        "microphone": Q(name__icontains="Micro"),
    }
    if kind in kind_filters:
        qs = qs.filter(kind_filters[kind])
    elif kind in {"laptop-office", "laptop-gaming", "laptop-creator"}:
        qs = qs.filter(category__slug="laptop")
        if kind == "laptop-office":
            qs = qs.exclude(Q(name__icontains="Gaming") | Q(name__icontains="Creator"))
        else:
            keyword = {"laptop-gaming": "Gaming", "laptop-creator": "Creator"}[kind]
            qs = qs.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
    elif kind in {"office-pc", "mini-pc"}:
        qs = qs.filter(category__slug="pc-van-phong")
        if kind == "mini-pc":
            qs = qs.filter(Q(name__icontains="mini") | Q(description__icontains="mini"))
    elif kind in {"gaming-pc", "streaming-pc"}:
        qs = qs.filter(category__slug="pc-gaming")
        if kind == "streaming-pc":
            qs = qs.filter(Q(name__icontains="stream") | Q(description__icontains="stream"))
    elif kind in {"monitor-gaming", "monitor-office", "monitor-creator"}:
        qs = qs.filter(category__slug="man-hinh")
        keyword = {"monitor-gaming": "Gaming", "monitor-office": "Office", "monitor-creator": "đồ họa"}[kind]
        if kind == "monitor-gaming":
            qs = qs.filter(Q(name__icontains="Gaming") | Q(name__icontains="UltraGear") | Q(specifications__has_key="Tần số quét"))
        else:
            qs = qs.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword) | Q(specifications__icontains=keyword))

    brand = (params.get("brand") or "").strip()
    if brand:
        qs = qs.filter(brand__iexact=brand)

    min_price = _to_decimal(params.get("min_price", ""))
    max_price = _to_decimal(params.get("max_price", ""))
    if min_price is not None and max_price is not None and min_price > max_price:
        return qs.none()
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    price_range = (params.get("price_range") or "").strip()
    price_kind = PRICE_RANGE_KIND_ALIASES.get(kind, kind)
    if price_kind not in PRICE_RANGE_OPTIONS:
        price_kind = (params.get("category") or "").strip()
    range_options = PRICE_RANGE_OPTIONS.get(price_kind, PRICE_RANGE_OPTIONS["default"])
    price_ranges = {
        value: (minimum, maximum)
        for value, _label, minimum, maximum in range_options
    }
    if price_range in price_ranges:
        lower, upper = price_ranges[price_range]
        if lower is not None:
            qs = qs.filter(price__gte=lower)
        if upper is not None:
            qs = qs.filter(price__lt=upper)

    laptop_purpose = (params.get("laptop_purpose") or "").strip()
    if laptop_purpose:
        qs = qs.filter(category__slug="laptop")
        if laptop_purpose == "Văn phòng":
            qs = qs.exclude(
                Q(name__icontains="gaming") | Q(name__icontains="creator") | Q(name__icontains="proart")
            )
        elif laptop_purpose == "Gaming":
            qs = qs.filter(Q(name__icontains="gaming") | Q(description__icontains="gaming"))
        elif laptop_purpose == "Creator":
            qs = qs.filter(Q(name__icontains="creator") | Q(name__icontains="proart") | Q(name__icontains="studio"))

    style = (params.get("style") or "").strip()
    style_keywords = {
        "Gaming": ("gaming", "katana", "tuf"),
        "Mỏng nhẹ": ("slim", "vivobook", "ultrabook", "thin"),
        "Sáng tạo": ("creator", "proart", "studio"),
    }
    if style in style_keywords:
        style_match = Q(name__icontains=style_keywords[style][0])
        for keyword in style_keywords[style][1:]:
            style_match |= Q(name__icontains=keyword)
        qs = qs.filter(category__slug="laptop").filter(style_match)

    gpu_brand = (params.get("gpu_brand") or "").strip().casefold()
    gpu_brand_markers = {
        "nvidia": ("NVIDIA", "GeForce", "RTX"),
        "amd": ("AMD", "Radeon", "RX"),
        "intel": ("Intel Arc",),
    }
    if gpu_brand in gpu_brand_markers:
        gpu_match = Q()
        for marker in gpu_brand_markers[gpu_brand]:
            gpu_match |= Q(name__icontains=marker)
            for key in ("VGA", "GPU", "Đồ họa"):
                gpu_match |= Q(**{f"specifications__{key}__icontains": marker})
        qs = qs.filter(gpu_match)

    spec_filter_keys = {
        "cpu": ("CPU", "Socket"),
        "cpu_family": ("CPU",),
        "mainboard": ("Mainboard",),
        "mainboard_family": ("Mainboard", "Chipset"),
        "ram": ("RAM", "RAM hỗ trợ", "Chuẩn", "Bus"),
        "ram_family": ("RAM",),
        "storage": ("Ổ cứng", "Dung lượng", "Chuẩn", "Loại ổ cứng"),
        "storage_family": ("Ổ cứng", "Dung lượng", "Chuẩn", "Loại ổ cứng"),
        "display": ("Màn hình", "Kích thước", "Tấm nền"),
        "gpu": ("VGA", "GPU", "VRAM", "Đồ họa"),
        "gpu_family": ("VGA", "GPU", "Đồ họa"),
        "display_size": ("Kích thước màn hình", "Màn hình"),
        "purpose": ("Mục đích", "Sử dụng"),
        "resolution": ("Độ phân giải", "Màn hình"),
        "refresh": ("Tần số quét", "Màn hình"),
        "os": ("Hệ điều hành", "OS"),
        "socket": ("Socket",),
        "cpu_cores": ("Số nhân / luồng",),
        "cpu_clock": ("Xung nhịp", "Xung nhịp tối đa"),
        "tdp": ("TDP",),
        "chipset": ("Chipset",),
        "ram_type": ("RAM hỗ trợ", "Chuẩn RAM", "Chuẩn", "RAM"),
        "form_factor": ("Kích thước", "Form Factor"),
        "vram": ("VRAM",),
        "interface": ("Giao tiếp", "Bus bộ nhớ", "Chuẩn"),
        "capacity": ("Dung lượng", "VRAM"),
        "memory_bus": ("Bus",),
        "latency": ("Độ trễ",),
        "storage_type": ("Loại ổ cứng", "Giao tiếp", "Chuẩn"),
        "wattage": ("Công suất",),
        "efficiency": ("Hiệu suất",),
        "modular": ("Kiểu dây",),
    }
    for attribute, keys in spec_filter_keys.items():
        value = (params.get(attribute) or "").strip()
        if value:
            # A pipe-separated value means every token must match, allowing
            # grouped options such as "16GB|DDR5" to match RAM specs in any order.
            terms = [term.strip() for term in value.split("|") if term.strip()]
            matches = None
            for term in terms:
                term_match = Q(name__icontains=term)
                for key in keys:
                    term_match |= Q(**{f"specifications__{key}__icontains": term})
                matches = term_match if matches is None else matches & term_match
            if matches is not None:
                qs = qs.filter(matches)

    case_type = (params.get("case_type") or "").strip()
    case_type_markers = {
        "full-tower": ("full tower", "full-tower"),
        "mid-tower": ("mid tower", "mid-tower"),
        "mini-tower": ("mini tower", "mini-tower"),
        "mini-itx": ("mini-itx", "mini itx", "sff"),
        "micro-atx": ("micro-atx", "micro atx", "matx"),
        "atx": ("atx",),
    }
    if case_type in case_type_markers:
        case_match = Q()
        for marker in case_type_markers[case_type]:
            case_match |= Q(name__icontains=marker)
            for key in ("Loại case", "Vỏ case", "Case"):
                case_match |= Q(**{f"specifications__{key}__icontains": marker})
        if case_type == "atx":
            other_case_types = Q()
            for marker in (
                "full tower", "full-tower", "mid tower", "mid-tower",
                "mini tower", "mini-tower", "mini-itx", "mini itx",
                "micro-atx", "micro atx", "matx", "sff",
            ):
                other_case_types |= Q(name__icontains=marker)
                for key in ("Loại case", "Vỏ case", "Case"):
                    other_case_types |= Q(**{f"specifications__{key}__icontains": marker})
            case_match &= ~other_case_types
        qs = qs.filter(case_match)

    touch = (params.get("touch") or "").strip()
    if touch in {"yes", "no"}:
        has_touch = Q(**{"specifications__Màn hình__icontains": "cảm ứng"})
        qs = qs.filter(has_touch if touch == "yes" else ~has_touch)

    if params.get("in_stock") in ("1", "true", "on"):
        qs = qs.filter(stock__gt=0)

    return qs.order_by(*SORT_OPTIONS.get(params.get("sort"), SORT_OPTIONS["newest"]))

