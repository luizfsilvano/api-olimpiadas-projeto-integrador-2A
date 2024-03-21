from utils import get_db_handle
from ..schemas import *
import json, jwt, os, logging
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from marshmallow import ValidationError
from dotenv import load_dotenv
from passlib.hash import bcrypt
from passlib.context import CryptContext

# Conexão com o banco de dados
uri = "mongodb+srv://luizfsilvano:luiz1605@olimpiadas.f0rs1ml.mongodb.net/?retryWrites=true&w=majority&appName=Olimpiadas"
db_handle, client = get_db_handle('Olimpiadas', uri)

load_dotenv('../secret_key.env')
# Definição de Chave Secreta
SECRET_KEY = os.getenv("SECRET_KEY")

# Definição de Logger
logger = logging.getLogger(__name__)

# Definição de Contexto de Senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Definição de Encoder JSON
class JSONEncoder(json.JSONEncoder):
    def default (self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

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
        if errors:
            return JsonResponse(errors, status=400)
        else:
            result = db_handle.esportes.insert_one(data)
            response_data = {
                "_id": str(result.inserted_id),
                "message": "201 - Esporte criado com sucesso!"
            }
            return JsonResponse(response_data, safe=False, status=201)
        
    # Método de requisição GET
    if request.method == "GET":
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
        data = json.loads(request.body)
        esporte_id = request.GET.get("_id")
        if esporte_id:
            schema = EsportesSchema()
            try:
                data = schema.load(data)
            except ValidationError as err:
                return JsonResponse(err.messages, status=400)
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