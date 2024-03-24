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

# Função para decodifiicar token
def decode(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})   

# Método para criar um juiz/usuario/admin
@csrf_exempt
def manage(request):

    # Criação de um juiz/usuario/admin
    if request.method == "POST":
        token = request.META.get("HTTP_AUTHORIZATION")
        token = token.replace("Bearer ", "") if token else None
        if token:
            try:
                payload = decode(token)
                user_type = payload["user_type"]
                if user_type != "admin":
                    return JsonResponse({"error": "403 - Acesso negado"}, status=403)
                username = request.POST.get("username")
                password = request.POST.get("password")
                user_type = request.POST.get("user_type")
                hashed_password = bcrypt.hash(password)
                user_data = {
                    "username": username,
                    "password": hashed_password,
                    "user_type": user_type
                }
                db_handle.users.insert_one(user_data)
                return JsonResponse({"message": "201 - Usuário criado com sucesso!"}, status=201)
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "401 - Token expirado"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "401 - Token inválido"}, status=401)
        else:
            return JsonResponse({"error": "401 - Token não fornecido"}, status=401)
    
    # Listagem de juizes/usuarios/admins
    if request.method == "GET":
        token = request.META.get("HTTP_AUTHORIZATION")
        token = token.replace("Bearer ", "") if token else None
        if token:
            try:
                payload = decode(token)
                user_type = payload["user_type"]
                if user_type != "admin":
                    return JsonResponse({"error": "403 - Acesso negado"}, status=403)
                
                user_id = request.GET.get('_id', None)
                if user_id:
                    try:
                        user = db_handle.users.find_one({"_id": ObjectId(user_id)})
                    except InvalidId:
                        return JsonResponse({"error": "400 - _id inválido"}, status=400)
                    if user:
                        response_data = {
                            "_id": str(user["_id"]),
                            "username": user["username"],
                            "user_type": user["user_type"]
                        }
                        return JsonResponse(response_data, status=200)
                    else:
                        return JsonResponse({"error": "404 - Usuário não encontrado"}, status=404)
                else:
                    users = db_handle.users.find()
                    users_list = []
                    for user in users:
                        response_data = {
                            "_id": str(user["_id"]),
                            "username": user["username"],
                            "user_type": user["user_type"]
                        }
                        users_list.append(response_data)
                    return JsonResponse(users_list, safe=False, status=200)
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "401 - Token expirado"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "401 - Token inválido"}, status=401)
        else:
            return JsonResponse({"error": "401 - Token não fornecido"}, status=401)
    
    # Atualização de usuário
    if request.method == "PATCH":
        token = request.META.get("HTTP_AUTHORIZATION")
        token = token.replace("Bearer ", "") if token else None
        if token:
            try:
                payload = decode(token)
                user_type = payload["user_type"]
                if user_type != "admin":
                    return JsonResponse({"error": "403 - Acesso negado"}, status=403)
                user_id = request.GET.get("_id")
                user = db_handle.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    data = json.loads(request.body.decode('utf-8'))
                    db_handle.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
                    response_data = {
                        "_id": str(user_id),
                        "message": "200 - Usuário atualizado com sucesso!"
                    }
                    return JsonResponse(response_data, status=200)
                else:
                    return JsonResponse({"error": "404 - Usuário não encontrado"}, status=404)
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "401 - Token expirado"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "401 - Token inválido"}, status=401)
        else:
            return JsonResponse({"error": "401 - Token não fornecido"}, status=401)

    


    # Deletar usuário
    if request.method == "DELETE":
        token = request.META.get("HTTP_AUTHORIZATION")
        token = token.replace("Bearer ", "") if token else None
        if token:
            try:
                payload = decode(token)
                user_type = payload["user_type"]
                if user_type != "admin":
                    return JsonResponse({"error": "403 - Acesso negado"}, status=403)
                user_id = request.GET.get("_id")
                try:
                    user_id = ObjectId(user_id)
                except InvalidId:
                    return JsonResponse({"error": "400 - Bad Request - ID informado inválido!"}, status=400)
                user = db_handle.users.find_one({"_id": user_id})
                if user:
                    db_handle.users.delete_one({"_id": user_id})
                    response_data = {
                        "_id": str(user_id),
                        "message": "200 - Usuário deletado com sucesso!"
                    }
                    return JsonResponse(response_data, status=200)
                else:
                    return JsonResponse({"error": "404 - Usuário não encontrado"}, status=404)
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "401 - Token expirado"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "401 - Token inválido"}, status=401)
        else:
            return JsonResponse({"error": "401 - Token não fornecido"}, status=401)


    # Se for tentado um método não permitido
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)
    

# Autenticação por token
@csrf_exempt
def login(request): 
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = db_handle.users.find_one({"username": username})
        if user and pwd_context.verify(password, user["password"]):
            token = jwt.encode({"username": username, "user_type": user["user_type"]}, SECRET_KEY, algorithm="HS256")
            return JsonResponse({"token": token}, status=200)
        else:
            return JsonResponse({"error": "Usuário ou senha inválidos"}, status=401)
    
    # Se for tentado um método não permitido
    else: 
        return JsonResponse({"error": "Método não permitido"}, status=405)
    
    

# Rota protegida para validação de token
@csrf_exempt
def protected_route(request):
    if request.method == "GET":
        token = request.META.get("HTTP_AUTHORIZATION")
        if token:
            try:
                payload = decode(token)
                username = payload["username"]
                return JsonResponse({"message": "Operação realizada com sucesso"})
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "401 - Token expirado"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "401 - Token inválido"}, status=401)
        else:
            return JsonResponse({"error": "401 - Token não fornecido"}, status=401)
        
    # Se for tentado um método não permitido
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)
    
@csrf_exempt
def first_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = "admin"
        hashed_password = bcrypt.hash(password)
        user_data = {
            "username": username,
            "password": hashed_password,
            "user_type": user_type
        }
        db_handle.users.insert_one(user_data)
        return JsonResponse({"message": "201 - Usuário criado com sucesso!"}, status=201)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)
