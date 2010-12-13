# -*- coding: utf8 -*-

import logging

from redis import Redis

from loso import util

# default delimiters for splitSentence
default_delimiters = set(u"""\n\r\t ,.:"()[]{}。，、；：！「」『』─（）﹝﹞…﹏＿‧""")

def splitSentence(text, delimiters=None):
    """Split article into sentences by delimiters
    
    """
    if delimiters is None:
        delimiters = default_delimiters
    
    sentence = []
    for c in text:
        if c in delimiters:
            yield ''.join(sentence)
            sentence = []
        else:
            sentence.append(c)
    yield ''.join(sentence)
    
def iterTerms(n, text, emmit_head_tail=True):
    """Iterate terms in given text and return a generator. 
    
    All English in 
    terms will be lower case. All first and last terms in a sentence will be
    emitted another term in the result with 'B' and 'E' prefix.
    
    For example:
    
    'C1C2C3'
    
    in uni-gram term will be emitted as
    
    ['C1', 'BC1', 'C2', 'C3', 'EC3']
    
    where the C1, C2 and C3 are Chinese words. 
    
    """
    for sentence in splitSentence(text):
        first = True
        term = None
        for term in util.ngram(n, sentence):
            term = term.lower()
            yield term
            if first:
                if emmit_head_tail:
                    yield 'B' + term
                first = False
        if term is not None:
            if emmit_head_tail:
                yield 'E' + term
                
def findBestSegment(grams, op=lambda a, b: a*b):
    """Find the best segmentation
    
    """
    def makeTuple(term):
        return ([term[0]], term[1])
    # n-gram
    n = len(grams)
    # size of terms in unigram
    size = len(grams[0])
    
    # table for best solution in range (begin, end)
    table = {}
    
    # initialize the best solution table
    for i in xrange(size):
        term = grams[0][i]
        table[(i, i)] = makeTuple(term)
        
    # get candidate in of (left items, right items) at i-th item
    def getCandidate(i, left, right):
        left_range = (i, i+left-1)
        right_range = (i+left, i+left+right-1)
        left_item = table[left_range]
        right_item = table[right_range]
        return (left_item[0]+right_item[0], op(left_item[1], right_item[1]))
    
    # handle current_size together cases, for example
    # e.g. C1,C2,C3,C4, if the current_size is 2, then the cases will be
    # [C1, C2], [C2, C3], [C3, C4]
    for current_size in xrange(2, size+1):
        for i in xrange(size - current_size + 1):
            # handle all possible partition cases, 
            # e.g. with current_size 4, we can have partition cases:
            # (1, 3), (3, 1), (2, 2)
            candidates = []
            for count in xrange(1, (current_size/2) + 1):
                # count of left and right partition
                left, right = count, current_size - count
                candidates.append(getCandidate(i, left, right))
                if left != right:
                    left, right = right, left
                    candidates.append(getCandidate(i, left, right))
            if current_size <= n:
                candidates.append(makeTuple(grams[current_size-1][i]))
            # sort candidates
            candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
            winner = candidates[0]
            current_range = (i, i+current_size-1)
            table[current_range] = winner
    return table[(0, size-1)]

