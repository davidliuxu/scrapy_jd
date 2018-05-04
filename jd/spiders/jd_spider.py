# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
import json
import re
import pprint

class JdSpiderSpider(CrawlSpider):
    name = 'jd_spider'    #老朋友，爬虫名字，必不可少
    allowed_domains = ['jd.com','p.3.cn']
    start_urls = ['http://m.jd.com/'] 

    rules = [
        Rule(LinkExtractor(allow = ()),      #允许抓取所有链接
             callback = 'parse_shop',        #回调parse_shop函数
             follow = True                   #跟随链接
             ),
        ]

    def parse_shop(self, response):
        pass
        ware_id_list = list()
        url_group_shop = LinkExtractor(allow = (r'(http|https)://item.m.jd.com/product/\d+.html')).extract_links(response)    #对链接使用正则表达式进行筛选

        re_get_id = re.compile(r'(http|https)://item.m.jd.com/product/(\d+).html')    #定义抓取正则表达式的抓取规则

        for url in url_group_shop:
            ware_id = re_get_id.search(url.url).group(2)    #抓取出商品id
            ware_id_list.append(ware_id)                    #商品id添加进ware_id_list

        for id in ware_id_list:
            """
            https://item.m.jd.com/ware/detail.json?wareId={}
            https://p.3.cn/prices/mgets?type=1&skuIds=J_{}
            """

            yield Request('https://item.m.jd.com/ware/detail.json?wareId={}'.format(id), #拼接详情页面的url
                          callback = self.detail_pag,
                          meta = {'id':id},
                          priority=5
                          )                         

    def detail_pag(self,response):
        data = json.loads(response.text)

        yield Request('https://p.3.cn/prices/mgets?type=1&skuIds=J_{}'.format(response.meta['id']),          #拼接价格页面的url
                      callback=self.get_price_pag,
                      meta={'id': response.meta['id'],    #把id和data传给下一个函数
                            'data':data
                            },
                      priority = 10
                      )

    def get_price_pag(self,response):
        data = json.loads(response.text)
        detail_data = response.meta['data']
        ware_id = response.meta['id']
        item = {
            'detail':detail_data,
            'price':data,
            'ware_id':ware_id
            }

        pprint.pprint(item)
        yield item           #转给管道
