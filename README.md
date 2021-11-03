# Reading Assistant

**CS410, Fall 2020**

> Christopher Rock (cmrock2)  
> Zichun Xu (zichunx2)  
> Kevin Ros (kjros2)

Video presentation: https://youtu.be/RO351eoZ1ZU
<!--
### Documentation Guidelines

The documentation should consist of the following elements: 1) An overview of
the function of the code (i.e., what it does and what it can be used for). 2)
Documentation of how the software is implemented with sufficient detail so that
others can have a basic understanding of your code for future extension or any
further improvement. 3) Documentation of the usage of the software including
either documentation of usages of APIs or detailed instructions on how to
install and run a software, whichever is applicable. 4) Brief description of
contribution of each team member in case of a multi-person team.
-->

Overview
========

Problem
-------
"Information overload" is something people in today’s society are accustomed.
Most people develop methods of coping with the huge amount of information
available. We filter things through trusted sources, prioritize information that
is actionable, and change our mental model of the situation as necessary.

Earlier this year, the 2019 novel Coronavirus epidemic turned the world on its
collective head and created a flurry of information. Large volumes of text data
are expected to be consumed and acted upon in a short period of time.

For humans, initially the challenge is simply to read and understand the
documents. However the difficulty quickly becomes identifying what is new
knowledge, and remembering the source of previously seen similar knowledge. New
documents may have significant overlap with prior knowledge. Differences between
documents must be reviewed, and often the progression of changes is important.

Information retrieval, text mining, and recommender systems have developed
algorithmic strategies to identify and extract useful information from
text-based knowledge. The focus of these tools has generally been to pull
relevant documents via (search), or push potentially interesting documents (
recommender). These techniques can be modified to assist a reader in identifying
new useful information.

What is our tool?
-----------
In line with our project proposal, our overall goal was to create a reading
assistant tool that allows a user to maintain a collection of *read* documents (
reflecting the current knowledge of the user)
and then provides insight about a new *unread* document when compared to the all
read documents. The output includes:

- A ranked list of documents that are most similar to the unread document based on BM25 scores and LSI similarity scores, respectively. 
- A ranked list of paragraphs that are most similar to each paragraph of the unread document based on BM25 scores and LSI similarity scores, respectively.

Our initial idea from the project proposal was to focus on the
differences between documents, however the reality is that there were so many
ways documents could be different that this was not particularly helpful. In
this final version we instead focus on the areas of similarity betwen the unread
document from the corpus of read. This allows the user to then quickly hone in
on areas where the new document reinforce or subtly change what they had
previously discovered from the read docuements.

What can it be used for?
------------------------
Although this is created as a command line tool, as described above the initial
inspiration for this idea was the surplus of information that was being pushed
out (in our case via email) during the first months of the COVID-19 pandemic.
One way to use this tool would be to integrate it with a mail server, so that
you could forward an email or attachment and indicate that you had or had not
read the document - then the server could spit back a new email with some
analysis of the document including a list (and linke) to the other read similar
documents, as well as highlight passages (paragraphs in our case)
of particular interest.

Implementation
==============
On start-up, text documents (directory path provided by user) are loaded by the
assistant. During loading, the documents are processed (remove non-ascii characters,
blank lines, etc) and added to an inverted Index. These documents are considered
to be the previously-read documents by the user. Once the loading is complete, 
the assistant waits for a path to a text file (unseen document). Given this path,
the assistant ranks the previously-read documents using the unseen document and
returns the most similar read document and paragraph names to the user. We also 
provided methods for a user to view, add and remove previously-read documents.

Currently, the assistant calculates similarity scores using two approaches: 
Okapi BM25 and Latent Semantic Indexing (LSI) similarity.

To implement the Okapi BM25 ranking function, first an inverted index is built 
based on the previously-read documents. From there, it calculates the term frequency, 
inverse document frequency, and document length normalization. Finally, the 
similarity score for each document is calculated and scores are sorted in 
descending order. In addition to document-level BM-25, we also implemented 
paragraph-level BM25, which follows a similar approach but considers each 
paragraph of the document as an individual “document”. This allows more 
detailed evaluation of unseen documents.

