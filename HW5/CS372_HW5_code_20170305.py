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
        tokenized_text (List of Tuples): result by function 'tokenize'
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

    Args:
        url (String): url in following format
            "http://en.wikipedia.org/wiki/~~"

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


def update_annotation(page_text, original_text, indexes):
    """Enlarge text with page_text, update indexes.

    Args:
        page_text (String): page text from wikipedia API
        original_text (String): original snippet text
        indexes (List of Tuples): result by function 'annotate_snippet'

    Returns:
        page_tokenized_text (List of Tuples): result by function 'tokenize'
        updated_indexes (List of Tuples): push indexes according to added page_text
    """
    # find original_text in page_text
    paragraph = None
    found_idx = -1
    for line in page_text.split("\n"):
        idx = line.find(original_text)
        if idx != -1:
            paragraph = line
            found_idx = idx
            break
    assert paragraph

    # update tokenized text, and indexes
    page_tokenized_text = tokenize(paragraph)
    shift = len(tokenize(paragraph[:found_idx]))
    updated_indexes = [
        (start_idx + shift, end_idx + shift)
        for start_idx, end_idx in indexes
    ]
    return page_tokenized_text, updated_indexes


def chunk(tokenized_text):
    """Chunk tokenized_text by part-of-speech tags.

    Args:
        tokenized_text (List of Tuples): result by function 'tokenize'

    Returns:
        chunked_text (Tree): chunked by 
            predefined syntax with RegexpParser.
    """
    return []


def extract(chunked_text, indexes):
    """Extract information from chunked_text, and determine result. 

    Args:
        chunked_text (Tree): result by function 'chunk'
        indexes (List of Tuples): result by function 'annotate_snippet'

    Returns:
        result (Tuple of Booleans): boolean whether names in indexes
            are coreferences of pronoun in indexes.
    """
    return (True, False)


def save(mode, result):
    """Build result tsv file.

    Args:
        mode (String): one of snippet, page.
    
    Creates:
        Saves output file in tsv format. 
        Three columns separated by '\t'.
    """
    f = open("CS372_HW5_%s_output_20170305.tsv", 'w')
    for idx, element in enumerate(result):
        content = ["development-%d" % (idx+1), "TRUE", "FALSE"]
        f.write("\t".join(content) + "\n")
    f.close()


def main():
    # get GAP datasets
    development, test, validation = parse_gap()

    # get results
    snippet_results = []
    page_results = []
    for idx, item in enumerate(test):
        # annotate the snippet
        tokenized_text, indexes, answer, url = annotate_snippet(item)
        chunked_text = chunk(tokenized_text)
        # result = extract(chunked_text, indexes)
        # snippet_results.append(result)

        # # adjust result with page context
        # page_text = get_page_context(url)
        # original_text = item[0]
        # if not page_text or original_text not in page_text:
        #     page_results.append(result)
        #     continue
        # # find original text and get neighbour texts.
        # page_tokenized_text, updated_indexes = update_annotation(page_text, original_text, indexes)
        # chunked_text = chunk(page_tokenized_text)
        # result = extract(chunked_text, updated_indexes)
        # page_results.append(result)

    # # save snippet, page results
    # save("snippet", snippet_results)
    # save("page", page_results)


if __name__ == "__main__":
    main()
