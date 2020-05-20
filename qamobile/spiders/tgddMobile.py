# -*- coding: utf-8 -*-
import scrapy
from qamobile.items import CrawlMobile
from scrapy import Selector, Request
from scrapy.spiders import CrawlSpider
import re
from scrapy_splash import SplashRequest
import time
import requests
import json

class TgddmobileSpider(scrapy.Spider):
    name = 'tgddMobile'
    allowed_domains = ['thegioididong.com']
    start_urls = ['https://www.thegioididong.com/dtdd/']
    domain = 'https://www.thegioididong.com'

    get_comment_script = """
    function main(splash, args)
      assert(splash:go(args.url))
      assert(splash:wait(1))
      page_elements = splash:select_all('div.pagcomment a')
      total_page_elements = page_elements[#page_elements-1]
      next_page_elements = page_elements[#page_elements]
      total_page = tonumber(total_page_elements:text())
      
        return_html = splash:select('ul.listcomment').outerHTML
        for i = 1,total_page-1 do
        next_page_elements:click()
        assert(splash:wait(1))
        return_html = return_html .. splash:select('ul.listcomment').outerHTML
      end
      
      return {
        html = return_html,
        png = splash:png(),
        har = splash:har(),
        total_page = total_page,
      }
    end
    """


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

class TgddmobileSpiderPost(scrapy.Spider):
    name = 'tgddMobilePost'
    allowed_domains = ['thegioididong.com']
    domain = 'https://www.thegioididong.com'

    custom_settings = {
        'DOWNLOAD_TIMEOUT' : 3600
    }

    get_comment_script = """
    function main(splash, args)
      assert(splash:go(args.url))
      assert(splash:wait(1))
      page_elements = splash:select_all('div.pagcomment a')
      total_page_elements = page_elements[#page_elements-1]
      
      total_page = tonumber(total_page_elements:text())
      
        return_html = splash:select('ul.listcomment').outerHTML
        for i = 1, total_page-2 do
        page_elements = splash:select_all('div.pagcomment a')
        next_page_elements = page_elements[#page_elements]
        next_page_elements:mouse_click()
        assert(splash:wait(3))
        return_html = return_html .. splash:select('ul.listcomment').outerHTML
      end
      
      return {
        html = return_html,
        png = splash:png(),
        har = splash:har(),
        total_page = total_page,
      }
    end
    """

    def __init__(self, url='https://www.thegioididong.com/dtdd/samsung-galaxy-a31', *args, **kwargs):
        super(TgddmobileSpiderPost, self).__init__(*args, *kwargs)
        self.start_urls = [url]


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse_detail, args={'lua_source' : self.get_comment_script, 'timeout' : 3600}, endpoint='execute')

 
    def parse_detail(self, response):
        item = CrawlMobile()

        for data in response.css('ul.listcomment li'):
            if data is not None:
                item['question'] = ''.join(data.css('div.question::text').getall())
                item['answer'] = ''.join(data.css('div.listreply div.reply div.cont::text').getall())
                # item['brand'] = response.meta['brand']
                # item['name'] = response.meta['name']
                yield item

