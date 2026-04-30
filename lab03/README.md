# Hướng Dẫn Cài Đặt và Chạy Ứng Dụng - Quản Lý Sinh Viên (Lab 03)

Ứng dụng này sử dụng Python (`tkinter`) làm giao diện và kết nối với SQL Server qua thư viện `pyodbc`. Dưới đây là các bước chi tiết để thiết lập Database và chạy ứng dụng.

## 1. Yêu Cầu Hệ Thống (Prerequisites)

- **Python 3.x** được cài đặt trên máy.
- **Microsoft SQL Server** (Local hoặc Remote) có bật SQL Server Authentication (ví dụ: tài khoản `sa`).
- **ODBC Driver 17 for SQL Server** (Thường đi kèm khi cài SQL Server, hoặc có thể tải từ trang chủ Microsoft).

## 2. Thiết Lập Môi Trường Ảo (Virtual Environment)

Khuyến nghị sử dụng môi trường ảo (virtual environment) để cài đặt các thư viện độc lập cho dự án.
Mở terminal/command prompt tại thư mục gốc của dự án (`Database-Lab3`) và chạy:

```bash
cd lab03

python -m venv venv
./venv/Scripts/activate

pip install -r requirements.txt
```

## 3. Thiết Lập Database

Trước khi chạy code Python, bạn bắt buộc phải tạo Database và các Stored Procedure trong SQL Server (có thể dùng SSMS hoặc DataGrip). Vui lòng chạy các script theo đúng thứ tự sau:

1. Chạy file `db/00_create_database.sql`để khởi tạo Database `QLSVNhom` và cấu trúc các bảng cơ bản.
2. Mở thư mục `lab03/db/` và chạy lần lượt các script sau trên Database `QLSVNhom`:
   - **`01_stored_procedures.sql`**: Tạo các Stored Procedures hỗ trợ mã hóa dữ liệu (RSA_2048, SHA2_512) và các tác vụ Create/Read/Update/Delete (CRUD).
   - **`02_sample_data.sql`**: Xóa dữ liệu cũ (nếu có) và thêm các nhân viên (Giảng viên), lớp học và sinh viên mẫu để test.

> **Tài khoản mẫu đã được tạo:**
>
> - Tên đăng nhập: `nva`
> - Mật khẩu: `abcd12`

## 4. Cấu Hình Ứng Dụng

Mở file `lab03p/config.py` và cập nhật lại thông tin đăng nhập SQL Server cho phù hợp với máy của bạn.

```python
DB_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": "localhost",       # Đổi thành tên Server
    "database": "QLSVNhom",
    "uid": "sa",                 # Tài khoản SQL Server
    "pwd": "yourpassword"        # Mật khẩu SQL Server
}
```

## 5. Chạy Ứng Dụng

Sau khi đã kích hoạt môi trường ảo, hãy di chuyển vào thư mục ứng dụng và chạy file `main.py`:

```bash
python main.py
```

## 6. Hướng Dẫn Sử Dụng

1. **Đăng nhập:**
   - Nhập Tên Đăng Nhập: `nva`
   - Mật khẩu: `abcd12`
   - Nhấn "ĐĂNG NHẬP" hoặc phím `Enter`.
2. **Quản lý dữ liệu (Tabs Sinh Viên & Lớp Học):**
   - Sau khi đăng nhập thành công, hệ thống sẽ mở màn hình quản lý.
   - Bạn có thể chuyển đổi qua lại giữa tab **"Sinh Viên"** và **"Lớp Học"**.
   - Nhấn vào một dòng để thông tin chi tiết tự động điền xuống form bên dưới.
   - Sử dụng các nút **[Thêm]**, **[Sửa]**, **[Xóa]**, **[Làm mới]** để quản lý dữ liệu.
   - Nhấn **[Đăng xuất]** ở góc phải phía trên để quay lại màn hình đăng nhập.
