import os
import argparse
import utils
import re


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
    lines = ["{} {}\n".format(os.path.join(images_main_dir, pair[0]), pair[1]) for pair in lines_list]
    with open(os.path.join(output_path, "{}_map.txt".format(dataset_name)), "w") as mf:
        mf.writelines(lines)

def split_into_target_and_alien(map_file, output_path, target_labels):
    images, labels = utils.read_dataset_map(map_file)

    target_paths = []
    alien_paths = []
    for i in range(len(images)):
        if labels[i] in target_labels:
            target_paths.append(images[i])
        else:
            alien_paths.append(images[i])










def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')
    parser.add_argument('--datasetdir', '-d', help='File to parse path')
    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')
    parser.add_argument('--datasetname', '-name', type=int, help='Maximum lines to parse')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_config()

    generate_path_label_file_map(args.datasetdir, args.datasetname, args.outputpath)

    image_name("")