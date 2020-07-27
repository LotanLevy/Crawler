
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import re

PATH_LABEL_SEP = "$"


def image_name(image_path):
    regex = ".*\\/(.*)\\/(.*).jpg"
    m = re.match(regex, image_path)
    return m.group(1) + "_" + m.group(2)

def read_dataset_map(data_map_path, line_sep):
    with open(data_map_path, "r") as lf:
        lines_list = lf.read().splitlines()
        lines = [line.split(line_sep) for line in lines_list]
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

            # augmented_images = [AugmentHelper.scale_by(image, 2),AugmentHelper.scale_by(image, 5),
            #                     AugmentHelper.flip(image, 0), AugmentHelper.flip(image, 1)]
            # augmented_paths = [os.path.join(new_dir, "{}_scaledby2.jpg").format(name),
            #                            os.path.join(new_dir, "{}_scaledby5.jpg").format(name),
            #                            os.path.join(new_dir, "{}_xflipped.jpg").format(name),
            #                            os.path.join(new_dir, "{}_yflipped.jpg").format(name)]
            augmented_images = [AugmentHelper.flip(image, 0), AugmentHelper.flip(image, 1)]
            augmented_paths = [os.path.join(new_dir, "{}_xflipped.jpg").format(name),
                                       os.path.join(new_dir, "{}_yflipped.jpg").format(name)]

            for image, path in list(zip(augmented_images, augmented_paths)):
                f = plt.figure()
                plt.imshow(image)
                plt.savefig(path)
                plt.close(fig=f)

            new_paths += augmented_paths
            new_labels += [labels[i]] * len(augmented_paths)
        return new_paths, np.array(new_labels)


def split_data_into_subsets_with_filename(data_map_path, test_classes, sizes):
    images, labels = read_dataset_map(data_map_path, PATH_LABEL_SEP)
    datasubsets = {"train":([], []), "val":([], []), "test":([], [])}
    train_size, val_size, test_size = int(np.floor(sizes[0] * len(images))),\
                                      int(np.floor(sizes[1] * len(images))),\
                                      int(np.floor(sizes[2] * len(images)))

    in_use_idxs = np.zeros(len(labels))
    if test_size > 0:
        relevant_idxs_map = np.zeros(len(labels))
        for cls in test_classes:
            relevant_idxs_map[labels == cls] = 1
        test_idxs = np.where(relevant_idxs_map == 1)[0]
        rand_test_idxs = np.random.choice(test_idxs, min(len(test_idxs), test_size), replace=False)
        datasubsets["test"] = ([images[i] for i in rand_test_idxs], labels[rand_test_idxs])
        in_use_idxs[rand_test_idxs] = 1


    if val_size > 0:
        val_idxs = np.where(in_use_idxs == 0)[0]
        rand_val_idxs = np.random.choice(val_idxs, min(len(val_idxs), val_size), replace=False)
        datasubsets["val"] = ([images[i] for i in rand_val_idxs], labels[rand_val_idxs])
        in_use_idxs[rand_val_idxs] = 1

    train_idxs = np.where(in_use_idxs == 0)[0]
    datasubsets["train"] = ([images[i] for i in train_idxs], labels[train_idxs])

    return datasubsets


def split_data_into_subsets_for_every_class(data_map_path, test_classes, sizes):
    images, labels = read_dataset_map(data_map_path, PATH_LABEL_SEP)
    datasubsets = {"train":([], []), "val":([], []), "test":([], [])}
    train_size, val_size, test_size = int(np.floor(sizes[0] * len(images))),\
                                      int(np.floor(sizes[1] * len(images))),\
                                      int(np.floor(sizes[2] * len(images)))

    unique_labels = np.unique(labels)
    for l in unique_labels:
        indices = np.where(labels == l)
        mask = np.zeros(len(indices)) # train if mask[i]=0, test if mask[i]=1, val if mask[i]=2
        if l in test_classes: # only when the label in the relevant
            test_size = int(np.floor(sizes[0] * len(indices)))
            test_indices = np.random.choice(np.where(mask == 0), test_size)
            mask[test_indices] = 1

        val_size = int(np.floor(sizes[1] * len(indices)))
        test_indices = np.random.choice(np.where(mask == 0), val_size)
        mask[test_indices] = 2

        datasubsets["train"][0] += [images[i] for i in indices[np.where(mask == 0)]]
        datasubsets["train"][1] += (l * np.ones(len(np.where(mask == 0)))).tolist()

        datasubsets["test"][0] += [images[i] for i in indices[np.where(mask == 1)]]
        datasubsets["test"][1] += (l * np.ones(len(np.where(mask == 1)))).tolist()

        datasubsets["val"][0] += [images[i] for i in indices[np.where(mask == 2)]]
        datasubsets["val"][1] += (l * np.ones(len(np.where(mask == 2)))).tolist()

    return datasubsets


def generate_datafile_from_dict_with_dirname(output_dir, data_dict, line_sep):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for key, tuple in data_dict.items():
        images_paths, labels = tuple
        lines_list = list(zip(images_paths, labels))
        lines = ["{}{}{}\n".format(pair[0], line_sep,  pair[1]) for pair in lines_list]
        with open(os.path.join(output_dir, "{}.txt".format(key)), 'w') as subdata:
            subdata.writelines(lines)

def get_map_file_path(output_path, dataset_name):
    return os.path.join(output_path, "{}_map.txt".format(dataset_name))

def get_target_file_path(output_path):
    return os.path.join(output_path, "target.txt")
def get_alien_file_path(output_path):
    return os.path.join(output_path, "alien.txt")

def split_into_target_and_alien(map_file, output_path, target_labels):
    images, labels = read_dataset_map(map_file, PATH_LABEL_SEP)

    target_paths = []
    alien_paths = []
    for i in range(len(images)):
        if str(labels[i]) in target_labels:
            target_paths.append(images[i])
        else:
            alien_paths.append(images[i])

    with open(get_target_file_path(output_path), 'w') as tf:
        lines = [path +PATH_LABEL_SEP+"1\n" for path in target_paths]
        tf.writelines(lines)

    with open(get_alien_file_path(output_path), 'w') as af:
        lines = [path +PATH_LABEL_SEP+"0\n" for path in alien_paths]
        af.writelines(lines)


def insert_lines(dest, paths, labels):
    assert len(paths) == len(labels)
    with open(dest, 'a') as df:
        lines = ["{}{}{}\n".format(paths[i], PATH_LABEL_SEP, labels[i]) for i in range(len(paths))]
        df.writelines(lines)
