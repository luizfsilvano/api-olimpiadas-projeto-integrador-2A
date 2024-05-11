from utils import get_db_handle
from ..schemas import *
import json, jwt, logging, traceback, sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from passlib.context import CryptContext
from Olimpiadas.settings import db_name, uri, SECRET_KEY
from datetime import datetime

# Conexão com o banco de dados
db_handle, client = get_db_handle(db_name, uri)

# Definição de Logger
logger = logging.getLogger(__name__)

# Definição de Contexto de Senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# verificação medalhas
def verifica(atleta_id_ouro, atleta_id_prata, atleta_id_bronze, ouro, prata, bronze):
    if atleta_id_ouro and not atleta_existe(atleta_id_ouro):
        return JsonResponse({"error": "Atleta de ouro não encontrado"}, status=404)
    if atleta_id_prata and not atleta_existe(atleta_id_prata):
        return JsonResponse({"error": "Atleta de prata não encontrado"}, status=404)
    if atleta_id_bronze and not atleta_existe(atleta_id_bronze):
        return JsonResponse({"error": "Atleta de bronze não encontrado"}, status=404)
    if ouro and not pais_existe(ouro):
        return JsonResponse({"error": "País de ouro não encontrado"}, status=404)
    if prata and not pais_existe(prata):
        return JsonResponse({"error": "País de prata não encontrado"}, status=404)
    if bronze and not pais_existe(bronze):
        return JsonResponse({"error": "País de bronze não encontrado"}, status=404)

# Verificar se o esporte existe
def esporte_existe(id_esporte):
    try: 
        esporte = db_handle.esportes.find_one({"_id": ObjectId(id_esporte)})
    except:
        return False
    return esporte is not None

# Verificar se o país existe
def pais_existe(id_pais):
    try:
        pais = db_handle.paises.find_one({"_id": ObjectId(id_pais)})
    except:
        return False
    return pais is not None

# verificar se o atleta existe
def atleta_existe(id_atleta):
    try:
        atleta = db_handle.atletas.find_one({"_id": ObjectId(id_atleta)})
    except:
        return False
    return atleta is not None

# Função para verificar administrador
def check_admin_permissions(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    token = token.replace("Bearer ", "") if token else None
    if not token:
        return False
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_type = payload["user_type"]
            if user_type != "admin":
                return False
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    return True

# Função para verificar árbitro
def check_refeer_permissions(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    token = token.replace("Bearer ", "") if token else None
    if not token:
        return False
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_type = payload["user_type"]
            if user_type == "admin":
                return True
            if user_type == "juiz":
                return True
            return False
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    return True

# Definição de Encoder JSON
class JSONEncoder(json.JSONEncoder):
    def default (self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Atualizar contador de medalhas
def atualizar_contador_medalhas(data):
    resultado = data.get("resultado")
    esporte_id = data.get("esporte_id")
    esporte = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})["nome"] if esporte_id else None
    coletivo = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})["coletivo"] if esporte_id else None
    atleta_id = data.get("atleta_id") if resultado else None
    atleta = db_handle.atletas.find_one({"_id": ObjectId(atleta_id)})["nome"] if atleta_id else None

    if data["fase"] == "final":
        if not resultado:
            raise ValueError("Resultado é necessário para partidas na fase final")
        
        if "ouro" in resultado:
            ouro_id = resultado["ouro"]
            ouro_nome = db_handle.paises.find_one({"_id": ObjectId(ouro_id)})["nome"]
            update_fields = {
                "$set": {
                    "pais_id": ouro_id,
                    "esporte_id": esporte_id,
                    "esporte": esporte
                },
                "$inc": {"ouro": 1, "total": 1}
            }
            if not coletivo and atleta:
                update_fields["$set"]["atleta"] = atleta
            db_handle.medalhas.update_one({"pais": ouro_nome}, update_fields, upsert=True)

        if "prata" in resultado:
            prata_id = resultado["prata"]
            prata_nome = db_handle.paises.find_one({"_id": ObjectId(prata_id)})["nome"]
            update_fields = {
                "$set": {
                    "pais_id": prata_id,
                    "esporte_id": esporte_id,
                    "esporte": esporte
                },
                "$inc": {"prata": 1, "total": 1}
            }
            if not coletivo and atleta:
                update_fields["$set"]["atleta"] = atleta
            db_handle.medalhas.update_one({"pais": prata_nome}, update_fields, upsert=True)

        if "bronze" in resultado:
            bronze_id = resultado["bronze"]
            bronze_nome = db_handle.paises.find_one({"_id": ObjectId(bronze_id)})["nome"]
            update_fields = {
                "$set": {
                    "pais_id": bronze_id,
                    "esporte_id": esporte_id,
                    "esporte": esporte
                },
                "$inc": {"bronze": 1, "total": 1}
            }
            if not coletivo and atleta:
                update_fields["$set"]["atleta"] = atleta
            db_handle.medalhas.update_one({"pais": bronze_nome}, update_fields, upsert=True)


