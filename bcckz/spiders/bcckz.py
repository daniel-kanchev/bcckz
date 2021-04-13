import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bcckz.items import Article


class bcckzSpider(scrapy.Spider):
    name = 'bcckz'
    start_urls = ['https://www.bcc.kz/about/press-sluzhba/news/']

    def parse(self, response):
        links = response.xpath('//a[@class="itdnone ibold"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="modern-page-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="aa_newshead_title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="aa_newshead_time"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="aa_nd_text"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
