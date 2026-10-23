# PCShop — Website quản lý và bán linh kiện máy tính

PCShop là website bán hàng phục vụ bài tập nhóm môn **Lập trình với Python**. Dự án dùng Django cho backend, Django REST Framework cho API, SQLite cho môi trường phát triển và có thể cấu hình PostgreSQL khi triển khai.

> **Lưu ý:** Đây là dự án học tập với dữ liệu, giá, tồn kho, tài khoản và thông tin chuyển khoản mẫu. Danh sách sản phẩm HACOM trong mã nguồn là bản dữ liệu được tuyển chọn, không đồng bộ trực tiếp với giá hoặc tồn kho hiện tại của HACOM. Không dùng tài khoản demo hoặc cấu hình mẫu cho cửa hàng thật.

## Mục lục

- [Chức năng](#chức-năng)
- [Công nghệ và yêu cầu](#công-nghệ-và-yêu-cầu)
- [Cài đặt và chạy trên Windows](#cài-đặt-và-chạy-trên-windows)
- [Cài đặt trên Linux và macOS](#cài-đặt-trên-linux-và-macos)
- [Khởi động và dừng website](#khởi-động-và-dừng-website)
- [Các địa chỉ trong website](#các-địa-chỉ-trong-website)
- [Tài khoản mẫu và quyền truy cập](#tài-khoản-mẫu-và-quyền-truy-cập)
- [Thêm và sửa sản phẩm](#thêm-và-sửa-sản-phẩm)
- [Cách hoạt động của danh mục và bộ lọc](#cách-hoạt-động-của-danh-mục-và-bộ-lọc)
- [Dữ liệu mẫu và sản phẩm HACOM](#dữ-liệu-mẫu-và-sản-phẩm-hacom)
- [Giỏ hàng, đặt hàng và đánh giá](#giỏ-hàng-đặt-hàng-và-đánh-giá)
- [So sánh sản phẩm và kiểm tra cấu hình PC](#so-sánh-sản-phẩm-và-kiểm-tra-cấu-hình-pc)
- [Đăng nhập Google, Facebook và Zalo](#đăng-nhập-google-facebook-và-zalo)
- [REST API](#rest-api)
- [Cơ sở dữ liệu và migrations](#cơ-sở-dữ-liệu-và-migrations)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Kiểm tra dự án](#kiểm-tra-dự-án)
- [Triển khai](#triển-khai)
- [Xử lý lỗi thường gặp](#xử-lý-lỗi-thường-gặp)

## Chức năng

### Phía khách hàng

- Xem sản phẩm theo danh mục: Laptop, PC văn phòng, PC gaming, Màn hình, Phụ kiện PC và Linh kiện PC.
- Lọc theo thương hiệu, khoảng giá, tình trạng hàng và thông số kỹ thuật.
- Trong danh mục Linh kiện PC, chọn CPU, Mainboard, VGA, RAM, SSD hoặc Nguồn trước khi xem bộ lọc riêng cho nhóm đó.
- Xem trang chi tiết, hình ảnh, tồn kho và thông số sản phẩm.
- Thêm, sửa số lượng và xóa sản phẩm trong giỏ hàng lưu theo phiên đăng nhập/trình duyệt.
- Đặt hàng với phương thức COD hoặc chuyển khoản ngân hàng.
- Theo dõi và hủy đơn khi đơn còn ở trạng thái chờ xác nhận.
- So sánh tối đa bốn sản phẩm.
- Dùng trình dựng cấu hình PC để kiểm tra một số tương thích cơ bản giữa CPU, mainboard, RAM, card màn hình và nguồn.
- Đánh giá sản phẩm sau khi đơn chứa sản phẩm đó đã hoàn thành.
- Đăng ký, đăng nhập bằng tài khoản website; OAuth Google, Facebook và Zalo hoạt động khi được cấu hình thông tin ứng dụng.

### Phía quản trị

- Quản lý danh mục, sản phẩm, ảnh và tồn kho.
- Xem danh sách đơn và cập nhật trạng thái theo luồng hợp lệ.
- Xem thống kê doanh thu và sản phẩm bán chạy.
- Có thể truy cập dashboard tại `/manage/`; tài khoản phải có quyền nhân viên/quản trị.

### Nghiệp vụ hiện có và giới hạn

- Tồn kho được kiểm tra khi thêm vào giỏ và kiểm tra lại lúc đặt hàng. Tạo đơn dùng transaction để tránh tạo một phần đơn nếu một sản phẩm không đủ hàng.
- Giá và tên sản phẩm được lưu thành bản chụp trong từng dòng đơn hàng.
- Hủy đơn hợp lệ sẽ hoàn lại tồn kho.
- Chuyển khoản hiện chỉ hiển thị thông tin ngân hàng cấu hình trong `pcshop/settings.py`; dự án chưa kết nối cổng thanh toán để tự xác nhận giao dịch.
- Hình ảnh có thể là tệp tải lên hoặc URL ảnh. URL ngoài cần có Internet và có thể bị nhà cung cấp ảnh thay đổi.

## Công nghệ và yêu cầu

| Thành phần | Công nghệ |
|---|---|
| Backend | Python, Django |
| API | Django REST Framework |
| Cơ sở dữ liệu mặc định | SQLite |
| Cơ sở dữ liệu tùy chọn | PostgreSQL |
| Giao diện | Django Templates, Bootstrap 5, CSS và JavaScript |
| Biểu đồ dashboard | Chart.js |
| Ảnh tải lên | Pillow |
| Đăng nhập xã hội | social-auth-app-django; backend OAuth Zalo riêng |

Yêu cầu tối thiểu: **Python 3.10 trở lên** và `pip`. Cần kết nối Internet khi cài dependencies; ảnh từ URL bên ngoài cũng cần Internet để hiển thị.

## Cài đặt và chạy trên Windows

Mở PowerShell hoặc Terminal tại thư mục có `manage.py`. Ví dụ:

```powershell
Set-Location "E:\Web_ban_linh_kien_dien_tu-main"
```

Kiểm tra Python:

```powershell
py -3 --version
```

Tạo môi trường ảo, cài thư viện, tạo bảng dữ liệu, nạp dữ liệu demo và chạy website:

```powershell
py -3 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_data
.\venv\Scripts\python.exe manage.py runserver
```

Khi Terminal hiện dòng tương tự `Starting development server at http://127.0.0.1:8000/`, mở địa chỉ đó trong trình duyệt.

### Cài nhanh bằng tệp batch

Trong PowerShell, chạy:

```powershell
.\setup.bat
```

Hoặc mở `setup.bat` từ File Explorer. Tệp này tạo môi trường ảo, cài thư viện, chạy migrations, nạp dữ liệu demo và khởi động server. Nếu muốn xem từng bước hoặc gặp lỗi, dùng các lệnh thủ công phía trên để biết chính xác bước nào thất bại.

### Môi trường ảo đã được tạo trước đó

Không cần tạo lại `venv`; chạy:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_data
.\venv\Scripts\python.exe manage.py runserver
```

## Cài đặt trên Linux và macOS

Từ thư mục dự án, chạy:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Hoặc dùng script:

```bash
bash setup.sh
```

## Khởi động và dừng website

- Để chạy server, mở Terminal tại thư mục chứa `manage.py` rồi chạy `python manage.py runserver`. Nếu đang ở thư mục khác, hãy dùng đường dẫn đầy đủ tới `manage.py` và Python trong môi trường ảo.
- Để dừng server, quay lại cửa sổ Terminal đang chạy và nhấn **Ctrl+C**.
- Để bật lại, chạy lại lệnh `runserver`; dữ liệu SQLite trong `db.sqlite3` vẫn còn sau khi tắt server.
- Mặc định website chỉ mở trên máy đang chạy server tại `http://127.0.0.1:8000/`.
- Nếu cổng 8000 đang bận, dùng `python manage.py runserver 8001` rồi mở `http://127.0.0.1:8001/`.
- Nếu muốn cho thiết bị khác trong mạng nội bộ truy cập, chạy `python manage.py runserver 0.0.0.0:8000`, cấu hình `DJANGO_ALLOWED_HOSTS` phù hợp và dùng địa chỉ IP nội bộ của máy chủ. Không dùng `runserver` để triển khai website công khai.

## Các địa chỉ trong website

| Đường dẫn | Chức năng |
|---|---|
| `/` | Trang chủ |
| `/products/` | Tất cả sản phẩm |
| `/category/laptop/` | Laptop |
| `/category/pc-van-phong/` | PC văn phòng |
| `/category/pc-gaming/` | PC gaming |
| `/category/man-hinh/` | Màn hình |
| `/category/phu-kien-pc/` | Phụ kiện PC |
| `/category/linh-kien-pc/` | Linh kiện PC; chọn nhóm CPU/Mainboard/VGA/RAM/SSD/Nguồn trên trang |
| `/category/linh-kien-pc/?kind=cpu` | Linh kiện CPU và bộ lọc dành cho CPU |
| `/category/linh-kien-pc/?kind=mainboard` | Linh kiện Mainboard |
| `/category/linh-kien-pc/?kind=vga` | Linh kiện VGA |
| `/category/linh-kien-pc/?kind=ram` | Linh kiện RAM |
| `/category/linh-kien-pc/?kind=ssd` | Linh kiện SSD |
| `/category/linh-kien-pc/?kind=psu` | Linh kiện Nguồn |
| `/products/<slug>/` | Trang chi tiết sản phẩm |
| `/compare/` | So sánh sản phẩm |
| `/pc-builder/` | Dựng cấu hình PC |
| `/cart/` | Giỏ hàng |
| `/checkout/` | Đặt hàng; cần đăng nhập |
| `/orders/` | Đơn hàng của tài khoản hiện tại |
| `/accounts/register/` | Đăng ký |
| `/accounts/login/` | Đăng nhập |
| `/accounts/profile/` | Hồ sơ tài khoản |
| `/manage/` | Dashboard quản trị |
| `/admin/` | Django Admin |
| `/api/` | REST API |

## Tài khoản mẫu và quyền truy cập

Sau khi chạy `seed_data`, nếu các tài khoản này chưa tồn tại, hệ thống tạo:

| Tên đăng nhập | Mật khẩu | Quyền |
|---|---|---|
| `admin` | `admin123` | Quản trị, truy cập `/manage/` và `/admin/` |
| `khach` | `khach123` | Khách hàng, có dữ liệu đơn mẫu nếu cơ sở dữ liệu chưa có đơn |

Đây là thông tin dùng để trình diễn trên máy phát triển. Đổi mật khẩu hoặc tạo tài khoản quản trị riêng trước khi chia sẻ ứng dụng. Có thể tạo superuser khác bằng:

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

Người chưa đăng nhập sẽ được chuyển tới trang đăng nhập khi mở khu quản trị. Người đã đăng nhập nhưng không có quyền nhân viên sẽ bị từ chối truy cập.

## Thêm và sửa sản phẩm

### Thêm sản phẩm trên website

1. Đăng nhập bằng tài khoản nhân viên/quản trị.
2. Mở `/manage/products/`.
3. Chọn **Thêm sản phẩm**.
4. Nhập danh mục, tên sản phẩm, thương hiệu, giá bằng VND, số lượng tồn kho và mô tả.
5. Thêm ảnh bằng trường tải tệp **Ảnh** hoặc nhập URL tại **Ảnh (URL)**. Nếu cả hai trường ảnh trống, giao diện dùng ảnh mặc định.
6. Nhập thông số theo dạng **mỗi dòng một cặp `Tên: Giá trị`**, rồi lưu.

Trường thông số của form quản trị **không nhận JSON**. Ví dụ cho CPU:

```text
Socket: AM5
Số nhân / luồng: 6 / 12
Xung nhịp: 3.7 - 5.0 GHz
TDP: 65W
RAM hỗ trợ: DDR5
```

Ví dụ cho PC gaming:

```text
CPU: AMD Ryzen 5 5500G
Mainboard: ASUS A520M
RAM: 16GB DDR4
Ổ cứng: 500GB SSD
VGA: ASUS RTX 3050
Loại case: Kính cường lực
Nguồn: AIGO 650W
```

Nếu nhập trực tiếp qua code hoặc API có trường JSON, một object hợp lệ phải dùng dấu ngoặc kép và dấu phẩy giữa các dòng, ví dụ:

```json
{
  "CPU": "AMD Ryzen 5 5500G",
  "Mainboard": "ASUS A520M",
  "RAM": "16GB DDR4",
  "Ổ cứng": "500GB SSD",
  "VGA": "ASUS RTX 3050",
  "Loại case": "Kính cường lực",
  "Nguồn": "AIGO 650W"
}
```

### Thêm ảnh

- **Tải ảnh lên:** dùng trường **Ảnh** trong dashboard. Tệp được lưu dưới `media/products/`.
- **Dùng ảnh từ URL:** nhập URL đầy đủ bắt đầu bằng `https://` tại trường **Ảnh (URL)**. Máy xem trang cần truy cập được URL này.
- Nếu sản phẩm có cả ảnh tải lên và URL, ảnh tải lên được ưu tiên.
- Ảnh chưa có hoặc URL hỏng sẽ hiển thị ảnh mặc định `static/img/no-image.svg`.
- Thư mục `media/` không được Git theo dõi. Hãy sao lưu riêng nếu ảnh tải lên quan trọng.

### Thông số ảnh hưởng đến việc phân nhóm linh kiện

Sản phẩm muốn xuất hiện trong các nhóm lọc CPU/Mainboard/VGA/RAM/SSD/Nguồn phải nằm trong danh mục **Linh kiện PC** và có thông số phù hợp. Mã phân loại nằm trong `catalog/compatibility.py` và bộ lọc nằm trong `catalog/filters.py`.

| Nhóm | Dấu hiệu nhận diện chính |
|---|---|
| CPU | Có `Socket` và không có `Chipset` |
| Mainboard | Có `Chipset`, hoặc tên có từ khóa mainboard/bo mạch chủ |
| VGA | Có `GPU` hoặc `VRAM`, hoặc tên có từ khóa card màn hình/GeForce/Radeon |
| RAM | Có `Bus`, `Dung lượng` và tên/thông số thể hiện chuẩn DDR; hoặc tên có RAM |
| SSD/ổ cứng | Tên có SSD/NVMe/HDD, hoặc có `Dung lượng` và `Chuẩn` phù hợp |
| Nguồn | Có thông số `Công suất`, hoặc tên bắt đầu bằng “Nguồn” |

Để trình dựng cấu hình kiểm tra tốt hơn, nên thống nhất các khóa như `Socket`, `Chipset`, `RAM hỗ trợ`, `Chuẩn`, `Nguồn đề nghị`, `Công suất` và ghi đơn vị vào giá trị, ví dụ `750W`, `DDR5`, `AM5`.

## Cách hoạt động của danh mục và bộ lọc

- Các tên và liên kết danh mục nằm trong dữ liệu `Category`; danh mục mẫu được tạo bởi `seed_data`.
- Nhóm lọc con và tiêu chí hiển thị được khai báo trong `catalog/views.py`.
- Quy tắc áp dụng bộ lọc, từ khóa thông số và khoảng giá nằm trong `catalog/filters.py`.
- Giá trị không khớp với sản phẩm nào trong danh mục hiện tại sẽ được ẩn khỏi một số nhóm lọc để tránh lựa chọn rỗng.
- Bộ lọc thương hiệu của Linh kiện PC được giới hạn theo nhóm đang chọn, ví dụ chọn CPU thì thương hiệu chỉ lấy từ sản phẩm CPU.
- Bộ lọc PC gaming được tạo từ thông số của các sản phẩm hiện có. Khi thêm sản phẩm PC gaming, điền các trường CPU, Mainboard, RAM, Ổ cứng, VGA và case nhất quán để bộ lọc nhận diện được chúng.
- Khi thêm một loại thông số hoàn toàn mới, chỉ thêm tùy chọn giao diện là chưa đủ: cần thêm xử lý tham số tương ứng trong `filter_products()` ở `catalog/filters.py`.

### Sửa khoảng giá

Mở `catalog/filters.py` và chỉnh `PRICE_RANGE_OPTIONS`. Mỗi khoảng giá có cấu trúc:

```python
("office-5m-7m", "5 triệu - 7 triệu", 5_000_000, 7_000_000)
```

Các phần lần lượt là giá trị gửi trên URL, nhãn hiển thị, giá thấp nhất và giá cao nhất **không bao gồm**. Ví dụ khoảng `5–7 triệu` bao gồm giá từ 5.000.000 đồng đến dưới 7.000.000 đồng. Mỗi danh mục hoặc nhóm linh kiện có thể có dải giá riêng trong từ điển này.

## Dữ liệu mẫu và sản phẩm HACOM

### Tạo dữ liệu demo

```powershell
.\venv\Scripts\python.exe manage.py seed_data
```

Lệnh này tạo/cập nhật các danh mục và sản phẩm demo, nạp bản sản phẩm HACOM được tuyển chọn, thêm ảnh tham chiếu còn thiếu, và tạo tài khoản/đơn mẫu nếu cần. Có thể chạy lại để cập nhật dữ liệu demo; lệnh không xóa đơn hiện có khi không có `--reset`.

### Chỉ thêm/cập nhật danh sách sản phẩm HACOM đã lưu trong mã nguồn

```powershell
.\venv\Scripts\python.exe manage.py add_hacom_products
```

Đây là bản chụp sản phẩm được khai báo trong `catalog/hacom_products.py`; lệnh **không tự thu thập dữ liệu trực tiếp từ hacom.vn**. Ảnh tham chiếu dùng URL bên ngoài. Số lượng tồn kho là dữ liệu demo của PCShop, không phải tồn kho cửa hàng HACOM.

### Cẩn trọng với `--reset`

```powershell
.\venv\Scripts\python.exe manage.py seed_data --reset
```

`--reset` xóa đơn hàng, đánh giá, sản phẩm và danh mục hiện có trước khi dựng lại dữ liệu mẫu. Không chạy lệnh này trên cơ sở dữ liệu cần giữ lại. Tài khoản người dùng không bị xóa bởi lệnh reset hiện tại.

## Giỏ hàng, đặt hàng và đánh giá

- Giỏ hàng được lưu trong session của trình duyệt; xóa cookie/session có thể làm mất giỏ.
- Không thể thêm sản phẩm ngừng bán hoặc vượt quá tồn kho.
- Checkout yêu cầu đăng nhập và kiểm tra tồn kho lại trước khi tạo đơn.
- Phương thức thanh toán hiện có: COD và chuyển khoản. Thông tin tài khoản ngân hàng mẫu được khai báo trong `BANK_TRANSFER_INFO` tại `pcshop/settings.py`; thay bằng thông tin thật trước khi trình diễn hoặc triển khai.
- Luồng trạng thái hợp lệ: **Chờ xác nhận → Đang xử lý → Đang giao → Hoàn thành**. Có thể hủy khi đang chờ xác nhận hoặc đang xử lý; không thể chuyển tiếp sau khi đơn hoàn thành/đã hủy.
- Khách chỉ được tự hủy đơn còn chờ xác nhận.
- Khách chỉ được đánh giá sau khi đơn chứa sản phẩm đã hoàn thành. Mỗi tài khoản có một đánh giá cho mỗi sản phẩm; gửi lại sẽ cập nhật đánh giá đó.
- Sản phẩm đã được dùng trong đơn hàng không bị xóa cứng để giữ lịch sử; dashboard chuyển nó sang trạng thái ngừng bán.

## So sánh sản phẩm và kiểm tra cấu hình PC

### So sánh

Thêm sản phẩm vào danh sách so sánh từ thẻ sản phẩm hoặc trang chi tiết, sau đó mở `/compare/`. Tối đa bốn sản phẩm được hiển thị. Thông số có tên `Nguồn tham khảo`/`source` không được hiển thị trong bảng so sánh.

### Dựng cấu hình PC

Mở `/pc-builder/`, chọn linh kiện còn hàng trong danh mục Linh kiện PC rồi yêu cầu kiểm tra. Mã hiện kiểm tra:

- Socket CPU và Mainboard.
- Chuẩn DDR của RAM và chuẩn RAM Mainboard hỗ trợ.
- Công suất nguồn so với công suất khuyến nghị của VGA.

Thiếu thông số sẽ hiện cảnh báo rằng chưa thể xác nhận tương thích. Xung đột được xác định sẽ ngăn thêm cấu hình vào giỏ. Đây là kiểm tra theo dữ liệu đã nhập, không thay thế việc kiểm tra tương thích kỹ thuật đầy đủ từ nhà sản xuất.

## Đăng nhập Google, Facebook và Zalo

Các nút đăng nhập xã hội chỉ hoạt động khi cả Client/App ID và Secret của nhà cung cấp được khai báo. Nếu chưa cấu hình, nút sẽ hiển thị trạng thái chưa bật; đăng nhập bằng username/password vẫn dùng được.

1. Tạo tệp `.env` từ mẫu:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Tạo ứng dụng OAuth tại trang dành cho nhà phát triển của nhà cung cấp và cấu hình callback local:

   | Nhà cung cấp | Callback local |
   |---|---|
   | Google | `http://127.0.0.1:8000/accounts/social/complete/google-oauth2/` |
   | Facebook | `http://127.0.0.1:8000/accounts/social/complete/facebook/` |
   | Zalo | `http://127.0.0.1:8000/accounts/social/complete/zalo/` |

3. Điền các biến tương ứng trong `.env`:

   ```dotenv
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=
   FACEBOOK_CLIENT_ID=
   FACEBOOK_CLIENT_SECRET=
   ZALO_APP_ID=
   ZALO_APP_SECRET=
   ```

4. Chạy migrations và khởi động lại server:

   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   .\venv\Scripts\python.exe manage.py runserver
   ```

Không đưa `.env` hoặc OAuth Secret lên Git, gửi trong ảnh chụp, hoặc đăng trong chat. `.env` đã được `.gitignore` loại trừ. Khi triển khai, phải đăng ký callback HTTPS đúng domain với từng nhà cung cấp. Tài khoản Google, Facebook và Zalo không tự được gộp chỉ vì có cùng email; đăng nhập lần đầu qua mỗi nhà cung cấp có thể tạo liên kết/tài khoản riêng. Zalo có thể không cung cấp email.

## REST API

API được đặt dưới `/api/`. Danh sách sản phẩm được phân trang mặc định 12 sản phẩm/trang.

| Phương thức và URL | Mô tả |
|---|---|
| `GET /api/products/` | Danh sách sản phẩm đang bán; hỗ trợ tìm kiếm, lọc, sắp xếp và phân trang |
| `GET /api/products/<id>/` | Chi tiết sản phẩm |
| `GET /api/categories/` | Danh sách danh mục |
| `GET /api/check-stock/?product_id=1&quantity=2` | Kiểm tra tồn kho; trả `404` nếu không tồn tại |
| `POST /api/cart/add/` | Thêm sản phẩm vào giỏ session |
| `POST /api/cart/update/` | Cập nhật số lượng; `quantity=0` xóa sản phẩm |
| `GET /api/dashboard/revenue/?days=30` | Doanh thu theo ngày; yêu cầu tài khoản staff |
| `GET /api/dashboard/top-products/?limit=5` | Sản phẩm bán chạy; yêu cầu tài khoản staff |

### Bộ lọc danh sách API

Ví dụ lấy CPU AMD socket AM5, còn hàng, giá tăng dần:

```text
/api/products/?category=linh-kien-pc&kind=cpu&brand=AMD&socket=AM5&in_stock=1&sort=price_asc
```

Các tham số thường dùng:

| Tham số | Ý nghĩa |
|---|---|
| `q` | Tìm trong tên, thương hiệu và thông số |
| `category` | Slug danh mục, ví dụ `laptop`, `pc-gaming`, `linh-kien-pc` |
| `kind` | Nhóm sản phẩm, ví dụ `cpu`, `mainboard`, `vga`, `ram`, `ssd`, `psu` |
| `brand` | Thương hiệu |
| `min_price`, `max_price` | Khoảng giá tùy chỉnh theo VND |
| `price_range` | Mã khoảng giá khai báo trong `catalog/filters.py` |
| `in_stock=1` | Chỉ lấy sản phẩm có tồn kho |
| `sort` | `newest`, `price_asc`, `price_desc` hoặc `name` |
| Thông số | Có thể dùng `socket`, `cpu_family`, `chipset`, `ram_type`, `capacity`, `storage_type`, `gpu_family`, `gpu_brand`, `wattage`, `efficiency` và các khóa tương ứng trong `catalog/filters.py` |

Ví dụ lọc PC gaming theo Intel Core i5 và khoảng giá 25–30 triệu:

```text
/api/products/?category=pc-gaming&cpu_family=i5&price_range=gaming-25m-30m
```

### Thêm/cập nhật giỏ qua API

Body JSON:

```json
{
  "product_id": 1,
  "quantity": 2
}
```

`quantity` nhận số nguyên từ 0 đến 999; API kiểm tra tồn kho. Lỗi tồn kho trả HTTP 400 cùng nội dung giải thích. API dùng session authentication; khi gọi POST từ trình duyệt cần gửi cookie session và CSRF token. Phản hồi giỏ chứa số lượng, tổng tiền và các dòng hàng.

## Cơ sở dữ liệu và migrations

Mặc định dự án dùng tệp SQLite `db.sqlite3` tại thư mục gốc. Tệp cơ sở dữ liệu này bị Git bỏ qua, vì vậy mỗi máy có thể có dữ liệu riêng.

Đồng bộ các bảng đã có trong migrations:

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

Khi chỉnh sửa model trong `accounts`, `catalog`, `orders` hoặc app khác, tạo migration rồi áp dụng:

```powershell
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate
```

Commit các tệp migration mới lên Git cùng thay đổi model. Máy khác chỉ cần lấy code mới và chạy `migrate`; không tự tạo migration lại nếu migration đã được commit.

### Dùng PostgreSQL

1. Cài và khởi động PostgreSQL.
2. Cài driver:

   ```powershell
   .\venv\Scripts\python.exe -m pip install psycopg2-binary
   ```

3. Đặt các biến môi trường sau trong `.env`:

   ```dotenv
   DB_ENGINE=postgres
   DB_NAME=pcshop
   DB_USER=postgres
   DB_PASSWORD=mat_khau_database
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. Tạo database tương ứng trong PostgreSQL và chạy:

   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   .\venv\Scripts\python.exe manage.py seed_data
   ```

SQLite và PostgreSQL là hai cơ sở dữ liệu riêng; đổi `DB_ENGINE` không tự chuyển dữ liệu cũ từ SQLite sang PostgreSQL.

## Cấu trúc thư mục

```text
pcshop/                 Cấu hình, URL gốc, tiện ích Django
accounts/               Tài khoản, đăng ký, đăng nhập, OAuth và hồ sơ
catalog/                Danh mục, sản phẩm, bộ lọc, tương thích, dữ liệu mẫu
  management/commands/  seed_data và add_hacom_products
dashboard/              Quản trị sản phẩm, danh mục, đơn hàng và thống kê
orders/                 Giỏ hàng, checkout, đơn và nghiệp vụ tồn kho
api/                    Django REST Framework endpoints và serializers
templates/              Django templates cho cửa hàng và dashboard
static/                 CSS, JavaScript, ảnh mặc định
media/                  Ảnh sản phẩm người dùng tải lên (bị Git bỏ qua)
docs/                   Ghi chú và danh sách việc phát triển
manage.py                Django management command entry point
requirements.txt         Dependencies của ứng dụng
setup.bat / setup.sh     Script cài đặt và chạy nhanh
```

Luồng xử lý tổng quát: **URL → View/API → nghiệp vụ và ORM → database → HTML hoặc JSON**. Logic lọc sản phẩm nằm trong `catalog/filters.py`; logic giỏ hàng trong `orders/cart.py`; nghiệp vụ tạo đơn và chuyển trạng thái trong `orders/services.py`; thống kê trong `dashboard/stats.py`.

## Kiểm tra dự án

Các lệnh hữu ích khi phát triển:

```powershell
# Kiểm tra cấu hình Django
.\venv\Scripts\python.exe manage.py check

# Xem migration nào chưa áp dụng
.\venv\Scripts\python.exe manage.py showmigrations

# Kiểm tra model có thay đổi chưa tạo migration hay không
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run

# Chạy bộ unit test hiện có
.\venv\Scripts\python.exe manage.py test
```

`check --deploy` có thể báo cảnh báo nếu đang dùng cấu hình phát triển. Trước khi đưa website lên Internet cần dùng secret key riêng, tắt `DEBUG`, cấu hình host hợp lệ, HTTPS, cookie bảo mật và thiết lập bảo mật phù hợp với máy chủ thực tế.

## Triển khai

Không triển khai website công khai bằng Django development server. Trước khi triển khai:

1. Tạo `DJANGO_SECRET_KEY` ngẫu nhiên và riêng cho môi trường production; không dùng secret mẫu.
2. Đặt `DJANGO_DEBUG=0` và `DJANGO_ALLOWED_HOSTS` thành danh sách domain thật, phân cách bằng dấu phẩy.
3. Cấu hình HTTPS tại ứng dụng hoặc reverse proxy; xác nhận cấu hình redirect/cookie bảo mật trước khi bật HSTS.
4. Chuyển sang PostgreSQL nếu cần dữ liệu bền vững và vận hành nhiều người dùng.
5. Chạy migrations và thu thập static files:

   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

6. Dùng WSGI/ASGI server như Gunicorn/Uvicorn phù hợp, đặt reverse proxy như Nginx/IIS và cấu hình nó phục vụ `staticfiles/` cùng `media/`.
7. Thay thông tin chuyển khoản mẫu, đổi mật khẩu demo, cấu hình OAuth HTTPS và sao lưu database cùng ảnh tải lên.
8. Không commit `.env`, `db.sqlite3`, secret, ảnh riêng tư hay dữ liệu khách hàng lên Git.

Cấu hình trong `settings.py` hiện hướng tới phát triển local; hãy rà soát security settings và kiểm tra `python manage.py check --deploy` trong đúng môi trường trước khi phát hành.

## Xử lý lỗi thường gặp

### `python` hoặc `py` không được nhận diện

Cài Python và bật tùy chọn thêm Python vào `PATH`, sau đó mở lại Terminal. Có thể kiểm tra bằng `py -3 --version`. Nếu không có lệnh `py`, thử `python --version`.

### `No module named django` hoặc thiếu thư viện

Đảm bảo đang dùng Python trong `venv` và cài dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Báo `no such table`, `relation does not exist` hoặc lỗi database

Chạy migrations:

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

Nếu database vừa tạo nhưng trang chưa có sản phẩm, chạy `seed_data`.

### Trang trống hoặc bộ lọc không có kết quả

- Kiểm tra sản phẩm có `is_active` và nằm đúng danh mục hay không.
- Kiểm tra `kind` và tên các trường trong thông số. Bộ lọc tìm trên dữ liệu sản phẩm hiện có; sai tên khóa hoặc khác cách ghi giá trị có thể khiến sản phẩm không khớp.
- Chọn **Xóa bộ lọc** rồi thử lại.
- Nếu vừa thêm loại bộ lọc mới, kiểm tra cả khai báo giao diện trong `catalog/views.py` lẫn quy tắc truy vấn trong `catalog/filters.py`.

### Không thấy ảnh sản phẩm

Kiểm tra URL bắt đầu bằng `https://` và mở được từ trình duyệt. Nếu ảnh là tệp tải lên, xác nhận tệp đã lưu dưới `media/products/`. Ảnh ngoài có thể bị xóa hoặc chặn hotlink; khi đó hãy tải ảnh hợp lệ lên website.

### Nút Google/Facebook/Zalo báo chưa bật hoặc OAuth trả lỗi

Mỗi nhà cung cấp cần đủ cả ID và Secret trong `.env`, callback phải trùng chính xác URL đã đăng ký với nhà cung cấp. Sau khi sửa `.env`, khởi động lại server. Thông tin OAuth local không mặc nhiên dùng được khi deploy.

### Lỗi `DisallowedHost`

Thêm hostname hiện đang truy cập vào `DJANGO_ALLOWED_HOSTS` trong `.env`, ví dụ `127.0.0.1,localhost`. Sau đó khởi động lại server.

### Cổng `8000` đã được sử dụng

Chọn cổng khác:

```powershell
.\venv\Scripts\python.exe manage.py runserver 8001
```

### Thông tin tài khoản demo không đăng nhập được

Tài khoản mẫu chỉ được tạo nếu chưa tồn tại. Nếu mật khẩu đã bị đổi, dùng Django Admin hoặc tạo superuser mới bằng `createsuperuser`; không chạy `seed_data --reset` chỉ để đặt lại mật khẩu vì lệnh đó xóa dữ liệu cửa hàng demo.

---

**Dự án học tập PCShop** · Cập nhật README theo cấu trúc mã nguồn hiện tại.
