import subprocess
import json
import matplotlib.pyplot as plt
import numpy as np
import mimetypes
import pyheif
import os
from PIL import Image
import filetype
import seaborn as sns 

def preprocessed_img():
    file_path = "src/align_dataset_mtcnn.py"
    raw_data_path = "Dataset/FaceData/raw"
    process_data_path = "Dataset/FaceData/processed"
    augment_data_path = "Dataset/FaceData/augment_data_10"
    additional_args = [raw_data_path, process_data_path, augment_data_path, "--image_size", "160",  "--margin",  "32",  "--random_order", "--gpu_memory_fraction",  "0.25", "--augment", "True"]
    
    subprocess.run(["python", file_path] + additional_args, shell=True)

def train(data_dir, pretrain_model, classify_model, batch_size = 1000, use_split_dataset = False, nrof_train_images_per_class = 10):
    file_path = "src/classifier.py"
    additional_args =['TRAIN', data_dir, pretrain_model, classify_model, 
                      '--batch_size', str(batch_size)]
    
    subprocess.run(["python", file_path] + additional_args, shell=True)

def classify(data_dir, pretrain_model, classify_model, batch_size = 1000, use_split_dataset = False, nrof_train_images_per_class = 10):
    file_path = "src/classifier.py"
    additional_args =['CLASSIFY', data_dir, pretrain_model, classify_model, 
                      '--batch_size', str(batch_size)]
    
    subprocess.run(["python", file_path] + additional_args, shell=True)

def evaluateAll():
    
    # Đọc file JSON chứa kết quả
    with open('classification_results.json', 'r') as f:
        results = json.load(f)

    # Trích xuất các kết quả
    model_names = []
    accuracy_train = []
    accuracy_test = []
    precision = []
    recall = []
    f1_scores = []
    confusion_matrices = []
    print(results.keys())

    for model in results.keys():
        if all(key in results[model] for key in ['accuracy_test', 'precision', 'recall', 'f1_score']):
            model_names.append(model)
            # accuracy_train.append(results[model]['accuracy_train'])
            accuracy_test.append(results[model]['accuracy_test'])
            precision.append(results[model]['precision'])
            recall.append(results[model]['recall'])
            f1_scores.append(results[model]['f1_score'])
            confusion_matrices.append(results[model]['confusion_matrix'])

    print(model_names)
    # Vẽ biểu đồ
    x = np.arange(len(model_names))  # vị trí của các nhóm
    width = 0.15  # chiều rộng của các thanh

    fig, ax = plt.subplots(figsize=(25, 13))

    # rects1 = ax.bar(x - 2*width, accuracy_train, width, label='Accuracy Train')
    rects2 = ax.bar(x - width, accuracy_test, width, label='Accuracy Test')
    rects3 = ax.bar(x, precision, width, label='Precision')
    rects4 = ax.bar(x + width, recall, width, label='Recall')
    rects5 = ax.bar(x + 2*width, f1_scores, width, label='F1 Score')

    # Thêm nhãn và tiêu đề
    ax.set_xlabel('Models')
    ax.set_ylabel('Scores')
    ax.set_title('Performance Comparison of Different Models')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()

    # Thêm nhãn cho mỗi thanh
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(round(height, 2)),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    # autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    autolabel(rects4)
    autolabel(rects5)

    fig.tight_layout()

    plt.show()
    # Plot confusion matrices
    for i, cm in enumerate(confusion_matrices):
        plt.figure(figsize=(8, 6))
        plt.title(f'Confusion Matrix - {model_names[i]}')
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.colorbar()
        tick_marks = np.arange(len(cm))
        plt.xticks(tick_marks, np.arange(len(cm)))
        plt.yticks(tick_marks, np.arange(len(cm)))
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()
        plt.show()

def convert_heic_to_jpg(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith('.heic'):
            heic_path = os.path.join(directory, filename)
            jpg_filename = os.path.splitext(filename)[0] + '.jpg'
            jpg_path = os.path.join(directory, jpg_filename)

            # Check if the file is a valid HEIC file
            kind = filetype.guess(heic_path)
            if kind is None or kind.extension != 'heic':
                print(f"Skipping {heic_path}: Not a valid HEIC file (detected type: {kind})")
                continue

            try:
                # Read the HEIC file
                heif_file = pyheif.read(heic_path)
                
                # Convert to a PIL Image
                image = Image.frombytes(
                    heif_file.mode, 
                    heif_file.size, 
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
                
                # Save as JPEG
                image.save(jpg_path, "JPEG")
                print(f"Converted {heic_path} to {jpg_path}")
            
            except ValueError as e:
                print(f"Failed to convert {heic_path}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while converting {heic_path}: {e}")

# Example usage:
# convert_heic_to_jpg('Dataset/FaceData/train_asia/102210072')
def main():
    # preprocessed_img()
    new_processed_dir = "Dataset/FaceData/new_test_processed"
    data_dir = "Dataset/FaceData/augment_data_10"
    pretrain_model = "Models/20180402-114759.pb"
    classify_model = "Models/20_SVC_5.pkl"
    # train(data_dir, pretrain_model, classify_model)
    classify(new_processed_dir, pretrain_model, classify_model)
evaluateAll()