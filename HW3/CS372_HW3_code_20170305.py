#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import brown, cmudict
from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from pprint import pprint
import time

# Globals
heteronym_keys = []
heteronyms = dict()
# tagged_sentences = brown.tagged_sents()
cdict = cmudict.dict()


def get_heteronyms():
    """Get heteronym list.

    If `heteronyms.txt` exists, parse it and return. 
    Else, build heteronym list.
    """
    file_name = 'heteronyms.txt'
    # Candidate for heteronyms
    heteronym_keys.extend([ word
        for word, pronounciations in cdict.items()
        # Has different pronounciations
        if len(pronounciations) >= 2
        # Has more than one meaning
        if len(wn.synsets(word)) >= 2
    ])

    # Web crawling
    file = open(file_name, "a")
    for idx, word in enumerate(heteronym_keys):
        entry = get_heteronym_entry(word)
        # Insert to dictionary
        if entry:
            file.write("".join([word, ": ", str(entry), "\n"]))
            heteronyms[word] = entry
        time.sleep(1) # HTTPError code 429: Too Many Requests
    file.close()


def get_heteronym_entry(word):
    """Web crawler to verify heteronym.

    Args:
        word (String): candidate `word` for heteronym. 
    
    Returns:
        List: Build heteronym entry. List of pronounciations dictionary, 
            with each entry as list of part-of-speech and meaning tuple. 
            If no entry exists, return empty list. 
            [
                {
                    pronounciation: [
                        (part-of-speech1, meaning1-1),
                        (part-of-speech1, meaning1-2),
                        (part-of-speech2, meaning2-1),
                        ...
                    ], ...
                },
                ...
            ]

    Raises:
        Exception: HTTPError except 404. 
        AttributeError: No required attribute for word in web.
    """
    # urllib
    url = "https://www.lexico.com/en/definition/"
    try:
        page = request.urlopen(url + word)
    except HTTPError as e:
        if e.code == 404:
            return []
        raise Exception
    html = page.read().decode('utf8')

    # beautifulsoup
    soup = BeautifulSoup(html, 'html.parser')
    homographs = soup.find_all(class_="entryGroup")

    # not a heteronym
    if len(homographs) <= 1: return []

    # html content elements
    contents = soup.find(class_="entryWrapper").contents
    locations = [
        contents.index(homograph)
        for homograph in homographs
    ]

    # find pronounciation, part-of-speech, and meaning.
    result = dict()

    # exclude ones with all same pronounciation
    try:
        pronounciations = [
            homograph.find_all(class_="phoneticspelling")[0].get_text()
            for homograph in homographs
        ]
        # not a heteronym, but homograph
        if len(set(pronounciations)) == 1: 
            return []

        for idx, homograph in enumerate(homographs):
            # grambs: for each pronounciation, for each part-of-speech
            start_location = locations[idx]
            end_location = locations[idx+1] if idx < len(homographs) - 1 else len(contents)
            grambs = [
                content
                for content in contents[start_location:end_location]
                if 'class="gramb"' in str(content)
            ]
            
            # add each part-of-speech with meaning.
            meaning_list = []
            for gramb in grambs:
                pos = gramb.h3.find(class_="pos").get_text()
                
                # search only direct children
                meaning_list.extend([ 
                    (
                        pos,
                        meaning.find(class_="trg").p.find(class_="ind").get_text()
                    )
                    for meaning in gramb.ul.find_all("li", recursive=False)
                ])

            # insert to existing pronounciation, else create new entry.
            try:
                existing_list = result[pronounciations[idx]]
                result[pronounciations[idx]] = existing_list + meaning_list
            except KeyError:
                result[pronounciations[idx]] = meaning_list
    except AttributeError:
        return []

    # close and return entry
    page.close()
    return list(result.items())


# Main function for word processing algorithm. 
def main():
    """
    """
    get_heteronyms()


if __name__ == "__main__":
    main()
