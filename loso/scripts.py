import sys
import logging
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError

import server

class InteractCommand(Command):
    description = 'provide interact interface for testing splitting terms'
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        service = server.SegumentService()
        while True:
            text = raw_input('Text:').decode(sys.stdin.encoding)
            terms = service.splitTerms(text)
            print ' '.join(terms)

class FeedCommand(Command):
    description = 'feed text data file'
    user_options = [
        ('file=', 'f', 'text file to feed'),
        ('encoding=', 'e', 'encoding of text file'),
    ]

    def initialize_options(self):
        self.encoding = 'utf8'
        self.file = None
    
    def finalize_options(self):
        import codecs
        if not self.file:
            raise DistutilsOptionError('Must set text file path to feed')
        self.text_file = codecs.open(self.file, 'rt', encoding=self.encoding)
        self.text = self.text_file.read()

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        service = server.SegumentService()
        service.feed(self.text)
        

class ResetCommand(Command):
    description = 'reset lexicon database'
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        service = server.SegumentService()
        service.db.reset()
        print 'Done.'