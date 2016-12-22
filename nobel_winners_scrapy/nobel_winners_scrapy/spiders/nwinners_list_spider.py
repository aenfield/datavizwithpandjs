import scrapy
import re

# define the data to be scraped
class NWinnerItem(scrapy.Item):
    country = scrapy.Field()
    name = scrapy.Field()
    link_text = scrapy.Field()
    
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
                    text = w.xpath('descendant-or-self::text()').extract()
                    if text:
                        yield NWinnerItem(
                            country=country[0], 
                            name = text[0],
                            link_text = ' '.join(text)
                        )
    