import nltk
from nltk.corpus import conll2000
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


class BigramChunker(nltk.ChunkParserI):
    def __init__(self, train_sents):
        train_data = [[(t,c) for w,t,c in nltk.chunk.tree2conlltags(sent)]
                      for sent in train_sents]
        self.tagger = nltk.BigramTagger(train_data)

    def parse(self, sentence):
        pos_tags = [pos for (word,pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word,pos),chunktag)
                     in zip(sentence, chunktags)]
        return nltk.chunk.conlltags2tree(conlltags)


def train_chunker(sentences):
    """
    """
    syntax = r"""
        # Determiner | Preposition, Adjectives, and Noun + Abbreviation with bracket.
        NP: {<\(>?<DT|PRP\$?>?<CD|VBN|VBP>?((<CC|,>?<JJ.*>*)+<NN.*>+<CD>?)+(<\(>(<CC>?<NN.*|JJ>+)+<\)>)?<\)>?}   
            # }{                              # chinking
    """
    # CoNLL dataset for training and test. 
    train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP', 'VP'])
    test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP', 'VP'])

    # Chunkers
    parse_chunker = nltk.RegexpParser(syntax)
    bigram_chunker = BigramChunker(train_sents)

    print(parse_chunker.evaluate(test_sents))
    print(bigram_chunker.evaluate(test_sents))

    for sentence in sentences:
        text, triple = sentence
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        chunked0 = parse_chunker.parse(tagged)
        chunked1 = bigram_chunker.parse(tagged)
        print(chunked0)
        print(chunked1)


def main():
    # divide sentences into train, and test sets.
    sentences = get_tagged_sentences()
    random.shuffle(sentences)
    train = sentences[:80]
    test = sentences[80:]

    # train chunker
    train_chunker(test)

    # detect_entities()
    # extract_relations()


if __name__ == "__main__":
    main()
