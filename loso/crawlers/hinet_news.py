import codecs
import urllib2
import cStringIO as StringIO

from lxml import etree

rss_urls = [
    'http://times.hinet.net/times/rss.do?option=entertainment',
    'http://times.hinet.net/times/rss.do?option=sport',
    'http://times.hinet.net/times/rss.do?option=society',
    'http://times.hinet.net/times/rss.do?option=infotech',
    'http://times.hinet.net/times/rss.do?option=politics',
    'http://times.hinet.net/times/rss.do?option=mainland',
    'http://times.hinet.net/times/rss.do?option=finance',
    'http://times.hinet.net/times/rss.do?option=internationality',
    'http://times.hinet.net/times/rss.do?option=weather'
]

def parseHtml(html):
    parser = etree.HTMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(html), parser)
    return tree

def parseXml(xml):
    parser = etree.XMLParser(encoding='utf8')
    tree = etree.parse(StringIO.StringIO(xml), parser)
    return tree

def getPage(url):
    file = urllib2.urlopen(url)
    content = file.read()
    file.close()   
    return content

def getLinks(rss_url):
    content = getPage(rss_url)
    tree = parseXml(content)
    return tree.xpath('//link/text()')

def getNewsText(news_url):
    content = getPage(news_url)
    tree = parseHtml(content)
    for paragraph in tree.xpath("//div[@id='newsp']/p/text()"):
        yield paragraph.strip()
    
def crawelCategory(rss_url):
    links = getLinks(rss_url)
    for link in links[1:]:
        yield ' '.join(getNewsText(link))
        
def main():
    with codecs.open('hinet_news.txt', 'wt', encoding='utf8') as file:
        for url in rss_urls:
            for text in crawelCategory(url):
                print 'Write %d bytes' % len(text)
                print >> file, text
    print 'Done.'
            
if __name__ == '__main__':
    main()
