"""Tạo dữ liệu demo: python manage.py seed_data  (thêm --reset để xóa dữ liệu cũ)."""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from catalog.models import Category, Product, Review
from catalog.hacom_products import fill_seed_product_images, import_hacom_products
from orders.models import Order
from orders.services import OrderError, change_status, create_order

CATEGORIES = {
    "Linh kiện PC": "CPU, mainboard, nguồn, RAM, SSD và card đồ họa cho máy tính để bàn.",
    "Laptop": "Máy tính xách tay cho học tập, công việc và giải trí.",
    "PC văn phòng": "Máy tính bộ ổn định cho công việc và học tập.",
    "PC gaming": "Máy tính bộ hiệu năng cao dành cho chơi game.",
    "Màn hình": "Màn hình máy tính cho công việc, sáng tạo và giải trí.",
    "Phụ kiện PC": "Chuột, bàn phím, camera, tai nghe và micro.",
}

# (danh mục, tên, hãng, giá, tồn kho, thông số)
PRODUCTS = [
    ("Linh kiện PC", "AMD Ryzen 5 7600X", "AMD", 5490000, 25, {"Socket": "AM5", "Số nhân / luồng": "6 / 12", "Xung nhịp": "4.7 - 5.3 GHz", "TDP": "105W", "RAM hỗ trợ": "DDR5"}),
    ("Linh kiện PC", "AMD Ryzen 7 7800X3D", "AMD", 11990000, 8, {"Socket": "AM5", "Số nhân / luồng": "8 / 16", "Cache": "96MB 3D V-Cache", "TDP": "120W", "RAM hỗ trợ": "DDR5"}),
    ("Linh kiện PC", "Intel Core i5-13400F", "Intel", 5190000, 30, {"Socket": "LGA1700", "Số nhân / luồng": "10 / 16", "Xung nhịp": "2.5 - 4.6 GHz", "TDP": "65W", "RAM hỗ trợ": "DDR4 / DDR5"}),
    ("Linh kiện PC", "Intel Core i7-14700K", "Intel", 10990000, 12, {"Socket": "LGA1700", "Số nhân / luồng": "20 / 28", "Xung nhịp": "3.4 - 5.6 GHz", "TDP": "125W", "RAM hỗ trợ": "DDR4 / DDR5"}),
    ("Linh kiện PC", "NVIDIA GeForce RTX 4060 8GB", "ASUS", 8490000, 15, {"GPU": "RTX 4060", "VRAM": "8GB GDDR6", "Nguồn đề nghị": "550W", "Cổng nguồn": "1 x 8-pin"}),
    ("Linh kiện PC", "NVIDIA GeForce RTX 4070 Super 12GB", "MSI", 16990000, 6, {"GPU": "RTX 4070 Super", "VRAM": "12GB GDDR6X", "Nguồn đề nghị": "650W", "Cổng nguồn": "1 x 16-pin"}),
    ("Linh kiện PC", "AMD Radeon RX 7800 XT 16GB", "Gigabyte", 13490000, 0, {"GPU": "RX 7800 XT", "VRAM": "16GB GDDR6", "Nguồn đề nghị": "700W", "Cổng nguồn": "2 x 8-pin"}),
    ("Linh kiện PC", "Corsair Vengeance 16GB (2x8GB) DDR5 5600", "Corsair", 1990000, 40, {"Dung lượng": "16GB (2x8GB)", "Chuẩn": "DDR5", "Bus": "5600 MHz", "Latency": "CL36"}),
    ("Linh kiện PC", "Kingston Fury Beast 32GB (2x16GB) DDR4 3200", "Kingston", 2290000, 35, {"Dung lượng": "32GB (2x16GB)", "Chuẩn": "DDR4", "Bus": "3200 MHz", "Latency": "CL16"}),
    ("Linh kiện PC", "Samsung 980 Pro 1TB NVMe", "Samsung", 2990000, 20, {"Dung lượng": "1TB", "Chuẩn": "M.2 NVMe PCIe 4.0", "Đọc / Ghi": "7000 / 5000 MB/s"}),
    ("Linh kiện PC", "WD Blue SA510 500GB SATA", "Western Digital", 990000, 50, {"Dung lượng": "500GB", "Chuẩn": "SATA III 2.5\"", "Đọc / Ghi": "560 / 510 MB/s"}),
    ("Linh kiện PC", "ASUS TUF Gaming B650-PLUS WiFi", "ASUS", 5290000, 10, {"Socket": "AM5", "Chipset": "B650", "RAM hỗ trợ": "DDR5", "Kích thước": "ATX"}),
    ("Linh kiện PC", "MSI PRO B760M-A WiFi DDR4", "MSI", 3490000, 18, {"Socket": "LGA1700", "Chipset": "B760", "RAM hỗ trợ": "DDR4", "Kích thước": "mATX"}),
    ("Linh kiện PC", "Corsair RM750e 750W 80 Plus Gold", "Corsair", 2790000, 14, {"Công suất": "750W", "Chuẩn": "80 Plus Gold", "Modular": "Full modular"}),
    ("Linh kiện PC", "Cooler Master MWE 550W Bronze", "Cooler Master", 1290000, 3, {"Công suất": "550W", "Chuẩn": "80 Plus Bronze", "Modular": "Non-modular"}),
    ("Laptop", "Laptop ASUS Vivobook 15 OLED", "ASUS", 16990000, 12, {"CPU": "Intel Core i5", "RAM": "16GB", "Ổ cứng": "512GB SSD", "Màn hình": "15.6 inch OLED"}),
    ("Laptop", "Laptop Lenovo IdeaPad Slim 5", "Lenovo", 18990000, 9, {"CPU": "AMD Ryzen 7", "RAM": "16GB", "Ổ cứng": "512GB SSD", "Màn hình": "14 inch WUXGA"}),
    ("Laptop", "Laptop MSI Katana Gaming 15", "MSI", 24990000, 6, {"CPU": "Intel Core i7", "RAM": "16GB", "VGA": "GeForce RTX 4060", "Màn hình": "15.6 inch 144Hz"}),
    ("Laptop", "Laptop ASUS ProArt Creator 16", "ASUS", 42990000, 4, {"CPU": "Intel Core Ultra 9", "RAM": "32GB", "VGA": "GeForce RTX Studio", "Màn hình": "16 inch OLED"}),
    ("PC văn phòng", "PC văn phòng Core i3 12100", "PCShop", 8990000, 10, {"CPU": "Intel Core i3-12100", "RAM": "16GB DDR4", "Ổ cứng": "512GB NVMe", "Đồ họa": "Intel UHD Graphics"}),
    ("PC văn phòng", "Mini PC văn phòng Intel N100", "PCShop", 4990000, 8, {"CPU": "Intel N100", "RAM": "16GB", "Ổ cứng": "512GB SSD", "Kích thước": "Mini PC"}),
    ("PC gaming", "PC Gaming Ryzen 5 RTX 4060", "PCShop", 22990000, 7, {"CPU": "AMD Ryzen 5 7500F", "RAM": "32GB DDR5", "VGA": "GeForce RTX 4060 8GB", "Nguồn": "650W"}),
    ("PC gaming", "PC Streaming Ryzen 7 RTX 4070", "PCShop", 36990000, 3, {"CPU": "AMD Ryzen 7 7800X3D", "RAM": "32GB DDR5", "VGA": "GeForce RTX 4070 Super", "Mục đích": "Gaming và streaming"}),
    ("Màn hình", "Màn hình LG UltraGear 24 inch 180Hz", "LG", 3490000, 14, {"Kích thước": "24 inch", "Độ phân giải": "Full HD", "Tần số quét": "180Hz", "Tấm nền": "IPS"}),
    ("Màn hình", "Màn hình Dell Office 24 inch IPS", "Dell", 3290000, 10, {"Kích thước": "24 inch", "Độ phân giải": "Full HD", "Tấm nền": "IPS", "Sử dụng": "Văn phòng"}),
    ("Màn hình", "Màn hình đồ họa ASUS ProArt 27 inch", "ASUS", 8990000, 5, {"Kích thước": "27 inch", "Độ phân giải": "2K", "Tấm nền": "IPS", "Sử dụng": "Đồ họa"}),
    ("Phụ kiện PC", "Chuột Logitech G102 Lightsync", "Logitech", 399000, 25, {"Kết nối": "USB", "DPI": "8000", "Đèn": "RGB"}),
    ("Phụ kiện PC", "Bàn phím cơ DareU EK87", "DareU", 699000, 18, {"Kiểu": "Tenkeyless", "Kết nối": "USB", "Switch": "Blue"}),
    ("Phụ kiện PC", "Webcam Logitech C270", "Logitech", 590000, 11, {"Độ phân giải": "720p", "Micro": "Tích hợp", "Kết nối": "USB-A"}),
    ("Phụ kiện PC", "Tai nghe HyperX Cloud Stinger 2", "HyperX", 1290000, 8, {"Kết nối": "3.5mm", "Âm thanh": "Stereo", "Micro": "Xoay gập"}),
    ("Phụ kiện PC", "Micro Fifine K669B", "Fifine", 990000, 6, {"Kiểu": "USB condenser", "Hướng thu": "Cardioid", "Điều khiển": "Volume trên thân mic"}),
]


