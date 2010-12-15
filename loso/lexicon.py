# -*- coding: utf8 -*-

import re
import logging

from redis import Redis

from loso import util

# default delimiters for splitSentence
default_delimiters = set(u"""\n\r\t ,.:"()[]{}。，、；：！「」『』─（）﹝﹞…﹏＿‧""")

eng_term_pattern = """[a-zA-Z0-9\\-_']+"""

def iterEnglishTerms(text):
    """Iterator English terms from Chinese text
    
    """
    terms = []
    parts = text.split()
    for part in parts:
        for term in re.finditer(eng_term_pattern, part):
            terms.append(term.group(0))
    return terms

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
    """Iterate n-gram terms in given text and return a generator. 
    
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
    
    def getStats(self):
        """Get statistics information
        
        """
        stats = {}
        n = 1
        while True:
            sum = self.getNgramSum(n)
            count = self.getNgramCount(n)
            if not sum or not count:
                break
            sum_key = '%s-gram_sum' % n
            count_key = '%s-gram_count' % n
            stats[sum_key] = sum
            stats[count_key] = count
            n += 1
        return stats
    
    def splitTerms(self, text, ngram=4):
        """Split text into terms
        
        """
        grams = []
        for n in xrange(1, ngram+1):
            terms = []
            for term in util.ngram(n, text):
                count = int(self.get(term) or 0)
                n = len(term)
                v = float(self.getNgramSum(n))/float(self.getNgramCount(n))
                v = v*v
                score = count/v
                if score == 0:
                    score = 0.00000001
                
                head_tail_score = 0
                head = 0
                tail = 0
                head_tail = self.getHeadTail(term)
                if head_tail is not None and n != 1:
                    head, tail = head_tail
                    if head > 3 and tail > 3:
                        score += (head + tail) / v
                
                self.logger.debug(
                    'Term=%s, Count=%s, Head=%s, Tail=%s, Score=%s', 
                    term, count, head, tail, score)
                terms.append((term, score))
            grams.append(terms)
        terms, best_score = findBestSegment(grams)
        self.logger.debug('Best score: %s', best_score)
        return terms
        
class LexiconBuilder(object):
    
    def __init__(self, db, ngram=4, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger('lexicon.builder')
        self.db = db
        self.ngram = ngram
    
    def feed(self, text):
        """Feed text into lexicon database and return total terms has been fed
        
        """
        total = 0
        for n in xrange(1, self.ngram+1):
            self.logger.debug('Processing %d-gram', n)
            terms_count = {}
            sum = 0
            count = 0
            # count number of terms
            for term in iterTerms(n, text):
                terms_count.setdefault(term, 0)
                if terms_count[term] == 0:
                    count += 1
                terms_count[term] += 1
                total += 1
            # add terms to database
            for term, delta in terms_count.iteritems():
                result = self.db.increase(term, delta)
                sum += delta
                self.logger.debug('Increase term %r to %d', term, result)
            # add n-gram count
            result = self.db.increaseNgramSum(n, sum)
            self.logger.debug('Increase %d-gram sum to %d', n, result)
            result = self.db.increaseNgramCount(n, count)
            self.logger.debug('Increase %d-gram count to %d', n, result)
        self.logger.info('Fed %d terms', total)
        return total