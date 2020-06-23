
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import re

def image_name(image_path):
    regex = ".*\\\(.*)\\\(.*).png"
    m = re.match(regex, image_path)
    return m.group(1) + "_" + m.group(2)

def read_dataset_map(data_map_path):
    with open(data_map_path, "r") as lf:
        lines_list = lf.read().splitlines()
        lines = [line.split(" ") for line in lines_list]
        images, labels = [], []
        if len(lines) > 0:
            images, labels = zip(*lines)
        labels = [int(label) for label in labels]
    return images, np.array(labels).astype(np.int)

def read_image(image_file):

    cv_image = cv2.imread(image_file)
    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    if cv_image is None:
        raise RuntimeError(f"Unable to open {image_file}")

    return np.array(cv_image)




class AugmentHelper:
    @staticmethod
    def scale_by(image, scale_factor):
        new_size = (image.shape[0] * scale_factor, image.shape[1] * scale_factor)
        pil_image = Image.fromarray(image.astype(np.uint8))
        pil_image = pil_image.resize(new_size)
        return np.array(pil_image)

    @staticmethod
    def flip(image, axis):
        return np.flip(image, axis=axis)

    @staticmethod
    def create_augmentation_dir(dir_name, to_augment_paths, labels, output_path):
        new_dir = os.path.join(output_path, dir_name)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        new_paths = []
        new_labels = []
        for i in range(len(to_augment_paths)):
            image = read_image(to_augment_paths[i])
            name = image_name(to_augment_paths[i])

            augmented_images = [AugmentHelper.scale_by(image, 2),AugmentHelper.scale_by(image, 5),
                                AugmentHelper.flip(image, 0), AugmentHelper.flip(image, 1)]
            augmented_paths = [os.path.join(new_dir, "{}_scaledby2.jpg").format(name),
                                       os.path.join(new_dir, "{}_scaledby5.jpg").format(name),
                                       os.path.join(new_dir, "{}_xflipped.jpg").format(name),
                                       os.path.join(new_dir, "{}_yflipped.jpg").format(name)]

            for image, path in list(zip(augmented_images, augmented_paths)):
                f = plt.figure()
                plt.imshow(image)
                plt.savefig(path)
                plt.close(fig=f)

            new_paths += augmented_paths
            new_labels += [labels[i]] * len(augmented_paths)
        return new_paths, np.array(new_labels)