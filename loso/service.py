# -*- coding: utf8 -*-
import logging

from loso import lexicon

class SegumentService(object):
    
    def __init__(self, ngram=4, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.ngram = ngram
        self.db = lexicon.LexiconDatabase()
        self.builder = lexicon.LexiconBuilder(self.db, self.ngram)
    
    def getStats(self):
        """Get statistics information
        
        """
        return self.db.getStats()
    
    def feed(self, text):
        """Feed text data to lexicon database
        
        """
        self.logger.info('Feed %d bytes data', len(text))
        return self.builder.feed(text)
        
    def splitTerms(self, text):
        """Split text into terms
        
        """
        terms = []
        for sentence in lexicon.splitSentence(text):
            if sentence:
                for mixed in lexicon.iterMixTerms(sentence):
                    # English term
                    if mixed.startswith('E'):
                        terms.append(mixed)
                    # Chinese sentence
                    else:
                        terms.extend(self.db.splitTerms(mixed, self.ngram))
        return terms
    
    def splitNgramTerms(self, text):
        """Split text into 1 to n gram terms
        
        """
        terms = []
        for sentence in lexicon.splitSentence(text):
            if sentence:
                for mixed in lexicon.iterMixTerms(sentence):
                    # English term
                    if mixed.startswith('E'):
                        terms.append(mixed)
                    # Chinese sentence
                    else:
                        for n in xrange(1, self.ngram+1):
                            terms.extend(lexicon.iterTerms(n, mixed, False))
        return terms
    
    def splitSentence(self, text):
        """Split text into sentence
        
        """
        return lexicon.splitSentence(text)
    
    def splitMixTerms(self, text):
        """Split text into Chinese sentence and English terms
        
        """
        return list(lexicon.iterMixTerms(text))