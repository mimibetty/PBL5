from datasets import load_dataset
from PIL import Image
import os
import random
import shutil


# # Tải dataset từ Hugging Face
# dataset = load_dataset("fptudsc/face-celeb-vietnamese")

# # Tạo thư mục gốc để lưu các hình ảnh nếu chưa tồn tại
# os.makedirs("face_celeb_images", exist_ok=True)

# # Lưu từng hình ảnh và nhãn tương ứng
# for i, data in enumerate(dataset['train']):
#     # Lấy hình ảnh và nhãn
#     image = data['image']
#     label = data['label']

#     # Tạo thư mục con cho nhãn nếu chưa tồn tại
#     label_dir = os.path.join("Dataset/face_celeb_images", label)
#     os.makedirs(label_dir, exist_ok=True)

#     # Đặt tên file cho hình ảnh
#     image_filename = os.path.join(label_dir, f"{label}_{i}.jpg")

#     # Lưu hình ảnh
#     image.save(image_filename)

#     print(f"Đã lưu {image_filename}")

# print("Hoàn thành lưu hình ảnh!")
# Tạo thư mục train và test
train_dir = "face_celeb_images/train"
test_dir = "face_celeb_images/test"

os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Di chuyển ngẫu nhiên 5 ảnh cho mỗi class vào thư mục train, các ảnh còn lại vào thư mục test
for label in os.listdir("Dataset/face_celeb_images"):
    label_dir = os.path.join("Dataset/face_celeb_images", label)
    
    if os.path.isdir(label_dir):
        # Lấy danh sách các ảnh
        images = os.listdir(label_dir)

        # Tạo thư mục train và test cho class hiện tại
        train_label_dir = os.path.join(train_dir, label)
        test_label_dir = os.path.join(test_dir, label)
        
        os.makedirs(train_label_dir, exist_ok=True)
        os.makedirs(test_label_dir, exist_ok=True)

        # Lựa chọn ngẫu nhiên 5 ảnh cho train
        selected_images = random.sample(images, min(5, len(images)))

        # Di chuyển ảnh vào thư mục train hoặc test
        for image in images:
            src = os.path.join(label_dir, image)
            if image in selected_images:
                dst = os.path.join(train_label_dir, image)
            else:
                dst = os.path.join(test_label_dir, image)
            
            # Check if source and destination are different
            if src != dst:
                shutil.move(src, dst)
                print(f"Đã di chuyển {image} vào {dst}")
            else:
                print(f"Đã tồn tại {dst}, không di chuyển {image}")

print("Hoàn thành chia tập dữ liệu!")