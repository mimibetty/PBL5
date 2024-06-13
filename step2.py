import tkinter as tk
import cv2
import requests
import numpy as np
from PIL import Image, ImageTk
import step3  # Import step 3
import time
from queue import Queue
import threading

# URL to the face recognition API (modify if needed)
SERVER_API_URL = "http://172.20.10.9:8000/recog"


def show_webcam(window, main_frame, data_storage, update_current_step):
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Initialize the webcam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 0 is the default webcam, change if needed

    def get_face_data(image, result_queue):
        # Convert image to bytes
        _, img_encoded = cv2.imencode('.jpg', image)
        # Send the image to the server as raw byte data
        try:
            response = requests.post(SERVER_API_URL, data=img_encoded.tobytes())
            if response.status_code == 200:
                result_queue.put(response.json())
            else:
                result_queue.put(None)
        except requests.exceptions.RequestException as e:
            result_queue.put(None)

    def show_frame():
        ret, frame = cap.read()
        if ret:
            result_queue = Queue()
            face_data_thread = threading.Thread(target=get_face_data, args=(frame, result_queue))
            face_data_thread.start()
            face_data_thread.join()  # Wait for the face data to be retrieved

            face_data = result_queue.get()

            # Display face info on the right side
            right_frame = np.zeros_like(frame)  # Create a blank frame for the right side
            if face_data:
                id = face_data['name']
                prob = face_data['probability']
                box = face_data['face_pos']

                # Extract the face image from the frame
                start_x, start_y, end_x, end_y = box
                face_image = frame[start_y:end_y, start_x:end_x]

                # Resize the face image to fit in the display frame
                display_frame_resized = cv2.resize(face_image, (frame.shape[1] // 3 + 5, frame.shape[0] // 3 + 40))
                # Calculate position to place the resized face image on the right
                x_offset = (frame.shape[1] // 3) - (display_frame_resized.shape[1] // 3) - 30
                y_offset = (frame.shape[0] // 2) - (display_frame_resized.shape[0] // 2)

                # Overlay the resized face image onto the right frame
                right_frame[y_offset:y_offset + display_frame_resized.shape[0],
                x_offset:x_offset + display_frame_resized.shape[1]] = display_frame_resized
                # Put text for ID and probabilities
                cv2.putText(right_frame, f"ID: {id}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                cv2.putText(right_frame, f"Prob: {prob:.2f}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                if data_storage.get_student_data()['student_id'] == id:
                    def transition_to_step3():
                        update_current_step(3)
                        step3.show_user_info(window, main_frame, data_storage, update_current_step,id)
                    # Schedule transition to step 3 after 5 seconds
                    main_frame.after(100, transition_to_step3)
                    return

        # Display the webcam frame
        combined_frame = np.hstack((frame, right_frame))
        img = cv2.cvtColor(combined_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        label_webcam.imgtk = imgtk  # Keep a reference!
        label_webcam.config(image=imgtk)

        # Schedule the next frame update after 10ms
        label_webcam.after(10, show_frame)


    # Create a label to display the webcam
    label_webcam = tk.Label(main_frame)
    label_webcam.pack()

    # Start displaying the webcam feed
    show_frame()
