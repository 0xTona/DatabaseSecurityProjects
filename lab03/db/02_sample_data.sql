USE QLSVNhom;
GO

-- Xóa dữ liệu cũ (theo thứ tự FK)
DELETE FROM BANGDIEM;
DELETE FROM SINHVIEN;
DELETE FROM LOP;
DELETE FROM NHANVIEN;
DELETE FROM HOCPHAN;
GO

-- ─── Nhân viên (Giảng viên) ───────────────────────────────
EXEC SP_INS_PUBLIC_NHANVIEN 'NV01', N'Nguyễn Văn An',   'nva@edu.vn',  8000000, 'nva', 'abcd12';
EXEC SP_INS_PUBLIC_NHANVIEN 'NV02', N'Trần Thị Bình',   'ttb@edu.vn',  9000000, 'ttb', 'abcd12';
EXEC SP_INS_PUBLIC_NHANVIEN 'NV03', N'Lê Hoàng Cường',  'lhc@edu.vn',  7500000, 'lhc', 'abcd12';
GO


-- Lớp của Thầy An (NV01)
EXEC SP_INS_LOP 'CNTT01', N'Công nghệ thông tin Khóa 1', 'NV01';
EXEC SP_INS_LOP 'CNTT04', N'Công nghệ thông tin Khóa 4', 'NV01';

-- Lớp của Cô Bình (NV02)
EXEC SP_INS_LOP 'CNTT02', N'Công nghệ thông tin Khóa 2', 'NV02';
EXEC SP_INS_LOP 'CNTT05', N'Công nghệ thông tin Khóa 5', 'NV02';

-- Lớp của Thầy Cường (NV03)
EXEC SP_INS_LOP 'CNTT03', N'Công nghệ thông tin Khóa 3', 'NV03';
EXEC SP_INS_LOP 'CNTT06', N'Công nghệ thông tin Khóa 6', 'NV03';
GO

USE QLSVNhom;
GO

-- Thêm học phần
INSERT INTO HOCPHAN (MAHP, TENHP, SOTC) VALUES 
('HP01', N'Cơ sở dữ liệu', 4),
('HP02', N'Mạng máy tính', 3),
('HP03', N'An toàn thông tin', 3),
('HP04', N'Lập trình Python', 3),
('HP05', N'Cấu trúc dữ liệu', 4);
GO

-- =================================================================
-- 4. THÊM SINH VIÊN (BẮT BUỘC KHỚP MÃ NV QUẢN LÝ LỚP ĐÓ)
-- Dùng SP: SP_INS_SINHVIEN (Tự động Hash mật khẩu)
-- Params: MASV, HOTEN, NGAYSINH, DIACHI, MALOP, TENDN, MATKHAU, MANV_LOGIN
-- =================================================================

-- Sinh viên thuộc NV01 (Lớp CNTT01, CNTT04)
EXEC SP_INS_SINHVIEN 'SV01', N'Đào Thanh Văn', '2005-01-15', N'Quận 1, TP.HCM', 'CNTT01', 'sv01', '123456', 'NV01';
EXEC SP_INS_SINHVIEN 'SV02', N'Lê Thị Hương',      '2005-02-20', N'Quận 2, TP.HCM', 'CNTT01', 'sv02', '123456', 'NV01';
EXEC SP_INS_SINHVIEN 'SV03', N'Trần Văn Nam',      '2005-03-10', N'Quận 3, TP.HCM', 'CNTT01', 'sv03', '123456', 'NV01';

-- Sinh viên thuộc NV02 (Lớp CNTT02, CNTT05)
EXEC SP_INS_SINHVIEN 'SV04', N'Đỗ Thị Hà',         '2005-06-18', N'Quận 6, TP.HCM', 'CNTT02', 'sv04', '123456', 'NV02';
EXEC SP_INS_SINHVIEN 'SV05', N'Vũ Văn Hải',        '2005-07-22', N'Quận 7, TP.HCM', 'CNTT02', 'sv05', '123456', 'NV02';
EXEC SP_INS_SINHVIEN 'SV06', N'Đặng Thị Yến',      '2005-08-30', N'Quận 8, TP.HCM', 'CNTT02', 'sv06', '123456', 'NV02';

-- Sinh viên thuộc NV03 (Lớp CNTT03, CNTT06)
EXEC SP_INS_SINHVIEN 'SV07', N'Châu Văn Phát',     '2005-11-25', N'Quận 11, TP.HCM', 'CNTT03', 'sv07', '123456', 'NV03';
EXEC SP_INS_SINHVIEN 'SV08', N'Hồ Thị Anh',        '2005-12-01', N'Quận 12, TP.HCM', 'CNTT03', 'sv08', '123456', 'NV03';
EXEC SP_INS_SINHVIEN 'SV09', N'Ngô Văn Tài',       '2005-01-08', N'Bình Thạnh, TP.HCM', 'CNTT03', 'sv09', '123456', 'NV03';
GO

-- =================================================================
-- 5. NHẬP ĐIỂM SỐ (MÃ HÓA BẰNG RSA CỦA TỪNG GIẢNG VIÊN)
-- Dùng SP: SP_INS_BANGDIEM (Ép kiểu chuỗi an toàn -> Mã hóa)
-- Params: MASV, MAHP, DIEMTHI, MANV_LOGIN
-- Chú ý: Phải truyền đúng MANV_LOGIN quản lý lớp của SV đó
-- =================================================================

-- NV01 nhập điểm cho SV lớp CNTT01 & CNTT04
EXEC SP_INS_BANGDIEM 'SV01', 'HP01', NULL, 'NV01';
EXEC SP_INS_BANGDIEM 'SV01', 'HP02', 9.0, 'NV01';
EXEC SP_INS_BANGDIEM 'SV01', 'HP03', 7.5, 'NV01';

EXEC SP_INS_BANGDIEM 'SV02', 'HP01', NULL, 'NV01';
EXEC SP_INS_BANGDIEM 'SV02', 'HP04', 8.0, 'NV01';

EXEC SP_INS_BANGDIEM 'SV03', 'HP02', 7.0, 'NV01';
EXEC SP_INS_BANGDIEM 'SV03', 'HP05', 9.5, 'NV01';

-- NV02 nhập điểm cho SV lớp CNTT02 & CNTT05
EXEC SP_INS_BANGDIEM 'SV04', 'HP01', NULL, 'NV02';
EXEC SP_INS_BANGDIEM 'SV04', 'HP02', 8.0, 'NV02';

EXEC SP_INS_BANGDIEM 'SV0', 'HP03', 9.0, 'NV02';
EXEC SP_INS_BANGDIEM 'SV05', 'HP04', 8.5, 'NV02';

EXEC SP_INS_BANGDIEM 'SV06', 'HP05', 6.0, 'NV02';

-- NV03 nhập điểm cho SV lớp CNTT03 & CNTT06
EXEC SP_INS_BANGDIEM 'SV07', 'HP01', 5.5, 'NV03';
EXEC SP_INS_BANGDIEM 'SV07', 'HP04', 6.5, 'NV03';

EXEC SP_INS_BANGDIEM 'SV08', 'HP02', 8.0, 'NV03';
EXEC SP_INS_BANGDIEM 'SV08', 'HP05', 7.5, 'NV03';

EXEC SP_INS_BANGDIEM 'SV09', 'HP01', 9.0, 'NV03';
EXEC SP_INS_BANGDIEM 'SV09', 'HP03', 8.5, 'NV03';
GO
