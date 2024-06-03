from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # lista de todas as rotas da API
        api_routes = ['/esportes', '/esportes/<str:_id>/partidas', '/atletas', '/atletas/<str:pais_id>/<str:esporte_id>', '/paises', '/medalhas', '/medalhas/esportes', '/medalhas/atletas', '/medalhas/pais', '/login/token', '/login/token/validar', '/login/token/admin', '/login/superuser']
        if any (request.path.startswith(route) for route in api_routes):
            client_ip = request.META['REMOTE_ADDR']
            requests = cache.get(client_ip, 0)
            if requests > 999999:  # Limite de 50 requisições por hora
                return JsonResponse({'message': 'Rate limit exceeded'}, status=429)
            else:
                cache.set(client_ip, requests + 1, 3600)  # Incrementa o contador e define o tempo de expiração para 1 hora
        return self.get_response(request)
            