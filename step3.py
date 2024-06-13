import base64
import io
import cv2
import json
from datetime import datetime
import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import requests
from gtts import gTTS
import pygame
import os
import step4

#url = "http://172.20.10.7:8000/get_user_info"  # Thay bằng URL của bạn

def show_user_info(window, main_frame, data_storage, update_current_step, id):
    # Xóa các widget cũ trên main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Thiết lập font chữ
    header_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
    label_font = tkFont.Font(family="Helvetica", size=12)

    # Tạo tiêu đề
    header_label = tk.Label(main_frame, text="User Information", font=header_font, fg="blue")
    header_label.pack(pady=10)

    # Lấy thông tin người dùng từ URL
    def get_user_info(uid):
        try:
            response = requests.get(f"http://172.20.10.7:8000/get_user_info?uid={uid}")
            response.raise_for_status()  # Kiểm tra nếu yêu cầu không thành công
            return response.json()  # Giả sử phản hồi là JSON
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return {}

    user_info = get_user_info(id)

    # Hiển thị thông tin người dùng
    if user_info:
        user_name = user_info.get('name', 'Unknown')
        class_name = user_info.get('class_name', 'Unknown')
        user_name_label = tk.Label(main_frame, text=f"Xin chào, {user_name} - {class_name}.", font=label_font)
        user_name_label.pack(pady=10)
        # Tạo câu chào mừng
        greeting_text = user_info.get('welcome_sentence', 'Welcome')
                # Lấy ảnh từ URL và hiển thị
        try:
            avatar_data = user_info.get('avatar', None)
            if avatar_data:
                img_bytes = base64.b64decode(avatar_data)
                img = Image.open(io.BytesIO(img_bytes))
                img = img.resize((400, 400))  # Điều chỉnh kích thước ảnh nếu cần
                photo = ImageTk.PhotoImage(img)
                avatar_label = tk.Label(main_frame, image=photo)
                avatar_label.image = photo  # Giữ tham chiếu đến ảnh để tránh bị garbage collected
                avatar_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading avatar: {e}")
        
    else:
        user_name_label = tk.Label(main_frame, text="Hello", font=label_font)
        user_name_label.pack(pady=10)
        # Nếu không lấy được thông tin người dùng, sử dụng câu chào mặc định
        greeting_text = "Hello, welcome to Library"

    window.update()
    # Tạo âm thanh từ văn bản và phát ra
    greeting_audio = gTTS(greeting_text, lang='vi', slow=False)
    greeting_audio.save("greeting.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("greeting.mp3")
    pygame.mixer.music.play()

    # Đợi cho âm thanh kết thúc
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # # Xóa file âm thanh sau khi phát
    # os.remove("greeting.mp3")

    # Gọi hàm continue_to_step4 sau 3 giây
    window.after(3000, lambda: continue_to_step4(window, main_frame, data_storage, update_current_step))

def continue_to_step4(window, main_frame, data_storage, update_current_step):
    # Xóa các widget cũ trên main_frame
    for widget in main_frame.winfo_children():
        widget.destroy()
    
    # Gọi hàm show_user_info() từ step4
    step4.show_book_list(window, main_frame, data_storage, update_current_step)
    # Cập nhật bước hiện tại thành bước 4
    update_current_step(4)
