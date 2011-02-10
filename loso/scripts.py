import sys
import logging
from distutils.cmd import Command
from distutils.errors import DistutilsOptionError

import yaml

import service

def _loadConfig(default_path='default.yaml'):
    import os
    logger = logging.getLogger(__name__)
    path = default_path
    k = 'LOSO_CONFIG_FILE'
    if k in os.environ:
        path = os.environ[k]
    cfg = yaml.load(open(path, 'rt'))
    logger.info('Load configuration %s', path)
    return cfg

class InteractCommand(Command):
    description = 'provide interact interface for testing splitting terms'
    user_options = [
        ('category=', 'c', 'category name, split by comma'),
    ]

    def initialize_options(self):
        self.category = None
    
    def finalize_options(self):
        if self.category:
            self.category = self.category.split(',')

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        cfg = _loadConfig()
        seg_service = service.SegumentService(cfg)
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
        cfg = _loadConfig()
        seg_service = service.SegumentService(cfg)
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
        cfg = _loadConfig()
        seg_service = service.SegumentService(cfg)
        seg_service.db.clean()
        print 'Done.'
        
class ServeCommand(Command):
    description = 'run segmentation server'
    user_options = []

    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass

    def run(self):
        from SimpleXMLRPCServer import SimpleXMLRPCServer

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('segment.main')
        
        cfg = _loadConfig()

        seg_service = service.SegumentService(cfg)
        
        xcfg= cfg['xmlrpc']
        interface = xcfg.get('interface', '0.0.0.0')
        port = xcfg.get('port', 5566)
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
        ('category=', 'c', 'category name'),
    ]

    def initialize_options(self):
        self.encoding = 'utf8'
        self.file = None
        self.category = None
    
    def finalize_options(self):
        import codecs
        if not self.file:
            raise DistutilsOptionError('Must set text file path to dump')
        if not self.category:
            raise DistutilsOptionError('Must set category to dump')
        self.text_file = codecs.open(self.file, 'wt', encoding=self.encoding)

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        cfg = _loadConfig()
        seg_service = service.SegumentService(cfg)
        c = seg_service.db.getCategory(self.category)
        if not c:
            print 'Category %s not exist' % self.category
            return
        c.dump(self.text_file)
        self.text_file.close()
        print 'Done.'
        
class InfoCommand(Command):
    description = 'Display info of lexicon database'
    user_options = [
        ('category=', 'c', 'category name to display, split by comma'),
    ]

    def initialize_options(self):
        self.category = None
    
    def finalize_options(self):
        if self.category:
            self.category = self.category.split(',')

    def run(self):
        logging.basicConfig(level=logging.DEBUG)
        cfg = _loadConfig()
        seg_service = service.SegumentService(cfg)
        c_list = self.category
        if not c_list:
            c_list = seg_service.db.getCategoryList()
        print 
        for name in c_list:
            c = seg_service.db.getCategory(name)
            if c is None:
                print 'No such category', name
                continue
            stats = c.getStats()
            print 'Category ' + name
            print '=========' + '='*len(name)
            print 'Ngram:', stats['gram']
            for n in xrange(1, stats['gram']+1):
                print '%d-gram sum:' % n, stats['%sgram_sum' % n]
                print '%d-gram variety:' % n, stats['%sgram_variety' % n]
            print 
