# apps/common/middleware.py
class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Incoming request: {request.scheme}://{request.get_host()}{request.path}")
        print(f"Secure: {request.is_secure()}")
        response = self.get_response(request)
        return response