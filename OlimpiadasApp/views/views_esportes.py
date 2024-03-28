from utils import get_db_handle
from ..schemas import *
import json, jwt, logging, traceback, sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from passlib.context import CryptContext
from Olimpiadas.settings import db_name, uri, SECRET_KEY

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
    resultado = data["resultado"] if "resultado" in data else None
    esporte_id = data["esporte_id"] if "esporte_id" in data else None
    esporte = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})["nome"] if esporte_id else None
    coletivo = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})["coletivo"] if esporte_id else None
    atleta_id = data["atleta_id"] if "atleta_id" in data else None
    atleta = db_handle.atletas.find_one({"_id": ObjectId(atleta_id)})["nome"] if atleta_id else None

    if data["fase"] == "final":
        if resultado is None:
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
    # Criar uma partida
    try:
        if request.method == "POST":
            if not check_refeer_permissions(request):
                return JsonResponse({"error": "403 - Acesso negado"}, status=403)
            
            # Verificar se o esporte existe
            if not esporte_existe(_id):
                return JsonResponse({"error": "404 - Esporte não encontrado"}, status=404)

            data = json.loads(request.body)
            esporte_id = _id
            esporte = db_handle.esportes.find_one({"_id": ObjectId(esporte_id)})
            esporte_nome = esporte["nome"]
            esporte_coletivo = esporte["coletivo"]
            data["esporte_id"] = esporte_id # Adicionar o id do esporte
            data["esporte"] = esporte_nome # Adicionar o nome do esporte
            
            schema = PartidasSchema()
            errors = schema.validate(data)
            if errors:
                return JsonResponse(errors, status=400)
            else:
                if data["fase"] == "final":
                    resultado = data["resultado"] if "resultado" in data else None
                    if not esporte_coletivo:
                        if not all(key in resultado for key in ["atleta_id_ouro", "atleta_id_prata", "atleta_id_bronze", "ouro", "prata", "bronze"]):
                            return JsonResponse({"error": "Os IDs dos atletas e os países vencedores são necessários para esportes individuais na fase final"}, status=400)
                    atleta_id_ouro = resultado["atleta_id_ouro"] if "ouro" in resultado else None
                    atleta_id_prata = resultado["atleta_id_prata"] if "prata" in resultado else None
                    atleta_id_bronze = resultado["atleta_id_bronze"] if "bronze" in resultado else None
                    ouro = resultado["ouro"] if "ouro" in resultado else None
                    prata = resultado["prata"] if "prata" in resultado else None
                    bronze = resultado["bronze"] if "bronze" in resultado else None
                    
                    # Verificar se os atletas existem
                    verifica(atleta_id_ouro, atleta_id_prata, atleta_id_bronze, ouro, prata, bronze)
                else:
                    if "resultado" in data:
                        return JsonResponse({"error": "Resultado não pode ser definido fora da fase final"}, status=400)

                result = db_handle.partidas.insert_one(data)
                response_data = {
                    "_id": str(result.inserted_id),
                    "esporte_id": esporte_id,
                    "esporte": esporte_nome,
                    "data": data["data"],
                    "local": data["local"],
                    "detalhes": data["detalhes"],
                    "fase": data["fase"],
                    "resultado": resultado if data["fase"] == "final" else None,
                    "message": "201 - Partida criada com sucesso!"
                }
                if data["fase"] == "final":
                    try:
                        atualizar_contador_medalhas(data)
                    except ValueError as e:
                        return JsonResponse({"error": str(e)}, status=400)
                return JsonResponse(response_data, safe=False, status=201)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        traceback.print_exc()
        return JsonResponse({"error": "Erro interno do servidor"}, status=500)
        
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
        schema = PartidasSchema()
        data = schema.load(json.loads(request.body), partial=True)
        partida_id = request.GET.get("_id")
        if partida_id:
            db_handle.partidas.update_one({"_id": ObjectId(partida_id)}, {"$set": data})
            response_data = {
                "_id": partida_id,
                "message": "200 - Partida atualizada com sucesso!"
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
    