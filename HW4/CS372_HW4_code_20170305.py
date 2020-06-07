import nltk
import re, random
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


def additional_tags(elem):
    word, tag = elem
    if word.lower() == 'but': tag = "BUT"
    if word.lower() == 'that': tag = "THAT"
    if word.lower() == 'whether': tag = "WHETHER"
    return (word, tag)


def chunk(sentence_text):
    """
    """
    syntax = r"""
        # Conjuctions
        CONJ: {<RB><,>}
        # Noun Phrase
        NP: {<DT|PRP\$>? (<JJ.*><CC>)* <CD|JJ.*|VBG|VBN>* <NN.*|VBG|CD|POS|PRP>+  (<\(>(<CC>?<NN.*|JJ>+)+<\)>)?}
            {<PRP|EX>}
        # Verb Phrase
        VP: {<VB|VBP|VBZ|VBD>(<VBN><IN|TO>)?}
            }<VBG>{  # chinking
        # Multiple Noun Phrase
        MNP: {<NP> (<,><NP>)+ (<,><CC><NP>)}
             {<NP> (<CC><NP>)?}     
        # Preposition Phrase
        INP: {<IN><MNP>}
        TOP: {<TO><MNP|VP>}
        # Clause
        CLAUSE: {<MNP|W.*><INP|TOP>* <VP><MNP>*<INP|TOP>* (<CC|,>? <VP><MNP>*<INP|TOP>*)*}
        # That Phrase
        THATP: {<THAT><CLAUSE>}
        # Whether Phrase
        WHETHERP: {<WHETHER><CLAUSE>}
        # How to distinguish preposition and subordinating conjunction?
    """
    # Chunkers
    parse_chunker = nltk.RegexpParser(syntax, loop=2)

    # Tokenize, pos_tag, and chunk.
    tokens = nltk.word_tokenize(sentence_text)
    tagged = list(map(additional_tags, [
        (word, tag)
        for word, tag in nltk.pos_tag(tokens)
        if not re.match(r"RB.*", tag)
        if not re.match(r"MD", tag)
    ]))

    return parse_chunker.parse(tagged)


def extract_relations(sentences):
    """
    """
    for idx, sentence in enumerate(sentences):
        text, triple = sentence
        chunked_sentence = chunk(text)
        print("(%d):" % (idx + 1), chunked_sentence)


def main():
    # divide sentences into train, and test sets.
    sentences = get_tagged_sentences()
    # random.shuffle(sentences)
    train = sentences[:80]
    test = sentences[80:]

    # train chunker
    extract_relations(sentences[90:100])


if __name__ == "__main__":
    main()
