"""
lop_screen.py — Quản lý Danh sách lớp học (Giao diện hiện đại).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from db_connection import call_sp
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


def create_form_entry(parent, row, col, label_text):
    """Helper: Tạo label & entry trong form."""
    tk.Label(parent, text=label_text, font=("Segoe UI", 10),
             bg=CARD, fg=TEXT_SEC).grid(row=row, column=col, padx=(20, 5), pady=8, sticky="e")
    entry = tk.Entry(parent, font=("Segoe UI", 10), bg=ENTRY_BG, fg=ENTRY_FG,
                     insertbackground=ACCENT, relief="flat", bd=4, width=25)
    entry.grid(row=row, column=col + 1, padx=(0, 20), pady=8, sticky="w")
    return entry


def open_lop_screen(root, on_logout_callback, nav_callbacks=None):
    """Hiển thị màn hình quản lý lớp học."""
    for w in root.winfo_children():
        w.destroy()

    setup_theme(root)
    root.title("QLSVNhom — Quản lý Lớp học")
    root.configure(bg=BG)

    W, H = 900, 600
    root.geometry(f"{W}x{H}")
    root.resizable(True, True)

    # ── Top Bar ─────────────────────────────────────────────────────────────
    top_bar = tk.Frame(root, bg=CARD, height=60)
    top_bar.pack(fill="x", side="top")
    top_bar.pack_propagate(False)

    title_lbl = tk.Label(top_bar, text="🏫 QUẢN LÝ LỚP HỌC",
                         font=("Segoe UI", 14, "bold"), bg=CARD, fg=TEXT_PRI)
    title_lbl.pack(side="left", padx=20)

    user_info = f"{session.current_user['HOTEN']} ({session.current_user['MANV']})"
    tk.Label(top_bar, text=f"👤 {user_info}",
             font=("Segoe UI", 11), bg=CARD, fg=ACCENT).pack(side="left", expand=True, anchor="e", padx=20)

    btn_logout = tk.Button(top_bar, text="Đăng xuất", font=("Segoe UI", 10, "bold"),
                           bg="#e63946", fg="white", activebackground="#f07167", activeforeground="white",
                           relief="flat", cursor="hand2", padx=15, command=on_logout_callback)
    btn_logout.pack(side="right", padx=20)

    # ── Main Content ────────────────────────────────────────────────────────
    content_frame = tk.Frame(root, bg=BG)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Treeview Lớp
    frame_tree_lop = tk.Frame(content_frame, bg=CARD, bd=1, relief="solid")
    frame_tree_lop.pack(fill="both", expand=True, pady=(0, 20))

    cols_lop = ("MALOP", "TENLOP", "MANV", "TEN_GVCN")
    tree_lop = ttk.Treeview(frame_tree_lop, columns=cols_lop, show="headings", selectmode="browse")
    for col, width in zip(cols_lop, [100, 300, 100, 300]):
        tree_lop.heading(col, text=col)
        tree_lop.column(col, width=width, anchor="w")
    tree_lop.pack(fill="both", expand=True, padx=2, pady=2)

    # Form Lớp
    form_lop = tk.Frame(content_frame, bg=CARD, pady=15)
    form_lop.pack(fill="x")

    e_malop = create_form_entry(form_lop, 0, 0, "Mã Lớp:")
    e_tenlop = create_form_entry(form_lop, 0, 2, "Tên Lớp:")
    e_manv = create_form_entry(form_lop, 1, 0, "Mã GVCN:")

    # Nút bấm Lớp
    btn_frame_lop = tk.Frame(content_frame, bg=BG)
    btn_frame_lop.pack(fill="x", pady=15)

    def load_lop():
        for item in tree_lop.get_children():
            tree_lop.delete(item)
        try:
            for row in call_sp("SP_SEL_LOP", {}):
                tree_lop.insert("", "end", values=(row[0], row[1], row[2], row[3]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp:\n{e}")

    def on_select_lop(e):
        selected = tree_lop.selection()
        if selected:
            v = tree_lop.item(selected[0])['values']
            e_malop.config(state="normal")
            e_malop.delete(0, 'end'); e_malop.insert(0, v[0])
            e_malop.config(state="readonly")  # Không cho sửa Khóa chính
            e_tenlop.delete(0, 'end'); e_tenlop.insert(0, v[1])
            e_manv.delete(0, 'end'); e_manv.insert(0, v[2] if v[2] else "")

    def clear_lop():
        e_malop.config(state="normal")
        e_malop.delete(0, 'end'); e_tenlop.delete(0, 'end'); e_manv.delete(0, 'end')
        load_lop()

    def add_lop():
        ml, tl, mn = e_malop.get(), e_tenlop.get(), e_manv.get()
        if not (ml and tl and mn): return messagebox.showwarning("Thiếu", "Nhập đủ thông tin")
        try:
            call_sp("SP_INS_LOP", {"MALOP": ml, "TENLOP": tl, "MANV": mn})
            clear_lop()
            messagebox.showinfo("Thành công", "Đã thêm lớp.")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def update_lop():
        ml, tl, mn = e_malop.get(), e_tenlop.get(), e_manv.get()
        if not (ml and tl and mn): return messagebox.showwarning("Thiếu", "Nhập đủ thông tin")
        try:
            call_sp("SP_UPD_LOP", {"MALOP": ml, "TENLOP": tl, "MANV": mn})
            clear_lop()
            messagebox.showinfo("Thành công", "Đã cập nhật lớp.")
        except Exception as e:
            messagebox.showerror("Lỗi DB", str(e))

    def delete_lop():
        ml = e_malop.get()
        if not ml: return
        if messagebox.askyesno("Xóa", f"Xóa lớp {ml}?"):
            try:
                call_sp("SP_DEL_LOP", {"MALOP": ml})
                clear_lop()
            except Exception as e:
                messagebox.showerror("Lỗi DB", str(e))

    def goto_sv():
        malop = e_malop.get().strip()
        if not malop:
            return messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn một lớp từ danh sách.")

        if malop and nav_callbacks and 'sv' in nav_callbacks:
            root.after(10, lambda: nav_callbacks['sv'](malop))


    tree_lop.bind("<<TreeviewSelect>>", on_select_lop)

    # Rendering Buttons
    def render_btns(parent, cmds):
        colors = {"Thêm": "#10b981", "Sửa": "#f59e0b", "Xóa": "#ef4444", "Quản lý Sinh viên": "#3b82f6", "Làm mới": "#6b7280"}
        for txt, cmd in cmds:
            tk.Button(parent, text=txt, font=("Segoe UI", 10, "bold"),
                      bg=colors[txt], fg="white", activebackground="white", activeforeground="black",
                      relief="flat", cursor="hand2", padx=20, pady=8, command=cmd).pack(side="left", padx=5)

    render_btns(btn_frame_lop, [("Thêm", add_lop), ("Sửa", update_lop), ("Xóa", delete_lop), ("Quản lý Sinh viên", goto_sv), ("Làm mới", clear_lop)])

    # Khởi tạo data
    load_lop()
