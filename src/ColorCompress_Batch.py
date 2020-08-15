#!/bin/env python3
# Color Compression - Batch edition

# Parameters
input_basepath = 'input/'
output_basepath = 'output/'
k_values = [3, 5, 7]
max_iterations = 1000
convergence_threshold = 10e-3

# Imports
import numpy as np
from PIL import Image
import copy
import os
import time
tnow = time.perf_counter

# The process
def the_process(input_file, output_file, k):

    global max_iterations
    global convergence_threshold
    actual_iterations = 0
    
    # Open from file
    image = np.array(Image.open(input_file), dtype=np.float64)
    width, height, channels = image.shape
    image = image.reshape((width*height, channels))
    
    # Get centroids
    get_random_pixel = lambda: image[np.random.randint(0, image.shape[0])]
    centroids = np.array([get_random_pixel()])
    while len(centroids) < k:
        random_pixel = np.array([get_random_pixel()])
        check = (random_pixel == centroids).all(1).any()
        if not check:
            centroids = np.concatenate((centroids, random_pixel), axis=0)
    
    # Cluster & update centroids
    for i in range(max_iterations):
        actual_iterations += 1
        last_known_centroids = copy.deepcopy(centroids)
        labels = np.argmin(np.linalg.norm(image - centroids[:, None], axis=2), axis=0)
        for label in range(k):
            point_labels = image[labels == label]
            centroids[label] = np.mean(point_labels, axis=0)
        if np.allclose(last_known_centroids, centroids, rtol=convergence_threshold, equal_nan=False):
            break
    
    # Round off centroids to ints and reconstruct image
    c_rounded_off = [[int(e) for e in each_centroid] for each_centroid in centroids]
    new_image = np.array([c_rounded_off[int(each_pixel)] for each_pixel in labels])
    new_image = new_image.reshape((width, height, channels))
    
    # Save as file
    new_image_file = Image.fromarray(new_image.astype(np.uint8))
    new_image_file.save(output_file)
    
    return actual_iterations

# For each file and k value
if __name__ == '__main__':
    print('{} input file(s)'.format(len(os.listdir(input_basepath))))
    
    for each_file in os.listdir(input_basepath):
        for k in k_values:
            filename, extension = os.path.splitext(each_file)
            
            if extension != '.jpg':
                print('{}: non-JPEG image, ignoring...'.format(each_file))
                break
            input_file = input_basepath + each_file
            output_file = output_basepath + filename + '_{}'.format(k) + extension
            
            t = tnow()
            i = the_process(input_file, output_file, k)
            t = tnow() - t
            print('{f} k={k} t={t:.2f}s i={i}'.format(f=each_file, k=k, t=t, i=i))
