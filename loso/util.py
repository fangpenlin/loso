def ngram(n, terms):
    """An iterator for iterating n-gram terms from a text, for example:
    
    >>> list(ngram(2, ['Today', 'is', 'my', 'day']))
    [['Today', 'is'], ['is', 'my'], ['my', 'day']] 
    
    >>> list(ngram(3, ['Today', 'is', 'my', 'day']))
    [['Today', 'is', 'my'], ['is', 'my', 'day']] 
    
    """
    for i in xrange(len(terms) - n + 1):
        yield terms[i:i+n]
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()