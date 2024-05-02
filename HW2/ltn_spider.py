import scrapy
from ltn_news.items import LtnNewsItem

class LtnSpider(scrapy.Spider):
    name = 'ltn'
    allowed_domains = ['news.ltn.com.tw']
    start_urls = ['https://news.ltn.com.tw/list/breakingnews']

    def parse(self, response):
        news_list = response.xpath('//ul[@class="list"]/li')
        for news in news_list:
            item = LtnNewsItem()
            item['title'] = news.xpath('.//p[@class="title"]/a/text()').get().strip()
            item['link'] = news.xpath('.//p[@class="title"]/a/@href').get()
            item['publish_time'] = news.xpath('.//p[@class="time"]/text()').get().strip()
            item['image_url'] = news.xpath('.//img/@data-src').get()
            yield item     
  class LtnNewsItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    publish_time = scrapy.Field()
    image_url = scrapy.Field()

