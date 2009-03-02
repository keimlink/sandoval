from django.template import Node, Library, Variable
import feedparser
import re
from urllib import urlopen

register = Library()

def do_images_for(parser, token):
    tags = re.search(r'images_for (.*) as', token.contents).group(1).split()
    tags = map(Variable, tags)
    return ImagesFor(re.search(r'as (.*)', token.contents).group(1), tags)

register.tag('images_for', do_images_for)

class ImagesFor(Node):
    def __init__(self, context_var, keywords):
        self.__context_var = context_var
        self.__keywords = keywords
    
    def render(self, context):
        keywords = [keyword.resolve(context) for keyword in self.__keywords]

        html = urlopen('http://de.altavista.com/image/results?itag=ody&q='+
                       ('+'.join(keywords)).replace(' ', '+')).read()        
        images = re.findall(r'src="(.*?)"',html)[4:]
        #feed = feedparser.parse('http://api.flickr.com/services/feeds/photos_public.gne?format=atom&tags='+','.join(keywords))
#        images = []
#        for entry in feed.entries:
#            for enclusure in entry.enclosures:
#                images.append(enclusure.href)
        
        context[self.__context_var] = images
        return ""
