class SetRegionAndRealmMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_kwargs.get('region') and view_kwargs.get('realm'):
            request.session['region'] = view_kwargs['region']
            request.session['realm'] = view_kwargs['realm']
        return None
