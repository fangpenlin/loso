# -*- coding: utf8 -*-
import logging

from loso import lexicon

class SegumentService(object):
    
    def __init__(self, ngram=4, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger('segment.service')
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
                terms.extend(self.db.splitTerms(sentence, self.ngram))
        return terms
    
    def splitNgramTerms(self, text):
        """Split text into 1 to n gram terms
        
        """
        terms = []
        for sentence in lexicon.splitSentence(text):
            if sentence:
                for n in xrange(1, self.ngram+1):
                    terms.extend(lexicon.iterTerms(n, sentence, False))
        return terms
    
    def splitSentence(self, text):
        """Split text into sentence
        
        """
        return lexicon.splitSentence(text)
    
    def extractEnglishTerms(self, text):
        """Extract English terms from Chinese text
        
        """
        return list(lexicon.iterEnglishTerms(text))