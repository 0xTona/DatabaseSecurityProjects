"""
sinhvien_screen.py — Quản lý Danh sách Sinh viên
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import call_sp
from crypto_utils import hash_password_sha1, rsa_encrypt, rsa_decrypt, generate_deterministic_rsa
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


def open_sinhvien_screen(root, on_logout_callback, nav_callbacks=None, current_malop=None):
    """Hiển thị màn hình quản lý sinh viên."""
    for w in root.winfo_children():
        w.destroy()

    setup_theme(root)
    root.title("QLSVNhom - Quản lý Sinh viên")
    root.configure(bg=BG)

    W, H = 1000, 700
    root.geometry(f"{W}x{H}")
    root.resizable(True, True)

    # ── Top Bar ─────────────────────────────────────────────────────────────
    top_bar = tk.Frame(root, bg=CARD, height=60)
    top_bar.pack(fill="x", side="top")
    top_bar.pack_propagate(False)

    title_text = f"QUẢN LÝ SINH VIÊN - LỚP {current_malop}" if current_malop else "QUẢN LÝ SINH VIÊN"
    title_lbl = tk.Label(top_bar, text=title_text,
                         font=("Segoe UI", 14, "bold"), bg=CARD, fg=TEXT_PRI)
    title_lbl.pack(side="left", padx=20)

    user_info = f"{session.current_user['HOTEN']} ({session.current_user['MANV']})"
    tk.Label(top_bar, text=f"👤 {user_info}",
             font=("Segoe UI", 11), bg=CARD, fg=ACCENT).pack(side="left", expand=True, anchor="e", padx=20)

    btn_logout = tk.Button(top_bar, text="Đăng xuất", font=("Segoe UI", 10, "bold"),
                           bg="#e63946", fg="white", activebackground="#f07167", activeforeground="white",
                           relief="flat", cursor="hand2", padx=15, command=lambda: root.after(10, on_logout_callback))
    btn_logout.pack(side="right", padx=20)

    if nav_callbacks:
        tk.Button(top_bar, text="Quản lý Lớp học", font=("Segoe UI", 10, "bold"),
                  bg=ACCENT, fg="white", activebackground=ACCENT_HOVER, relief="flat", cursor="hand2", padx=10, 
                  command=lambda: root.after(10, nav_callbacks['lop'])).pack(side="right", padx=5)

    # ── Main Content ────────────────────────────────────────────────────────
    content_frame = tk.Frame(root, bg=BG)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Treeview Sinh viên
    frame_tree_sv = tk.Frame(content_frame, bg=CARD, bd=1, relief="solid")
    frame_tree_sv.pack(fill="both", expand=True, pady=(0, 20))

    cols_sv = ("MASV", "HOTEN", "NGAYSINH", "DIACHI", "MALOP", "TENDN")
    tree_sv = ttk.Treeview(frame_tree_sv, columns=cols_sv, show="headings", selectmode="browse")
    for col, width in zip(cols_sv, [100, 200, 120, 200, 100, 150]):
        tree_sv.heading(col, text=col)
        tree_sv.column(col, width=width, anchor="w")
    tree_sv.pack(fill="both", expand=True, padx=2, pady=2)

    # Form Sinh viên
    form_sv = tk.Frame(content_frame, bg=CARD, pady=15)
    form_sv.pack(fill="x")

    e_masv = create_form_entry(form_sv, 0, 0, "Mã SV:")
    e_hoten = create_form_entry(form_sv, 0, 2, "Họ Tên:")
    e_ngaysinh = create_form_entry(form_sv, 1, 0, "Ngày Sinh (YYYY-MM-DD):")
    e_diachi = create_form_entry(form_sv, 1, 2, "Địa Chỉ:")
    e_malop = create_form_entry(form_sv, 2, 0, "Mã Lớp:")
    
    if current_malop:
        e_malop.insert(0, current_malop)
        e_malop.config(state="disabled")

    e_tendn = create_form_entry(form_sv, 2, 2, "Tên Đăng Nhập:")
    e_matkhau = create_form_entry(form_sv, 3, 0, "Mật khẩu:", show_char="*")

    # Nút bấm Sinh viên
    btn_frame_sv = tk.Frame(content_frame, bg=BG)
    btn_frame_sv.pack(fill="x", pady=15)

    btn_dict = {}
    lop_managers = {}  # Cache cho việc kiểm tra quyền sở hữu lớp
    is_manager = False

    def load_sv():
        nonlocal is_manager
        if not current_malop: return

        # Cập nhật cache quản lý lớp
        lop_managers.clear()
        try:
            for row in call_sp("SP_SEL_LOP", {}):
                lop_managers[row[0]] = row[2]  # MALOP -> MANV
        except:
            pass

        is_manager = (str(lop_managers.get(current_malop, "")) == session.current_user["MANV"])

        for item in tree_sv.get_children():
            tree_sv.delete(item)
            
        try:
            for row in call_sp("SP_SEL_SINHVIEN", {"MALOP": current_malop}):
                ngaysinh = str(row[2])[:10] if row[2] else ""
                tree_sv.insert("", "end", values=(row[0], row[1], ngaysinh, row[3], row[4], row[5]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên:\n{e}")

    def on_select_sv(e):
        selected = tree_sv.selection()
        if selected:
            v = tree_sv.item(selected[0])['values']
            
            e_masv.config(state="normal")
            e_masv.delete(0, 'end'); e_masv.insert(0, v[0])
            e_masv.config(state="disabled")  # Không cho sửa Khóa chính
            
            e_hoten.delete(0, 'end'); e_hoten.insert(0, v[1] if v[1] else "")
            e_ngaysinh.delete(0, 'end'); e_ngaysinh.insert(0, v[2] if v[2] else "")
            e_diachi.delete(0, 'end'); e_diachi.insert(0, v[3] if v[3] else "")
            
            e_tendn.delete(0, 'end'); e_tendn.insert(0, v[5] if v[5] else "")
            e_matkhau.delete(0, 'end')

            # UX Improvement: Disable Update/Delete/Score buttons if user is not the owner
            if not is_manager:
                if "Sửa" in btn_dict: btn_dict["Sửa"].config(state="disabled", bg="#6b7280", cursor="arrow")
                if "Xoá" in btn_dict: btn_dict["Xoá"].config(state="disabled", bg="#6b7280", cursor="arrow")
                if "Quản lý Điểm" in btn_dict: btn_dict["Quản lý Điểm"].config(state="disabled", bg="#6b7280", cursor="arrow")
            else:
                if "Sửa" in btn_dict: btn_dict["Sửa"].config(state="normal", bg="#f59e0b", cursor="hand2")
                if "Xoá" in btn_dict: btn_dict["Xoá"].config(state="normal", bg="#ef4444", cursor="hand2")
                if "Quản lý Điểm" in btn_dict: btn_dict["Quản lý Điểm"].config(state="normal", bg="#8b5cf6", cursor="hand2")

    def clear_sv():
        e_masv.config(state="normal")
        for e in [e_masv, e_hoten, e_ngaysinh, e_diachi, e_tendn, e_matkhau]:
            e.delete(0, 'end')
            
        if is_manager:
            if "Sửa" in btn_dict: btn_dict["Sửa"].config(state="normal", bg="#f59e0b", cursor="hand2")
            if "Xoá" in btn_dict: btn_dict["Xoá"].config(state="normal", bg="#ef4444", cursor="hand2")
            if "Quản lý Điểm" in btn_dict: btn_dict["Quản lý Điểm"].config(state="normal", bg="#8b5cf6", cursor="hand2")
        
        load_sv()

    def add_sv():
        masv, hoten, ngaysinh = e_masv.get(), e_hoten.get(), e_ngaysinh.get()
        diachi, tendn = e_diachi.get(), e_tendn.get()
        matkhau = e_matkhau.get()
        matkhau_hash = bytearray.fromhex(hash_password_sha1(matkhau))
        malop = current_malop
        
        if not (masv and hoten and ngaysinh and malop and tendn and matkhau):
            return messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ thông tin bắt buộc")
            
        manv_login = session.current_user["MANV"]
        try:
            call_sp("SP_INS_SINHVIEN", {
                "MASV": masv,
                "HOTEN": hoten,
                "NGAYSINH": ngaysinh,
                "DIACHI": diachi,
                "MALOP": malop,
                "TENDN": tendn,
                "MATKHAU_HASH": matkhau_hash,
                "MANV_LOGIN": manv_login
            })
            clear_sv()
            messagebox.showinfo("Thành công", "Đã thêm sinh viên.")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def update_sv():
        e_masv.config(state="normal") # Tạm mở để lấy data
        masv = e_masv.get()
        e_masv.config(state="disabled")
        
        hoten, ngaysinh = e_hoten.get(), e_ngaysinh.get()
        diachi, tendn = e_diachi.get(), e_tendn.get()
        
        if not (masv and hoten and ngaysinh and tendn):
            return messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ thông tin bắt buộc")
            
        manv_login = session.current_user["MANV"]
        try:
            call_sp("SP_UPD_SINHVIEN", {
                "MASV": masv,
                "HOTEN": hoten,
                "NGAYSINH": ngaysinh,
                "DIACHI": diachi,
                "TENDN": tendn,
                "MANV_LOGIN": manv_login
            })
            clear_sv()
            messagebox.showinfo("Thành công", "Đã cập nhật sinh viên.")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def delete_sv():
        e_masv.config(state="normal") # Tạm mở để lấy data
        masv = e_masv.get()
        e_masv.config(state="disabled")
        
        if not masv: return
        
        manv_login = session.current_user["MANV"]
        if messagebox.askyesno("Xoá", f"Xoá sinh viên {masv}?"):
            try:
                call_sp("SP_DEL_SINHVIEN", {
                    "MASV": masv,
                    "MANV_LOGIN": manv_login
                })
                clear_sv()
            except Exception as e:
                messagebox.showerror("Loi DB", str(e))

    def open_score_popup():
        selected = tree_sv.selection()
        if not selected:
            return messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một sinh viên từ danh sách để quản lý điểm.")
            
        row_values = tree_sv.item(selected[0])['values']
        masv = row_values[0]
        hoten = row_values[1]
            
        popup = tk.Toplevel(root)
        popup.title("Quản lý Điểm")
        popup.geometry("600x500")
        popup.configure(bg=BG)
        popup.transient(root)
        popup.grab_set()

        # Top
        top_frame = tk.Frame(popup, bg=CARD, pady=10, padx=10)
        top_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(top_frame, text=f"Điểm của SV: {masv}", font=("Segoe UI", 12, "bold"), bg=CARD, fg=TEXT_PRI).pack(side="left")
        
        e_mk_popup = tk.Entry(top_frame, font=("Segoe UI", 10), bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ACCENT, relief="flat", bd=4, width=15, show="*")
        e_mk_popup.pack(side="right", padx=(0, 10))
        tk.Label(top_frame, text="Mật khẩu GV:", font=("Segoe UI", 10), bg=CARD, fg=TEXT_SEC).pack(side="right", padx=(0, 5))

        # Middle
        tree_frame = tk.Frame(popup, bg=CARD, bd=1, relief="solid")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_diem = ttk.Treeview(tree_frame, columns=("MAHP", "DIEMTHI"), show="headings", selectmode="browse")
        for col, w in zip(["MAHP", "DIEMTHI"], [200, 200]):
            tree_diem.heading(col, text=col)
            tree_diem.column(col, width=w, anchor="center")
        tree_diem.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bottom
        bot_frame = tk.Frame(popup, bg=CARD, pady=15, padx=15)
        bot_frame.pack(fill="x", side="bottom", pady=10, padx=10)
        
        tk.Label(bot_frame, text="Mã HP:", font=("Segoe UI", 10), bg=CARD, fg=TEXT_SEC).grid(row=0, column=0, padx=5, pady=5)
        e_mahp_popup = tk.Entry(bot_frame, font=("Segoe UI", 10), bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ACCENT, relief="flat", bd=4, width=15)
        e_mahp_popup.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(bot_frame, text="Điểm Thi:", font=("Segoe UI", 10), bg=CARD, fg=TEXT_SEC).grid(row=0, column=2, padx=5, pady=5)
        e_diem_popup = tk.Entry(bot_frame, font=("Segoe UI", 10), bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ACCENT, relief="flat", bd=4, width=10)
        e_diem_popup.grid(row=0, column=3, padx=5, pady=5)

        def load_popup_scores():
            mk = e_mk_popup.get()
            if not mk:
                return messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập mật khẩu giảng viên.")
            
            private_key, _ = generate_deterministic_rsa(mk, session.current_user["MANV"])
            
            for item in tree_diem.get_children():
                tree_diem.delete(item)
                
            try:
                rows = call_sp("SP_SEL_BANGDIEM", {
                    "MASV": masv,
                    "MANV_LOGIN": session.current_user["MANV"]
                })

                for r in rows:
                    mahp = r[1]
                    diem_encrypt = r[2]
                    try:
                        diem_decrypt = rsa_decrypt(private_key, diem_encrypt)
                    except Exception:
                        diem_decrypt = "Sai MK / Lỗi giải mã"
                    tree_diem.insert("", "end", values=(mahp, diem_decrypt))
            except Exception as e:
                messagebox.showerror("Lỗi DB", str(e))


        def on_select_diem(e):
            selected = tree_diem.selection()
            if selected:
                v = tree_diem.item(selected[0])['values']
                e_mahp_popup.config(state="normal")
                e_mahp_popup.delete(0, 'end')
                e_mahp_popup.insert(0, v[0])
                e_mahp_popup.config(state="disabled") # Disable when editing existing score
                
                e_diem_popup.delete(0, 'end')
                e_diem_popup.insert(0, v[1])

        tree_diem.bind("<<TreeviewSelect>>", on_select_diem)

        btn_xem = tk.Button(top_frame, text="Xem Điểm", font=("Segoe UI", 10, "bold"),
                            bg=ACCENT, fg="white", activebackground=ACCENT_HOVER, relief="flat", cursor="hand2", padx=10, command=load_popup_scores)
        btn_xem.pack(side="right", padx=(10, 10))

        def save_popup_score():
            e_mahp_popup.config(state="normal")
            mahp = e_mahp_popup.get().strip()
            
            diem = e_diem_popup.get().strip()
            
            if not (mahp and diem):
                return messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Ma HP và Điểm.")
                
            try:
                diem_float = float(diem)
                if diem_float < 0 or diem_float > 10:
                    return messagebox.showerror("Lỗi", "Điểm thi phải từ 0 đến 10.")
            except ValueError:
                return messagebox.showerror("Lỗi", "Điểm thi phải là số.")
                
            try:
                public_key = session.current_user["PUBKEY"]
                diem_encrypt = bytearray(rsa_encrypt(public_key, str(diem_float)))
                
                call_sp("SP_INS_BANGDIEM", {
                    "MASV": masv,
                    "MAHP": mahp,
                    "DIEMTHI_ENCRYPT": diem_encrypt,
                    "MANV_LOGIN": session.current_user["MANV"]
                })
                messagebox.showinfo("Thành công", "Đã lưu điểm.")
                e_mahp_popup.delete(0, 'end')
                e_diem_popup.delete(0, 'end')
                e_mahp_popup.config(state="normal")
                
                if e_mk_popup.get():
                    load_popup_scores()
            except Exception as e:
                messagebox.showerror("Lỗi DB", str(e))

        btn_luu = tk.Button(bot_frame, text="Lưu Điểm", font=("Segoe UI", 10, "bold"),
                            bg="#10b981", fg="white", activebackground="white", activeforeground="black",
                            relief="flat", cursor="hand2", padx=20, command=save_popup_score)
        btn_luu.grid(row=0, column=4, padx=(15, 0))

    tree_sv.bind("<<TreeviewSelect>>", on_select_sv)

    # Rendering Buttons
    def render_btns(parent, cmds):
        colors = {"Thêm": "#10b981", "Sửa": "#f59e0b", "Xoá": "#ef4444", "Quản lý Điểm": "#8b5cf6", "Làm mới": "#6b7280"}
        for txt, cmd in cmds:
            btn = tk.Button(parent, text=txt, font=("Segoe UI", 10, "bold"),
                            bg=colors.get(txt, "#6b7280"), fg="white", activebackground="white", activeforeground="black",
                            relief="flat", cursor="hand2", padx=20, pady=8, command=cmd)
            btn.pack(side="left", padx=5)
            btn_dict[txt] = btn

    render_btns(btn_frame_sv, [("Thêm", add_sv), ("Sửa", update_sv), ("Xoá", delete_sv), ("Quản lý Điểm", open_score_popup), ("Làm mới", clear_sv)])

    # Khởi tạo data
    load_sv()

    if not is_manager:
        for b in ["Thêm", "Sửa", "Xoá", "Quản lý Điểm"]:
            if b in btn_dict:
                btn_dict[b].config(state="disabled", bg="#6b7280", cursor="arrow")
