import json
import inflect
import os
IMAGENET_CLASSES_PATH = "C:\\Users\\lotan\\Downloads\\class_id_to_label.txt"

AMAZON_CLASSES_PATH = "C:\\Users\\lotan\\Documents\\studies\\Affordances\\deep-one-class\\Crawler\\output\\labelToCls.json"

process_word = lambda word: word.strip().lower()
engine = inflect.engine()


def read_classes_from_imagenet_file(path):
    with open(path, 'r') as f:
        data = eval(f.read())
        words = set()
        for description in data.values():
            sub_words = description.split(',')
            for subword in sub_words:
                words.add(process_word(subword))
                subword_splitted = subword.split(" ")
                if len(subword_splitted) > 1:
                    words.add(process_word(subword_splitted[-1]))
        return words

def filter_amazon_classes_by_keywords(path, keywords, dest):
    relevant_objects = dict()
    with open(path, 'r') as f:
        data = json.load(f)
        classes = data.keys()
        relevant_objects = dict()
        for cls_name in classes:
            word = process_word(cls_name)
            plural = engine.plural(word)
            if word in keywords or plural in keywords:
                relevant_objects[cls_name] = data[cls_name]
    with open(os.path.join(dest, "amazon_relevant_classes.json"), 'w') as f:
        json.dump(relevant_objects, f)
    return relevant_objects

keywords = read_classes_from_imagenet_file(IMAGENET_CLASSES_PATH)
results = filter_amazon_classes_by_keywords(AMAZON_CLASSES_PATH, keywords, "C:\\Users\\lotan\\Documents\\studies\\Affordances\\deep-one-class\\Crawler\\output")

