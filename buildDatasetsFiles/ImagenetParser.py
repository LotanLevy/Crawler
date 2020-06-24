
import os
import argparse
import numpy as np
from buildDatasetsFiles import utils
from buildDatasetsFiles.utils import PATH_LABEL_SEP



def get_map_path(output_path, name):
    return os.path.join(output_path, "{}_map.txt".format(name))



def generate_path_label_file_map(main_dir, output_path, label_file, name):
    images_names = os.listdir(main_dir)
    with open(label_file, "r") as lf:
        labels = lf.readlines()
        labels = [int(i) for i in labels]

    lines_list = list(zip(images_names, labels))
    lines = ["{}{}{}\n".format(os.path.join(main_dir, pair[0]),PATH_LABEL_SEP, pair[1]) for pair in lines_list]
    with open(get_map_path(output_path, name), "w") as mf:
        mf.writelines(lines)





def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')

    parser.add_argument('--inputpath', '-ip', help='File to parse path')
    parser.add_argument('--labelspath', '-lp', help='File to parse the labels')

    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')

    return parser.parse_args()


if __name__ == "__main__":
    name = "imagenet"
    args = get_config()
    if not os.path.exists(args.outputpath):
        os.makedirs(args.outputpath)
    generate_path_label_file_map(args.inputpath, args.outputpath, args.labelspath, name)
    datasubsets = utils.split_data_into_subsets_with_filename(get_map_path( args.outputpath, name), [], [0.9,0.1,0])
    utils.generate_datafile_from_dict_with_dirname(args.outputpath, datasubsets, PATH_LABEL_SEP)