import sys
import logging
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError

import yaml

import service

class InteractCommand(Command):
    description = 'provide interact interface for testing splitting terms'
    user_options = [
        ('category=', 'c', 'category name'),
    ]

    def initialize_options(self):
        self.category = None
    
    def finalize_options(self):
        pass

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        seg_service = service.SegumentService()
        while True:
            text = raw_input('Text:').decode(sys.stdin.encoding)
            terms = seg_service.splitTerms(text, self.category)
            print ' '.join(terms)

class FeedCommand(Command):
    description = 'feed text data file'
    user_options = [
        ('file=', 'f', 'text file to feed'),
        ('encoding=', 'e', 'encoding of text file'),
        ('category=', 'c', 'category name'),
    ]

    def initialize_options(self):
        self.encoding = 'utf8'
        self.file = None
        self.category = None
    
    def finalize_options(self):
        import codecs
        if not self.file:
            raise DistutilsOptionError('Must set text file path to feed')
        if not self.category:
            raise DistutilsOptionError('Must set category to feed')
        self.text_file = codecs.open(self.file, 'rt', encoding=self.encoding)
        self.text = self.text_file.read()

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        seg_service = service.SegumentService()
        seg_service.feed(self.category, self.text)
        
class ResetCommand(Command):
    description = 'reset lexicon database'
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        seg_service = service.SegumentService()
        seg_service.db.clean()
        print 'Done.'
        
class ServeCommand(Command):
    description = 'run segmentation server'
    user_options = [
        ('config=', 'c', 'path to configuration'),
    ]

    def initialize_options(self):
        self.config_file = 'config.yaml'
    
    def finalize_options(self):
        self.config = yaml.load(open(self.config_file, 'rt'))

    def run(self):
        from SimpleXMLRPCServer import SimpleXMLRPCServer

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('segment.main')
        
        seg_service = service.SegumentService()
        
        xmlrpc_config = self.config['xmlrpc']
        interface = xmlrpc_config.get('interface', '0.0.0.0')
        port = xmlrpc_config.get('port', 5566)
        logger.info('Start segmentation service at %s:%d', interface, port)
        
        server = SimpleXMLRPCServer((interface, port), allow_none=True)
        server.register_introspection_functions()
        server.register_instance(seg_service)
        server.serve_forever()
        
class DumpCommand(Command):
    description = 'dump lexicon database as a text file'
    user_options = [
        ('file=', 'f', '/path/to/text'),
        ('encoding=', 'e', 'encoding of text file'),
    ]

    def initialize_options(self):
        self.encoding = 'utf8'
        self.file = None
    
    def finalize_options(self):
        import codecs
        if not self.file:
            raise DistutilsOptionError('Must set text file path to feed')
        self.text_file = codecs.open(self.file, 'wt', encoding=self.encoding)

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        seg_service = service.SegumentService()
        seg_service.db.dump(self.text_file)
        self.text_file.close()
        print 'Done.'