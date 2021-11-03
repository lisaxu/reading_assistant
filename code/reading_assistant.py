import re
# import os
import sys
import math
from gensimlsi import *
from html_generator import *
import numpy

# Allow use of raw_input on python3
try: raw_input = input
except NameError: pass

from os import listdir
from os.path import isfile, join

def list_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and not f.startswith('.'))]
    return onlyfiles

class Document(object):
    def __init__(self, document_id, processed_text, unprocessed_text):
        """
        Initializes a document
        """
        self.document_id = document_id
        self.unprocessed_text = unprocessed_text  # list of sentences
        self.processed_text = processed_text  # list of sentences
        self.document_length = sum([len(sentence) for sentence in self.processed_text])

    def __str__(self):
        return "{} {} {}".format(self.document_id, self.processed_text, self.document_length)


class DocumentProcessor(object):
    """
    A DocumentProcessor broken down an article by whole document, paragraphs, and sentences
    """

    def __init__(self, document_path, level):
        """
        Initializes a document
        """
        self.document_path = document_path
        self.document_id = None
        self.unprocessed_text = None
        self.processed_text = []
        self.level = level

        self.docs = []  # a list of Document objects
        self.load_document()
        self.preprocess_document()

    def load_document(self):
        """
        Loads a document given a document path to a text file
        """
        with open(self.document_path, 'r', encoding="utf8", errors='ignore') as f:
        # with open(self.document_path, 'r') as f:
            self.unprocessed_text = f.read().split('\n')
            self.document_id = self.document_path.split("/")[-1]
        #print('Document ' + self.document_id + " loaded.")

    def preprocess_document(self):
        """
        Preprocesses and stores a document
        Array indexed by paragraph, which are all indexed by sentences
        """
        if self.level == 'document':
            text_by_sentence = " ".join(self.unprocessed_text).split(
                '.')  # <-- adding \n for each sentence is a null-op since you joined then again and split by periods
            processed_sentences = []
            for sentence in text_by_sentence:
                if len(sentence) > 2:
                    processed_sentence = re.sub("[^a-zA-Z -]+", "", sentence.lower().strip())
                    processed_sentence = [w for w in processed_sentence.split(" ") if len(w) > 0]
                    # self.document_length += len(processed_sentence)
                    self.processed_text.append(processed_sentence)
           #print('Document ' + self.document_id + ' processed.')

            self.docs = [Document(self.document_id, self.processed_text, self.unprocessed_text)]

        elif self.level == 'paragraph':
            idx = 0
            for paragraph in self.unprocessed_text:
                document_id = self.document_id + '_pg' + str(idx)
                 
                text_by_sentence = [x for x in paragraph.split('.') if x is not []]
                processed_paragraph = []
                for sentence in text_by_sentence:
                    if len(sentence) > 2:
                        processed_sentence = re.sub("[^a-zA-Z -]+", "", sentence.lower().strip())
                        processed_sentence = [w for w in processed_sentence.split(" ") if len(w) > 0]
                        if len(processed_sentence) > 0:
                            processed_paragraph.append(processed_sentence)
                # print('Paragraph ' + document_id + ' processed.')
                if processed_paragraph:
                     self.docs.append(Document(document_id, processed_paragraph, paragraph))
                     idx += 1

    def get_docs(self):
        return self.docs


class InvertedIndex(object):
    """
    The inverted index for all seen documents
    """

    def __init__(self):
        """
        Initializes the inverted index
        """
        self.index = {}
        self.number_of_documents = 0
        self.average_document_length = 0

    def add_document(self, document):
        """
        Adds Document to inverted index
        """
        for sentence in document.processed_text:
            for word in sentence:
                if word in self.index.keys():
                    if document.document_id in self.index[word].keys():
                        self.index[word][document.document_id] += 1
                    else:
                        self.index[word][document.document_id] = 1
                else:
                    self.index[word] = {}
                    self.index[word][document.document_id] = 1
        new_total_length = (self.number_of_documents * self.average_document_length) + document.document_length
        self.number_of_documents += 1
        self.average_document_length = new_total_length / self.number_of_documents
        #print('Document ' + document.document_id + ' added to inverted index.')
        #print('Current read document count: ' + str(self.number_of_documents))

    def remove_document(self, document):
        """
        Removes Document from inverted index given document id
        """
        for word in self.index.keys():
            if document.document_id in self.index[word].keys():
                del self.index[word][document.document_id]

        new_total_length = (self.number_of_documents * self.average_document_length) - document.document_length
        self.number_of_documents -= 1
        self.average_document_length = new_total_length / self.number_of_documents
        print('Document ' + document.document_id + ' removed from inverted index.')
        print('Current read document count: ' + str(self.number_of_documents))


