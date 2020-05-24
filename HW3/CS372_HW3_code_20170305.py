#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import brown, cmudict

# Globals
heteronyms = dict()
heteronym_keys = []
tagged_sentences = brown.tagged_sents()
pronounce = cmudict.dict()


def get_heteronyms(heteronyms, heteronym_keys):
    """
    Add heteronyms from wordnet synsets.
    Update dictionary of heteronyms. 
    {
        word1: [(Pos1-1, definition1-1), (Pos1-2, definition1-2), ..],
        word2: [(Pos2-1, definition2-1), (Pos2-2, definition2-2), ..],
        ..
    } # 'Pos' can be equal or different. 
    """
    for lemma_name in list(wn.all_lemma_names()):
        heteronyms[lemma_name] = [
            (synset.pos(), synset.definition())
            for synset in wn.synsets(lemma_name)
        ]
    heteronym_keys.extend(heteronyms.keys())


# Main function for word processing algorithm. 
def main():
    """
    """
    get_heteronyms(heteronyms, heteronym_keys)


if __name__ == "__main__":
    main()
