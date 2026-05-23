"""
login_screen.py — Màn hình đăng nhập với giao diện hiện đại.
"""

import tkinter as tk
from tkinter import font as tkfont
from db_connection import call_sp
import session

# ── Bảng màu ────────────────────────────────────────────────────────────────
BG = "#0f1117"
CARD = "#1a1d27"
ACCENT = "#4f8ef7"
ACCENT_DARK = "#2563eb"
TEXT_PRI = "#f0f4ff"
TEXT_SEC = "#8892a4"
ENTRY_BG = "#252836"
ENTRY_FG = "#e2e8f0"
ENTRY_BORD = "#2e3347"
ERROR_FG = "#ff6b6b"
SUCCESS_FG = "#4ade80"
HOVER_BTN = "#3b82f6"


def open_login_screen(root, on_success_callback):
    """
    Hiển thị màn hình đăng nhập trên cửa sổ `root`.
    Khi đăng nhập thành công sẽ gọi on_success_callback().
    """
    # ── Xóa widget cũ ───────────────────────────────────────────────────────
    for w in root.winfo_children():
        w.destroy()

    root.title("QLSVNhom — Đăng nhập")
    root.configure(bg=BG)
    W, H = 440, 520
    root.geometry(f"{W}x{H}")
    root.resizable(False, False)
    # Căn giữa màn hình
    root.update_idletasks()
    sx = (root.winfo_screenwidth() - W) // 2
    sy = (root.winfo_screenheight() - H) // 2
    root.geometry(f"{W}x{H}+{sx}+{sy}")

    # ── Font ────────────────────────────────────────────────────────────────
    f_title = tkfont.Font(family="Segoe UI", size=22, weight="bold")
    f_sub = tkfont.Font(family="Segoe UI", size=10)
    f_label = tkfont.Font(family="Segoe UI", size=10, weight="bold")
    f_entry = tkfont.Font(family="Segoe UI", size=11)
    f_btn = tkfont.Font(family="Segoe UI", size=11, weight="bold")
    f_footer = tkfont.Font(family="Segoe UI", size=9)

    # ── Outer container ─────────────────────────────────────────────────────
    outer = tk.Frame(root, bg=BG)
    outer.place(relx=0.5, rely=0.5, anchor="center")

    # ── Card ────────────────────────────────────────────────────────────────
    card = tk.Frame(
        outer,
        bg=CARD,
        padx=40,
        pady=35,
        highlightbackground="#2e3347",
        highlightthickness=1,
    )
    card.pack()

    # Logo icon (giả lập bằng Canvas tròn)
    logo_canvas = tk.Canvas(card, width=64, height=64, bg=CARD, highlightthickness=0)
    logo_canvas.pack(pady=(0, 16))
    logo_canvas.create_oval(2, 2, 62, 62, fill=ACCENT, outline="")
    logo_canvas.create_text(32, 32, text="👨‍🎓", font=("Segoe UI Emoji", 24))

    # Tiêu đề
    tk.Label(card, text="Đăng Nhập", font=f_title, bg=CARD, fg=TEXT_PRI).pack()
    tk.Label(card, text="Quản lý sinh viên", font=f_sub, bg=CARD, fg=TEXT_SEC).pack(
        pady=(4, 24)
    )

    # ── Helper: tạo field ───────────────────────────────────────────────────
    def make_field(parent, label_text, placeholder="", show=None):
        tk.Label(
            parent, text=label_text, font=f_label, bg=CARD, fg=TEXT_SEC, anchor="w"
        ).pack(fill="x", pady=(0, 4))

        frame = tk.Frame(parent, bg=ENTRY_BORD, pady=1)
        frame.pack(fill="x", pady=(0, 14))

        inner = tk.Frame(frame, bg=ENTRY_BG)
        inner.pack(fill="x", padx=1, pady=1)

        entry = tk.Entry(
            inner,
            font=f_entry,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            relief="flat",
            bd=6,
            insertbackground=ACCENT,
            show=show,
        )
        entry.pack(fill="x")
        entry.insert(0, placeholder)

        def on_focus_in(e):
            frame.config(bg=ACCENT)

        def on_focus_out(e):
            frame.config(bg=ENTRY_BORD)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry

    entry_tendn = make_field(card, "TÊN ĐĂNG NHẬP")
    entry_mk = make_field(card, "MẬT KHẨU", show="●")

    # ── Thông báo lỗi ───────────────────────────────────────────────────────
    lbl_error = tk.Label(
        card, text="", font=f_sub, bg=CARD, fg=ERROR_FG, wraplength=320
    )
    lbl_error.pack(pady=(0, 10))

    # ── Nút đăng nhập ───────────────────────────────────────────────────────
    btn_var = tk.StringVar(value="ĐĂNG NHẬP")

    btn = tk.Button(
        card,
        textvariable=btn_var,
        font=f_btn,
        bg=ACCENT,
        fg="white",
        activebackground=HOVER_BTN,
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2",
    )
    btn.pack(fill="x", pady=(4, 0))

    # Hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg=HOVER_BTN))
    btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))

    # ── Footer ──────────────────────────────────────────────────────────────
    tk.Label(
        card,
        text="Database Lab 03",
        font=f_footer,
        bg=CARD,
        fg=TEXT_SEC,
    ).pack(pady=(20, 0))

    # ── Logic đăng nhập ─────────────────────────────────────────────────────
    def set_loading(loading: bool):
        if loading:
            btn.config(state="disabled", bg="#3b4460")
            btn_var.set("Đang xử lý…")
        else:
            btn.config(state="normal", bg=ACCENT)
            btn_var.set("ĐĂNG NHẬP")

    def on_login(event=None):
        try:
            tendn = entry_tendn.get().strip()
            mk = entry_mk.get().strip()
        except tk.TclError:
            return  # Widget might be destroyed already
        
        lbl_error.config(text="", fg=ERROR_FG)

        if not tendn or not mk:
            lbl_error.config(text="⚠  Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        set_loading(True)
        root.update()

        try:
            result = call_sp("SP_SEL_PUBLIC_NHANVIEN", {"TENDN": tendn, "MK": mk})
            if result:
                session.set_user(result[0])
                lbl_error.config(
                    text=f"✓ Xin chào, {session.current_user['HOTEN']}!", fg=SUCCESS_FG
                )
                root.after(500, on_success_callback)
            else:
                lbl_error.config(text="✗ Tên đăng nhập hoặc mật khẩu không đúng.")
        except Exception as exc:
            lbl_error.config(text=f"✗ Lỗi kết nối: {exc}")
        finally:
            set_loading(False)

    btn.config(command=on_login)
    root.bind("<Return>", on_login)
    entry_tendn.focus_set()