class ReadingAssistant(object):
    """
    An assistant that finds differences between what a user has and has not read
    """

    def __init__(self, read_documents_path, level):
        """
        Initialize the ReadingAssistant

        Depending on the 'level' parameter, a document could either be the whole wikipeida article,
        a paragraph of the wikipeida article, or a sentence in the wikipeida article 
        """
        self.read_documents_path = read_documents_path
        # list of read documents / paragraphs / sentences
        self.read_document_list = []
        # the inverted index is built based on analysis 'level'. i.e. document level, paragraph level, etc
        self.inv_idx = InvertedIndex()
        # the level at which the reading assistant does its analysis, choose from document|paragraph|sentence
        self.level = level

    def add_document(self, document_path):
        """
        Adds document to read collection, assumes path is to text file
        """
        # split article into documents based on level
        docs = DocumentProcessor(document_path, level=self.level).get_docs()

        for doc in docs:
            # doc.load_document()
            # doc.preprocess_document()
            self.inv_idx.add_document(doc)
            self.read_document_list.append(doc)

    def remove_document(self, document_path):
        """
        Removes document and associated paragraphs from read collection, assumes path contains id
        """
        doc_id = document_path.split("/")[-1]

        removed_index = []
        for i, doc in enumerate(self.read_document_list):
            if doc.document_id == doc_id or "{}_pg".format(doc_id) in doc.document_id:
                self.inv_idx.remove_document(doc)
                removed_index.append(i)
        if removed_index:
            for r in sorted(removed_index, reverse=True): # so that indexes of the rest do not change after deleting the first one
                del self.read_document_list[r]

    def load_documents(self):
        """
        Loads all read documents 
        Assumes document path is path to directory containing text files
        """
        for doc_path in os.listdir(self.read_documents_path):
            self.add_document(self.read_documents_path + doc_path)

    def score_document(self, document_path, k1=1.2, b=0.75):
        """
        Scores new document against collection of already-read documents
        Returns list of most-similar and most different documents?
        """
        # new_document = Document(document_path)
        # new_document.load_document()
        # new_document.preprocess_document()
        new_docs = DocumentProcessor(document_path, level=self.level).get_docs()

        rankings = {}
        for new_document in new_docs:
            ranking = []
            for doc in self.read_document_list:
                doc_score = 0
                for sentence in new_document.processed_text:
                    for word in sentence:
                        tf = self.TF_score_helper(word, doc.document_id)
                        idf = self.IDF_score_helper(word)
                        numerator = tf * (k1 + 1)
                        denominator = tf + (
                                    k1 * (1 - b + (b * (doc.document_length / self.inv_idx.average_document_length))))
                        doc_score += idf * (numerator / denominator)
                raw_txt = "\n".join(doc.unprocessed_text) if isinstance(doc.unprocessed_text, list) else doc.unprocessed_text
                ranking.append((doc.document_id, doc_score, raw_txt))
            rankings[new_document.document_id] = {}
            raw_txt = "\n".join(new_document.unprocessed_text) if isinstance(doc.unprocessed_text, list) else new_document.unprocessed_text
            rankings[new_document.document_id]['raw_txt'] = raw_txt
            rankings[new_document.document_id]['processed_txt'] = new_document.processed_text
            rankings[new_document.document_id]['ranking'] = sorted(ranking, key=lambda x: x[1], reverse=True)
        return rankings

    def TF_score_helper(self, keyword, doc_id):
        """
        Given a keyword and doc_id, calculates the term frequency of keyword in document
        """
        tf = 0
        if keyword in self.inv_idx.index.keys():
            if doc_id in self.inv_idx.index[keyword].keys():
                tf = self.inv_idx.index[keyword][doc_id]
        return tf

    def IDF_score_helper(self, keyword):
        """
        Given a keyword, calculates the inverse document frequency
        """
        N = self.inv_idx.number_of_documents
        docs_containing_keyword = 0
        if keyword in self.inv_idx.index.keys():
            docs_containing_keyword = len(self.inv_idx.index[keyword])
        numerator = N - docs_containing_keyword + 0.5
        denominator = docs_containing_keyword + 0.5
        return max(0, math.log((numerator / denominator) + 1))

