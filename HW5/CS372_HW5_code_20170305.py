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


def filter(sentence):
    """Filter given sentence before any processing.

    Args:
        sentence (List): each sentence from 'tokenize'.
    
    Returns:
        filtered (List): removes elements according to 
            filter below.
    """
    filtered = [(word, tag)
        for word, tag in sentence
        if not re.match(r"RB.*", tag)  # remove adverbs
        if not re.match(r"MD", tag)  # remove modals
    ]
    return filtered


def tokenize(text):
    """Returns text tokenized as sentences with nltk.

    Split into sentences, then words, and annotate with part-of-speech 
    tags. Next, each sentence is filtered by 'filter'.
    """
    return [
        filter(nltk.pos_tag(nltk.word_tokenize(sent)))
        for sent in nltk.sent_tokenize(text)
    ]


def annotate_snippet(item):
    """Annotate snippet of pronoun, A, B.

    Returns:
        sentences (List of List): result by function 'tokenize'
        indexes (List of Tuples): Locates the indexes of desired pronoun, 
            name A, name B of sentences above. Each element is shown as 
            tuple, with sent_index, word_index, and length. 
            [
                (sent_index, word_index, length),  # pronoun
                ... # name A, name B
            ]
        answer (Tuple of Booleans): whether name A, name B is a reference of the given 
            pronoun. (coreference of name A, coreference of name B)
        url (String): wikipedia url used for getting page context.
    """
    text, pron, pron_offset, name_a, a_offset, a_coref, name_b, b_offset, b_coref, url = item

    # initialize return values
    sentences = tokenize(text)
    indexes = [None, None, None]
    answer = (a_coref == "TRUE", b_coref == "TRUE")

    # offsets to simple indexes
    simple_indexes = [
        sum([len(sent) for sent in tokenize(text[:int(pron_offset)])]),
        sum([len(sent) for sent in tokenize(text[:int(a_offset)])]),
        sum([len(sent) for sent in tokenize(text[:int(b_offset)])]),
    ]

    # find name A, name B. 
    index_count = 0
    for sent_index, sentence in enumerate(sentences):
        for word_index, word in enumerate(sentence):

            # check if pronoun, name A, or name B.
            for idx, simple_index in enumerate(simple_indexes):
                if simple_index == index_count:
                    word_length = 0
                    if idx == 0:
                        word_length = sum([len(sent) for sent in tokenize(pron)])
                    elif idx == 1:
                        word_length = sum([len(sent) for sent in tokenize(name_a)])
                    elif idx == 2:
                        word_length = sum([len(sent) for sent in tokenize(name_b)])
                    
                    # assert word length exists
                    assert word_length
                    indexes[idx] = (sent_index, word_index, word_length)

            # update simple index
            index_count += 1

    # assert indexes are found
    assert indexes[0] and indexes[1] and indexes[2]
    return sentences, indexes, answer, url


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
        page_sentences (List of Tuples): result by function 'tokenize'
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
        (sent_index + shift, word_index, length)
        for sent_index, word_index, length in indexes
    ]
    return page_tokenized_text, updated_indexes


def chunk(sentences, indexes):
    """Chunk each sentence using RegexpParser.

    Args:
        sentences (List of List): result by function 'tokenize'
        indexes (List of Tuples): result by function 'annotate_snippet'

    Returns:
        chunked_sentences (Tree): chunked by predefined syntax according 
            to part-of-speech tags.
        chunked_indexes (List of Tuples): updated indexes due to chunking.
            The format changes to ..
            [
                (sent_index, tree_index, length),  # pronoun
                ...  # name A, name B
            ]
            tree_index (Tuple): locate start of the word.
    """
    syntax = r"""
        # Noun Phrase
        NP: {<NNP><CD><,><CD>}  # Date
            {<DT|PRP\$>? (<JJ.?><CC>)*<CD|JJ.?>* <NN.?|CD|PRP|POS>+}

        # Multiple Noun Phrase
        MNP: {<NP>*<``><NP><''><NP>*}  # Quotation Mark
             {<NP><\(><NP><\)>}
             {<NP> (<,><NP>)+ (<,><CC><NP>)}
             {<NP> <CC><NP>}
             {<NP>}

        # Preposition Phrase
        PP: {<IN><MNP|VP>}

        # Verb Phrase
        V: {<VBD><VBN><RP>}
           {<VB.?>}
        VP: {<V><MNP|PP>+}
    """
    # chunker
    parse_chunker = nltk.RegexpParser(syntax, loop=2)

    # separate into sentences
    chunked_sentences = []
    for sentence in sentences:
        chunked_sentence = parse_chunker.parse(sentence)
        chunked_sentences.append(chunked_sentence)

    # locate indexes..
    def find_index(tree, count):
        """Find index of word count.

        Args:
            tree (Tree): tree-like structure by RegexpParser.
            count (Integer): smaller than number of leaves in tree.

        Returns:
            tree_index (Tuple): index of specific leaf in tree.
                ex. (0, 1) - first branch's second leaf.
        """
        curr = 0
        for idx, element in enumerate(tree):
            try:
                element.label()
            except AttributeError:
                if curr == count:
                    return (idx, )
                curr += 1
            else:
                elem_count = word_count(element)
                if count <= curr + (elem_count - 1):
                    recursive_index = find_index(element, count - curr)
                    return (idx, *recursive_index)
                curr += elem_count
        assert False  # not reached

    chunked_indexes = []
    for sent_index, word_index, length in indexes:
        tree_index = find_index(chunked_sentences[sent_index], word_index)
        chunked_indexes.append((sent_index, tree_index, length))
    return chunked_sentences, chunked_indexes


def word_count(tree):
    """Count number of words in tree.
    
    Returns:
        count (Integer): number of words.
    """
    count = 0
    for element in tree:
        try:
            element.label()
        except AttributeError: # leaf
            count += 1
        else: # branch
            count += word_count(element)
    return count


def extract(chunked_sentences, chunked_indexes):
    """Extract information from chunked_sentences, and determine result. 

    Args:
        chunked_sentences (Tree): result by function 'chunk'
        chunked_indexes (List of Tuples): result by function 'chunk'

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
    for idx, item in enumerate(test[1:2]):
        # annotate the snippet
        sentences, indexes, answer, url = annotate_snippet(item)
        chunked_sentences, chunked_indexes = chunk(sentences, indexes)

        # print("sentences: ", sentences)
        # print("indexes: ", indexes)
        # print("answer: ", answer)
        print("Raw text: ", item[0])
        for e in chunked_sentences:
            print(e)
        # print("chunked_indexes: ", chunked_indexes)

        # print(item[1], item[3], item[6])
        # for sent, word, length in indexes:
        #     print(sentences[sent][word:word+length])
        # for sent, tree, length in chunked_indexes:
        #     cs = chunked_sentences[sent]
        #     for idx, num in enumerate(tree):
        #         if idx == len(tree) - 1:
        #             print(cs[num:num+length])
        #         else:
        #             cs = cs[num]

        # result = extract(chunked_sentences, chunked_indexes)
        # snippet_results.append(result)

        # # adjust result with page context
        # page_text = get_page_context(url)
        # original_text = item[0]
        # if not page_text or original_text not in page_text:
        #     page_results.append(result)
        #     continue
        # # find original text and get neighbour texts.
        # page_sentences, updated_indexes = update_annotation(page_text, original_text, indexes)
        # chunked_sentences = chunk(page_sentences)
        # result = extract(chunked_sentences, updated_indexes)
        # page_results.append(result)

    # # save snippet, page results
    # save("snippet", snippet_results)
    # save("page", page_results)


if __name__ == "__main__":
    main()