class Command(BaseCommand):
    help = "Tạo dữ liệu demo (danh mục, sản phẩm, tài khoản, đơn hàng mẫu)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Xóa đơn hàng, sản phẩm, danh mục demo trước khi tạo")

    @transaction.atomic
    def handle(self, *args, **opts):
        User = get_user_model()
        if opts["reset"]:
            Order.objects.all().delete()
            Review.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

        cats = {}
        for name, desc in CATEGORIES.items():
            cats[name], _ = Category.objects.get_or_create(name=name, defaults={"description": desc})

        for cat, name, brand, price, stock, specs in PRODUCTS:
            Product.objects.update_or_create(
                name=name,
                defaults={"category": cats[cat], "brand": brand, "price": price, "stock": stock, "specifications": specs,
                          "description": f"{name} chính hãng, bảo hành 36 tháng."},
            )

        import_hacom_products()
        fill_seed_product_images()

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@pcshop.local", "admin123", full_name="Quản trị viên")
        customer = User.objects.filter(username="khach").first()
        if customer is None:
            customer = User.objects.create_user(
                "khach", "khach@pcshop.local", "khach123",
                full_name="Nguyễn Văn Khách", phone="0912345678", address="12 Lê Lợi, Hà Nội",
            )

        if not Order.objects.exists():
            self._demo_orders(customer)

        self.stdout.write(self.style.SUCCESS(
            "Seed xong. Tài khoản: admin / admin123 (quản trị) • khach / khach123 (khách hàng)"
        ))

    def _demo_orders(self, customer):
        rng = random.Random(42)
        in_stock = list(Product.objects.filter(stock__gte=5, is_active=True))
        now = timezone.now()
        for i in range(12):
            chosen = rng.sample(in_stock, k=rng.randint(1, 3))
            items = {p.pk: rng.randint(1, 2) for p in chosen}
            try:
                order = create_order(
                    customer, items, full_name=customer.full_name, phone=customer.phone,
                    shipping_address=customer.address, payment_method=rng.choice(["cod", "bank"]),
                )
            except OrderError:
                continue  # hết hàng demo → bỏ qua đơn này
            # i < 9: hoàn thành, 9: đang giao, 10: đang xử lý, 11: chờ xác nhận
            flow = ["processing", "shipping", "completed"]
            steps = 3 if i < 9 else {9: 2, 10: 1, 11: 0}[i]
            for s in flow[:steps]:
                change_status(order, s)
            Order.objects.filter(pk=order.pk).update(created_at=now - timedelta(days=rng.randint(0, 25)))
            if i < 9:
                for item in order.items.all():
                    Review.objects.get_or_create(
                        product=item.product, user=customer,
                        defaults={"rating": rng.randint(4, 5), "comment": "Hàng chính hãng, giao nhanh."},
                    )
