"""Curated product snapshot from public HACOM listings (18/10/2026).

The image URLs point to HACOM's public image CDN. ``stock`` values are local
PCShop demo inventory, not a claim about HACOM branch stock.
"""
from catalog.models import Category, Product

CATEGORY_DESCRIPTIONS = {
    "Linh kiện PC": "CPU, mainboard, nguồn, RAM, SSD và card đồ họa cho máy tính để bàn.",
    "Laptop": "Máy tính xách tay cho học tập, công việc và giải trí.",
    "PC văn phòng": "Máy tính bộ ổn định cho công việc và học tập.",
    "PC gaming": "Máy tính bộ hiệu năng cao dành cho chơi game.",
    "Màn hình": "Màn hình máy tính cho công việc, sáng tạo và giải trí.",
    "Phụ kiện PC": "Chuột, bàn phím, camera, tai nghe và micro.",
}

# Giá bán lẻ và thông số lấy từ trang sản phẩm HACOM; ảnh trỏ tới CDN HACOM.
HACOM_PRODUCTS = [
    {
        "category": "Laptop",
        "name": "Laptop Acer Aspire Go AG15-72P-54GY",
        "brand": "Acer",
        "price": 19_999_000,
        "stock": 8,
        "specifications": {
            "CPU": "Intel Core 5 120U",
            "RAM": "16GB DDR4",
            "Ổ cứng": "512GB SSD NVMe",
            "Màn hình": "15.6 inch Full HD IPS 60Hz",
            "Hệ điều hành": "Windows 11 Home",
            "Nguồn tham khảo": "https://hacom.vn/laptop-acer-aspire-go-ag15-72p-54gy-ltac1001",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/30102025/laptop-acer-aspire-go-ag15-72p-54gy-ltac1001_0005_ace1.jpg",
    },
    {
        "category": "Laptop",
        "name": "Laptop Asus VivoBook S3407QA-SF043W",
        "brand": "ASUS",
        "price": 21_490_000,
        "stock": 6,
        "specifications": {
            "CPU": "Qualcomm Snapdragon X1-26-100",
            "RAM": "16GB LPDDR5X",
            "Ổ cứng": "512GB SSD",
            "Màn hình": "14 inch OLED",
            "Hệ điều hành": "Windows 11",
            "Nguồn tham khảo": "https://hacom.vn/laptop-asus-vivobook-s3407qa-sf043w-ltau1098",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/21072026/Laptop-Asus-VivoBook-S3407QA-SF043W-X1-26-100-16GB-RAM-D5X-512GB-SSD-14-OLED-W6E-BT-Win11SL-Xam33.jpg",
    },
    {
        "category": "Laptop",
        "name": "Laptop Lenovo Yoga Slim 7 14ILL10 OLED 83QM002FVN",
        "brand": "Lenovo",
        "price": 52_699_000,
        "stock": 4,
        "specifications": {
            "CPU": "Intel Core Ultra 7 355",
            "RAM": "32GB LPDDR5X",
            "Ổ cứng": "1TB SSD PCIe Gen 4",
            "Màn hình": "14 inch WUXGA OLED cảm ứng",
            "Hệ điều hành": "Windows 11 + Office",
            "Nguồn tham khảo": "https://hacom.vn/laptop-lenovo-yoga-slim-7-14ill10-oled-83qm002fvn-ltlv0362",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/27052026/Laptop-Lenovo-Yoga-Slim-7-14ILL10-Oled-83QM002FVN-U7-35532GB-RAM1TB-SSD14-WUXGA-OledWin11OfficeXam3Y-1.jpg",
    },
    {
        "category": "PC văn phòng",
        "name": "PC Acer Veriton VX2710G FR180W12V",
        "brand": "Acer",
        "price": 18_899_000,
        "stock": 5,
        "specifications": {
            "CPU": "Intel Core i5-14400",
            "Mainboard": "Intel H610",
            "RAM": "16GB DDR4",
            "Ổ cứng": "512GB SSD NVMe",
            "Đồ họa": "Intel Graphics tích hợp",
            "Hệ điều hành": "Chưa cài sẵn",
            "Nguồn tham khảo": "https://hacom.vn/pc-acer-veriton-vx2710g-fr180w12v-pcac0135",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/26032026/pc-acer-veriton-vx2710g-fr180w12v-pcac0135-2.jpg",
    },
    {
        "category": "PC văn phòng",
        "name": "PC HACOM ECONOMY 080 Ryzen 5 5500GT",
        "brand": "HACOM",
        "price": 8_399_000,
        "stock": 9,
        "specifications": {
            "CPU": "AMD Ryzen 5 5500GT",
            "Mainboard": "A520",
            "RAM": "8GB DDR4 3200MHz",
            "Ổ cứng": "256GB SSD SATA",
            "Đồ họa": "AMD Radeon tích hợp",
            "Nguồn": "350W",
            "Nguồn tham khảo": "https://hacom.vn/pc-hacom-economy-080-pcvp0720",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/13052026/080.jpg",
    },
    {
        "category": "PC gaming",
        "name": "PC Gaming 5060 i5-14400F RTX 5060",
        "brand": "HACOM",
        "price": 26_499_000,
        "stock": 3,
        "specifications": {
            "CPU": "Intel Core i5-14400F",
            "Mainboard": "B760",
            "RAM": "16GB",
            "Ổ cứng": "512GB SSD",
            "VGA": "NVIDIA GeForce RTX 5060 8GB",
            "Nguồn": "650W",
            "Nguồn tham khảo": "https://hacom.vn/pc-hacom-gold-pro-088-pcgm1176",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/18092026/PCGM1176.jpg",
    },
    {
        "category": "Màn hình",
        "name": "Màn hình AOC 27B36X 27 inch FHD IPS 144Hz",
        "brand": "AOC",
        "price": 2_490_000,
        "stock": 10,
        "specifications": {
            "Kích thước": "27 inch",
            "Độ phân giải": "Full HD 1920 x 1080",
            "Tấm nền": "IPS",
            "Tần số quét": "144Hz",
            "Thời gian phản hồi": "0.5ms",
            "Cổng kết nối": "HDMI, DisplayPort, Audio 3.5mm",
            "Nguồn tham khảo": "https://hacom.vn/man-hinh-aoc-27b36x",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/man-hinh-aoc-27b36x-3.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "AMD Ryzen 5 7500F",
        "brand": "AMD",
        "price": 4_199_000,
        "stock": 12,
        "specifications": {
            "Socket": "AM5",
            "Số nhân / luồng": "6 / 12",
            "Xung nhịp": "3.7 - 5.0 GHz",
            "TDP": "65W",
            "RAM hỗ trợ": "DDR5",
            "Nguồn tham khảo": "https://hacom.vn/cpu-amd-ryzen-5-7500f-cpua0313",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/CPU-AMD-Ryzen-5-7500F.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Mainboard ASUS TUF GAMING B650M-E WIFI DDR5",
        "brand": "ASUS",
        "price": 3_899_000,
        "stock": 7,
        "specifications": {
            "Socket": "AMD AM5",
            "Chipset": "B650",
            "RAM hỗ trợ": "DDR5",
            "Kết nối": "Wi-Fi 6, Ethernet 2.5G",
            "Kích thước": "micro-ATX",
            "Nguồn tham khảo": "https://hacom.vn/mainboard-asus-tuf-gaming-b650m-e-wifi-ddr5",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/85669_mainboard_asus_tuf_gaming_b650m_e_wifi_ddr5__2_.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Card màn hình ASUS DUAL RTX 5060 8GB OC GDDR7",
        "brand": "ASUS",
        "price": 13_799_000,
        "stock": 4,
        "specifications": {
            "GPU": "NVIDIA GeForce RTX 5060",
            "VRAM": "8GB GDDR7",
            "Bus bộ nhớ": "128-bit",
            "Giao tiếp": "PCI Express 5.0",
            "Nguồn đề nghị": "550W",
            "Nguồn tham khảo": "https://hacom.vn/card-man-hinh-asus-dual-rtx-5060-8g-oc-gddr7-dual-rtx5060-o8g",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/91266_card_man_hinh_asus_dual_rtx_5060_8g_oc_gddr7_dual_rtx5060_o8g.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "RAM Kingston Fury Beast Black EXPO 16GB DDR5 6000MHz",
        "brand": "Kingston",
        "price": 6_890_000,
        "stock": 9,
        "specifications": {
            "Dung lượng": "16GB (1 x 16GB)",
            "Chuẩn": "DDR5",
            "Bus": "6000MHz",
            "Độ trễ": "CL36",
            "Tương thích": "AMD EXPO",
            "Nguồn tham khảo": "https://hacom.vn/ram-kingston-fury-beast-black-expo-16gb-ddr5-6000mhz-kf560c36bbe2-16",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/90732_ram_desktop_kingston_fury_beast_black_expo_kf560c36bbe2_16_16gb_1x16gb_ddr5_6000mhz__1_.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Nguồn Jetek MAXWATT MW650 V2 650W",
        "brand": "Jetek",
        "price": 799_000,
        "stock": 11,
        "specifications": {
            "Công suất": "650W",
            "Hiệu suất": "80 Plus",
            "Quạt làm mát": "120mm",
            "Bảo vệ": "OVP, UVP, SCP",
            "Nguồn tham khảo": "https://hacom.vn/nguon-jetek-model-maxwatt-mw650-v2",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/86860_nguon_jetek_model_maxwatt_mw650_v2__6_.jpg",
    },
    {
        "category": "Phụ kiện PC",
        "name": "Bàn phím cơ gaming EDRA EK375v2 Alpha Linear",
        "brand": "EDRA",
        "price": 399_000,
        "stock": 14,
        "specifications": {
            "Layout": "75%, 82 phím",
            "Switch": "EDRA Linear Custom",
            "Keycap": "PBT Doubleshot",
            "Kết nối": "USB-C to USB-A có dây",
            "Đèn nền": "Rainbow",
            "Nguồn tham khảo": "https://hacom.vn/ban-phim-co-gaming-edra-ek375v2-alpha-linear-switch",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/88811_ban_phim_co_gaming_edra_ek375v2_alpha_linear_switch.jpg",
    },
    {
        "category": "Phụ kiện PC",
        "name": "Chuột không dây Logitech G304 Lightspeed",
        "brand": "Logitech",
        "price": 719_000,
        "stock": 16,
        "specifications": {
            "Kết nối": "Wireless 2.4GHz qua USB receiver",
            "Cảm biến": "HERO",
            "DPI tối đa": "12.000",
            "Thời lượng pin": "Tối đa 250 giờ",
            "Nguồn tham khảo": "https://hacom.vn/chuot-game-khong-day-logitech-g304-den-usb",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/47117_mouse_logitech_g304_light_speed_wireless_gaming_0001_1.jpg",
    },
    {
        "category": "Laptop",
        "name": "Laptop Lenovo IdeaPad Slim 5 14IRH10R 83J0006EVN",
        "brand": "Lenovo",
        "price": 19_999_000,
        "stock": 5,
        "specifications": {
            "CPU": "Intel Core 5 210H",
            "RAM": "16GB",
            "Ổ cứng": "512GB SSD",
            "Màn hình": "14 inch WUXGA OLED",
            "Hệ điều hành": "Windows 11",
            "Nguồn tham khảo": "https://hacom.vn/laptop-lenovo-ideapad-slim-5-14irh10r-83j0006evn-ltlv0279",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/19102025/laptop-lenovo-ideapad-slim-5-14irh10r-83j0006evn-ltlv0279_0009_83J0006EVN-1.jpg",
    },
    {
        "category": "Laptop",
        "name": "Laptop MSI Gaming Katana 15 B13VFK-676VN",
        "brand": "MSI",
        "price": 29_999_000,
        "stock": 3,
        "specifications": {
            "CPU": "Intel Core i7-13620H",
            "RAM": "16GB DDR5",
            "Ổ cứng": "1TB SSD PCIe Gen 4",
            "VGA": "NVIDIA GeForce RTX 4060 8GB",
            "Màn hình": "15.6 inch Full HD 144Hz",
            "Nguồn tham khảo": "https://hacom.vn/laptop-msi-katana-15-b13vfk-676vn-i7-13620h-rtx-4060-8gb-144hz-chinh-hang",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/70977_laptop_msi_gaming_katana_15_b13_6.png",
    },
    {
        "category": "Laptop",
        "name": "Laptop ASUS ProArt P16 H7606WP-SR335W",
        "brand": "ASUS",
        "price": 119_999_000,
        "stock": 2,
        "specifications": {
            "CPU": "AMD Ryzen AI 9 HX 370",
            "RAM": "64GB LPDDR5X",
            "Ổ cứng": "2TB SSD PCIe 4.0",
            "VGA": "NVIDIA GeForce RTX 5070 8GB",
            "Màn hình": "16 inch 3K OLED cảm ứng",
            "Hệ điều hành": "Windows 11 Home",
            "Nguồn tham khảo": "https://hacom.vn/laptop-asus-proart-p16-h7606wp-sr335w-ltau1132",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/23072026/Laptop-ASUS-ProArt-P16-H7606WP-SR335W-Ryzen-AI-9-HX-37064GB-D5X2TB-SSDRTX5070-8GB-D716-3KOLED-TW11HDen-7.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "AMD Ryzen 5 7600X",
        "brand": "AMD",
        "price": 6_199_000,
        "stock": 7,
        "specifications": {
            "Socket": "AM5",
            "Số nhân / luồng": "6 / 12",
            "Xung nhịp": "4.7 - 5.3 GHz",
            "TDP": "105W",
            "RAM hỗ trợ": "DDR5",
            "Nguồn tham khảo": "https://hacom.vn/cpu-amd-ryzen-5-7600x-4.7-ghz-upto-5.3ghz-38mb-6-cores-12-threads-105w-socket-am5",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/67743_cpu_amd_ryzen_5_7600x_4_7_ghz_upto_5_3ghz_38mb_6_cores_12_threads_105w_socket_am5_fix.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "AMD Ryzen 7 7800X3D",
        "brand": "AMD",
        "price": 9_999_000,
        "stock": 4,
        "specifications": {
            "Socket": "AM5",
            "Số nhân / luồng": "8 / 16",
            "Xung nhịp": "4.2 - 5.0 GHz",
            "Cache": "96MB 3D V-Cache",
            "TDP": "120W",
            "RAM hỗ trợ": "DDR5",
            "Nguồn tham khảo": "https://hacom.vn/cpu-amd-ryzen-7-7800x3d",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/71574_cpu_amd_ryzen_7_7800x3d_4_2ghz_up_to_5_0ghz_105mb_8_cores_16_threads_120w_socket_am5.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Intel Core i7-14700K",
        "brand": "Intel",
        "price": 11_499_000,
        "stock": 3,
        "specifications": {
            "Socket": "LGA1700",
            "Số nhân / luồng": "20 / 28",
            "Xung nhịp tối đa": "5.6 GHz",
            "Cache": "33MB",
            "TDP": "125W",
            "RAM hỗ trợ": "DDR4 / DDR5",
            "Nguồn tham khảo": "https://hacom.vn/cpu-intel-core-i7-14700k",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/77008_cpu_intel_core_i7_14700k.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Mainboard ASUS TUF GAMING B650-PLUS WIFI",
        "brand": "ASUS",
        "price": 5_999_000,
        "stock": 5,
        "specifications": {
            "Socket": "AMD AM5",
            "Chipset": "B650",
            "RAM hỗ trợ": "DDR5, tối đa 128GB",
            "Kích thước": "ATX",
            "Kết nối": "Wi-Fi 6, LAN 2.5Gb",
            "Nguồn tham khảo": "https://hacom.vn/mainboard-asus-tuf-gaming-b650-plus-wifi",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/media/lib/18-10-2022/tuf-gaming-alliance1.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Mainboard MSI PRO B760M-A WIFI DDR4",
        "brand": "MSI",
        "price": 3_599_000,
        "stock": 6,
        "specifications": {
            "Socket": "Intel LGA1700",
            "Chipset": "B760",
            "RAM hỗ trợ": "DDR4, tối đa 128GB",
            "Kích thước": "micro-ATX",
            "Kết nối": "Wi-Fi 6E, LAN 2.5Gb",
            "Nguồn tham khảo": "https://hacom.vn/mainboard-msi-pro-b760m-a-wifi-ddr4",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/69774_mainboard_msi_pro_b760m_a_wifi_ddr4__4_.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Card màn hình ASUS ProArt RTX 4070 SUPER 12GB",
        "brand": "ASUS",
        "price": 22_499_000,
        "stock": 2,
        "specifications": {
            "GPU": "NVIDIA GeForce RTX 4070 SUPER",
            "VRAM": "12GB GDDR6X",
            "Bus bộ nhớ": "192-bit",
            "Giao tiếp": "PCI Express 4.0",
            "Nguồn đề nghị": "750W",
            "Nguồn tham khảo": "https://hacom.vn/card-man-hinh-asus-proart-rtx-4070-super-o12g",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/79236__card_man_hinh_asus_proart_rtx_4070_super_o12g__3_.jpg",
    },
    {
        "category": "Linh kiện PC",
        "name": "Nguồn Corsair RM750e ATX 3.1 750W 80 Plus Gold",
        "brand": "Corsair",
        "price": 2_749_000,
        "stock": 5,
        "specifications": {
            "Công suất": "750W",
            "Hiệu suất": "80 Plus Gold",
            "Chuẩn": "ATX 3.1, PCIe 5.0",
            "Kiểu dây": "Full modular",
            "Nguồn tham khảo": "https://hacom.vn/nguon-may-tinh-corsair-rm750e-atx-3.1-80-plus-gold-mau-den",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/89688_corsair_rm750e_009.jpg",
    },
    {
        "category": "PC văn phòng",
        "name": "PC Mini ZOTAC ZBOX-CI337 Nano Intel N100",
        "brand": "ZOTAC",
        "price": 5_599_000,
        "stock": 4,
        "specifications": {
            "CPU": "Intel Processor N100",
            "RAM": "8GB DDR5",
            "Ổ cứng": "256GB SSD",
            "Đồ họa": "Intel UHD Graphics tích hợp",
            "Kết nối": "Wi-Fi 6, Bluetooth 5.2, LAN",
            "Nguồn tham khảo": "https://hacom.vn/pc-mini-zotac-zbox-ci337-nano-be1-n100-wifi-bt-8gb-ddr5-5600-ssd-256gb-den",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/89895_pc_mini_zotac_zbox_ci337_nano_be1_1.jpg",
    },
    {
        "category": "Phụ kiện PC",
        "name": "Webcam Logitech HD C270 720p",
        "brand": "Logitech",
        "price": 399_000,
        "stock": 8,
        "specifications": {
            "Độ phân giải": "HD 720p, 30fps",
            "Micro": "Tích hợp giảm nhiễu",
            "Kết nối": "USB-A",
            "Nguồn tham khảo": "https://hacom.vn/webcam-logitech-hd-270",
        },
        "image_url": "https://hanoicomputercdn.com/media/product/17151_webcam_logitech_hd_c270.jpg",
    },
    {
        "category": "Phụ kiện PC",
        "name": "Bàn phím cơ Gaming DareU EK87 Pro Black Golden",
        "brand": "DareU",
        "price": 999_000,
        "stock": 7,
        "specifications": {
            "Layout": "Tenkeyless 87 phím",
            "Switch": "DareU Cloud Linear, hot-swap 5 pin",
            "Kết nối": "USB, Bluetooth, Wireless 2.4GHz",
            "Đèn nền": "RGB",
            "Nguồn tham khảo": "https://hacom.vn/ban-phim-co-gaming-dareu-ek87-pro-black-golden-cloud-switch",
        },
        "image_url": "https://cdn-files.hacom.vn/hacom/cdn/web/media/lib/11-03-2025/ban-phim-co-gaming-dareu-ek87-pro.jpg",
    },
]


# Ảnh HACOM dùng minh họa cho các sản phẩm demo đã có trong seed_data.py.
# Một số tên là dữ liệu mẫu tổng quát, vì vậy trang chi tiết vẫn giữ nguyên
# thông số demo và các URL ảnh trỏ đến mặt hàng cùng nhóm trên HACOM.
SEED_PRODUCT_IMAGES = {
    "Laptop ASUS ProArt Creator 16": (
        "https://cdn-files.hacom.vn/hacom/cdn/web/23072026/Laptop-ASUS-ProArt-P16-H7606WP-SR335W-Ryzen-AI-9-HX-37064GB-D5X2TB-SSDRTX5070-8GB-D716-3KOLED-TW11HDen-7.jpg",
        "https://hacom.vn/laptop-asus-proart-p16-h7606wp-sr335w-ltau1132",
    ),
    "Laptop ASUS Vivobook 15 OLED": (
        "https://cdn-files.hacom.vn/hacom/cdn/web/21072026/Laptop-Asus-VivoBook-S3407QA-SF043W-X1-26-100-16GB-RAM-D5X-512GB-SSD-14-OLED-W6E-BT-Win11SL-Xam33.jpg",
        "https://hacom.vn/laptop-asus-vivobook-s3407qa-sf043w-ltau1098",
    ),
    "Laptop Lenovo IdeaPad Slim 5": (
        "https://cdn-files.hacom.vn/hacom/cdn/web/19102025/laptop-lenovo-ideapad-slim-5-14irh10r-83j0006evn-ltlv0279_0009_83J0006EVN-1.jpg",
        "https://hacom.vn/laptop-lenovo-ideapad-slim-5-14irh10r-83j0006evn-ltlv0279",
    ),
    "Laptop MSI Katana Gaming 15": (
        "https://hanoicomputercdn.com/media/product/70977_laptop_msi_gaming_katana_15_b13_6.png",
        "https://hacom.vn/laptop-msi-katana-15-b13vfk-676vn-i7-13620h-rtx-4060-8gb-144hz-chinh-hang",
    ),
    "AMD Ryzen 5 7600X": (
        "https://hanoicomputercdn.com/media/product/67743_cpu_amd_ryzen_5_7600x_4_7_ghz_upto_5_3ghz_38mb_6_cores_12_threads_105w_socket_am5_fix.jpg",
        "https://hacom.vn/cpu-amd-ryzen-5-7600x-4.7-ghz-upto-5.3ghz-38mb-6-cores-12-threads-105w-socket-am5",
    ),
    "AMD Ryzen 7 7800X3D": (
        "https://hanoicomputercdn.com/media/product/71574_cpu_amd_ryzen_7_7800x3d_4_2ghz_up_to_5_0ghz_105mb_8_cores_16_threads_120w_socket_am5.jpg",
        "https://hacom.vn/cpu-amd-ryzen-7-7800x3d",
    ),
    "Intel Core i5-13400F": (
        "https://hanoicomputercdn.com/media/product/75624_69895_cpu_intel_core_i5_13400f_up_to_4_6ghz_10_nhan_16_luong_20mb_cache_65w_socket_intel_lga_1700_raptor_lake.jpg",
        "https://hacom.vn/cpu-intel-core-i5-13400f-up-to-4.6ghz-10-nhan-16-luong-20mb-cache-65w-socket-intel-lga-1700-raptor-lake-hang-nk",
    ),
    "Intel Core i7-14700K": (
        "https://hanoicomputercdn.com/media/product/77008_cpu_intel_core_i7_14700k.jpg",
        "https://hacom.vn/cpu-intel-core-i7-14700k",
    ),
    "NVIDIA GeForce RTX 4060 8GB": (
        "https://hanoicomputercdn.com/media/product/73447_card_man_hinh_msi_rtx_4060_ventus_2x_black_8g_oc__5_.jpg",
        "https://hacom.vn/card-man-hinh-msi-rtx-4060-ventus-2x-black-8g-oc",
    ),
    "NVIDIA GeForce RTX 4070 Super 12GB": (
        "https://hanoicomputercdn.com/media/product/79236__card_man_hinh_asus_proart_rtx_4070_super_o12g__3_.jpg",
        "https://hacom.vn/card-man-hinh-asus-proart-rtx-4070-super-o12g",
    ),
    "AMD Radeon RX 7800 XT 16GB": (
        "https://hanoicomputercdn.com/media/product/83997_card_man_hinh_sapphire_pure_rx_7800_xt_gaming_oc_16gbx__2_.jpg",
        "https://hacom.vn/card-man-hinh-sapphire-pure-rx-7800-xt-gaming-oc-16gb",
    ),
    "Corsair Vengeance 16GB (2x8GB) DDR5 5600": (
        "https://cdn-files.hacom.vn/hacom/cdn/web/04032026/ram-desktop-corsair-vengeance-rgb-grey-raco0426-2.jpg",
        "https://hacom.vn/ram-desktop-corsair-vengeance-rgb-grey-raco0426",
    ),
    "Kingston Fury Beast 32GB (2x16GB) DDR4 3200": (
        "https://hanoicomputercdn.com/media/product/78437_ram_desktop_kingston_fury_beast_rgb_kf436c18bb2ak2_32_32gb_2x16gb_ddr4_3600mhzxx__.jpg",
        "https://hacom.vn/ram-kingston-fury-beast-rgb-32gb-ddr4-3200mhz-kf432c16bb12ak2-32-kf432c16bb2ak2-32",
    ),
    "Samsung 980 Pro 1TB NVMe": (
        "https://hanoicomputercdn.com/media/product/69429_o_cung_ssd_samsung_990_pro_1tb_pcie_nvme_4__3_.jpg",
        "https://hacom.vn/o-cung-ssd-samsung-990-pro-1tb-m.2-2280-pcie-gen4-x4",
    ),
    "WD Blue SA510 500GB SATA": (
        "https://hanoicomputercdn.com/media/product/66719_o_cung_ssd_wd_blue_500gb_sata_2__2_.jpg",
        "https://hacom.vn/o-cung-ssd-wd-blue-500gb-2.5-inch-sata-iii",
    ),
    "ASUS TUF Gaming B650-PLUS WiFi": (
        "https://hanoicomputercdn.com/media/product/68301_mainboard_asus_tuf_gaming_b650_plus_wifi__2_.jpg",
        "https://hacom.vn/mainboard-asus-tuf-gaming-b650-plus-wifi",
    ),
    "MSI PRO B760M-A WiFi DDR4": (
        "https://hanoicomputercdn.com/media/product/69774_mainboard_msi_pro_b760m_a_wifi_ddr4__4_.jpg",
        "https://hacom.vn/mainboard-msi-pro-b760m-a-wifi-ddr4",
    ),
    "Corsair RM750e 750W 80 Plus Gold": (
        "https://hanoicomputercdn.com/media/product/89688_corsair_rm750e_009.jpg",
        "https://hacom.vn/nguon-may-tinh-corsair-rm750e-atx-3.1-80-plus-gold-mau-den",
    ),
    "Cooler Master MWE 550W Bronze": (
        "https://hanoicomputercdn.com/media/product/55755__cooler_master_mwe_v2_230v_550_550w_plus_bronze_0005_1__4_.jpg",
        "https://hacom.vn/nguon-may-tinh-cooler-master-mwe-v2-230v-550-550w-plus-bronze-80-plus-bronze-den",
    ),
    "Màn hình LG UltraGear 24 inch 180Hz": (
        "https://hanoicomputercdn.com/media/product/86761_man_hinh_lg_ultragear_24gs65f_b_1.jpg",
        "https://hacom.vn/man-hinh-lg-ultragear-24gs65f-b",
    ),
    "Màn hình Dell Office 24 inch IPS": (
        "https://hanoicomputercdn.com/media/product/65390_m__n_dell_p2423de_850x850_1.jpg",
        "https://hacom.vn/man-hinh-dell-p2423de",
    ),
    "Màn hình đồ họa ASUS ProArt 27 inch": (
        "https://hanoicomputercdn.com/media/product/66530_man_hinh_pro_art_pa279cv_850x850_a.jpg",
        "https://hacom.vn/man-hinh-asus-pro-art-pa279cv-27-inch-uhd-ips-60hz-5ms-350-nits-hdmi-dp-usb-usbc-audio-79903",
    ),
    "PC Gaming Ryzen 5 RTX 4060": (
        "https://hanoicomputercdn.com/media/product/83860_pc_hacom_designer_d144_new_1.jpg",
        "https://hacom.vn/pc-hacom-designer-d144-i5-13400f-rtx-4060",
    ),
    "PC Streaming Ryzen 7 RTX 4070": (
        "https://hanoicomputercdn.com/media/product/87306_pc_hacom_001_raphael_amd_ryzen_7700x_vga_rtx_4070xs.jpg",
        "https://hacom.vn/pc-hacom-001-raphael-amd-ryzen-7700x-vga-rtx-4070s",
    ),
    "PC văn phòng Core i3 12100": (
        "https://cdn-files.hacom.vn/hacom/cdn/web/26032026/pc-acer-veriton-vx2710g-fr180w12v-pcac0135-2.jpg",
        "https://hacom.vn/pc-acer-veriton-vx2710g-fr180w12v-pcac0135",
    ),
    "Mini PC văn phòng Intel N100": (
        "https://hanoicomputercdn.com/media/product/89895_pc_mini_zotac_zbox_ci337_nano_be1_1.jpg",
        "https://hacom.vn/pc-mini-zotac-zbox-ci337-nano-be1-n100-wifi-bt-8gb-ddr5-5600-ssd-256gb-den",
    ),
    "Chuột Logitech G102 Lightsync": (
        "https://hanoicomputercdn.com/media/product/53013_mouse_logitech_g102_lightsync_rgb_white_0002_3.jpg",
        "https://hacom.vn/chuot-game-logitech-g102-gen2-white-usb-rgb-trang",
    ),
    "Bàn phím cơ DareU EK87": (
        "https://cdn-files.hacom.vn/hacom/cdn/web/media/lib/11-03-2025/ban-phim-co-gaming-dareu-ek87-pro.jpg",
        "https://hacom.vn/ban-phim-co-gaming-dareu-ek87-pro-black-golden-cloud-switch",
    ),
    "Webcam Logitech C270": (
        "https://hanoicomputercdn.com/media/product/17151_webcam_logitech_hd_c270.jpg",
        "https://hacom.vn/webcam-logitech-hd-270",
    ),
    "Tai nghe HyperX Cloud Stinger 2": (
        "https://hanoicomputercdn.com/media/product/90833_tai_nghe_gaming_hyperx_cloud_stinger_ii_519t1aa_1.jpg",
        "https://hacom.vn/tai-nghe-gaming-hyperx-cloud-stinger-ii-519t1aa",
    ),
    "Micro Fifine K669B": (
        "https://hanoicomputercdn.com/media/product/83172_microphone_co_day_fifine_k669b.jpg",
        "https://hacom.vn/microphone-co-day-fifine-k669b",
    ),
}


def import_hacom_products():
    """Create or update only the curated HACOM products; leave orders untouched."""
    for product in HACOM_PRODUCTS:
        category_name = product["category"]
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={"description": CATEGORY_DESCRIPTIONS[category_name]},
        )
        defaults = {
            "category": category,
            "brand": product["brand"],
            "price": product["price"],
            "stock": product["stock"],
            "specifications": product["specifications"],
            "description": (
                "Thông tin và ảnh tham khảo từ HACOM. Giá được ghi nhận ngày "
                "18/10/2026 và có thể thay đổi theo thời điểm."
            ),
            "image_url": product["image_url"],
            "is_active": True,
        }
        Product.objects.update_or_create(name=product["name"], defaults=defaults)
    return len(HACOM_PRODUCTS)


def fill_seed_product_images():
    """Attach relevant HACOM image references to demo products missing photos."""
    filled = 0
    for name, (image_url, source_url) in SEED_PRODUCT_IMAGES.items():
        product = Product.objects.filter(name=name).first()
        if product is None or product.image or product.image_url:
            continue
        product.image_url = image_url
        specs = dict(product.specifications or {})
        specs.setdefault("Nguồn tham khảo", source_url)
        product.specifications = specs
        product.save(update_fields=["image_url", "specifications", "updated_at"])
        filled += 1
    return filled