To implement LSI similarity ranking function, we utilized the external gensim library. This is 
currently in a separate script (gensimlsi.py) and is integrated to the reading 
assistant. During document pre-processing, it removes stop words, blank lines, 
and words that only appeared once in the document to achieve better topic discovery. 
It first transforms the previously-read documents to Tf-Idf vectors. It then builds an 
LSI model with 200 (default) topics. Note that if the number of read documents 
is less than 200 then the number of read documents will be used. This LSI model 
will discover topics based on all the previously-read documents, and map the document vectors
to LSI space, i.e. describe how strongly each document is related to each topic.
Upon receiving the unseen document specified by the user, it will transform the
document into LSI space and compute the cosine similarity. The scores will then
be sorted in descending order. Similarly, we also implemented paragraph level 
analysis for LSI similarity.

The code is written in a modular fashion, so that we can easily
extend the assistant to use different similarity/difference measures and
methods

Usage
=====
View our usage video here:

<a href="https://www.youtube.com/watch?v=RO351eoZ1ZU&feature=youtu.be"><img src="https://github.com/chrispebble/CourseProject/blob/main/presentation.png" alt="Link to Youtube Presentation" width="75%"></a>

We recommend using python 3.6 or 3.7, with gensim (and its dependencies), as
well as the smart_open package.

To start the reading assistant, you must first have two directories of text
files. One directory should be "read"
documents, and the other is "unread" documents. Start the program by running the
script like so:

```
python reading_assistant.py read_docs_path unread_docs_path [k1] [b]
```

`read_docs_path`   : path containing text files that have been read by the
user  
`unread_docs_path` : path containing text files that have not been read by the
user  
`[k1]`             : value for BM25. Default: 1.2 (optional)  
`[b]` : the b value for BM25. Default: 0.75

The script will load the read documents into an inverted index, and then go into
the Read-Eval-Print Loop (REPL).  
Once the REPL is running, you will be presented with a list of *Read* documents
and *Un-Read* documents. For example, you may see the following:

```
-= READ FILES: =-
    0 : covid-bhc-contact-sop-1.txt
    1 : covid-isos-brief.txt
    2 : covid-update-4.txt
    3 : covid-dod-mgmt-guide.txt
    4 : covid-update-1.txt
    5 : covid-update-3.txt
    6 : covid-bhc-pt.txt
    7 : covid-update-2.txt
    8 : covid-yoko-sop.txt
    9 : covid-fragord.txt
   10 : covid-bhc-extended-use.txt
=- UN-READ FILES: -=
    0 : covid-bhc-contact-sop-2.txt
    1 : covid-annex-1.txt
Please use one of the following commands:
  rank [unread_file_#]            --> Compares new document to previously-read documents
  read [unread_file_#]            --> add the document from the unread list to the read list
  forget [read_file_#]            --> remove a document from the read list
  view document [document name]   --> prints the document
  view paragraph [paragraph name] --> prints the paragraph
  set scope [integer]             --> only documents above this number of standard deviations above mean ranking score are returned
  exit                            --> Exits the program


```

To see the rank of the unread document **covid-annex-1.txt** you would
enter `rank 1` at the prompt. An "output.html" will also be generated 
in the directory where the command is issued. It contains the same info 
as the console output and provides a better visual representation.

To move a document **covid-bhc-contact-sop-2.txt** from the *unread* into the *
read* grouping, type `read 0`.

Or, to move document **covid-fragord.txt** from *read* to *unread*,
type `forget 9`.

To view the text of document **covid-yoko-sop.txt**,
type 'view document covid-yoko-sop.txt'. Note that this only works with
documents listed under READ FILES.

Similarly, to view the first paragraph of document **covid-yoko-sop.txt**,
type 'view paragraph covid-yoko-sop.txt_parag0'. Note that this only works with
documents listed under READ FILES. 

The 'set scope [integer]' command determines scope of the ranking results. As each document
and paragraph in READ FILES is given a ranking score, the [integer] determines the cut-off
of these scores. More specifically, the [integer] is the number of standard deviations above the mean
ranking score. That is, a scope of 2 means that only documents and paragraphs that are two or more
standard deviations above the mean score are returned. A scope of 0 means that all documents and paragraphs above the mean ranking score are returned. Generally, a higher scope means fewer documents and paragraphs returned, but these documents and paragraphs are much more relevant. 

Results
==============
To heuristically gauge the effectiveness of the reading assistant, each team member collected approximately 8-10 documents. These documents were loaded as the previously-read documents, and additional documents were provided as the unseen documents. From the preliminary examination, the results seem promising and inline with our qualitative evaluation of the documents.

