from ..schemas import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .views_esportes import *


# para o quadro de medalhas, será dividido as requisições em medalhas por esportes, paises e atletas
# para isso, será necessário criar uma função para cada tipo de requisição

# @csrf_exempt
# def medalhas_por_esportes(request):
#     if request.method == 'GET':
#         esporte_id = request.GET.get('esporte_id', None)
#         if esporte_id:
#             if not esporte_existe(esporte_id):
#                 return JsonResponse({'message': '404 - Esporte não encontrado'}, status=404)
            
#             medalhas = db_handle.medalhas.find({'esporte_id': esporte_id})
#             medalhas_list = []
#             for medalha in medalhas:
#                 response_data = {
#                     "pais": medalha["pais"],
#                     "ouro": medalha["ouro"],
#                     "prata": medalha["prata"],
#                     "bronze": medalha["bronze"],
#                     "total": medalha["total"]
#                 }
#                 if "atleta" in medalha:
#                     response_data["atleta"] = medalha["atleta"]
#                 medalhas_list.append(response_data)
#             return JsonResponse({'medalhas': medalhas_list}, status=200)
#         else:
#             return JsonResponse({'message': '400 - Esporte não informado'}, status=400)
#     else:
#         return JsonResponse({'message': '405 - Método não permitido'}, status=405)


# @csrf_exempt
# def medalhas_por_atleta(request):
#     if request.method == 'GET':
#         atleta_id = request.GET.get('atleta_id', None)
#         if atleta_id:
#             if not atleta_existe(atleta_id):
#                 return JsonResponse({'message': '404 - Atleta não encontrado'}, status=404)
            
#             medalhas = db_handle.medalhas.find({'atleta_id': atleta_id})
#             medalhas_list = []
#             for medalha in medalhas:
#                 response_data = {
#                     "pais": medalha["pais"],
#                     "ouro": medalha["ouro"],
#                     "prata": medalha["prata"],
#                     "bronze": medalha["bronze"],
#                     "total": medalha["total"]
#                 }
#                 if "atleta" in medalha:
#                     response_data["atleta"] = medalha["atleta"]
#                 medalhas_list.append(response_data)
#             return JsonResponse({'medalhas': medalhas_list}, status=200)
#         else:
#             return JsonResponse({'message': '400 - Atleta não informado'}, status=400)
#     else:
#         return JsonResponse({'message': '405 - Método não permitido'}, status=405)
        

@csrf_exempt
def medalhas_geral(request):
    if request.method == "GET":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
    medalhas = db_handle.medalhas.find()
    medalhas_list = []
    for medalha in medalhas:
        response_data = {
            "_id": str(medalha["_id"]),
            "pais": medalha["pais"],
            "ouro": medalha.get("ouro", 0),
            "prata": medalha.get("prata", 0),
            "bronze": medalha.get("bronze", 0),
            "total": medalha.get("total", 0)
        }
        if "atleta" in medalha:
            response_data["atleta"] = medalha["atleta"]
        medalhas_list.append(response_data)
    return JsonResponse(medalhas_list, safe=False, status=200)


# @csrf_exempt
# def medalhas_paises(request):
#     if request.method == 'GET':
#         pais_id = request.GET.get('pais_id', None)
#         if pais_id:
#             if not pais_existe(pais_id):
#                 return JsonResponse({'message': '404 - País não encontrado'}, status=404)
            
#             medalhas = db_handle.medalhas.find({'pais_id': pais_id})
#             medalhas_list = []
#             for medalha in medalhas:
#                 response_data = {
#                     "pais": medalha["pais"],
#                     "ouro": medalha["ouro"],
#                     "prata": medalha["prata"],
#                     "bronze": medalha["bronze"],
#                     "total": medalha["total"]
#                 }
#                 if "atleta" in medalha:
#                     response_data["atleta"] = medalha["atleta"]
#                 medalhas_list.append(response_data)
#             return JsonResponse({'medalhas': medalhas_list}, status=200)
#         else:
#             return JsonResponse({'message': '400 - País não informado'}, status=400)
#     else:
#         return JsonResponse({'message': '405 - Método não permitido'}, status=405)