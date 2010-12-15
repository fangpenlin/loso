import logging

import server

def main():
    logging.basicConfig(level=logging.DEBUG)
    service = server.SegumentService()
    while True:
        text = unicode(raw_input('Text:'))
        terms = service.splitTerms(text)
        print ' '.join(terms)

if __name__ == '__main__':
    main()