current_user: dict = {
    "MANV": None,
    "HOTEN": None,
    "EMAIL": None,
    "LUONGCB": None,
    "PUBKEY": None,
    "ISADMIN": False,
}


def set_user(row) -> None:
    """Gán thông tin người dùng sau khi đăng nhập thành công."""
    current_user["MANV"] = row[0]
    current_user["HOTEN"] = row[1]
    current_user["EMAIL"] = row[2]
    current_user["LUONGCB"] = row[3]
    current_user["PUBKEY"] = row[4]
    current_user["ISADMIN"] = bool(row[5]) if len(row) > 5 else False


def clear_user() -> None:
    """Xóa session khi đăng xuất."""
    for k in current_user:
        current_user[k] = None
    current_user["ISADMIN"] = False


def is_logged_in() -> bool:
    return current_user["MANV"] is not None


def is_admin() -> bool:
    return current_user.get("ISADMIN", False)
