import nltk
import re, random
from pprint import pprint


def get_tagged_sentences():
    """Reads pre-processed tagged sentences.

    Returns:
        sentences (list): each item follows below format;
            (
                sentence_text, 
                [(X, Action, Y), ..]
            )
    """
    f = open('CS372_HW4_output_20170305.csv', 'r')
    lines = f.readlines()

    # parse sentences
    train = []
    test = []
    text = None
    dataType = "train"
    for line in lines:
        if line.startswith("Text"):
            text = line.strip()[6:]
        elif line.startswith("DataType"):
            dataType = "test" if "test" == line.strip()[10:] else "train"
        elif line.startswith("Tags"):
            if dataType == "train":
                if not line.strip()[6:]: continue  # TO REMOVE
                train.append(
                    (text, eval(line.strip()[6:]))
                )
            else:
                if not line.strip()[6:]: continue  # TO REMOVE
                test.append(
                    (text, eval(line.strip()[6:]))
                )
        else: continue
    f.close()
    return train, test


def additional_tags(elem):
    """Modify tags for certain words."""
    word, tag = elem
    if word.lower() == 'but': tag = "BUT"
    if word.lower() == 'that': tag = "THAT"
    if word.lower() == 'whether': tag = "WHETHER"
    return (word, tag)


def chunk(sentence_text):
    """Chunk the given sentence text.

    Args:
        sentence_text (string): given sentence 
            in plain text.

    Returns:
        chunked_sentence (tree): chunked by 
            predefined syntax with RegexpParser.
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
        # How to distinguish preposition and subordinating conjunction?
        # That Phrase
        THATP: {<THAT><CLAUSE>}
        # Whether Phrase
        WHETHERP: {<WHETHER><CLAUSE>}
    """
    # Chunker
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


def extract(chunked_sentence):
    """Extract relations <X, Action, Y> from chunked tree. 

    Args:
        chunked_sentence (tree): chunked sentence 
            expressed in tree.

    Returns:
        relations (list): [(X, Action, Y), ..]
    """
    def traverse(t):
        try:
            t.label()
        except AttributeError:
            print(t, end=" ")
        else:
            # Now we know that t.node is defined
            print('(', t.label(), end=" ")
            for child in t:
                traverse(child)
            print(')', end=" ")

    relations = traverse(chunked_sentence)
    return [("X", "Action", "Y")]


def evaluate(result):
    """Evaluate extraced relations.

    Args:
        result (list): list of tuples;
            [
                (
                    extracted_relations,
                    answer_relations
                ),
                ...
            ]
            extracted_relations, answer_relations;
            [(X, Action, Y), ..]

    Prints:
        Precision (float): --
        Recall (float): --
        F-score (float): --
    """


def main():
    # divide sentences into train, and test sets.
    train, test = get_tagged_sentences()

    # build chunker and relation extraction module
    # from train data with manual modification.
    for idx, sentence in enumerate(train[0:10]):
        text, triples = sentence
        chunked_sentence = chunk(text)
        print("(%d):" % (idx + 1), chunked_sentence)
        relations = extract(chunked_sentence)
        print(relations)

    # # input test data
    # result = []
    # for idx, sentence in enumerate(test):
    #     text, triples = sentence
    #     chunked_sentence = chunk(text)
    #     relations = extract(chunked_sentence)
    #     result.append((relations, triples))

    # # evaluate
    # evaluate(result)


if __name__ == "__main__":
    main()
