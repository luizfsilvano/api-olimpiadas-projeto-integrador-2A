from utils import get_db_handle
from ..schemas import *
import json, jwt, os, logging, re
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from marshmallow import ValidationError
from dotenv import load_dotenv
from passlib.hash import bcrypt
from passlib.context import CryptContext
from .views_esportes import esporte_existe, pais_existe, check_admin_permissions, check_refeer_permissions

# Conexão com o banco de dados
uri = "mongodb+srv://luizfsilvano:luiz1605@olimpiadas.f0rs1ml.mongodb.net/?retryWrites=true&w=majority&appName=Olimpiadas"
db_handle, client = get_db_handle('Olimpiadas', uri)

load_dotenv('../secret_key.env')
# Definição de Chave Secreta
SECRET_KEY = str(os.getenv("SECRET_KEY"))

# Definição de Logger
logger = logging.getLogger(__name__)

# Definição de Contexto de Senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JSONEncoder(json.JSONEncoder):
    def default (self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Função para verificar se o nome é válido
def is_valid_name(name):
    return bool(re.match(r"^[a-zA-Z\s]*$", name))


# Método para criar um atleta
@csrf_exempt
def create_atleta(request):
    # Criar um atleta
    if request.method == "POST":
        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        data = json.loads(request.body)
        nome = data.get('nome')
        if not is_valid_name(nome):
            return JsonResponse({"error": "400 - Nome inválido"}, status=400)
        pais_id = data.get("pais")
        esporte_id = data.get("esporte")
        schema = AtletasSchema()
        errors = schema.validate(data)
        
        # Verificar se o país existe
        if not pais_existe(pais_id):
            return JsonResponse({"error": "404 - País não encontrado"}, status=404)

        # Verificar se o esporte existe
        if not esporte_existe(esporte_id):
            return JsonResponse({"error": "404 - Esporte não encontrado"}, status=404)
        
        # Verificar se o atleta já existe
        atleta = db_handle.atletas.find_one({"nome": data["nome"]})
        
        if atleta:
            return JsonResponse({"error": "409 - Atleta já existe"}, status=409)
        
        # Verificar se há erros
        if errors:
            return JsonResponse(errors, status=400)
        else:
            # Inserir o atleta
            result = db_handle.atletas.insert_one(data)
            response_data = {
                "_id": str(result.inserted_id),
                "message": "201 - Atleta criado com sucesso!"
            }
            return JsonResponse(response_data, safe=False, status=201)
    
    # Obter todos os atletas ou um atleta específico
    if request.method == "GET":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        atleta_id = request.GET.get('_id')
        pais_id = request.GET.get('pais')
        if atleta_id:
            atleta = db_handle.atletas.find_one({'_id': ObjectId(atleta_id)})
            if atleta:
                response_data = {
                    "_id": str(atleta["_id"]),
                    "nome": atleta["nome"],
                    "idade": atleta["idade"],
                    "pais": atleta["pais"],
                    "esporte": atleta["esporte"],
                    "mensagem": "200 - Atleta obtido com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "Atleta não encontrado"}, status=404)
        elif pais_id:
            try:
                pais_id = data.get("pais")
            except:
                return JsonResponse({"error": "Invalid pais_id"}, status=400)
            atletas = db_handle.atletas.find({'pais': pais_id})
            atletas_list = []
            for atleta in atletas:
                response_data = {
                    "_id": str(atleta["_id"]),
                    "nome": atleta["nome"],
                    "idade": atleta["idade"],
                    "pais": atleta["pais"],
                    "esporte": atleta["esporte"],
                    "mensagem": "atletas por pais obtidos com sucesso!"
                }
                atletas_list.append(response_data)
            return JsonResponse(atletas_list, safe=False, status=200)
        else:
            atletas = db_handle.atletas.find()
            atletas_list = []
            for atleta in atletas:
                response_data = {
                    "_id": str(atleta["_id"]),
                    "nome": atleta["nome"],
                    "idade": atleta["idade"],
                    "pais": atleta["pais"],
                    "esporte": atleta["esporte"]
                }
                atletas_list.append(response_data)
            return JsonResponse(atletas_list, safe=False, status=200)
        
    if request.method == "PATCH":
        if check_admin_permissions != True:
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        schema = AtletasSchema()
        data = schema.load(json.loads(request.body), partial=True)
        atleta_id = data.get("_id")
        atleta = db_handle.atletas.find_one({"_id": ObjectId(atleta_id)})

        # Verificar se o atleta existe
        if not atleta:
            return JsonResponse({"error": "404 - Atleta não encontrado"}, status=404)
        
        # Verificar se o atleta atualizado já existe
        existing_atleta = db_handle.atletas.find_one({"nome": data["nome"]})
        if existing_atleta and existing_atleta["_id"] != atleta_id:
            return JsonResponse({"error": "409 - Atleta já existe"}, status=409)
        
        # Verificar se há erros
        schema = AtletasSchema()
        errors = schema.validate(data)
        if errors:
            return JsonResponse(errors, status=400)
        
        # Atualizar o atleta
        else:
            db_handle.atletas.update_one({"_id": ObjectId(atleta_id)}, {"$set": data})
            return JsonResponse({"message": "200 - Atleta atualizado com sucesso!"}, status=200)
        

    if request.method == "DELETE":
        if check_admin_permissions != True:
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        
        atleta_id = request.GET.get('_id')
        atleta = db_handle.atletas.find_one({"_id": ObjectId(atleta_id)})

        # Verificar se o atleta existe
        if not atleta:
            return JsonResponse({"error": "404 - Atleta não encontrado"}, status=404)
        db_handle.atletas.delete_one({"_id": ObjectId(atleta_id)})
        return JsonResponse({"message": "200 - Atleta deletado com sucesso!"}, status=200)
    
    return JsonResponse({"error": "400 - Método não permitido"}, status=400)    
