import time
import cv2
from pyzbar import pyzbar
import json
from datetime import datetime
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import requests
import step1  # Assuming you have a module step1 for handling other steps

url = "http://172.20.10.7:8000/save_checkin"  # Replace with your URL

def show_book_list(window, main_frame, data_storage, update_current_step):
    # Clear existing widgets on main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Initialize necessary variables
    cap = cv2.VideoCapture(2)
    book_quantities = {}
    last_scanned_book = None

    # Set up fonts
    header_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
    label_font = tkFont.Font(family="Helvetica", size=12)
    button_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

    # Create a canvas and scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create header
    header_label = tk.Label(scrollable_frame, text="Library Book Scanner", font=header_font, fg="blue")
    header_label.pack(pady=10)

    # Create frame for webcam
    webcam_frame = tk.Frame(scrollable_frame, bd=2, relief=tk.SUNKEN)
    webcam_frame.pack(pady=20, fill="both", expand=True)

    # Create label to display webcam images
    webcam_label = tk.Label(webcam_frame)
    webcam_label.pack(expand=True)

    # Create frame for book list with scrollbar
    book_list_frame = tk.Frame(scrollable_frame)
    book_list_frame.pack(pady=10, fill="both", expand=True)

    # Create scrollbar for book list
    book_list_scrollbar = tk.Scrollbar(book_list_frame)
    book_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create label and text widget for displaying book list
    book_list_label = tk.Label(book_list_frame, text="Scanned Book List:", font=label_font)
    book_list_label.pack()
    book_list_text = tk.Text(book_list_frame, height=10, width=40, font=label_font, yscrollcommand=book_list_scrollbar.set)
    book_list_text.pack(side=tk.LEFT, fill="both", expand=True)
    book_list_scrollbar.config(command=book_list_text.yview)

    # Create frame for buttons
    button_frame = tk.Frame(scrollable_frame)
    button_frame.pack(pady=20, fill="both", expand=True)

    # Function to update book list display
    def update_book_list_display():
        book_list_text.delete("1.0", tk.END)
        for book_id, quantity in book_quantities.items():
            book_list_text.insert(tk.END, f'ID: {book_id}, Quantity: {quantity}\n')

    # Function to decode QR code from webcam frame
    last_scan_time = 0
    def decode_qr_code(frame):
        nonlocal last_scan_time

        current_time = time.time()
        if current_time - last_scan_time >= 2:
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                book_quantities[barcode_data] = book_quantities.get(barcode_data, 0) + 1
            
            update_book_list_display()
            last_scan_time = current_time

    # Function to handle borrow or return button click
    def on_borrow_return_click(is_borrow, window, main_frame, data_storage, update_current_step):
        if not book_quantities:
            book_list_text.delete("1.0", tk.END)
            book_list_text.insert(tk.END, "No books scanned yet!!!")
            return

        time_out = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "uid": data_storage.get_student_data()['student_id'],
            "time_in": data_storage.get_student_data()['time_in'],
            "time_out": time_out,
            "mode": "Borrow" if is_borrow else "Return",
            "books": book_quantities
        }

        def send_data_and_get_response(data):
            try:
                response = requests.post(url, json=data)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                return {"error": str(e)}
                
        response = send_data_and_get_response(data)
        print(response)
        print(json.dumps(data))

        def release_webcam():
            cap.release()

        temp_data_file = "book_transaction.json"
        with open(temp_data_file, "w") as f:
            json.dump(data, f)

        data_storage.clear_data()
        release_webcam()
        step1.show_input_form(window, main_frame, data_storage, update_current_step)
        update_current_step(1)

    # Function to update webcam frame
    def update_webcam_frame():
        ret, frame = cap.read()
        if ret:
            decode_qr_code(frame)
            if book_list_text:
                update_book_list_display()
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            webcam_label.imgtk = imgtk
            webcam_label.configure(image=imgtk)
        window.after(10, update_webcam_frame)

    # Create "Borrow Book" and "Return Book" buttons
    btn_borrow = tk.Button(button_frame, text="Borrow Book", font=button_font, bg="green", fg="white", command=lambda: on_borrow_return_click(True, window, main_frame, data_storage, update_current_step))
    btn_borrow.pack(side=tk.LEFT, padx=10)

    btn_return = tk.Button(button_frame, text="Return Book", font=button_font, bg="red", fg="white", command=lambda: on_borrow_return_click(False, window, main_frame, data_storage, update_current_step))
    btn_return.pack(side=tk.LEFT, padx=10)

    update_webcam_frame()