class LexiconDatabase(object):
    
    def __init__(
        self, 
        lexicon_prefix='Lexicon_', 
        meta_prefix='Meta_', 
        logger=None
    ):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger('lexicon.database')
        self.redis = Redis()
        self.lexicon_prefix = lexicon_prefix
        self.meta_prefix = meta_prefix
        
    def getHeadTailTerms(self):
        """Get all terms which appears both in head and tails
        
        """
        def getKeys(prefix):
            keys = self.redis.keys(prefix + '*')
            # strip prefix
            keys = map(lambda x: x.decode('utf8').lstrip(prefix), keys)
            # filter by length
            keys = filter(lambda x: len(x) > 1, keys)
            return set(keys)
        
        head_prefix = self.lexicon_prefix + 'B'
        head_keys = getKeys(head_prefix)
        
        tail_prefix = self.lexicon_prefix + 'E'
        tail_keys = getKeys(tail_prefix)
        
        common_set = head_keys & tail_keys
        values = self.redis.mget([self.prefix + term for term in common_set])
        
        for term, value in zip(common_set, values):
            value = int(value)
            yield term, value
    
    def getHeadTail(self, key):
        head = self.redis.get(self.lexicon_prefix + 'B' + key)
        tail = self.redis.get(self.lexicon_prefix + 'E' + key)
        if not (head and tail):
            return None
        return int(head), int(tail)
        
    def reset(self):
        """Clean lexicon up
        
        """
        keys = self.redis.keys(self.lexicon_prefix + '*')
        if keys:
            self.redis.delete(*keys)
        keys = self.redis.keys(self.meta_prefix + '*')
        if keys:
            self.redis.delete(*keys)
    
    def get(self, key):
        """Get a value from database by key
        
        """
        return self.redis.get(self.lexicon_prefix + key)
        
    def increase(self, key, value=1):
        """Increase count of a word
        
        """
        return self.redis.incr(self.lexicon_prefix + key, value)
    
    def increaseNgramSum(self, n, value):
        """Increase sum of n-gram terms
        
        """
        return self.redis.incr('%s%d-gram_sum' % (self.meta_prefix, n), value)
    
    def increaseNgramCount(self, n, value):
        """Increase count of n-gram terms
        
        """
        return self.redis.incr('%s%d-gram_count' % (self.meta_prefix, n), value)
    
    def getNgramSum(self, n):
        """Get sum of n-gram terms
        
        """
        return self.redis.get('%s%d-gram_sum' % (self.meta_prefix, n))
    
    def getNgramCount(self, n):
        """Get count of n-gram terms
        
        """
        return self.redis.get('%s%d-gram_count' % (self.meta_prefix, n))
        
class LexiconBuilder(object):
    
    def __init__(self, db, ngram=4, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger('lexicon.builder')
        self.db = db
        self.ngram = ngram
    
    def feed(self, text):
        for n in xrange(1, self.ngram+1):
            self.logger.info('Processing %d-gram', n)
            terms_count = {}
            sum = 0
            count = 0
            # count number of terms
            for term in iterTerms(n, text):
                terms_count.setdefault(term, 0)
                if terms_count[term] == 0:
                    count += 1
                terms_count[term] += 1
            # add terms to database
            for term, delta in terms_count.iteritems():
                result = self.db.increase(term, delta)
                sum += delta
                self.logger.debug('Increase term %r to %d', term, result)
            # add n-gram count
            result = self.db.increaseNgramSum(n, sum)
            self.logger.info('Increase %d-gram sum to %d', n, result)
            result = self.db.increaseNgramCount(n, count)
            self.logger.info('Increase %d-gram count to %d', n, result)
            
if __name__ == '__main__':
    import codecs
    logging.basicConfig(level=logging.INFO)
    db = LexiconDatabase()
    
    for n in xrange(1, 5):
        print '-'*10, 'n', n, '-'*10
        print 'Sum', db.getNgramSum(n)
        print 'Count', db.getNgramCount(n)
        v = float(db.getNgramSum(n))/float(db.getNgramCount(n))
        print 'v', v
        
    def analysis(s):
        grams = []
        for n in xrange(1, 5):
            terms = []
            for term in iterTerms(n, s, False):
                count = int(db.get(term) or 0)
                n = len(term)
                v = float(db.getNgramSum(n))/float(db.getNgramCount(n))
                v = v*v
                #print 'v of %s-gram' % n, v
                # lower the score of unigram
                #if n == 1:
                #   v *= 100
                #print term, count, count/v, db.getHeadTail(term)
                terms.append((term, count/v))
            grams.append(terms)
        #print repr(grams)
        terms, value = findBestSegment(grams)
        print ' '.join(terms)
        #print '-'*5, s, '-'*5
    
    analysis(u'今天天氣真好')
    analysis(u'我晚餐想吃漢堡')
    analysis(u'下班回家窩')
    analysis(u'花蓮真是一個生活步調很奇妙的地方')
    analysis(u'今天終於知道為什麼要常常在學校了')
    analysis(u'對外公布大批美國政府的外交機密文件')
    analysis(u'只想在對得起家人跟對得起自己之中尋得一個平衡點')
    analysis(u'大吃裡面那家雞肉飯的泰式火鍋好吃耶')
    analysis(u'靠吃素來減少肉類碳排放不容易')
    analysis(u'今天真是禍不單行')
    
#    db.reset()
#    builder = LexiconBuilder(db)
#    file = codecs.open('sample_tr_ch', 'rt', 'utf8')
#    content = file.read()
#    #content = '\n'.join(content)
#    #print len(content)
#    builder.feed(content)
#    print 'done'
#    
    #db.getHeadTailTerms()