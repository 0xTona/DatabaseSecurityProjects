"""
main.py — Entry point của ứng dụng.
Xử lý logic luân chuyển giữa các màn hình.
"""

import tkinter as tk
import login_screen
import lop_screen
import session


def main():
    root = tk.Tk()
    
    # Ẩn window tạm thời để tránh nháy giật khi cấu hình
    root.withdraw()

    def show_login():
        session.clear_user()
        login_screen.open_login_screen(root, on_success_callback=show_main_app)
        root.deiconify()

    def show_main_app():
        lop_screen.open_lop_screen(root, show_login, nav_callbacks)
        root.deiconify()

    def show_sv(selected_malop=None):
        import sinhvien_screen
        sinhvien_screen.open_sinhvien_screen(root, show_login, nav_callbacks, current_malop=selected_malop)
        root.deiconify()

    nav_callbacks = {'lop': show_main_app, 'sv': show_sv}        

    # Bắt đầu luồng ở login
    show_login()

    root.mainloop()


if __name__ == "__main__":
    main()
