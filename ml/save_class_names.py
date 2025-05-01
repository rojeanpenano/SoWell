import numpy as np
import os

# Dataset folder path
DATASET_DIR = "rice_leaf_diseases"

# Automatically get the folder names as class labels
class_names = sorted([
    folder for folder in os.listdir(DATASET_DIR)
    if os.path.isdir(os.path.join(DATASET_DIR, folder))
])

# Save to .npy file
np.save("class_names.npy", class_names)

print("Class names saved to class_names.npy")
print("Classes:", class_names)