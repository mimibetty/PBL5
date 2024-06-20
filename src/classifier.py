"""An example of how to use your own dataset to train a classifier that recognizes people.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import argparse
import facenet
import os
import sys
import math
import pickle
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, log_loss

import json

def main(args):
  
    with tf.Graph().as_default():
      
        with tf.compat.v1.Session() as sess:
            
            np.random.seed(seed=args.seed)
            
            # Chọn train hay là classify
            if args.use_split_dataset:
                dataset_tmp = facenet.get_dataset(args.data_dir)
                train_set, test_set = split_dataset(dataset_tmp, args.min_nrof_images_per_class, args.nrof_train_images_per_class)
                if (args.mode=='TRAIN'):
                    dataset = train_set
                elif (args.mode=='CLASSIFY'):
                    dataset = test_set
            else:
                dataset = facenet.get_dataset(args.data_dir)

            # Check that there are at least one training image per class
            for cls in dataset:
                assert(len(cls.image_paths)>0, 'There must be at least one image for each class in the dataset')

                 
            paths, labels = facenet.get_image_paths_and_labels(dataset)
            print("lables: ", labels)
            
            print('Number of classes: %d' % len(dataset))
            print('Number of images: %d' % len(paths))
            
            # Load the model
            print('Loading feature extraction model')
            facenet.load_model(args.model)
            
            # Get input and output tensors
            #images_placeholder: Đây là placeholder cho các hình ảnh đầu vào. Nó sẽ chứa các hình ảnh được đưa vào mô hình để xử lý.
            # embeddings: Đây là tensor đầu ra của mô hình, chứa các đặc trưng (embeddings) của khuôn mặt. Embeddings là các vector đặc trưng đại diện cho các khuôn mặt.
            # phase_train_placeholder: Đây là placeholder để xác định xem mô hình đang ở chế độ huấn luyện (training) hay kiểm tra (inference). Trong trường hợp này, chúng ta đặt nó là False để biểu thị chế độ kiểm tra.
            # embedding_size: Lấy kích thước của vector embedding, tức là số chiều của vector đặc trưng.
            images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]
            
            # Run forward pass to calculate embeddings
            print('Calculating features for images')
            nrof_images = len(paths)
            nrof_batches_per_epoch = int(math.ceil(1.0*nrof_images / args.batch_size))
            emb_array = np.zeros((nrof_images, embedding_size))
            for i in range(nrof_batches_per_epoch):
                start_index = i*args.batch_size
                end_index = min((i+1)*args.batch_size, nrof_images)
                paths_batch = paths[start_index:end_index]
                images = facenet.load_data(paths_batch, False, False, args.image_size)
                print("Shape: ", images.shape)
                # Load imgs vào trong feedict
                feed_dict = { images_placeholder:images, phase_train_placeholder:False }
                # Lấy ra embeddings và đưa vào mảng emb_arr
                emb_array[start_index:end_index,:] = sess.run(embeddings, feed_dict=feed_dict)
                print("Emb: ", emb_array.shape)
            

                
            
            classifier_filename_exp = os.path.expanduser(args.classifier_filename)

            if (args.mode=='TRAIN'):
                # Train classifier
                # print('Training classifier')
                
                # # model = SVC(kernel='linear', probability=True)
                # # model = RandomForestClassifier()
                # # model = LogisticRegression()
                # # model = DecisionTreeClassifier()
                # model = KNeighborsClassifier(n_neighbors=5, metric='euclidean')
                # # model = SGDClassifier(loss="modified_huber")
                # # model = GaussianNB()
                # model.fit(emb_array, labels)

                # # Create a list of class names
                # class_names = [ cls.name.replace('_', ' ') for cls in dataset]

                # # Saving classifier model
                # with open(classifier_filename_exp, 'wb') as outfile:
                #     pickle.dump((model, class_names), outfile)
                # print('Saved classifier model to file "%s"' % classifier_filename_exp)

                # Khởi tạo danh sách các mô hình
                models = {
                    'SVC': SVC(kernel='linear', probability=True),
                    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
                    'LogisticRegression': LogisticRegression(max_iter=1000),
                    'DecisionTree': DecisionTreeClassifier(),
                    'SGDClassifier': SGDClassifier(loss="modified_huber"),
                    'GaussianNB': GaussianNB(),
                    # 'GradientBoosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
                    'MLPClassifier': MLPClassifier(hidden_layer_sizes=(100,), max_iter=500, random_state=42)
                }

                results = {}
                class_names = [ cls.name.replace('_', ' ') for cls in dataset]
                # Tạo thư mục để lưu các mô hình nếu chưa tồn tại
                os.makedirs(classifier_filename_exp, exist_ok=True)
                
                for model_name, model in models.items():
                    print(model_name)
                    model.fit(emb_array, labels)
                    print("Bug")
                    predictions = model.predict_proba(emb_array)
                    # Sẽ có dạng [0.3, 0.6, 0.1]...
                    print("Prediction:", predictions)
                    # Lấy ra chỉ số cao nhất
                    best_class_indices = np.argmax(predictions, axis=1)
                    print("Best class indices: ",best_class_indices)
                    best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
                    
                    for i in range(len(best_class_indices)):
                        print('%4d  %s: %.3f' % (i, class_names[best_class_indices[i]], best_class_probabilities[i]))
                        
                    accuracy = np.mean(np.equal(best_class_indices, labels))
                    print('Accuracy: %.3f' % accuracy)
                    # Tính các chỉ số đánh giá
                    # accuracy_train = accuracy_score(model.premdTrainX_norm, labels)
                    results[model_name] = {
                        'accuracy_train': accuracy,
                    }

                    model_file = os.path.join(classifier_filename_exp, f"{model_name}.pkl")
                    with open(model_file, 'wb') as outfile:
                        pickle.dump((model, class_names), outfile)
                with open('model_results.json', 'w') as f:
                    json.dump(results, f, indent=4)

            elif (args.mode=='CLASSIFY'):
                # # Classify images
                # print('Testing classifier')
                # with open(classifier_filename_exp, 'rb') as infile:
                #     (model, class_names) = pickle.load(infile)

                # print('Loaded classifier model from file "%s"' % classifier_filename_exp)
                # print("Shape", emb_array.shape)
                # predictions = model.predict_proba(emb_array)
                # print("Prediction:", predictions)
                # best_class_indices = np.argmax(predictions, axis=1)
                # print("Best class indices: ",best_class_indices)
                # best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
                
                # for i in range(len(best_class_indices)):
                #     print('%4d  %s: %.3f' % (i, class_names[best_class_indices[i]], best_class_probabilities[i]))
                    
                # accuracy = np.mean(np.equal(best_class_indices, labels))
                # print('Accuracy: %.3f' % accuracy)

                # # Show confusion matrix
                # show_confusion_matrix(class_names, labels, best_class_indices)

                # Classify images
                print('Testing classifiers')
                
                # Directory containing the saved models
                classifier_dir = classifier_filename_exp

                # Initialize results dictionary
                results = {}

                # Iterate over all .pkl files in the directory
                for model_file in os.listdir(classifier_dir):
                    if model_file.endswith('.pkl'):
                        model_path = os.path.join(classifier_dir, model_file)
                        with open(model_path, 'rb') as infile:
                            model, class_names = pickle.load(infile)

                        print(f'Loaded classifier model from file "{model_path}"')
                        print("Shape", emb_array.shape)
                        predictions = model.predict_proba(emb_array)
                        print("Prediction:", predictions)
                        best_class_indices = np.argmax(predictions, axis=1)
                        print("Best class indices: ", best_class_indices)
                        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]

                        for i in range(len(best_class_indices)):
                            print('%4d  %s: %.3f' % (i, class_names[best_class_indices[i]], best_class_probabilities[i]))

                        accuracy_test = np.mean(np.equal(best_class_indices, labels))
                        precision = precision_score(labels, best_class_indices, average='weighted')
                        recall = recall_score(labels, best_class_indices, average='weighted')
                        f1 = f1_score(labels, best_class_indices, average='weighted')
                        conf_matrix = confusion_matrix(labels, best_class_indices)

                        # Save the results for the current model
                        results[model_file] = {
                            'threshold': np.mean(best_class_probabilities),
                            'accuracy_test': accuracy_test,
                            'precision': precision,
                            'recall': recall,
                            'f1_score': f1,
                            'confusion_matrix': conf_matrix.tolist()  # Chuyển ma trận nhầm lẫn thành danh sách để lưu vào JSON
                        }
                        show_confusion_matrix(class_names, labels, best_class_indices)


                # Save results to JSON file
                with open('classification_results.json', 'w') as f:
                    json.dump(results, f, indent=4)

                # Show confusion matrix for the last evaluated model
                # show_confusion_matrix(class_names, labels, best_class_indices)
                
                
            
def split_dataset(dataset, min_nrof_images_per_class, nrof_train_images_per_class):
    train_set = []
    test_set = []
    for cls in dataset:
        paths = cls.image_paths
        # Remove classes with less than min_nrof_images_per_class
        if len(paths)>=min_nrof_images_per_class:
            np.random.shuffle(paths)
            train_set.append(facenet.ImageClass(cls.name, paths[:nrof_train_images_per_class]))
            test_set.append(facenet.ImageClass(cls.name, paths[nrof_train_images_per_class:]))
    return train_set, test_set

# def show_confusion_matrix(class_names, y_true, y_predict):
#     cm = confusion_matrix(y_true, y_predict)
#     # Calculate accuracy percentages
#     cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    
#     # Thiết lập kích thước của figure
#     plt.figure(figsize=(8, 8))  # Thay đổi kích thước tại đây
    
#     # Plot confusion matrix
#     plt.imshow(cm_percent, interpolation='nearest', cmap=plt.cm.Blues)
#     plt.title('Confusion Matrix (Accuracy %)')
#     plt.colorbar()
#     tick_marks = np.arange(len(class_names))
#     plt.xticks(tick_marks, class_names, rotation=45)
#     plt.yticks(tick_marks, class_names)
#     plt.xlabel('Predicted Label')
#     plt.ylabel('True Label')

#     # # Fill matrix with percentage values
#     # for i, j in np.ndindex(cm.shape):
#     #     plt.text(j, i, format(cm_percent[i, j], '.2f') + '%', ha='center', va='center',
#     #             color='white' if cm_percent[i, j] > 50 else 'black')
    
#     plt.show()
def show_confusion_matrix(class_names, y_true, y_predict):
    cm = confusion_matrix(y_true, y_predict)
    
    # Thiết lập kích thước của figure
    plt.figure(figsize=(8, 8))  # Thay đổi kích thước tại đây
    
    # Plot confusion matrix
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix (Counts)')
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')

    # Fill matrix with count values
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, str(cm[i, j]), ha='center', va='center',
                     color='white' if cm[i, j] > cm.max() / 2 else 'black')
    
    plt.show()
def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('mode', type=str, choices=['TRAIN', 'CLASSIFY'],
        help='Indicates if a new classifier should be trained or a classification ' + 
        'model should be used for classification', default='CLASSIFY')
    parser.add_argument('data_dir', type=str,
        help='Path to the data directory containing aligned LFW face patches.')
    parser.add_argument('model', type=str, 
        help='Could be either a directory containing the meta_file and ckpt_file or a model protobuf (.pb) file')
    parser.add_argument('classifier_filename', 
        help='Classifier model file name as a pickle (.pkl) file. ' + 
        'For training this is the output and for classification this is an input.')
    parser.add_argument('--use_split_dataset', 
        help='Indicates that the dataset specified by data_dir should be split into a training and test set. ' +  
        'Otherwise a separate test set can be specified using the test_data_dir option.', action='store_true')
    parser.add_argument('--test_data_dir', type=str,
        help='Path to the test data directory containing aligned images used for testing.')
    parser.add_argument('--batch_size', type=int,
        help='Number of images to process in a batch.', default=90)
    parser.add_argument('--image_size', type=int,
        help='Image size (height, width) in pixels.', default=160)
    parser.add_argument('--seed', type=int,
        help='Random seed.', default=666)
    parser.add_argument('--min_nrof_images_per_class', type=int,
        help='Only include classes with at least this number of images in the dataset', default=20)
    parser.add_argument('--nrof_train_images_per_class', type=int,
        help='Use this number of images from each class for training and the rest for testing', default=10)
    
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
