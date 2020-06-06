import nltk
import random
from pprint import pprint


def get_tagged_sentences():
    """Reads pre-processed tagged sentences.

    Returns:
        sentences (list): each item follows below format;
            (
                sentence_text,
                (X, action, Y)
            )
    """
    f = open('sentences.txt', 'r')
    lines = f.readlines()

    # parse sentences
    sentences = []
    text = None
    for line in lines:
        if line.startswith("(Text)"):
            text = line.strip()[7:]
        elif line.startswith("(Tags)"):
            sentences.append(
                (text, eval(line.strip()[7:]))
            )
        else: continue
    f.close()
    return sentences


def main():
    # divide sentences into train, and test sets.
    sentences = get_tagged_sentences()
    random.shuffle(sentences)
    train = sentences[:80]
    test = sentences[80:]


if __name__ == "__main__":
    main()
