import tkinter as tk
from checkData import TempDataStorage
import step1
import step2
import step3

def create_gui():
    window = tk.Tk()
    window.title("Giao Dien Quan Ly Muon Tra Sach")
    window.geometry("1000x700")

    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)

    btn_quay_lai = tk.Button(button_frame, text="Quay Lai")
    btn_quay_lai.pack(side=tk.LEFT, padx=5)

    current_step = 1

    def update_current_step(new_step):
        nonlocal current_step
        current_step = new_step

    def on_back_click():
        nonlocal current_step

        if current_step == 1:
            window.destroy()  # Close the program at step 1
        else:
            # Clear the main frame
            for widget in main_frame.winfo_children():
                widget.destroy()
            # Go back to step 1
            step1.show_input_form(window, main_frame, data_storage, update_current_step)
            update_current_step(1)

    btn_quay_lai.config(command=on_back_click)

    main_frame = tk.Frame(window, bg="lightgray")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    data_storage = TempDataStorage()
    step1.show_input_form(window, main_frame, data_storage, update_current_step)

    return window, main_frame

if __name__ == "__main__":
    window, main_frame = create_gui()
    window.mainloop()
