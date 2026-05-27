USE QLSVNhom;

-- quản lý đăng nhập
GO 
CREATE
    OR ALTER PROCEDURE SP_SEL_PUBLIC_NHANVIEN @TENDN NVARCHAR(100),
    @MK NVARCHAR(100) AS BEGIN
SET NOCOUNT ON;
DECLARE @MANV NVARCHAR(20);
DECLARE @LUONG_ENCRYPT VARBINARY(MAX);
SELECT @MANV = MANV,
    @LUONG_ENCRYPT = LUONG
FROM NHANVIEN
WHERE TENDN = @TENDN;
IF @MANV IS NULL BEGIN PRINT N'TENDN NOT EXISTS';
RETURN;
END IF NOT EXISTS (
    SELECT 1
    FROM NHANVIEN
    WHERE TENDN = @TENDN
        AND MATKHAU = HASHBYTES('SHA2_512', @MK)
) BEGIN PRINT N'MAT KHAU ERROR';
RETURN;
END
DECLARE @LUONGCB INT;
SET @LUONGCB = CAST(
        DecryptByAsymKey(AsymKey_ID(@MANV), @LUONG_ENCRYPT, @MK) AS INT
    );
SELECT MANV,
    HOTEN,
    EMAIL,
    @LUONGCB AS LUONGCB,
    PUBKEY
FROM NHANVIEN
WHERE TENDN = @TENDN;
END

-- =================================================================
-- 1. QUẢN LÝ LỚP HỌC
-- =================================================================

-- 1. SP_SEL_LOP
GO 
CREATE OR ALTER PROCEDURE SP_SEL_LOP AS BEGIN
SET NOCOUNT ON;
SELECT L.MALOP,
    L.TENLOP,
    L.MANV,
    N.HOTEN AS TEN_GVCN
FROM LOP L
    LEFT JOIN NHANVIEN N ON L.MANV = N.MANV
ORDER BY L.MALOP;
END

GO
-- 2. SP_INS_LOP
CREATE OR ALTER PROCEDURE SP_INS_LOP
    @MALOP VARCHAR(20),
    @TENLOP NVARCHAR(100),
    @MANV VARCHAR(20),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Kiểm tra: Mã GVCN được gán có đúng là người đang đăng nhập không?
    IF @MANV <> @MANV_LOGIN
    BEGIN
        THROW 50001, 'Unauthorized action: You can only assign yourself as the manager of a new class.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        INSERT INTO LOP (MALOP, TENLOP, MANV)
        VALUES (@MALOP, @TENLOP, @MANV);
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

-- 3. SP_UPD_LOP
CREATE OR ALTER PROCEDURE SP_UPD_LOP
    @MALOP VARCHAR(20),
    @TENLOP NVARCHAR(100),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = @MALOP AND MANV = @MANV_LOGIN)
    BEGIN
        THROW 50001, 'Unauthorized action: You do not manage this class.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        UPDATE LOP
        SET TENLOP = @TENLOP
        WHERE MALOP = @MALOP;
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

-- 4. SP_DEL_LOP
CREATE OR ALTER PROCEDURE SP_DEL_LOP
    @MALOP VARCHAR(20),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = @MALOP AND MANV = @MANV_LOGIN)
    BEGIN
        THROW 50001, 'Unauthorized action: You do not manage this class.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        -- Delete class. (Assuming no students attached, else FK error will occur safely)
        DELETE FROM LOP WHERE MALOP = @MALOP;
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO


-- GO 
-- CREATE
--     OR ALTER PROCEDURE SP_INS_LOP @MALOP VARCHAR(20),
--     @TENLOP NVARCHAR(100),
--     @MANV VARCHAR(20) AS BEGIN
-- SET NOCOUNT ON;
-- INSERT INTO LOP (MALOP, TENLOP, MANV)
-- VALUES (@MALOP, @TENLOP, @MANV);
-- END

-- GO 
-- CREATE
--     OR ALTER PROCEDURE SP_UPD_LOP @MALOP VARCHAR(20),
--     @TENLOP NVARCHAR(100),
--     @MANV VARCHAR(20) AS BEGIN
-- SET NOCOUNT ON;
-- UPDATE LOP
-- SET TENLOP = @TENLOP,
--     MANV = @MANV
-- WHERE MALOP = @MALOP;
-- END

-- GO 
-- CREATE
--     OR ALTER PROCEDURE SP_DEL_LOP @MALOP VARCHAR(20) AS BEGIN
-- SET NOCOUNT ON;
-- UPDATE SINHVIEN
-- SET MALOP = NULL
-- WHERE MALOP = @MALOP;
-- DELETE FROM LOP
-- WHERE MALOP = @MALOP;
-- END
-- GO




-- =======================================================
-- 2. QUẢN LÝ SINH VIÊN
-- =======================================================


