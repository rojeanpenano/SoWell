import os
import numpy as np
import cv2
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import pickle

# Dataset paths
TRAIN_DIR = "rice_leafs_disease_dataset/train"
VAL_DIR = "rice_leafs_disease_dataset/validation"
IMG_SIZE = 128

# Prepare training data
def load_images_from_folder(folder_path, class_names):
    images = []
    labels = []
    for label_index, class_name in enumerate(class_names):
        class_path = os.path.join(folder_path, class_name)
        if not os.path.isdir(class_path):
            continue
        for filename in os.listdir(class_path):
            img_path = os.path.join(class_path, filename)
            try:
                img = cv2.imread(img_path)
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                images.append(img)
                labels.append(label_index)
            except Exception as e:
                print(f"Error reading {img_path}: {e}")
    return np.array(images), to_categorical(labels)

# Get class names from folders
class_names = sorted(os.listdir(TRAIN_DIR))
print(f"Class labels: {class_names}")

# Load train and validation data
X_train, y_train = load_images_from_folder(TRAIN_DIR, class_names)
X_val, y_val = load_images_from_folder(VAL_DIR, class_names)

# Normalize
X_train = X_train / 255.0
X_val = X_val / 255.0

# Model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(len(class_names), activation='softmax')
])

model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Train
history = model.fit(X_train, y_train, epochs=10, validation_data=(X_val, y_val))

# Save model and class names
model.save("crop_disease_model.h5")
np.save("class_names.npy", class_names)

# Plot accuracy
plt.plot(history.history['accuracy'], label="Train")
plt.plot(history.history['val_accuracy'], label="Validation")
plt.title("Model Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.show()