USE QLSVNhom;
GO

-- Xóa dữ liệu cũ (theo thứ tự FK)
DELETE FROM BANGDIEM;
DELETE FROM SINHVIEN;
DELETE FROM LOP;
DELETE FROM NHANVIEN;
GO

-- ─── Nhân viên (Giảng viên) ───────────────────────────────
EXEC SP_INS_PUBLIC_NHANVIEN 'NV01', N'Nguyễn Văn An',   'nva@edu.vn',  8000000, 'nva', 'abcd12';
EXEC SP_INS_PUBLIC_NHANVIEN 'NV02', N'Trần Thị Bình',   'ttb@edu.vn',  9000000, 'ttb', 'abcd12';
EXEC SP_INS_PUBLIC_NHANVIEN 'NV03', N'Lê Hoàng Cường',  'lhc@edu.vn',  7500000, 'lhc', 'abcd12';
GO

-- ─── Lớp học ─────────────────────────────────────────────
INSERT INTO LOP (MALOP, TENLOP, MANV) VALUES ('CNTT01', N'CNTT Khóa 1', 'NV01');
INSERT INTO LOP (MALOP, TENLOP, MANV) VALUES ('CNTT02', N'CNTT Khóa 2', 'NV02');
INSERT INTO LOP (MALOP, TENLOP, MANV) VALUES ('CNTT03', N'CNTT Khóa 3', 'NV03');
GO
