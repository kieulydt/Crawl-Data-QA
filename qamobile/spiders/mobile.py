# -*- coding: utf-8 -*-
import scrapy


class MobileSpider(scrapy.Spider):
    name = 'mobile'
    allowed_domains = ['fptshop.com.vn']
    start_urls = ['https://fptshop.com.vn/dien-thoai/']
    domain = 'https://fptshop.com.vn'

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_brand)
    def parse_brand(self, response):
        list_brand = response.css('div.fs-ctbrand div.owl-carousel a::attr(href)').getall()
        for item in list_brand:
            if item is not None:
                next_page = self.domain + item
                brand = item.split('/')[-1]
                if brand == 'apple-iphone':
                    brand = 'iphone'
                request = scrapy.Request(url=next_page, callback=self.parse_item)
                request.meta['brand'] = brand
                yield request


    def parse_item(self, response):
        list_name = response.css('div.fs-carow div.fs-lpil a.fs-lpil-img::attr(href)').getall()
        for item in list_name:
            if item is not None:
                detail_item = self.domain + item
                name = item.split('/')[-1]
                request = scrapy.Request(url=detail_item, callback=self.parse_detail)
                request.meta['brand'] = response.meta['brand']
                request.meta['name'] = name
                yield request
