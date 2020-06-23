import os
import argparse
import utils

PATH_LABEL_SEP = "$"


def get_map_file_path(output_path, dataset_name):
    return os.path.join(output_path, "{}_map.txt".format(dataset_name))

def get_target_file_path(output_path):
    return os.path.join(output_path, "target.txt")
def get_alien_file_path(output_path):
    return os.path.join(output_path, "alien.txt")



def generate_path_label_file_map(images_main_dir, dataset_name, output_path):
    labels_id = os.listdir(images_main_dir)
    images = []
    labels = []
    for dir in labels_id:
        full_path = os.path.join(images_main_dir, dir)
        images_names = os.listdir(full_path)
        images += [os.path.join(dir, name) for name in images_names]
        labels += [int(dir)] * len(images_names)

    lines_list = list(zip(images, labels))
    lines = ["{}{}{}\n".format(os.path.join(images_main_dir, pair[0]),PATH_LABEL_SEP, pair[1]) for pair in lines_list]
    with open(get_map_file_path(output_path, dataset_name), "w") as mf:
        mf.writelines(lines)

def split_into_target_and_alien(map_file, output_path, target_labels):
    images, labels = utils.read_dataset_map(map_file, PATH_LABEL_SEP)

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









def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')
    parser.add_argument('--map', '-m', action="store_true", default=False, help='creating map for the data')
    parser.add_argument('--split', '-s', action="store_true", default=False, help='splitting into target and alien')
    parser.add_argument('--augment_target', '-at', action="store_true", default=False, help='create augmentation files for the target')
    parser.add_argument('--augment_alien', '-aa', action="store_true", default=False, help='create augmentation files for the alien')



    parser.add_argument('--datasetdir', '-d', help='File to parse path')
    parser.add_argument('--augmentdir', '-ad', help='path to save the augmented images')

    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')
    parser.add_argument('--datasetname', '-name', help='dataset name')
    parser.add_argument("--targetlabels", "-l", help='labels split by comma')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_config()

    output_path = args.outputpath
    if not os.path.exists(output_path):
        os.makedirs(output_path)


    if args.map:
        generate_path_label_file_map(args.datasetdir, args.datasetname, output_path)
    if args.split:
        target_labels = args.targetlabels.split(",")
        map_path = get_map_file_path(output_path, args.datasetname)
        split_into_target_and_alien(map_path, output_path, args.targetlabels)
    if args.augment_target:
        to_augment_paths, labels = utils.read_dataset_map(get_target_file_path(output_path), PATH_LABEL_SEP)
        paths, labels = utils.AugmentHelper.create_augmentation_dir("augmented_target", to_augment_paths, labels, args.augmentdir)
        insert_lines(get_target_file_path(output_path), paths, labels)
    if args.augment_alien:
        to_augment_paths, labels = utils.read_dataset_map(get_alien_file_path(output_path), PATH_LABEL_SEP)
        paths, labels = utils.AugmentHelper.create_augmentation_dir("augmented_alien", to_augment_paths, labels, args.augmentdir)
        insert_lines(get_alien_file_path(output_path), paths, labels)
