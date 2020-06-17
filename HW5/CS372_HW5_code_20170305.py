import nltk, re
from pprint import pprint


def parse_gap():
    """Parse GAP reference datasets

    Returns:
        development, test, validation (List): each lists all contain
            same element form as below. 
            [
                (
                    text, pronoun, pronoun-offset, 
                    A, A-offset, A-coref, 
                    B, B-offset, B-coref, 
                    URL
                )
                , ...
            ]
    """
    development = []
    f = open("gap-coreference/gap-development.tsv", 'r')
    f.readline()  # Remove first line
    for line in f.readlines():
        elem = tuple(line.strip().split('\t')[1:])
        development.append(elem)
    f.close()

    test = []
    f = open("gap-coreference/gap-test.tsv", 'r')
    f.readline()  # Remove first line
    for line in f.readlines():
        elem = tuple(line.strip().split('\t')[1:])
        test.append(elem)
    f.close()

    validation = []
    f = open("gap-coreference/gap-validation.tsv", 'r')
    f.readline()  # Remove first line
    for line in f.readlines():
        elem = tuple(line.strip().split('\t')[1:])
        validation.append(elem)
    f.close()

    return development, test, validation


def tokenize_sentences(text):
    """Returns sentences tokenized with nltk.

    First split into sentences, then annotated with
    part-of-speech tags. 
    """
    return [
        nltk.pos_tag(nltk.word_tokenize(sent))
        for sent in nltk.sent_tokenize(text)
    ]


def annotate_snippet(item):
    """Annotate snippet of pronoun, A, B.

    Returns:
        sentences (List): result by function tokenize_sentences()
        pronoun_index (Tuple): (sent_index, word_index) of sentences
            above. Locates desired pronoun. 
        a_index (Tuple): (sent_index, word_index) of sentences
            above. Locates desired name A. 
        b_index (Tuple): (sent_index, word_index) of sentences
            above. Locates desired name B. 
        answer (Tuple): (A_coref, B_coref)
        url (String): returns url
    """
    text, pronoun, pronoun_offset, A, A_offset, A_coref, B, B_offset, B_coref, url = item

    # initialize return values
    sentences = tokenize_sentences(text)
    pronoun_index, a_index, b_index = None, None, None
    modified = [False, False, False]
    answer = (A_coref, B_coref)

    offset = 0  # current offset
    # for attaching next word..
    attach = False  # if true, attach current word without offset.
    for sent_idx, sentence in enumerate(sentences):
        for word_idx, word in enumerate(sentence):
            # on specific patterns, do not add space
            no_space = word[0] in ['.', ',', '!', '?', '*', "'s", ')', "''", ':', '...', ';']
            if not (sent_idx == 0 and word_idx == 0) and \
               not no_space and not attach:
                offset += 1

            if int(pronoun_offset) - 2 <= offset <= int(pronoun_offset) + 2:
                pronoun_index = (sent_idx, word_idx)
                modified[0] = True
            if int(A_offset) - 2 <= offset <= int(A_offset) + 2:
                a_index = (sent_idx, word_idx)
                modified[1] = True
            if int(B_offset) - 2 <= offset <= int(B_offset) + 2:
                b_index = (sent_idx, word_idx)
                modified[2] = True

            # decide attach
            attach = word[0] in ['*', '(', '``', '#']
            offset += len(word[0])

    assert modified[0] and modified[1] and modified[2]
    return sentences, pronoun_index, a_index, b_index, answer, url


def main():
    # get GAP datasets
    development, test, validation = parse_gap()

    for idx, item in enumerate(test[:]):
        print(idx, item)
        print(annotate_snippet(item))
        

if __name__ == "__main__":
    main()