def print_rankings(method, level, rankings, scope):
    """
    Prints a rankings dict to the console
    """
    for i in rankings.keys():
        print("---------------------\n")
        print(method, level, "ranking of", str(i))
        mean = numpy.mean([x[1] for x in rankings[i]['ranking']])
        sd = numpy.std([x[1] for x in rankings[i]['ranking']])
        for x in rankings[i]['ranking']:
            if x[1] > (mean + (scope * sd)):
                print('   {:<23}{:50}'.format(x[1], x[0]))

def write_html_rankings(rankings, scope, html):
    """
    Writes the rankings info to an HMTL file for easier perusal
    """
    for i in rankings.keys():
        mean = numpy.mean([x[1] for x in rankings[i]['ranking']])
        sd = numpy.std([x[1] for x in rankings[i]['ranking']])
        html.add_title(str(i))
        if isinstance(rankings[i]['raw_txt'], list):
            html.add_text("<br><br>".join(str(v) for v in rankings[i]['raw_txt']))
        else:
            html.add_text(rankings[i]['raw_txt'])
        for x in rankings[i]['ranking']:
            if x[1] > mean + (scope * sd):
                html.add_match(match_name=x[0], match_score=x[1], match_text=x[2])

def main(arg_read_path, arg_unread_path, arg_k1, arg_b):

    # initialize document-level bm25
    doc_reading_assistant = ReadingAssistant(arg_read_path, level="document")
    doc_reading_assistant.load_documents()

    # initialize paragraph-level bm25
    parag_reading_assistant = ReadingAssistant(arg_read_path, level="paragraph")
    parag_reading_assistant.load_documents()

    # scope (standard deviation) for ranking specificity
    scope = 2

    # user interaction code
    while True:

        print()
        print("-= READ FILES: =-")
        read_file_list = list_files(arg_read_path)
        for i, f in enumerate(read_file_list):
            print('{:>5} : {}'.format(i, f))

        print("=- UN-READ FILES: -=")
        unread_file_list = list_files(arg_unread_path)
        for i, f in enumerate(unread_file_list):
            print('{:>5} : {}'.format(i, f))

        n = raw_input("Please use one of the following commands:\n"
                       "  rank [unread_file_#]            --> Compares new document to previously-read documents\n"
                       "  read [unread_file_#]            --> add the document from the unread list to the read list\n"
                       "  forget [read_file_#]            --> remove a document from the read list\n"
                       "  view document [document name]   --> prints the document\n"
                       "  view paragraph [paragraph name] --> prints the paragraph\n"
                       "  set scope [integer]             --> only documents above this number of standard deviations above mean ranking score are returned\n" 
                       "  exit                            --> Exits the program\n"
                       "> ")
        print()
        print()
        # exit command
        if n == 'exit': exit()

        try:

            # new document command
            if n.startswith('rank'):
                target = os.path.join(arg_unread_path, unread_file_list[int(n[5:].strip())])

                # do the BM25 document-level analysis
                doc_bm25_rankings = doc_reading_assistant.score_document(target, k1=arg_k1, b=arg_b)

                # initialize lsi + do the analysis
                doc_lsi_rankings = gensim_lsi(arg_read_path, target, 'document')

                # do the BM25 paragraph-level analysis
                parag_bm25_rankings = parag_reading_assistant.score_document(target, k1=arg_k1, b=arg_b)

                # do paragraph level lsi analysis
                parag_lsi_rankings = gensim_lsi(arg_read_path, target, 'paragraph')

                # show the user
                print("========================================================================= Your Results =========================================================================")
                print_rankings("BM25", "paragraph", parag_bm25_rankings, scope)
                print_rankings("LSI", "paragraph", parag_lsi_rankings, scope)
                print_rankings("BM25", "document", doc_bm25_rankings, scope)
                print_rankings("LSI", "document", doc_lsi_rankings, scope)
                print("================================================================================================================================================================")

                # output BM25 html file for more viewing
                html_gen = HTML_Generator(outfile="output-bm25.html", name=target)
                html_gen.add_divide("BM25 Document, >= " + str(scope) + " standard deviations")
                write_html_rankings(doc_bm25_rankings, scope, html_gen)
                html_gen.add_divide("BM25 Paragraph, >= " + str(scope) + " standard deviations")
                write_html_rankings(parag_bm25_rankings, scope, html_gen)
                html_gen.close_file()

                # output LSI html file for more viewing
                html_gen = HTML_Generator(outfile="output-lsi.html", name=target)
                html_gen.add_divide("LSI Document, >= " + str(scope) + " standard deviations")
                write_html_rankings(doc_lsi_rankings, scope, html_gen)
                html_gen.add_divide("LSI Paragraph, >= " + str(scope) + " standard deviations")
                write_html_rankings(parag_lsi_rankings, scope, html_gen)
                html_gen.close_file()

                print("\nDropping your pen and rubbing your temples, you look over output-bm25.html and output-lsi.html, and smile knowing the analysis is done.  ")


            # add document to read list
            elif n.startswith('read'):
                target_file = unread_file_list[int(n[5:].strip())]
                src_loc = os.path.join(arg_unread_path, target_file)
                dst_loc = os.path.join(arg_read_path, target_file)
                # remove from the inverted index (more efficient than recreating the entire index)
                print('Over a delightful espresso you peruse {}.  What a good read!'.format(src_loc, dst_loc))
                os.rename(src_loc, dst_loc)
                # add to the inverted index (once it's in the read path)
                doc_reading_assistant.add_document(dst_loc)
                parag_reading_assistant.add_document(dst_loc)
            # add document to read list
            elif n.startswith('forget'):
                target_file = read_file_list[int(n[7:].strip())]
                src_loc = os.path.join(arg_read_path, target_file)
                dst_loc = os.path.join(arg_unread_path, target_file )
                # remove from the inverted index while still in the read path
                doc_reading_assistant.remove_document(src_loc)
                parag_reading_assistant.remove_document(src_loc)
                print('You wander about, seeing glimpses of {} everywhere, but remembering nothing...'.format(src_loc))
                os.rename(src_loc, dst_loc)
            elif n.startswith('set scope'):
                # update standard deviation measure
                new_scope = int(n[10:].strip())
                scope = new_scope
                print('Perhaps another perspective will help...')
            elif n.startswith('view document'):
                document_id = n[14:]
                print('Good idea, let\'s take a look at ' + document_id)
                text = [x.processed_text for x in doc_reading_assistant.read_document_list if x.document_id == document_id]
                raw_text = [x.unprocessed_text for x in doc_reading_assistant.read_document_list if x.document_id == document_id]
                if text:
                    print(raw_text)
                    print(text)
                else:
                    print('After sifting through the cluttered pile of of documents it is clear:', document_id,
                          "can\'t be found.")
                    # print('Sorry, the document you requested was not found.')
            elif n.startswith('view paragraph'):
                paragraph_id = n[15:]
                print('Well now I am intrigued, what is so great about paragraph', paragraph_id, "?")
                text = [x.processed_text for x in parag_reading_assistant.read_document_list if x.document_id == paragraph_id]
                raw_text = [x.unprocessed_text for x in parag_reading_assistant.read_document_list if x.document_id == paragraph_id]
                if text:
                    print(raw_text)
                    print(text)
                else:
                    print('Paragraph after paragraph are searched, yet ', paragraph_id, "just isn\'t here.")
                    # print('Sorry, the paragraph you requested was not found.')
            else:
                print("...you stare at the screen blankly, wondering why it it says \'invalid command.\'")

        except Exception as e:
            print("...sorry, you did something strange:\n".format(sys.exc_info()[0]))
            print("Maybe this will give you a hint:\n")
            print(e)

