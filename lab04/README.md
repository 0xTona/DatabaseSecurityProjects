# Hướng Dẫn Cài Đặt và Chạy Ứng Dụng - Quản Lý Sinh Viên (Lab 04 - Mã hóa ở Client)

Ứng dụng này sử dụng Python (`tkinter`) làm giao diện và kết nối với SQL Server qua thư viện `pyodbc`. Dưới đây là các bước chi tiết để thiết lập Database và chạy ứng dụng.

## 1. Yêu Cầu Hệ Thống (Prerequisites)

- **Python 3.x** được cài đặt trên máy.
- **Microsoft SQL Server** (Local hoặc Remote) có bật SQL Server Authentication (ví dụ: tài khoản `sa`).
- **ODBC Driver 17 for SQL Server** (Thường đi kèm khi cài SQL Server, hoặc có thể tải từ trang chủ Microsoft).

## 2. Thiết Lập Môi Trường Ảo (Virtual Environment)

Khuyến nghị sử dụng môi trường ảo (virtual environment) để cài đặt các thư viện độc lập cho dự án.
Mở terminal/command prompt tại thư mục gốc của dự án và chạy:

```bash
cd lab04

python -m venv venv
# Windows:
.\venv\Scripts\activate

pip install -r requirements.txt
```

## 3. Cấu Hình Ứng Dụng

Mở file `config.py` và cập nhật lại thông tin đăng nhập SQL Server cho phù hợp với máy của bạn.

```python
DB_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": "localhost",       # Đổi thành tên Server của bạn
    "database": "QLSVNhom",
    "uid": "sa",                 # Tài khoản SQL Server
    "pwd": "yourpassword"        # Mật khẩu SQL Server
}
```

## 4. Thiết Lập Database & Nạp Dữ Liệu Mẫu

Trước khi chạy code Python, bạn bắt buộc phải tạo Database và các Stored Procedure trong SQL Server (có thể dùng SSMS hoặc DataGrip). Vui lòng chạy các script theo đúng thứ tự sau:

1. Mở file `db/00_create_database.sql` và chạy để khởi tạo Database `QLSVNhom` cùng cấu trúc các bảng cơ bản.
2. Mở file `db/01_stored_procedures.sql` và chạy để tạo các Stored Procedures thực hiện mã hóa và các tác vụ CRUD. Đảm bảo chạy script này dưới context database `QLSVNhom` (ví dụ: bôi đen dòng `USE QLSVNhom;` và chạy cùng).
3. Chạy script nạp dữ liệu mẫu (`seed_data.py`). Script này sẽ tự động mã hóa mật khẩu, tạo key RSA cho giảng viên, và thêm dữ liệu mẫu:

```bash
python seed_data.py
```

> **Các tài khoản mẫu đã được tạo:**
>
> **1. Quản trị viên (Admin):**
> - Tên đăng nhập: `admin`
> - Mật khẩu: `Admin123!`
>
> **2. Giảng viên:**
> - Tên đăng nhập: `nva` (Nguyễn Văn An), `ttb` (Trần Thị Bình), `lhc` (Lê Hoàng Cường)
> - Mật khẩu chung: `Abcd123!`
>
> **3. Sinh viên:**
> - Tên đăng nhập: `sv01`, `sv02`,...
> - Mật khẩu chung: `123456`

## 5. Chạy Ứng Dụng

Sau khi đã thiết lập Database và kích hoạt môi trường ảo, hãy chạy file `main.py`:

```bash
python main.py
```

## 6. Hướng Dẫn Sử Dụng

1. **Đăng nhập:**
   - Sử dụng tài khoản Admin hoặc Giảng viên (như thông tin ở trên).
   - Nhấn "ĐĂNG NHẬP" hoặc phím `Enter`.
2. **Quyền Admin:**
   - Chỉ tài khoản Admin mới có quyền truy cập vào chức năng **Quản lý Nhân Viên**.
   - Admin có thể thêm nhân viên mới (hệ thống sẽ tự động tạo cặp khóa RSA và mã hóa lương/mật khẩu ở client trước khi gửi xuống DB).
3. **Quản lý Lớp Học:**
   - Giảng viên có thể thêm, sửa, xóa các lớp học do mình làm chủ nhiệm.
4. **Quản lý Sinh viên (Điều hướng theo Lớp):**
   - Chọn một lớp học và nhấn **[Quản lý Sinh viên]** để xem danh sách sinh viên của lớp đó.
   - Chỉ giảng viên chủ nhiệm mới có quyền thêm/sửa/xóa hoặc nhập điểm cho sinh viên lớp mình.
5. **Quản lý Điểm (Mã hóa ở Client):**
   - Tại trang Quản lý Sinh viên, chọn một sinh viên và nhấn **[Quản lý Điểm]**.
   - Điểm số khi nhập vào sẽ được **mã hóa ở phía Client** bằng Public Key RSA của giảng viên chủ nhiệm trước khi lưu vào Database.
   - Để xem được điểm thực tế, giảng viên phải nhập đúng mật khẩu đăng nhập của mình để giải mã Private Key và hiển thị điểm (Client-side decryption).