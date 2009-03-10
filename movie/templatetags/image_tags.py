import re
from urllib import urlopen
from django.template import Node, Library, Variable
import feedparser

register = Library()

def do_images_for(parser, token):
    tags = re.search(r'images_for (.*) as', token.contents).group(1).split()
    engine = re.search(r'from (.*)', token.contents).group(1)
    tags = map(Variable, tags)
    context_var = re.search(r'as (.*) from', token.contents).group(1)
    return ImagesFor(context_var, tags, engine)

register.tag('images_for', do_images_for)

class ImagesFor(Node):
    def __init__(self, context_var, keywords, engine='flickr'):
        self.__context_var = context_var
        self.__keywords = keywords
        self.__engine = engine
    
    def render(self, context):
        keywords = [keyword.resolve(context) for keyword in self.__keywords]

        if self.__engine == 'flickr':
            feed = feedparser.parse('http://api.flickr.com/services/feeds/photos_public.gne?format=atom&tags='+','.join(keywords))
            images = [re.search(r'src="(.*?)"', entry.subtitle).group(1) for entry in feed.entries]
        elif self.__engine == 'altavista':
            html = urlopen('http://de.altavista.com/image/results?itag=ody&q='+
                           ('+'.join(keywords)).replace(' ', '+')).read()        
            images = re.findall(r'src="(.*?)"',html)[4:]
        
        context[self.__context_var] = images
        return ""
