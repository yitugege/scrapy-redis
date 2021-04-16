from scrapy import item
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from ..pipelines import ScrapyRedisTestPipeline
import re
import datetime
from ..items import ScrapyRedisTestItem
from scrapy_redis.spiders import RedisCrawlSpider


class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mercado'
    redis_key = 'mercado:start_urls'

    rules = (
        
        Rule(LinkExtractor(allow=r'.*/c/.*#c_id=.*'),follow=True),
        Rule(LinkExtractor(allow=r'.*CATEGORY_ID=M\w\w.\d+.*'), follow=True),
        Rule(LinkExtractor(allow=r'.*/_Desde_\d+$'),follow=True),#下一页  follow = true的意思是下一次提取网页中包含我们我们需要提取的信息,True代表继续提取
        Rule(LinkExtractor(allow=r'.*/M\w\w(\d+|-\d+|/).*',deny=( r'.*/jms/mlm/lgz/login.*',
                                                            r'.*noindex.*',
                                                            r'.*auth.*',
                                                            r'.*product_trigger_id=MLM+\d+',
                                                            r'.*/seller-info$',
                                                            r'.*pdp_filters=category:.*',
                                                            r'.*method=add.*',
                                                            r'.*/s$')),callback='parse',follow=True)
        
    )  

    def parse (self,response):
        #print('--------------------当前连接----------------')
        #print(response.url)
        items = ScrapyRedisTestItem()
        #标题
        title = response.xpath('//h1[@class="ui-pdp-title"]/text()').get()
        if  title == None:
            return
        #链接
        url = response.url
        #获取商品ID
        id = re.findall(r"\d{6,}",url)
        if  id == None:
            return
        else:
            id = id[0]
        


        #获取价格
        price = response.xpath('//div[@class="ui-pdp-price__second-line"]/span[@class="price-tag ui-pdp-price__part"]/span[@class="price-tag-fraction"]/text()').get()
        if  price == None:
            return
        #打印点赞人数,把数组中的数字提取出来转换城数字
        like_count = response.xpath('//a[@class="ui-pdp-review__label ui-pdp-review__label--link"]/span[@class="ui-pdp-review__amount"]/text()').get()
        if like_count != None:
            like_count = re.findall(r"\d{1,}",like_count)
            like_count = list(map(int,like_count))
            like_count = like_count = like_count[0]
        else:
            like_count = None

        #print("-----------------------------------likeaccount--------------------------")
        #print(like_count)
        #打印店铺
        seller = response.xpath('//a[@class="ui-pdp-action-modal__link"]/span[@class="ui-pdp-color--BLUE"]/text()').get()
        #获取销量,判读是否为usado,如果不是那么取整数，如果是不做操作
        Num_sell = response.xpath('//div[@class="ui-pdp-header"]/div[@class="ui-pdp-header__subtitle"]/span[@class="ui-pdp-subtitle"]/text()').get()
        if  Num_sell is None:
            return
        #print("-----------------------------------Num_sell--------------------------")
        #print(Num_sell)
        #print(type(Num_sell))
        elif bool(re.findall(r'\d+',Num_sell)):
            Num_sell = re.findall(r"\d+",Num_sell)
            Num_sell = list(map(int,Num_sell))
            Num_sell = Num_sell[0]
            #print("-----------------------------------Num_sell--------------------------")
            #print(Num_sell)
            #print(type(Num_sell))
        else:
            return
        #获取60天销量
        days60_sell=response.xpath('//strong[@class="ui-pdp-seller__sales-description"]/text()').get()
        if days60_sell is None:
            return
        elif bool(re.findall(r'\d+',days60_sell)):
            days60_sell = re.findall(r'\d+',days60_sell)
            days60_sell = list(map(int,days60_sell))
            days60_sell = days60_sell[0]
        else:
            return
        #记录爬取的时间
        #GMT_FORMAT = '%D %H:%M:%S'
        GMT_FORMAT = '%D'
        current_time = datetime.datetime.utcnow().strftime(GMT_FORMAT)

        items['title']=title
        items['url']=url
        items['price']=price
        items['like_count']=like_count
        items['id']=id
        items['seller']=seller
        items['Num_sell']=Num_sell
        items['current_time']=current_time
        items['days60_sell']=days60_sell

        return items
