from .models import Category


SUBCATEGORIES = {
    "linh-kien-pc": [
        ("CPU - Bộ vi xử lý", [("CPU Intel", "brand=Intel"), ("CPU AMD", "brand=AMD"), ("Xem toàn bộ CPU", "kind=cpu")]),
        ("Mainboard - Bo mạch chủ", [("Mainboard Intel", "kind=mainboard-intel"), ("Mainboard AMD", "kind=mainboard-amd"), ("Xem toàn bộ Mainboard", "kind=mainboard")]),
        ("VGA - Card màn hình", [("VGA NVIDIA", "kind=vga-nvidia"), ("VGA AMD", "kind=vga-amd"), ("Xem toàn bộ VGA", "kind=vga")]),
        ("RAM - Bộ nhớ trong", [("RAM DDR4", "kind=ram-ddr4"), ("RAM DDR5", "kind=ram-ddr5"), ("RAM theo hãng", "kind=ram")]),
        ("Ổ cứng SSD", [("SSD NVMe", "kind=ssd-nvme"), ("SSD SATA", "kind=ssd-sata"), ("SSD theo hãng", "kind=ssd")]),
        ("Nguồn máy tính", [("Nguồn theo công suất", "kind=psu"), ("Nguồn Corsair", "kind=psu&brand=Corsair"), ("Nguồn 80 Plus", "kind=psu-80plus")]),
    ],
    "laptop": [
        ("Theo nhu cầu", [("Laptop văn phòng", "kind=laptop-office"), ("Laptop gaming", "kind=laptop-gaming"), ("Laptop đồ họa", "kind=laptop-creator")]),
        ("Thương hiệu", [("Laptop ASUS", "brand=ASUS"), ("Laptop Lenovo", "brand=Lenovo"), ("Laptop MSI", "brand=MSI")]),
    ],
    "man-hinh": [
        ("Theo nhu cầu", [("Màn hình Gaming", "kind=monitor-gaming"), ("Màn hình văn phòng", "kind=monitor-office"), ("Màn hình đồ họa", "kind=monitor-creator")]),
        ("Thương hiệu", [("Màn hình LG", "brand=LG"), ("Màn hình Dell", "brand=Dell"), ("Màn hình ASUS", "brand=ASUS")]),
    ],
    "phu-kien-pc": [
        ("Thiết bị điều khiển", [("Chuột", "kind=mouse"), ("Bàn phím", "kind=keyboard")]),
        ("Âm thanh và hình ảnh", [("Camera / Webcam", "kind=camera"), ("Tai nghe", "kind=headset"), ("Micro", "kind=microphone")]),
    ],
}


def categories(request):
    preferred_order = {name: index for index, name in enumerate(("Laptop", "PC văn phòng", "PC gaming", "Màn hình", "Phụ kiện PC", "Linh kiện PC"))}
    categories = sorted(Category.objects.all(), key=lambda category: preferred_order.get(category.name, 99))
    store_menu = []
    for category in categories:
        groups = []
        for title, options in SUBCATEGORIES.get(category.slug, []):
            groups.append({
                "title": title,
                "links": [
                    {"label": label, "url": f"{category.get_absolute_url()}?{query}"}
                    for label, query in options
                ],
            })
        store_menu.append({"category": category, "groups": groups})
    return {"nav_categories": categories, "store_menu": store_menu}
