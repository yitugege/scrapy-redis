class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = 'http://107.173.122.99:8888'
        