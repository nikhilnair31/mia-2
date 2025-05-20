import os
import random
from PIL import Image
from sklearn.cluster import KMeans
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import matplotlib.pyplot as plt
import numpy as np

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def rgb_to_lab(rgb):
    srgb = sRGBColor(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    return convert_color(srgb, LabColor)

def merge_similar_colors(colors, threshold=20):
    distinct = []
    for color in colors:
        lab1 = rgb_to_lab(color)
        if all(delta_e_cie2000(lab1, rgb_to_lab(other)) > threshold for other in distinct):
            distinct.append(color)
    return distinct

def extract_distinct_colors(image_path, num_clusters=30, num_colors=10, merge_threshold=20):
    image = Image.open(image_path).convert('RGB')
    image = image.resize((100, 100))  # speed
    pixels = np.array(image).reshape(-1, 3)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(pixels)
    centers = kmeans.cluster_centers_.astype(int)

    merged = merge_similar_colors(centers, threshold=merge_threshold)
    merged = sorted(merged, key=lambda c: -np.sum((pixels == c).all(axis=1)))  # sort by frequency

    return [rgb_to_hex(c) for c in merged[:num_colors]]

def show_image_and_swatch(image_path, hex_colors):
    image = Image.open(image_path)

    fig, axs = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={'height_ratios': [4, 1]})
    axs[0].imshow(image)
    axs[0].axis('off')
    axs[0].set_title("Original Image")

    for i, color in enumerate(hex_colors):
        axs[1].fill_between([i, i+1], 0, 1, color=color)
    axs[1].set_xlim(0, len(hex_colors))
    axs[1].set_ylim(0, 1)
    axs[1].axis('off')
    axs[1].set_title("Distinct Color Swatch")

    plt.tight_layout()
    plt.show()

# Pick a random image
image_folder_path = r'C:\Users\Nikhil\Pictures\Screenshots'
image_files = [f for f in os.listdir(image_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

if not image_files:
    print("No image files found in the specified folder.")
else:
    image_path = os.path.join(image_folder_path, random.choice(image_files))
    distinct_hex_colors = extract_distinct_colors(image_path, num_clusters=30, num_colors=10)
    print("Distinct Hex Colors:", distinct_hex_colors)
    show_image_and_swatch(image_path, distinct_hex_colors)
