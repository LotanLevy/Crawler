
import json
import nltk

nltk.download('averaged_perceptron_tagger')


JSON_PATH =  "C:\\Users\\lotan\\Downloads\\labelToCls.json"


if __name__ == "__main__":
    with open(JSON_PATH, 'r') as json_file:
        data = json.load(json_file)
        words = []
        for word in data.keys():
            if len(word) >= 1:
                words.append(word.strip())


        print(words)
        print(nltk.pos_tag(words))