class DummyTokenizer(object):
    """A dummy tokenizer for split Chinese text into a list of one words
        
    """
    
    def tokenize(self, text):
        terms = []
        for i, word in enumerate(text):
            if word.strip():
                terms.append((i, word))
        return terms