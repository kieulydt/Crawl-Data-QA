# -*- coding: utf-8 -*-
import scrapy
from qamobile.items import CrawlMobile


class TgddmobileSpider(scrapy.Spider):
    name = 'tgddMobile'
    allowed_domains = ['thegioididong.com']
    start_urls = ['https://www.thegioididong.com/dtdd/']
    domain = 'https://www.thegioididong.com'


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_brand)
    def parse_brand(self, response):
        list_brand = response.css('div.manu a::attr(href)').getall()
        list_brand.remove('javascript:;')
        for item in list_brand:
            if item is not None:
                next_page = self.domain + item
                brand = item.split('-')[-1]
                request = scrapy.Request(url=next_page, callback=self.parse_item)
                request.meta['brand'] = brand
                yield request
    def parse_item(self, response):
        list_name = response.css('ul.homeproduct li.item a::attr(href)').getall()
        for item in list_name:
            if item is not None:
                detail_item = self.domain + item
                name = item.split('/')[-1]
                request = scrapy.Request(url=detail_item, callback=self.parse_detail)
                request.meta['brand'] = response.meta['brand']
                request.meta['name'] = name
                yield request
    def parse_detail(self, response):
        item = CrawlMobile()
        for data in response.css('ul.listcomment li'):
            if data is not None:
                item['question'] = data.css('div.question::text').getall()
                item['answer'] = data.css('div.listreply div.reply div.cont::text').getall()
                item['brand'] = response.meta['brand']
                item['name'] = response.meta['name']
                yield item
