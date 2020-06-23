import os
import gzip
import json
import re
import argparse

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

def get_config():
    parser = argparse.ArgumentParser(description='Parse Amazon json file')
    parser.add_argument('--inputpath', '-ip', help='File to parse path')
    parser.add_argument('--outputpath', '-op', help='Directory for the outputs')
    parser.add_argument('--maxlines', '-ml', type=int, help='Maximum lines to parse')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_config()
    p = Parser(args.inputpath, args.maxlines)
    if not os.path.exists(args.outputpath):
        os.makedirs(args.outputpath)
    p.write_items(args.outputpath)