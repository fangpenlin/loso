# -*- coding: utf8 -*-
import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import yaml

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
    
    def splitSentence(self, text):
        """Split text into sentence
        
        """
        return lexicon.splitSentence(text)
    
    def extractEnglishTerms(self, text):
        """Extract English terms from Chinese text
        
        """
        return list(lexicon.iterEnglishTerms(text))
    
def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('segment.main')
    
    config = yaml.load(open('config.yaml', 'rt'))
    
    service = SegumentService()
    
    xmlrpc_config = config['xmlrpc']
    interface = xmlrpc_config.get('interface', '0.0.0.0')
    port = xmlrpc_config.get('port', 5566)
    logger.info('Start segmentation service at %s:%d', interface, port)
    
    server = SimpleXMLRPCServer((interface, port), allow_none=True)
    server.register_introspection_functions()
    server.register_instance(service)
    server.serve_forever()

if __name__ == '__main__':
    main()