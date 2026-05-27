"""
seed_data.py — Nạp dữ liệu mẫu cho Lab 04 (Mã hóa ở Client)
"""

from db_connection import get_connection, call_sp
from crypto_utils import hash_password_sha1, generate_deterministic_rsa, rsa_encrypt

def run_sql(sql: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()

def main():
    print("Đang xóa dữ liệu cũ...")
    run_sql("DELETE FROM BANGDIEM; DELETE FROM SINHVIEN; DELETE FROM LOP; DELETE FROM NHANVIEN; DELETE FROM HOCPHAN;")
    
    print("Đang thêm Admin...")
    admin_mk = 'Admin123!'
    admin_mk_hash = hash_password_sha1(admin_mk)
    _, admin_pub = generate_deterministic_rsa(admin_mk, 'admin')
    run_sql(f"""
        INSERT INTO NHANVIEN (MANV, HOTEN, EMAIL, LUONG, TENDN, MATKHAU, PUBKEY, ISADMIN)
        VALUES ('NV00', N'Quản trị viên', 'admin@edu.vn', NULL, 'admin', 0x{admin_mk_hash}, '{admin_pub.decode('utf-8')}', 1)
    """)

    print("Đang thêm nhân viên (Giảng viên)...")
    # Tên Đăng Nhập: nva, ttb, lhc | Mật khẩu: Abcd123!
    nhanviens = [
        ('NV01', 'Nguyễn Văn An', 'nva@edu.vn', '8000000', 'nva', 'Abcd123!'),
        ('NV02', 'Trần Thị Bình', 'ttb@edu.vn', '9000000', 'ttb', 'Abcd123!'),
        ('NV03', 'Lê Hoàng Cường', 'lhc@edu.vn', '7500000', 'lhc', 'Abcd123!')
    ]
    
    pub_keys = {}
    
    for manv, hoten, email, luong, tendn, mk in nhanviens:
        priv_key, pub_key = generate_deterministic_rsa(mk, tendn)
        pub_keys[manv] = pub_key
        
        luong_encrypt = bytearray(rsa_encrypt(pub_key, luong))
        matkhau_hash = bytearray.fromhex(hash_password_sha1(mk))
        
        call_sp("SP_INS_PUBLIC_ENCRYPT_NHANVIEN", {
            "MANV": manv,
            "HOTEN": hoten,
            "EMAIL": email,
            "LUONG": luong_encrypt,
            "TENDN": tendn,
            "MATKHAU_HASH": matkhau_hash,
            "PUBKEY": pub_key.decode('utf-8'),
            "MANV_LOGIN": "NV00"
        })

    print("Đang thêm lớp học...")
    call_sp("SP_INS_LOP", {"MALOP": 'CNTT01', "TENLOP": 'Công nghệ thông tin Khóa 1', "MANV": 'NV01', "MANV_LOGIN": 'NV01'})
    call_sp("SP_INS_LOP", {"MALOP": 'CNTT04', "TENLOP": 'Công nghệ thông tin Khóa 4', "MANV": 'NV01', "MANV_LOGIN": 'NV01'})
    
    call_sp("SP_INS_LOP", {"MALOP": 'CNTT02', "TENLOP": 'Công nghệ thông tin Khóa 2', "MANV": 'NV02', "MANV_LOGIN": 'NV02'})
    call_sp("SP_INS_LOP", {"MALOP": 'CNTT05', "TENLOP": 'Công nghệ thông tin Khóa 5', "MANV": 'NV02', "MANV_LOGIN": 'NV02'})
    
    call_sp("SP_INS_LOP", {"MALOP": 'CNTT03', "TENLOP": 'Công nghệ thông tin Khóa 3', "MANV": 'NV03', "MANV_LOGIN": 'NV03'})
    call_sp("SP_INS_LOP", {"MALOP": 'CNTT06', "TENLOP": 'Công nghệ thông tin Khóa 6', "MANV": 'NV03', "MANV_LOGIN": 'NV03'})
    
    print("Đang thêm học phần...")
    run_sql("""
    INSERT INTO HOCPHAN (MAHP, TENHP, SOTC) VALUES 
    ('HP01', N'Cơ sở dữ liệu', 4),
    ('HP02', N'Mạng máy tính', 3),
    ('HP03', N'An toàn thông tin', 3),
    ('HP04', N'Lập trình Python', 3),
    ('HP05', N'Cấu trúc dữ liệu', 4);
    """)

    print("Đang thêm sinh viên...")
    sv_mk = bytearray.fromhex(hash_password_sha1("123456"))
    # SV cho NV01
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV01', "HOTEN": 'Đào Thanh Văn', "NGAYSINH": '2005-01-15', "DIACHI": 'Quận 1, TP.HCM', "MALOP": 'CNTT01', "TENDN": 'sv01', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV01'})
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV02', "HOTEN": 'Lê Thị Hương', "NGAYSINH": '2005-02-20', "DIACHI": 'Quận 2, TP.HCM', "MALOP": 'CNTT01', "TENDN": 'sv02', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV01'})
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV03', "HOTEN": 'Trần Văn Nam', "NGAYSINH": '2005-03-10', "DIACHI": 'Quận 3, TP.HCM', "MALOP": 'CNTT01', "TENDN": 'sv03', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV01'})
    
    # SV cho NV02
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV04', "HOTEN": 'Đỗ Thị Hà', "NGAYSINH": '2005-06-18', "DIACHI": 'Quận 6, TP.HCM', "MALOP": 'CNTT02', "TENDN": 'sv04', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV02'})
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV05', "HOTEN": 'Vũ Văn Hải', "NGAYSINH": '2005-07-22', "DIACHI": 'Quận 7, TP.HCM', "MALOP": 'CNTT02', "TENDN": 'sv05', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV02'})
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV06', "HOTEN": 'Đặng Thị Yến', "NGAYSINH": '2005-08-30', "DIACHI": 'Quận 8, TP.HCM', "MALOP": 'CNTT02', "TENDN": 'sv06', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV02'})
    
    # SV cho NV03
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV07', "HOTEN": 'Châu Văn Phát', "NGAYSINH": '2005-11-25', "DIACHI": 'Quận 11, TP.HCM', "MALOP": 'CNTT03', "TENDN": 'sv07', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV03'})
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV08', "HOTEN": 'Hồ Thị Anh', "NGAYSINH": '2005-12-01', "DIACHI": 'Quận 12, TP.HCM', "MALOP": 'CNTT03', "TENDN": 'sv08', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV03'})
    call_sp("SP_INS_SINHVIEN", {"MASV": 'SV09', "HOTEN": 'Ngô Văn Tài', "NGAYSINH": '2005-01-08', "DIACHI": 'Bình Thạnh, TP.HCM', "MALOP": 'CNTT03', "TENDN": 'sv09', "MATKHAU_HASH": sv_mk, "MANV_LOGIN": 'NV03'})

    print("Đang nhập bảng điểm...")
    
    def add_score(masv, mahp, score, manv):
        pub_key = pub_keys[manv]
        score_encrypt = bytearray(rsa_encrypt(pub_key, str(score)))
        call_sp("SP_INS_BANGDIEM", {"MASV": masv, "MAHP": mahp, "DIEMTHI_ENCRYPT": score_encrypt, "MANV_LOGIN": manv})

    add_score('SV01', 'HP02', 9.0, 'NV01')
    add_score('SV01', 'HP03', 7.5, 'NV01')
    add_score('SV02', 'HP04', 8.0, 'NV01')
    add_score('SV03', 'HP02', 7.0, 'NV01')
    add_score('SV03', 'HP05', 9.5, 'NV01')
    
    add_score('SV04', 'HP02', 8.0, 'NV02')
    add_score('SV05', 'HP03', 9.0, 'NV02')
    add_score('SV05', 'HP04', 8.5, 'NV02')
    add_score('SV06', 'HP05', 6.0, 'NV02')
    
    add_score('SV07', 'HP01', 5.5, 'NV03')
    add_score('SV07', 'HP04', 6.5, 'NV03')
    add_score('SV08', 'HP02', 8.0, 'NV03')
    add_score('SV08', 'HP05', 7.5, 'NV03')
    add_score('SV09', 'HP01', 9.0, 'NV03')
    add_score('SV09', 'HP03', 8.5, 'NV03')

    print("Hoàn tất nạp dữ liệu!")

if __name__ == "__main__":
    main()