-- 1. SP_SEL_SINHVIEN
CREATE OR ALTER PROCEDURE SP_SEL_SINHVIEN
    @MALOP VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT MASV, HOTEN, NGAYSINH, DIACHI, MALOP, TENDN 
    FROM SINHVIEN
    WHERE MALOP = @MALOP
    ORDER BY MASV;
END
GO

-- 2. SP_INS_SINHVIEN
CREATE OR ALTER PROCEDURE SP_INS_SINHVIEN
    @MASV VARCHAR(20),
    @HOTEN NVARCHAR(100),
    @NGAYSINH DATETIME,
    @DIACHI NVARCHAR(200),
    @MALOP VARCHAR(20),
    @TENDN NVARCHAR(100),
    @MATKHAU_HASH VARBINARY(MAX),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check Authorization: Is @MANV_LOGIN the manager of @MALOP?
    DECLARE @Manager VARCHAR(20);
    SELECT @Manager = MANV FROM LOP WHERE MALOP = @MALOP;
    
    IF @Manager IS NULL OR @Manager <> @MANV_LOGIN
    BEGIN
        THROW 50001, 'Authorization Failed: You can only add students to the class you manage.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        
        INSERT INTO SINHVIEN (MASV, HOTEN, NGAYSINH, DIACHI, MALOP, TENDN, MATKHAU)
        VALUES (@MASV, @HOTEN, @NGAYSINH, @DIACHI, @MALOP, @TENDN, @MATKHAU_HASH);
        
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

-- 3. SP_UPD_SINHVIEN
CREATE OR ALTER PROCEDURE SP_UPD_SINHVIEN
    @MASV VARCHAR(20),
    @HOTEN NVARCHAR(100),
    @NGAYSINH DATETIME,
    @DIACHI NVARCHAR(200),
    @TENDN NVARCHAR(100),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Find current MALOP for the student
    DECLARE @MALOP VARCHAR(20);
    SELECT @MALOP = MALOP FROM SINHVIEN WHERE MASV = @MASV;
    
    IF @MALOP IS NULL
    BEGIN
        THROW 50001, 'Student not found.', 1;
    END
    
    -- Check Authorization: Is @MANV_LOGIN the manager of the student's current class?
    DECLARE @Manager VARCHAR(20);
    SELECT @Manager = MANV FROM LOP WHERE MALOP = @MALOP;
    
    IF @Manager IS NULL OR @Manager <> @MANV_LOGIN
    BEGIN
        THROW 50001, 'Authorization Failed: You can only update students in the class you manage.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        
        UPDATE SINHVIEN
        SET HOTEN = @HOTEN,
            NGAYSINH = @NGAYSINH,
            DIACHI = @DIACHI,
            TENDN = @TENDN
        WHERE MASV = @MASV;
        
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

-- 4. SP_DEL_SINHVIEN
CREATE OR ALTER PROCEDURE SP_DEL_SINHVIEN
    @MASV VARCHAR(20),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Find current MALOP for the student
    DECLARE @MALOP VARCHAR(20);
    SELECT @MALOP = MALOP FROM SINHVIEN WHERE MASV = @MASV;
    
    IF @MALOP IS NULL
    BEGIN
        THROW 50001, 'Student not found.', 1;
    END
    
    -- Check Authorization: Is @MANV_LOGIN the manager of the student's current class?
    DECLARE @Manager VARCHAR(20);
    SELECT @Manager = MANV FROM LOP WHERE MALOP = @MALOP;
    
    IF @Manager IS NULL OR @Manager <> @MANV_LOGIN
    BEGIN
        THROW 50001, 'Authorization Failed: You can only delete students in the class you manage.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        
        -- Delete dependent records if any exist in BANGDIEM to avoid FK constraint violation
        DELETE FROM BANGDIEM WHERE MASV = @MASV;
        
        DELETE FROM SINHVIEN WHERE MASV = @MASV;
        
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

-- =======================================================
-- 3. QUẢN LÝ BẢNG ĐIỂM
-- =======================================================

