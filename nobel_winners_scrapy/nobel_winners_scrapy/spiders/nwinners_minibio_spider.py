import scrapy
import re

# I don't like the duplication at all, but that's the way the book does it and I 
# won't try to fix it while learning... I'll just roll with it

BASE_URL = 'https://en.wikipedia.org'

class NWinnerItemBio(scrapy.Item):
    link = scrapy.Field()
    name = scrapy.Field()
    mini_bio = scrapy.Field()
    image_urls = scrapy.Field()
    bio_image = scrapy.Field()
    images = scrapy.Field()
    
    
# Note that as of 12/23/16, the ImagesPipeline (I think that's the relevant code)
# doesn't follow redirects. It looks like the images are behind 301s, so the
# code below doesn't actually download files. There are in-progress requests on 
# GitHub to change this. For example, see 
# https://github.com/scrapy/scrapy/issues/2004
# For now, I'll just modify the stuff downstream to not use images.
    
class NWinnerSpiderSpider(scrapy.Spider):
    
    name = 'nwinners_minibio'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [
        "https://en.wikipedia.org/wiki/List_of_Nobel_laureates_by_country"
    ]
    
    custom_settings = {
        'ITEM_PIPELINES':{'nobel_winners_scrapy.pipelines.NobelImagesPipeline':1},
        'IMAGES_STORE':'images'    
    }
    
    # parse deals with the HTTP response
    def parse(self, response):
        filename = response.url.split('/')[-1]        
        h2s = response.xpath('//h2')
        
        for h2 in h2s:
            country = h2.xpath('span[@class="mw-headline"]/text()').extract()
            if country:
                winners = h2.xpath('following-sibling::ol[1]')
                for w in winners.xpath('li'):
                    if w.xpath('text()').extract():
                        wdata = {}
                        wdata['link'] = BASE_URL + w.xpath('a/@href').extract()[0]
                        request = scrapy.Request(wdata['link'],
                                                 callback=self.get_mini_bio)
                        request.meta['item'] = NWinnerItemBio(**wdata)
                        yield request
                    
    def get_mini_bio(self, response):
        BASE_URL_ESCAPED = 'https:\/\/en.wikipedia.org'
        item = response.meta['item']
        item['image_urls'] = []
        img_src = response.xpath('//table[contains(@class,"infobox")]//img/@src')
        if img_src:
            item['image_urls'] = ['http:' + img_src[0].extract()]
        mini_bio = ''
        paras = response.xpath('//*[@id="mw-content-text"]/p[text() or' \
                               'normalize-space(.)=""]').extract()
                               
        for p in paras:
            if p == '<p></p>': # stop point
                break
            mini_bio += p
            
        mini_bio = mini_bio.replace('href="/wiki', 'href="' + BASE_URL + '/wiki')
        mini_bio = mini_bio.replace('href="#"', item['link'] + "#")
        item['mini_bio'] = mini_bio
        
        yield item
