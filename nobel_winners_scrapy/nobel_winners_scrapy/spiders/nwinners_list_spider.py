import scrapy
import re

BASE_URL = 'http://en.wikipedia.org'

# define the data to be scraped
class NWinnerItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    year = scrapy.Field()
    category = scrapy.Field()
    country = scrapy.Field()
    gender = scrapy.Field()
    born_in = scrapy.Field()
    date_of_birth = scrapy.Field()
    date_of_death = scrapy.Field()
    place_of_birth = scrapy.Field()
    place_of_death = scrapy.Field()
    text = scrapy.Field()
    
def process_winner_li(w, country=None):
    """
    Process a winner's <li> tag, adding country of birth or 
    nationality, as applicable."""
    
    # some rows (at least one) are li tags with no data - we can't do anything with them
    # (another option would be to filter these li tags out with the parent xpath)
    if not w.xpath('text()').extract():
        return None
    
    wdata = {}
    
    wdata['link'] = BASE_URL + w.xpath('a/@href').extract()[0]
    
    text = ' '.join(w.xpath('descendant-or-self::text()').extract())
    wdata['name'] = text.split(',')[0].strip()
    
    year = re.findall('\d{4}', text)
    if year:
        wdata['year'] = int(year[0])
    else:
        wdata['year'] = 0
        print('No year in ', text)
    
    category = re.findall(
        'Physics|Chemistry|Physiology or Medicine|Literature|Peace|Economics', text
    )
    if category:
        wdata['category'] = category[0]
    else:
        wdata['category'] = ''
        print('No category in ', text)
        
    if country:
        if text.find('*') != -1:    # * in the text says the country is the winner's by birth
            wdata['country'] = ''
            wdata['born_in'] = country
        else:
            wdata['country'] = country
            wdata['born_in'] = ''
            
    # store the link's text for manual corrections
    wdata['text'] = text
    return wdata
            
        
        
    
# create named spider
class NWinnerSpider(scrapy.Spider):
    """Scrapes the country and link text of Nobel Prize winners."""
    
    name = 'nwinners_list'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        "http://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_country"
    ]
    
    # parse deals with the HTTP response
    def parse(self, response):
        h2s = response.xpath('//h2')
        
        for h2 in h2s:
            country = h2.xpath('span[@class="mw-headline"]/text()').extract()
            if country:
                winners = h2.xpath('following-sibling::ol[1]')
                for w in winners.xpath('li'):
                    wdata = process_winner_li(w, country[0])
                    if wdata:
                        yield NWinnerItem(wdata)


                    # text = w.xpath('descendant-or-self::text()').extract()
                    # if text:
                    #     yield NWinnerItem(
                    #         country=country[0],
                    #         name = text[0],
                    #         link_text = ' '.join(text)
                    #     )
    