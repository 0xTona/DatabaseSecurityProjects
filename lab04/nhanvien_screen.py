"""
nhanvien_screen.py — Quản lý Danh sách Nhân viên
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import call_sp
from crypto_utils import hash_password_sha1, rsa_encrypt, generate_deterministic_rsa
import session

# ── Colors ──────────────────────────────────────────────────────────────────
BG = "#0f1117"
CARD = "#1a1d27"
ACCENT = "#4f8ef7"
ACCENT_HOVER = "#3b82f6"
TEXT_PRI = "#f0f4ff"
TEXT_SEC = "#8892a4"
ENTRY_BG = "#252836"
ENTRY_FG = "#e2e8f0"
BORDER = "#2e3347"


def setup_theme(root):
    """Cấu hình style ttk cho giao diện dark."""
    style = ttk.Style(root)
    style.theme_use("default")

    # Treeview
    style.configure("Treeview",
                    background=ENTRY_BG,
                    foreground=ENTRY_FG,
                    fieldbackground=ENTRY_BG,
                    borderwidth=0,
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
                    background=CARD,
                    foreground=TEXT_SEC,
                    borderwidth=1,
                    relief="flat",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", ACCENT)])
    style.map("Treeview.Heading", background=[("active", BORDER)])


def create_form_entry(parent, row, col, label_text, show_char=""):
    """Helper: Tạo label & entry trong form."""
    tk.Label(parent, text=label_text, font=("Segoe UI", 10),
             bg=CARD, fg=TEXT_SEC).grid(row=row, column=col, padx=(20, 5), pady=8, sticky="e")
    entry = tk.Entry(parent, font=("Segoe UI", 10), bg=ENTRY_BG, fg=ENTRY_FG,
                     insertbackground=ACCENT, relief="flat", bd=4, width=25, show=show_char)
    entry.grid(row=row, column=col + 1, padx=(0, 20), pady=8, sticky="w")
    return entry


def open_nhanvien_screen(root, on_logout_callback, nav_callbacks=None):
    """Hiển thị màn hình quản lý nhân viên (chỉ dành cho Admin)."""
    # ── Admin guard ──────────────────────────────────────────────────────
    if not session.is_admin():
        messagebox.showwarning("Không có quyền", "Chỉ Admin mới được quản lý nhân viên.")
        if nav_callbacks and 'lop' in nav_callbacks:
            root.after(10, nav_callbacks['lop'])
        return

    for w in root.winfo_children():
        w.destroy()

    setup_theme(root)
    root.title("QLSVNhom — Quản lý Nhân viên")
    root.configure(bg=BG)

    W, H = 1000, 700
    root.geometry(f"{W}x{H}")
    root.resizable(True, True)

    # ── Top Bar ─────────────────────────────────────────────────────────────
    top_bar = tk.Frame(root, bg=CARD, height=60)
    top_bar.pack(fill="x", side="top")
    top_bar.pack_propagate(False)

    title_lbl = tk.Label(top_bar, text="👨‍💼 QUẢN LÝ NHÂN VIÊN",
                         font=("Segoe UI", 14, "bold"), bg=CARD, fg=TEXT_PRI)
    title_lbl.pack(side="left", padx=20)

    user_info = f"{session.current_user['HOTEN']} ({session.current_user['MANV']})"
    tk.Label(top_bar, text=f"👤 {user_info}",
             font=("Segoe UI", 11), bg=CARD, fg=ACCENT).pack(side="left", expand=True, anchor="e", padx=20)

    btn_logout = tk.Button(top_bar, text="Đăng xuất", font=("Segoe UI", 10, "bold"),
                           bg="#e63946", fg="white", activebackground="#f07167", activeforeground="white",
                           relief="flat", cursor="hand2", padx=15, command=on_logout_callback)
    btn_logout.pack(side="right", padx=20)

    if nav_callbacks:
        tk.Button(top_bar, text="Quản lý Lớp học", font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg="white", activebackground=ACCENT_HOVER, relief="flat", cursor="hand2", padx=10, 
                  command=lambda: root.after(10, nav_callbacks['lop'])).pack(side="right", padx=5)

    # ── Main Content ────────────────────────────────────────────────────────
    content_frame = tk.Frame(root, bg=BG)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Treeview Nhân viên
    frame_tree_nv = tk.Frame(content_frame, bg=CARD, bd=1, relief="solid")
    frame_tree_nv.pack(fill="both", expand=True, pady=(0, 20))

    cols_nv = ("MANV", "HOTEN", "EMAIL", "TENDN", "PUBKEY_STATUS", "ROLE")
    tree_nv = ttk.Treeview(frame_tree_nv, columns=cols_nv, show="headings", selectmode="browse")
    for col, width in zip(cols_nv, [100, 200, 180, 130, 120, 80]):
        tree_nv.heading(col, text=col)
        tree_nv.column(col, width=width, anchor="w")
    tree_nv.pack(fill="both", expand=True, padx=2, pady=2)

    # Form Nhân viên
    form_nv = tk.Frame(content_frame, bg=CARD, pady=15)
    form_nv.pack(fill="x")

    e_manv = create_form_entry(form_nv, 0, 0, "Mã NV:")
    e_hoten = create_form_entry(form_nv, 0, 2, "Họ Tên:")
    e_email = create_form_entry(form_nv, 1, 0, "Email:")
    e_luongcb = create_form_entry(form_nv, 1, 2, "Lương CB:")
    e_tendn = create_form_entry(form_nv, 2, 0, "Tên Đăng Nhập:")
    e_matkhau = create_form_entry(form_nv, 2, 2, "Mật khẩu:", show_char="*")

    # Nút bấm Nhân viên
    btn_frame_nv = tk.Frame(content_frame, bg=BG)
    btn_frame_nv.pack(fill="x", pady=15)

    btn_dict = {}

    def load_nv():
        for item in tree_nv.get_children():
            tree_nv.delete(item)
        try:
            for row in call_sp("SP_SEL_NHANVIEN", {}):
                pubkey_status = "[Có Key]" if row[4] else "[Trống]"
                is_admin_flag = "Admin" if row[5] else ""
                tree_nv.insert("", "end", values=(row[0], row[1], row[2], row[3], pubkey_status, is_admin_flag))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách nhân viên:\n{e}")

    def on_select_nv(e):
        selected = tree_nv.selection()
        if selected:
            v = tree_nv.item(selected[0])['values']
            e_manv.config(state="normal")
            e_manv.delete(0, 'end'); e_manv.insert(0, v[0])
            e_manv.config(state="readonly")
            
            e_hoten.delete(0, 'end'); e_hoten.insert(0, v[1] if v[1] else "")
            e_email.delete(0, 'end'); e_email.insert(0, v[2] if v[2] else "")
            
            # Reset the confidential fields on selection
            e_tendn.delete(0, 'end'); e_tendn.insert(0, v[3] if v[3] else "")
            e_luongcb.delete(0, 'end')
            e_matkhau.delete(0, 'end')

            if "Thêm" in btn_dict: btn_dict["Thêm"].config(state="disabled", bg="#6b7280")
            if "Sửa" in btn_dict: btn_dict["Sửa"].config(state="normal", bg="#f59e0b")
            if "Xóa" in btn_dict: btn_dict["Xóa"].config(state="normal", bg="#ef4444")

    def clear_nv():
        e_manv.config(state="normal")
        for e in [e_manv, e_hoten, e_email, e_luongcb, e_tendn, e_matkhau]:
            e.delete(0, 'end')
        
        if "Thêm" in btn_dict: btn_dict["Thêm"].config(state="normal", bg="#10b981")
        if "Sửa" in btn_dict: btn_dict["Sửa"].config(state="disabled", bg="#6b7280")
        if "Xóa" in btn_dict: btn_dict["Xóa"].config(state="disabled", bg="#6b7280")
            
        load_nv()

    def add_nv():
        manv = e_manv.get()
        hoten = e_hoten.get()
        email = e_email.get()
        luong = e_luongcb.get()
        tendn = e_tendn.get()
        mk = e_matkhau.get()
        
        if not (manv and hoten and luong and tendn and mk):
            return messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ thông tin bắt buộc (MANV, HOTEN, LUONGCB, TENDN, MATKHAU).")
            
        try:
            # 1. Sinh khóa RSA deterministically based on mk and manv
            private_key, public_key = generate_deterministic_rsa(mk, manv)
            
            # 2. Mã hóa lương bằng khóa public
            luong_encrypt = bytearray(rsa_encrypt(public_key, luong))
            
            # 3. Băm mật khẩu
            matkhau_hash = bytearray.fromhex(hash_password_sha1(mk))
            
            # 4. Lưu vào DB
            call_sp("SP_INS_PUBLIC_ENCRYPT_NHANVIEN", {
                "MANV": manv,
                "HOTEN": hoten,
                "EMAIL": email,
                "LUONG": luong_encrypt,
                "TENDN": tendn,
                "MATKHAU_HASH": matkhau_hash,
                "PUBKEY": public_key.decode('utf-8'),
                "MANV_LOGIN": session.current_user["MANV"]
            })
            clear_nv()
            messagebox.showinfo("Thành công", "Đã thêm nhân viên.")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def update_nv():
        e_manv.config(state="normal")
        manv = e_manv.get()
        e_manv.config(state="readonly")
        
        hoten = e_hoten.get()
        email = e_email.get()
        
        if not manv: return
        
        try:
            call_sp("SP_UPD_NHANVIEN", {
                "MANV": manv,
                "HOTEN": hoten,
                "EMAIL": email,
                "MANV_LOGIN": session.current_user["MANV"]
            })
            clear_nv()
            messagebox.showinfo("Thành công", "Đã cập nhật nhân viên.")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def delete_nv():
        e_manv.config(state="normal")
        manv = e_manv.get()
        e_manv.config(state="readonly")
        
        if not manv: return
        
        if messagebox.askyesno("Xóa", f"Xóa nhân viên {manv}?"):
            try:
                call_sp("SP_DEL_NHANVIEN", {"MANV": manv, "MANV_LOGIN": session.current_user["MANV"]})
                clear_nv()
            except Exception as e:
                messagebox.showerror("Lỗi DB", str(e))

    tree_nv.bind("<<TreeviewSelect>>", on_select_nv)

    # Rendering Buttons
    def render_btns(parent, cmds):
        nonlocal btn_dict
        colors = {"Thêm": "#10b981", "Sửa": "#f59e0b", "Xóa": "#ef4444", "Làm mới": "#6b7280"}
        for txt, cmd in cmds:
            btn = tk.Button(parent, text=txt, font=("Segoe UI", 10, "bold"),
                      bg=colors.get(txt, "#3b82f6"), fg="white", activebackground="white", activeforeground="black",
                      relief="flat", cursor="hand2", padx=20, pady=8, command=cmd)
            btn.pack(side="left", padx=5)
            btn_dict[txt] = btn

    render_btns(btn_frame_nv, [("Thêm", add_nv), ("Sửa", update_nv), ("Xóa", delete_nv), ("Làm mới", clear_nv)])

    # Khởi tạo data
    clear_nv()