CREATE OR ALTER PROCEDURE SP_INS_BANGDIEM
    @MASV VARCHAR(20),
    @MAHP VARCHAR(20),
    @DIEMTHI_ENCRYPT VARBINARY(MAX),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Kiểm tra quyền: Có phải sinh viên lớp mình quản lý không?
    DECLARE @MALOP VARCHAR(20);
    SELECT @MALOP = MALOP FROM SINHVIEN WHERE MASV = @MASV;
    
    IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = @MALOP AND MANV = @MANV_LOGIN)
    BEGIN
        THROW 50001, N'Từ chối truy cập: Bạn không quản lý lớp của sinh viên này.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        
        IF EXISTS (SELECT 1 FROM BANGDIEM WHERE MASV = @MASV AND MAHP = @MAHP)
        BEGIN
            UPDATE BANGDIEM
            SET DIEMTHI = @DIEMTHI_ENCRYPT
            WHERE MASV = @MASV AND MAHP = @MAHP;
        END
        ELSE
        BEGIN
            INSERT INTO BANGDIEM (MASV, MAHP, DIEMTHI)
            VALUES (@MASV, @MAHP, @DIEMTHI_ENCRYPT);
        END
        
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE SP_SEL_BANGDIEM
    @MASV VARCHAR(20),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- Kiểm tra quyền: Có phải sinh viên lớp mình quản lý không?
    DECLARE @MALOP VARCHAR(20);
    SELECT @MALOP = MALOP FROM SINHVIEN WHERE MASV = @MASV;
    
    IF NOT EXISTS (SELECT 1 FROM LOP WHERE MALOP = @MALOP AND MANV = @MANV_LOGIN)
    BEGIN
        THROW 50001, N'Từ chối truy cập: Bạn không quản lý lớp của sinh viên này.', 1;
    END

    -- Lọc sinh viên theo lớp quản lý & Giải mã điểm bằng @PUBKEY
    SELECT 
        BD.MASV, 
        BD.MAHP, 
        BD.DIEMTHI
    FROM BANGDIEM BD
    INNER JOIN SINHVIEN SV ON BD.MASV = SV.MASV
    INNER JOIN LOP L ON SV.MALOP = L.MALOP
    WHERE L.MANV = @MANV_LOGIN AND BD.MASV = @MASV;
END
GO

-- =======================================================
-- 4. QUẢN LÝ NHÂN VIÊN (LAB 4)
-- =======================================================

CREATE OR ALTER PROCEDURE SP_SEL_PUBLIC_ENCRYPT_NHANVIEN
    @TENDN NVARCHAR(100),
    @MATKHAU_HASH VARBINARY(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF NOT EXISTS (
        SELECT 1
        FROM NHANVIEN
        WHERE TENDN = @TENDN AND MATKHAU = @MATKHAU_HASH
    )
    BEGIN
        THROW 50001, 'Invalid username or password.', 1;
    END

    SELECT MANV,
        HOTEN,
        EMAIL,
        LUONG,
        PUBKEY,
        ISADMIN
    FROM NHANVIEN
    WHERE TENDN = @TENDN;
END
GO

CREATE OR ALTER PROCEDURE SP_SEL_NHANVIEN
AS
BEGIN
    SET NOCOUNT ON;
    SELECT MANV, HOTEN, EMAIL, TENDN, PUBKEY, ISADMIN
    FROM NHANVIEN
    ORDER BY MANV;
END
GO

CREATE OR ALTER PROCEDURE SP_INS_PUBLIC_ENCRYPT_NHANVIEN
    @MANV VARCHAR(20),
    @HOTEN NVARCHAR(100),
    @EMAIL VARCHAR(20),
    @LUONG VARBINARY(MAX),
    @TENDN NVARCHAR(100),
    @MATKHAU_HASH VARBINARY(MAX),
    @PUBKEY VARCHAR(MAX),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- Only admin can add employees
    IF NOT EXISTS (SELECT 1 FROM NHANVIEN WHERE MANV = @MANV_LOGIN AND ISADMIN = 1)
    BEGIN
        THROW 50001, 'Unauthorized: Only admin can add employees.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        INSERT INTO NHANVIEN (MANV, HOTEN, EMAIL, LUONG, TENDN, MATKHAU, PUBKEY, ISADMIN)
        VALUES (@MANV, @HOTEN, @EMAIL, @LUONG, @TENDN, @MATKHAU_HASH, @PUBKEY, 0);
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE SP_UPD_NHANVIEN
    @MANV VARCHAR(20),
    @HOTEN NVARCHAR(100),
    @EMAIL VARCHAR(20),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- Only admin can update employees
    IF NOT EXISTS (SELECT 1 FROM NHANVIEN WHERE MANV = @MANV_LOGIN AND ISADMIN = 1)
    BEGIN
        THROW 50001, 'Unauthorized: Only admin can update employees.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        UPDATE NHANVIEN
        SET HOTEN = @HOTEN, EMAIL = @EMAIL
        WHERE MANV = @MANV;
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE SP_DEL_NHANVIEN
    @MANV VARCHAR(20),
    @MANV_LOGIN VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- Only admin can delete employees
    IF NOT EXISTS (SELECT 1 FROM NHANVIEN WHERE MANV = @MANV_LOGIN AND ISADMIN = 1)
    BEGIN
        THROW 50001, 'Unauthorized: Only admin can delete employees.', 1;
    END

    -- Admin cannot delete themselves
    IF @MANV = @MANV_LOGIN
    BEGIN
        THROW 50001, 'Unauthorized: Admin cannot delete their own account.', 1;
    END

    BEGIN TRY
        BEGIN TRAN;
        DELETE FROM NHANVIEN WHERE MANV = @MANV;
        COMMIT TRAN;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRAN;
        THROW;
    END CATCH
END
GO
