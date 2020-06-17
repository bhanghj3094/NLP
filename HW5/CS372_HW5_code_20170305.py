import nltk, re, wikipediaapi
from pprint import pprint


# wikipedia API
wiki = wikipediaapi.Wikipedia(language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)


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


def tokenize(text):
    """Returns text tokenized with nltk.

    Split into words, and then annotate with part-of-speech tags.
    """
    return nltk.pos_tag(nltk.word_tokenize(text))


def annotate_snippet(item):
    """Annotate snippet of pronoun, A, B.

    Returns:
        tokenized_text (List): result by function 'tokenize'
        indexes (List of Tuples): Locates the indexes of desired pronoun, 
            name A, name B of tokenized_text above. Each element is shown as 
            tuple, with start and end index.
            [
                (start_idx, end_idx),  # pronoun
                ... # name A, name B
            ]
        answer (Tuple of Booleans): whether name A, name B is a reference of the given 
            pronoun. (coreference of name A, coreference of name B)
        url (String): wikipedia url used for getting page context.
    """
    text, pronoun, pronoun_offset, A, A_offset, A_coref, B, B_offset, B_coref, url = item

    # initialize return values
    tokenized_text = []
    indexes = [None, None, None]
    answer = (A_coref, B_coref)

    # sort offsets
    offsets = [(int(pronoun_offset), "P"), (int(A_offset), "A"), \
               (int(B_offset), "B"), (len(text), "END")]
    offsets.sort()

    # divide, tokenize, and join. 
    recent_offset = 0
    for offset, word_type in offsets:
        tokens = tokenize(text[recent_offset:offset])
        tokenized_text.extend(tokens)

        # modify indexes
        start_idx = len(tokenized_text)
        if word_type == "P":
            word_len = len(nltk.word_tokenize(pronoun))
            indexes[0] = (start_idx, start_idx + word_len)
        elif word_type == "A":
            word_len = len(nltk.word_tokenize(A))
            indexes[1] = (start_idx, start_idx + word_len)
        elif word_type == "B":
            word_len = len(nltk.word_tokenize(B))
            indexes[2] = (start_idx, start_idx + word_len)
        elif word_type == "END":
            break
        else:  # not reached
            assert False
        
        # update recent_offset
        recent_offset = offset

    assert indexes[0] and indexes[1] and indexes[2]
    return tokenized_text, indexes, answer, url


def get_page_context(url):
    """Get page context from the url.

    Returns:
        text (String): text of wikipedia page. 
            None if page does not exist.
    """
    base_len = len("http://en.wikipedia.org/wiki/")
    page_name = url[base_len:]
    wiki_page = wiki.page(page_name)
    if not wiki_page.exists():
        return None
    return wiki_page.text


def main():
    # get GAP datasets
    development, test, validation = parse_gap()

    # annotate the snippet
    for idx, item in enumerate(test):
        tokenized_text, indexes, answer, url = annotate_snippet(item)
        page_text = get_page_context(url)
        

if __name__ == "__main__":
    main()
