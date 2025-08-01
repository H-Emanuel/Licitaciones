from django.shortcuts import redirect

class GlobalExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            if response.status_code in [400, 403, 404, 500]:
                return self.handle_error(request, response.status_code)
            return response
        except Exception as e:
            # Para errores 500 no manejados
            return self.handle_error(request, 500)

    def handle_error(self, request, status_code):
        return redirect('gestion_licitaciones')