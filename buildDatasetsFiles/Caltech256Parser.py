import argparse
import os
from buildDatasetsFiles import utils
from buildDatasetsFiles.utils import PATH_LABEL_SEP

def create_label_map(full_labels, output_path, name):
    # create labels map
    labels_dict = dict()
    label_to_dir_dict = dict()
    for full in full_labels:
        pair = full.split(".")
        labels_dict[pair[0]] = pair[1]
        label_to_dir_dict[full] = pair[0]
    with open(os.path.join(output_path, "{}_class_id_to_label.txt".format(name)), "w") as lf:
        lf.write(str(labels_dict))
    return label_to_dir_dict


def generate_path_label_file_map(main_dir, output_path, name):
    full_labels = os.listdir(main_dir)
    label_to_dir_dict = create_label_map(full_labels, output_path, name)
    images = []
    labels = []
    for dir in full_labels:
        full_path = os.path.join(main_dir, dir)
        images_names = os.listdir(full_path)
        images += [os.path.join(dir, name) for name in images_names]
        labels += [int(label_to_dir_dict[dir])] * len(images_names)

    lines_list = list(zip(images, labels))
    lines = ["{}{}{}\n".format(os.path.join(main_dir, pair[0]), PATH_LABEL_SEP, pair[1]) for pair in lines_list]
    with open(utils.get_map_file_path(output_path, name), "w") as mf:
        mf.writelines(lines)


def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')

    parser.add_argument('--inputpath', '-ip', help='File to parse path')
    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')
    parser.add_argument("--targetlabels", "-l", help='labels split by comma')


    return parser.parse_args()


if __name__ == "__main__":
    args = get_config()
    name = "caltech"
    if not os.path.exists(args.outputpath):
        os.makedirs(args.outputpath)
    generate_path_label_file_map(args.inputpath, args.outputpath, name)

    #spliting to target and alien
    target_map = utils.get_target_file_path(args.outputpath)
    map_file = utils.get_map_file_path(args.outputpath, name)
    target_labels = args.targetlabels.split(",")
    utils.split_into_target_and_alien(map_file, args.outputpath, target_labels)

    #augmentation
    to_augment_paths, labels = utils.read_dataset_map(target_map, PATH_LABEL_SEP)
    paths, labels = utils.AugmentHelper.create_augmentation_dir("augmented_target", to_augment_paths, labels,
                                                                args.augmentdir)
    utils.insert_lines(target_map, paths, labels)

    #splitting target into subsets
    datasubsets = utils.split_data_into_subsets_with_filename(target_map, [1], [0.5, 0, 0.5])
    utils.generate_datafile_from_dict_with_dirname(args.outputpath, datasubsets, PATH_LABEL_SEP)