We found these results to be interesting and potentially be useful in a real world application.  Using the results from our tool, one could easily find related previously read documents.  Additionally if a paragraph was interesting one could find the similar passages.  Alternatively, a document highlighter with links to related documents could be created.  After creating the tool the existence of similar functionality became evident in other software such as Evernote, which shows similar notes to the one the user is currently viewing.  The Evernote use case is not quite the same as our stated use case, but likely relies on some similar information retrievel techniques to generate the list of similar documents.

Interestingly, the original impetus behind creating the tool was to find similar **and** different documents, however in the process of creating this tool we came to understand how the BM25 and LSI algorithms are powered towards similarities, not differences.  The root of this is that there are only a few ways a document can be similar, but many ways documents can be different.  This was an interesting realization, and further thought towards how to find *useful* differences could be discovered was an interesting thought experiment, although we did not make significant headway into how to solve that problem.  

If we were to continue to develop this project further, there are a few areas where we could easily improve the tool.  One would be to integrate the data structures between the BM25 and gensim LSI algorithm so that the reading and memory usage was more efficient.  Additionally, the LSI algorithm is capable of adding documents without needing to completely recreate it's underying data structures.  Depending on how the tool would be used (if for instance documents would be frequently added) this would improve the efficiency of the tool.  Manipulation of the parameters of the algorithms would be another area where improvements could be made.  Manipulation of either with the **k** value of BM25, or the topic number of LSI coud lead to subtle improvements in results.  Creating of a data set with user rankings for comparison to the results would also be very helpful in objectively analyzing the results of these tweaks.  Creation of such a data set - with human-choosen similar paragarphs - would be time consuming to create but could result in use of comparison functions such as the F1 score which would facilitate further development.  

Overall we felt this tool was a strong starting point to further work in the realm of a reading assistant.

Team Contributions
==================
All team members were active participants throughout the entire project
lifecycle process. Our team worked well together and all members contributed
meaningfully to our end result. All met via Zoom on the following days (30-60
minute meetings):

- Sep 10th: initial team meeting and plan for future meeting timeline
- Oct 3rd: draft concept of reading assistant formed
- Oct 9th: discussion of unit 1 concepts and relation to project
- Oct 21st: formalized topic and planned submission of topic to CMT
- Oct 24th: discussed status, potential roadblocks, and plan forward
- Nov 14th: reviewed TA comments and initial review of BM25 document-level
  rankings
- Nov 17th: discussed additional methods to rank articles
- Nov 29th: reviewed progress report, paragraph ranking, and formulated final
  plan for code breakdown
- Dec 6th: reviewed integration of gensim, paragraph ranking, CLI, and initial
  REPL
- Dec 11th: reviewed final product and discussed last touches necessary to
  complete project
- Dec 13th: recorded tutorial

Specific Contributions
------------------------------
All members contributed to write-ups, review of code, reviewing submission
requirements, and ensuring deadlines were met.

*Kevin Ros*:

- Created initial BM25 document-level code, with necessary ability to
  dynamically add and remove documents.
- Drafted initial documents (proposal, progress report)
- Added initial REPL interface
- Added standard deviation analysis of results to simplify interpretation of
  ranking data

*Zichun Xu*

- Created paragraph level analysis of BM25 analysis method
- Modified gensim LSI analysis for paragraph level analysis

*Christopher Rock*

- Added gensim LSI ranking methods
- Added CLI and finalized REPL
- Added HTML generator for better visual representation of results

References
==========
<sup>1</sup>https://github.com/meta-toolkit/metapy

<sup>2</sup>https://tac.nist.gov/2008/summarization/update.summ.08.guidelines.html

<sup>3</sup>Andrei V, Arandjelović O. Complex temporal topic evolution
modelling using the Kullback-Leibler divergence and the Bhattacharyya distance.
EURASIP J Bioinform Syst Biol. 2016 Sep 29;2016(1):16. doi:
10.1186/s13637-016-0050-0. PMID: 27746813; PMCID: PMC5042987.

<sup>4</sup>Liu, Heng-Hui & Huang, Yi-Ting & Chiang, Jung-Hsien. (2010). A
study on paragraph ranking and recommendation by topic information retrieval
from biomedical literature. ICS 2010 - International Computer Symposium.
10.1109/COMPSYM.2010.5685393.

<sup>5</sup>https://radimrehurek.com/gensim/models/lsimodel.html
