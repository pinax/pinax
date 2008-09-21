class SortOrderMiddleware(object):
    def process_request(self, request):
        request.sort_order = request.GET.get('sort_order')