if __name__ == "__main__":
    """
    Run from the command line, specifying level of analysis and path to read and unread documents.
    """

    if len(sys.argv) < 3:
        print("\nUsage: python reading_assistant.py read_docs_path unread_docs_path [k1] [b] \n"
              "    ... read_docs_path   : path containing text files that have been read by the user\n"
              "    ... unread_docs_path : path containing text files that have not been read by the user\n"              
              "    ... [k1]             : is the k1 value for BM25. Default: 1.2\n"
              "    ... [b] (optional)   : is the b value for BM25. Default: 0.75\n\n"
              )

    else:
        # tidy up some of the command line args

        # just add trailing "/" if necessary
        arg_read_path = os.path.join(sys.argv[1], '')
        arg_unread_path = os.path.join(sys.argv[2], '')

        # and set default values for k1 and b
        arg_k1 = 1.2
        arg_b = 0.75
        if len(sys.argv) == 5:
            arg_k1 = sys.argv[3]
            arg_b = sys.argv[4]

        outstr = "\nReading Assistant\n" \
                 "    read: {}\n" \
                 "  unread: {}\n".format(arg_read_path, arg_unread_path)

        outstr += "      k1: {}\n" \
                  "       b: {}\n".format(arg_k1, arg_b)

        outstr += "\n"

        #print (outstr)

        # call main with command line args
        main(arg_read_path=arg_read_path, arg_unread_path=arg_unread_path, arg_k1=arg_k1, arg_b=arg_b)
