import os
import gzip
import json
import re
import argparse
import urllib.request

DESCRIPTION_REGEX = ".*(description: \".*\"),"
pattern = re.compile(DESCRIPTION_REGEX)


AMAZON_FILE_PATH = "C:\\Users\\lotan\\Documents\\AmazonParser\\metadata.json.gz"

class Parser:

    def __init__(self, filepath, maxlines):
        self.items = dict()

        self.parse_file(filepath, maxlines)

    def write_items(self, outputpath):
        key_dict = dict()

        i = 0

        with open(os.path.join(outputpath, "urlfile.txt"), 'w') as file:
            for key in self.items.keys():
                key_dict[key] = i
                key_items = self.items[key]
                labels = [str(i)]*len(key_items)
                lines = list(zip(key_items, labels))
                for line in lines:

                    file.write(line[0] + " " + line[1] + "\n")
                i += 1

        with open(os.path.join(outputpath, "labelToCls.json"), 'w') as file:
            json.dump(key_dict, file)





    def parse_file(self, filepath, maxlines):
        lines = 0
        with gzip.open(filepath , 'r') as gzip_file:
            for line in gzip_file:  # Read one line.
                line = line.decode('utf-8')

                try:
                    if line:  # Any JSON data on it?
                        category_pattern = re.compile("'categories': \[\[(((?!\]).)*)\]\]")
                        url_pattern = re.compile("'imUrl': \'(((?!\').)*)\'")

                        m1 = category_pattern.search(line)
                        m2 = url_pattern.search(line)
                        if m1 is not None and m2 is not None:
                            categories = m1.group(1).replace("\'", "").split(",")
                            url = m2.group(1)
                            for c in categories:
                                if c not in self.items:
                                    self.items[c] = []
                                self.items[c].append(url)

                        lines += 1
                        if maxlines > 0 and lines >= maxlines:
                            break

                except json.decoder.JSONDecodeError as e:
                    print("line {} cant be parsed".format(line))
                    continue


def save_images(outputpath, urls_labels_map_file, max_items_for_cls, classes):
    main_path = os.path.join(outputpath, "amazon_dataset")
    item_num_dict = dict()
    image_num=0
    with open(urls_labels_map_file, 'r') as file:
        for line in file:  # Read one line.
            line_items = line.split(" ")
            label = line_items[1].strip()
            if label not in classes:
                continue
            path = os.path.join(main_path, label)
            if label in item_num_dict:
                if item_num_dict[label] > max_items_for_cls:
                    continue
                item_num_dict[label] += 1
            else:
                item_num_dict[label] = 1

            if not os.path.exists(path):
                os.makedirs(path)


            try:
                urllib.request.urlretrieve(line_items[0].strip(),
                                           os.path.join(path, "{}.jpg".format(image_num)))
                image_num += 1

            except urllib.error.HTTPError:
                continue

def parseClassesFile(filepath):
    classes = []
    with open(filepath, 'r') as file:
        lines = file.read().splitlines()
        for line in lines:
            classes.append(int(line.strip().split(":")[1]))
    return classes






def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')
    parser.add_argument('--parse', '-p', action="store_true", default=False, help='parse for urls')
    parser.add_argument('--download', '-d', action="store_true", default=False, help='download images')


    parser.add_argument('--inputpath', '-ip', help='File to parse path')
    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')
    parser.add_argument('--maxlines', '-ml', default=-1, type=int, help='Maximum lines to parse')
    parser.add_argument('--maxforcls', '-mc', default=1000, type=int, help='Maximum items for cls')
    parser.add_argument('--relevantcls', '-l', help='a list of the relevant labels')



    return parser.parse_args()

if __name__ == "__main__":
    args = get_config()
    if not os.path.exists(args.outputpath):
        os.makedirs(args.outputpath)
    if args.parse:
        p = Parser(args.inputpath, args.maxlines)
        p.write_items(args.outputpath)
    if args.download:
        # classes = args.relevantcls.split(",")
        classes = parseClassesFile(args.relevantcls)
        save_images(args.outputpath, os.path.join(args.outputpath, "urlfile.txt"), args.maxforcls, classes)