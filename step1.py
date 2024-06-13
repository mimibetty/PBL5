import tkinter as tk
import step2
import GUI
def show_input_form(window, main_frame, data_storage,update_current_step):
    for widget in main_frame.winfo_children():  
        widget.destroy()
    def on_confirm_click():
        student_id = entry_mssv.get()
        if student_id:
            # Xóa thông báo lỗi nếu có
            for widget in main_frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text") == "Vui lòng nhập MSSV":
                    widget.destroy()
                    break
            data_storage.add_student_data(student_id)
            step2.show_webcam(window, main_frame, data_storage,update_current_step)
            update_current_step(2)
        else:
            # Hiển thị thông báo lỗi nếu chưa nhập MSSV
            tk.Label(main_frame, text="Vui lòng nhập MSSV").pack(pady=10)

    # Ô nhập MSSV và nút xác nhận
    label_mssv = tk.Label(main_frame, text="Nhập MSSV:")
    label_mssv.pack(pady=5)
    entry_mssv = tk.Entry(main_frame)
    entry_mssv.pack(pady=5)
    btn_confirm = tk.Button(main_frame, text="Xác Nhận", command=on_confirm_click)
    btn_confirm.pack(pady=10)
