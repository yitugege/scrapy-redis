import random
class ProxyMiddleware(object):
    #def process_request(self, request, spider):
    #    request.meta['proxy'] = 'http://107.173.122.99:8888'
    def process_request(self, request, spider):
        ip = random.choice(spider.settings.get('PROXIES'))   
        print('测试IP:', ip)
        request.meta['proxy'] = ip



        