import os
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import remove_stopwords
from smart_open import smart_open
from gensim import corpora
from collections import defaultdict
from gensim import models
from gensim import similarities

import logging
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# contains the names of the files, and corresponding text, for reference later.
read_docs = []
read_paragraphs = []
read_docs_txt = {}
read_paragraphs_txt = {}
unread_docs = []
unread_paragraphs = []
unread_docs_txt = {}
unread_paragraphs_txt = {}

class ListOfWords(object):
     def __init__(self, list_of_words):
        self.list = list_of_words

class ReadTxtFiles(object):
    def __init__(self, dirname, level='document'):
        self.dirname = dirname
        self.level = level

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            path = os.path.join(self.dirname, fname)
            self.doc = smart_open(path, encoding='latin')
            # read_docs.append(fname)

            if self.level == 'document':
                self.list = []
                doc_txt = ""
                for line in self.doc:
                    doc_txt += line + "\n"
                    if (len(line.strip()) == 0):
                        continue  # skip blank lines
                    self.list = self.list + simple_preprocess(remove_stopwords(line), deacc=True)
                read_docs.append(fname)
                read_docs_txt[fname] = doc_txt
                yield ListOfWords(self.list)

            elif self.level == 'paragraph':
                paragraph_idx = 0
                for line in self.doc:
                    if (len(line.strip()) == 0):
                        continue  # skip blank lines
                    para_name = "{}_pg{}".format(fname, str(paragraph_idx))
                    # read_paragraphs.append("{}_pg{}".format(fname, str(paragreraph_idx)))
                    read_paragraphs.append(para_name)
                    read_paragraphs_txt[para_name] = line
                    paragraph_idx += 1
                    yield ListOfWords(simple_preprocess(remove_stopwords(line), deacc=True))

class ListOfUnreadWords(object):
    def __init__(self, list_of_wrods, name):
        self.word_list = list_of_wrods
        self.name = name

class ReadUnreadTxtFiles(object):
    def __init__(self, fname, level='document'):
        self.fname = fname
        self.level = level

    def __iter__(self):
        # iterator isn't really needed, left over from when this pointed to a directory rather than a file
        # for fname in os.listdir(self.dirname):
        self.doc = smart_open(self.fname, encoding='latin')

        if self.level == 'document':
            self.word_list = []  # list of all words in the doc
            doc_txt = ""
            for line in self.doc:
                doc_txt += line
                if (len(line.strip()) == 0):
                    continue  # skip blank lines
                self.word_list = self.word_list + simple_preprocess(remove_stopwords(line), deacc=True)
            name = self.fname.split("/")[-1]
            unread_docs.append(name)
            unread_docs_txt[name] = doc_txt
            yield ListOfUnreadWords(self.word_list, name)
        elif self.level == 'paragraph':
            self.word_list = []  # list of all words in the doc
            paragraph_idx  = 0
            for line in self.doc:
                if (len(line.strip()) == 0):
                    continue  # skip blank lines
                name = "{}_pg{}".format(self.fname.split("/")[-1], str(paragraph_idx))
                unread_paragraphs.append(name)
                unread_paragraphs_txt[name] = line
                paragraph_idx += 1
                yield ListOfUnreadWords(simple_preprocess(remove_stopwords(line), deacc=True), name)


def gensim_lsi(arg_read_path, arg_unread_file, level='document'):

    list_of_list_of_words = ReadTxtFiles(arg_read_path, level)
    list_of_list_of_unread_docs = ReadUnreadTxtFiles(arg_unread_file, level)

    texts = []
    for doc in list_of_list_of_words:  # each doc is a ListOfWords: list of all words for that doc/paragraph
        texts.append(doc.list)

    # remove words that appear only once
    frequency = defaultdict(int) # defaultdict never raises keyError
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [
        [token for token in text if frequency[token] > 1]
        for text in texts
    ]

    dictionary = corpora.Dictionary(texts) # create gensim dictionary structure from words

    corpus = [dictionary.doc2bow(text) for text in texts] # turn all words into the general corpus

    tfidf = models.TfidfModel(corpus)  # initialize a model

    corpus_tfidf = tfidf[corpus]  # use the model to transform vectors

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=200)  # initialize an LSI transformation

    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it

    ### Now we have the model.  We need to query it with the unread documents.

    # this iterates, but for our purposes, this is always just one document...
    rankings = {}
    for doc in list_of_list_of_unread_docs:
        print("unread document = ", doc.name.upper())

        # create the vectors for the bag of words from all the words in the document
        vec_bow = dictionary.doc2bow(doc.word_list)

        # convert the query to LSI space
        vec_lsi = lsi[vec_bow]

        # perform a similarity query against the corpus
        sims = index[vec_lsi]

        # sort the most similar documents to the top
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        # create the ranking array
        ranking = []
        for i, doc_score in sims:
            if level == 'document':
                ranking.append((read_docs[i], doc_score, read_docs_txt[read_docs[i]]))
            elif level == 'paragraph':
                ranking.append((read_paragraphs[i], doc_score, read_paragraphs_txt[read_paragraphs[i]]))

        rankings[doc.name] = ranking
        if level == 'document':
            rankings[doc.name] = {'raw_txt': unread_docs_txt[doc.name], 'ranking': ranking}
        elif level == 'paragraph':
            rankings[doc.name] = {'raw_txt': unread_paragraphs_txt[doc.name], 'ranking': ranking}
        # rankings[doc.name] = {'raw_txt': doc.name, 'ranking': ranking}

    return rankings
