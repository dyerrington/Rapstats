#!/Users/davidyerrington/virtualenvs/data/bin/python

import logging, gensim, bz2, os, string, glob, os
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
from os import path

class LDAExplorer:

    stopwords_file  =   'stopwords.txt'
    stopwords       =   False
    corpus_files    =   False
    corpus_data     =   '/tmp/corpus_data.mm'
    dictionary_data =   '/tmp/dictionary.data'
    model_file      =   '/tmp/model.lda'
    logfile         =   'lda_stats.log'
    logging         =   {
        'filename': 'lda_stats.log',
        'format':   '%(asctime)s : %(levelname)s : %(message)s',
        'level':    logging.INFO
    }

    number_of_topics =  20

    def __init__(self):

        logging.basicConfig(filename=self.logging['filename'], format=self.logging['format'], level=self.logging['level'])
        self.set_stopwords()

    def set_stopwords(self):

        try:
            with open(self.stopwords_file) as fp:
                self.stopwords = set(fp.read().encode('utf-8').strip().split())

        except IOError as e:
            print "set_stopwords() error: {})".format(e)

    def clean_corpus(self, corpus):

        # remove punctuation table
        # table = string.maketrans("","")
        words = []

        if word.strip() not in cachedStopWords and word.strip() not in stopwords:
            words.append(word)

        return words


    def load_text(self, corpus_file):
        """Loads text file from reference, and returns list of words

        Args:
            text_file: File reference to text file.

        Returns:
            A list of words with punctuation and stopwords removed. 

            For example:

            ['spots', 'roof', 'can', 'dog', 'food']

        Raises:
            IOError: An error occurred accessing the text_file resource.
        """

        try:
            with open(corpus_file) as fp:

                words = []

                # remove punctuation table
                table = string.maketrans("","")

                for line in fp:

                    for word in line.lower().translate(table, string.punctuation).split():

                        if word not in self.stopwords:
                            words.append(word)

                # remove words that occur only once
                tokens_once =   set(word for word in set(words) if words.count(word) == 1)
                words       =   [word for word in words if word not in tokens_once]

            return words

        except IOError as e:
            raise IOError("({})".format(e)) 

    def load_corpus_directory(self, directory):

        # do we have a serialized corpus already?  Try to load that first
        try:
            self.corpus     =   corpora.MmCorpus(self.corpus_data)
            self.dictionary =   corpora.Dictionary.load(self.dictionary_data)
            print "{corpus_data} loaded successfully".format(corpus_data = self.corpus_data)

        except:

            albums  =   [f for f in os.listdir(directory) if os.path.isdir(directory + f)]
            files   =   [glob.glob(directory + file + '/*.txt') for file in albums]

            # flatten that shizz
            self.corpus_files   =   [item for files in files for item in files]
            self.documents      =   [self.load_text(file) for file in self.corpus_files]

            print "%d documents loaded" % len(self.documents)

            self.dictionary     =   corpora.Dictionary(self.documents)
            self.dictionary.save(self.dictionary_data)

            self.corpus         =   [self.dictionary.doc2bow(doc) for doc in self.documents]

            # corpus_vectors = (dictionary.doc2bow(doc) for doc in dictionary)
            self.corpus_vectors =   self.dictionary.doc2bow(self.documents[0])

            # save for later..
            gensim.corpora.MmCorpus.serialize(self.corpus_data, self.corpus)

    def generate_topics_lda(self):

        lda     =   gensim.models.ldamodel
        
        try:
            model = lda.LdaModel.load(self.model_file)
        except:
            print "Generating new model..."
            model = lda.LdaModel(corpus=self.corpus, id2word=self.dictionary, num_topics=self.number_of_topics, update_every=1, chunksize=1000, passes=4)
            model.save(self.model_file)

        i   =   0

        for idx, topic in enumerate(model.show_topics(num_topics=self.number_of_topics, num_words=25, formatted=False)): # topn=20
            
            print "Topic #%d:\n------------------------" % idx
            
            for p, id in topic:
                print p, id.encode('utf-8').strip()

            print ""

        


lda = LDAExplorer()
lda.load_corpus_directory('/var/www/htdocs/rapalytics/data/albums/')
lda.generate_topics_lda()

# print lda.stopwords

# print lda.corpus_vectors
print lda