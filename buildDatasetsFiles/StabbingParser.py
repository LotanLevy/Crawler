
import os
import argparse

from buildDatasetsFiles.utils import PATH_LABEL_SEP


def generate_path_label_file_map(main_dir, output_path, name):
    sub_cls_dirs = os.listdir(main_dir)
    images = []
    labels = []
    for subcls in sub_cls_dirs:
        full_path = os.path.join(main_dir, subcls)
        dirs = os.listdir(full_path)
        for subsubcls in dirs:
            full_full_path = os.path.join(full_path, subsubcls)
            files = os.listdir(full_full_path)
            images += [os.path.join(full_full_path, imagename) for imagename in files]
            labels += [1] * len(files)


    lines_list = list(zip(images, labels))
    lines = ["{}{}{}\n".format(os.path.join(main_dir, pair[0]),PATH_LABEL_SEP,  pair[1]) for pair in lines_list]
    with open(os.path.join(output_path, "{}_map.txt".format( name)), "w") as mf:
        mf.writelines(lines)

def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')

    parser.add_argument('--inputpath', '-ip', help='File to parse path')
    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_config()
    if not os.path.exists(args.outputpath):
        os.makedirs(args.outputpath)
    generate_path_label_file_map(args.inputpath, args.outputpath, "stabbing")
