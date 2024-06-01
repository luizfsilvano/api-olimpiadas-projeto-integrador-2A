from ..schemas import *
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from marshmallow import ValidationError
from .views_esportes import *


# Método para criar um atleta passando o nome, idade. Pais e esportes são passados por ID no path da requisição
@csrf_exempt
def create_atleta(request, pais_id, esporte_id):
    if request.method == 'POST':
        try:
            # Verifica se o usuário é um juiz
            if not check_refeer_permissions(request):
                return JsonResponse({'message': '403 - Permissão negada'}, status=403)
            
            # Recebe os dados da requisição
            data = json.loads(request.body)

            # Adiciona os IDs do país e do esporte aos dados
            data['pais_id'] = pais_id
            data['esporte_id'] = esporte_id

            # buscar nome do país e do esporte
            pais = db_handle.paises.find_one({'_id': ObjectId(pais_id)})
            esporte = db_handle.esportes.find_one({'_id': ObjectId(esporte_id)})

            if pais is None:
                return JsonResponse({'message': 'País não encontrado'}, status=404)
            
            if esporte is None:
                return JsonResponse({'message': 'Esporte não encontrado'}, status=404)

            # Adiciona o nome do país e do esporte aos dados
            data['pais'] = pais['nome']
            data['esporte'] = esporte['nome']

            # Valida os dados da requisição
            atleta = AtletasSchema().load(data)

            # Insere o atleta no banco de dados
            result = db_handle.atletas.insert_one(atleta)

            # Adiciona o ID do atleta aos dados
            atleta['_id'] = str(result.inserted_id)

            # Retorna os dados do atleta com a mensagem de sucesso
            atleta['message'] = 'Atleta criado com sucesso!'
            return JsonResponse(atleta, status=201)
        except ValidationError as err:
            return JsonResponse(err.messages, status=400)
        except InvalidId:
            return JsonResponse({'message': 'ID inválido'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Chave inválida'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)


        
@csrf_exempt
def get_atletas(request):
    
    # Método para buscar um atleta passando o ID do atleta
    if request.method == 'GET':
        try:
            # Pega o ID do atleta da query da requisição
            atleta_id = request.GET.get('_id', None)

            if atleta_id:
                # Converte o ID do atleta para ObjectId
                oid = ObjectId(atleta_id)
                # Busca o atleta no banco de dados
                atleta = db_handle.atletas.find_one({'_id': oid})
                # Verifica se o atleta foi encontrado
                if atleta:
                    return JsonResponse(atleta, status=200, encoder=JSONEncoder)
                else:
                    return JsonResponse({'message': 'Atleta não encontrado!'}, status=404)
            else:
                # Busca todos os atletas no banco de dados
                atletas = list(db_handle.atletas.find())
                # Verifica se os atletas foram encontrados
                if atletas:
                    return JsonResponse(atletas, status=200, encoder=JSONEncoder, safe=False)
                else:
                    return JsonResponse({'message': 'Atletas não encontrados!'}, status=404)
        except InvalidId:
            return JsonResponse({'message': 'ID inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    
    # Método para atualizar um atleta passando o ID do atleta
    if request.method == 'PATCH':
        try:
            # Verifica se o usuário é um juiz
            if not check_refeer_permissions(request):
                return JsonResponse({'message': '403 - Permissão negada'}, status=403)
            
            # Pega o ID do atleta da query da requisição
            atleta_id = request.GET.get('_id', None)
            if not atleta_id:
                return JsonResponse({'message': 'ID do atleta não fornecido'}, status=400)

            # Recebe os dados da requisição
            data = json.loads(request.body)

            # Se o ID do país foi fornecido, busca o nome correspondente
            if 'pais_id' in data:
                pais = db_handle.paises.find_one({'_id': ObjectId(data['pais_id'])})
                if pais:
                    data['pais_nome'] = pais['nome']
                else:
                    return JsonResponse({'message': 'País não encontrado'}, status=404)
                
            # Se o ID do esporte foi fornecido, busca o nome do esporte correspondente 
            if 'esporte_id' in data:
                esporte = db_handle.esportes.find_one({'_id': ObjectId(data['esporte_id'])})
                if esporte:
                    data['esporte_nome'] = esporte['nome']
                else:
                    return JsonResponse({'message': 'Esporte não encontrado'}, status=404)

            # Valida os dados da requisição
            atleta = AtletasSchema().load(data, partial=True)

            # Atualiza o atleta no banco de dados
            result = db_handle.atletas.update_one({'_id': ObjectId(atleta_id)}, {'$set': atleta})

            # Verifica se o atleta foi atualizado
            if result.modified_count == 1:
                return JsonResponse({'message': 'Atleta atualizado com sucesso!'}, status=200)
            else:
                return JsonResponse({'message': 'Atleta não encontrado!'}, status=404)
        except ValidationError as err:
            return JsonResponse(err.messages, status=400)
        except InvalidId:
            return JsonResponse({'message': 'ID inválido'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Chave inválida'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    
    # Método para deletar um atleta passando o ID do atleta
    if request.method == 'DELETE':
        try:
            # verifica se o usuario é um juiz
            if not check_refeer_permissions(request):
                return JsonResponse({'message': '403 - Permissão negada'}, status=403)
            
            # Pega o ID do atleta da query da requisição
            atleta_id = request.GET.get('_id', None)
            if not atleta_id:
                return JsonResponse({'message': 'ID do atleta não fornecido'}, status=400)

            # Deleta o atleta do banco de dados
            result = db_handle.atletas.delete_one({'_id': ObjectId(atleta_id)})

            # Verifica se o atleta foi deletado
            if result.deleted_count == 1:
                return JsonResponse({'message': 'Atleta deletado com sucesso!'}, status=200)
            else:
                return JsonResponse({'message': 'Atleta não encontrado!'}, status=404)
        except InvalidId:
            return JsonResponse({'message': 'ID inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