# Método para criar um esporte
@csrf_exempt
def create_esporte(request):
    # Método de requisição POST
    if request.method == 'POST':
        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        data = json.loads(request.body)
        schema = EsportesSchema()
        errors = schema.validate(data)
         
        # Verificar se já existe um esporte com o mesmo nome
        esporte = db_handle.esportes.find_one({"nome": data["nome"]})
        if esporte:
            return JsonResponse({"error": "400 - Esporte já existe!"}, status=400)
        
        # Se houver erros, retornar os erros 
        if errors:
            return JsonResponse(errors, status=400)
        else: # Se não houver erros, inserir o esporte no banco de dados
            result = db_handle.esportes.insert_one(data)
            response_data = {
                "_id": str(result.inserted_id),
                "nome": data["nome"],
                "coletivo": data["coletivo"],
                "message": "201 - Esporte criado com sucesso!"
            }
            return JsonResponse(response_data, safe=False, status=201)
        
    # Método de requisição GET
    if request.method == "GET":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        esporte_id = request.GET.get('_id')
        if esporte_id:
            esporte = db_handle.esportes.find_one({'_id': ObjectId(esporte_id)})
            if esporte:
                response_data = {
                    "_id": str(esporte["_id"]),
                    "nome": esporte["nome"],
                    "mensagem": "200 - Esporte obtido com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "Esporte não encontrado"}, status=404)
        else:
            esportes = db_handle.esportes.find()
            esportes_list = []
            for esporte in esportes:
                response_data = {
                    "_id": str(esporte["_id"]),
                    "nome": esporte["nome"],
                }
                esportes_list.append(response_data)
            return JsonResponse(esportes_list, safe=False, status=200)
    
    # Método de requisição PUT
    if request.method == "PUT":
        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        schema = EsportesSchema()
        data = schema.load(json.loads(request.body), partial=True)
        esporte_id = request.GET.get("_id")
        if esporte_id:
            db_handle.esportes.update_one({"_id": ObjectId(esporte_id)}, {"$set": data})
            response_data = {
                "_id": esporte_id,
                "message": "200 - Esporte atualizado com sucesso!"
            }
            return JsonResponse(response_data, status=200)
        else:
            return JsonResponse({"error": "400 - Bad Request - Você forneceu o id?"}, status=400)

    # Método de requisição DELETE
    if request.method == "DELETE":
        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        esporte_id = request.GET.get("_id")
        try:
            esporte_id = ObjectId(esporte_id)
        except InvalidId:
            return JsonResponse({"error": "400 - Bad Request - ID informado inválido!"}, status=400)
        if esporte_id:
            esporte = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})
            if esporte:
                db_handle.esportes.delete_one({"_id": ObjectId(esporte_id)})
                response_data = {
                    "_id": str(esporte_id),
                    "message": "200 - Esporte deletado com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "404 - Esporte não encontrado"}, status=404)
        else:
            return JsonResponse({"error": "400 - Bad Request - Você forneceu o id?"}, status=400)
        
    # Se for tentado um método não permitido
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)
    
    
@csrf_exempt
def create_match(request,_id):
    # Agenda uma partida
    if request.method == "POST":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        data = json.loads(request.body)
        try:
            # Verifica se a data é futura
            match_date = datetime.strptime(data["data"], "%Y-%m-%dT%H:%M:%S-03:00")
            # if match_date < datetime.now():
            #     return JsonResponse({"error": "400 - Bad Request - A data deve ser futura!"}, status=400)

            # Busca o nome do esporte
            esporte = db_handle.esportes.find_one({"_id": ObjectId(_id)})
            esporte_nome = esporte["nome"] if esporte else "Esporte não encontrado"


            data["esporte_id"] = _id
            data["esporte_nome"] = esporte_nome
            data["local"] = data["local"]
            data["fase"] = data["fase"].lower()
            data["data"] = data["data"].lower()
            # Inclui os participantes
            data["participantes"] = data["participantes"]
            db_handle.partidas.insert_one(data)


            response_data = {
                "_id": str(data["_id"]),
                "esporte": esporte_nome,
                "participantes": data["participantes"],
                "data": data["data"],
                "message": "201 - Partida agendada com sucesso!"
            }
            return JsonResponse(response_data, status=201)
        except Exception as e:
            return JsonResponse({"error": f"400 - Bad Request - {str(e)}"}, status=400)
        
    # Consultar partidas ou uma partida específica
    if request.method == "GET":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        partida_id = request.GET.get('_id')
        if partida_id:
            partida = db_handle.partidas.find_one({'_id': ObjectId(partida_id)})
            if partida:
                resultado = partida["resultado"] if "resultado" in partida else None
                response_data = {
                    "_id": str(partida["_id"]),
                    "esporte": partida["esporte"],
                    "data": partida["data"],
                    "local": partida["local"],
                    "fase": partida["fase"],
                    "resultado": resultado,
                    "detalhes": partida["detalhes"],
                    "mensagem": "200 - Partida obtida com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "Partida não encontrada"}, status=404)
        else:
            partidas = db_handle.partidas.find()
            partidas_list = []
            for partida in partidas:
                resultado = partida["resultado"] if "resultado" in partida else None
                response_data = {
                    "_id": str(partida["_id"]),
                    "esporte": partida["esporte"],
                    "data": partida["data"],
                    "local": partida["local"],
                    "fase": partida["fase"],
                    "resultado": resultado,
                    "detalhes": partida["detalhes"]
                }
                partidas_list.append(response_data)
            return JsonResponse(partidas_list, safe=False, status=200)
        
    # Atualizar uma partida
    if request.method == "PATCH":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        
        data = json.loads(request.body)
        partida_id = data.get("_id")
        if partida_id:
            # Verifica se a data da partida é passada
            match_date = datetime.strptime(data.get("data", ""), "%Y-%m-%dT%H:%M:%S-03:00")
            if match_date and match_date > datetime.now():
                return JsonResponse({"error": "400 - Bad Request - A partida ainda não ocorreu!"}, status=400)

            detalhes = data.get("detalhes")
            if not detalhes or not isinstance(detalhes, dict):
                return JsonResponse({"error": "400 - Bad Request - Detalhes da partida são necessários e devem ser um objeto"}, status=400)

            # Remove o campo _id dos dados antes de atualizar a partida
            data.pop("_id", None)

            # Atualiza a partida com os novos dados e detalhes da partida
            db_handle.partidas.update_one({"_id": ObjectId(partida_id)}, {"$set": data})

            # Busca a partida atualizada para retornar na resposta
            updated_partida = db_handle.partidas.find_one({"_id": ObjectId(partida_id)})

            # Convert ObjectId to string
            updated_partida["_id"] = str(updated_partida["_id"])

            # Check if 'esporte_id' exists in the dictionary
            esporte_id = _id
            if esporte_id is None:
                return JsonResponse({"error": "Esporte ID not found in the updated match data"}, status=400)

            # Busca o nome do esporte
            esporte = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})
            esporte_nome = esporte["nome"] if esporte else "Esporte não encontrado"

            # Get the phase of the match from the database
            fase = updated_partida.get("fase")
            data["fase"] = fase

            atualizar_contador_medalhas(data)

            response_data = {
                "partida_id": partida_id,
                "esporte_id": esporte_id,
                "esporte_nome": esporte_nome,
                "message": "200 - Partida atualizada com sucesso!",
                "partida": updated_partida  # Retorna a partida atualizada na resposta
            }
            return JsonResponse(response_data, status=200)
        else:
            return JsonResponse({"error": "400 - Bad Request - Você forneceu o id?"}, status=400)
        
    # Deletar uma partida
    if request.method == "DELETE":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        partida_id = request.GET.get("_id")
        try:
            partida_id = ObjectId(partida_id)
        except InvalidId:
            return JsonResponse({"error": "400 - Bad Request - ID informado inválido!"}, status=400)
        if partida_id:
            partida = db_handle.partidas.find_one({"_id": ObjectId(partida_id)})
            if partida:
                db_handle.partidas.delete_one({"_id": ObjectId(partida_id)})
                response_data = {
                    "_id": str(partida_id),
                    "message": "200 - Partida deletada com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "404 - Partida não encontrada"}, status=404)
        else:
            return JsonResponse({"error": "400 - Bad Request - Você forneceu o id?"}, status=400)
    