from ..schemas import *
import json, jwt, traceback, sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from bson.errors import InvalidId
from passlib.hash import bcrypt
from .views_esportes import *


# Função para verificar se já existe um usuário com o mesmo username
def check_username(username):
    print(f"Checking username: {username}")
    existing_user = db_handle.users.find_one({"username": username})
    if existing_user:
        print(f"Username {username} already exists")
        return True
    else:
        print(f"Username {username} does not exist")
        return False

# Função para decodifiicar token
def decode(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])   

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

                try:
                    if check_username(username):
                        return JsonResponse({"error": "409 - Usuário já existe"}, status=409)
                except Exception as e:
                    return JsonResponse({"error": "Erro interno do servidor"}, status=500)

                hashed_password = pwd_context.hash(password)
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
    try:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = db_handle.users.find_one({"username": username})
            if user and pwd_context.verify(password, user["password"]):
                token = jwt.encode({"username": username, "user_type": user["user_type"]}, SECRET_KEY, algorithm="HS256").decode('utf-8')
                return JsonResponse({"token": token}, status=200)
            else:
                return JsonResponse({"error": "Usuário ou senha inválidos"}, status=401)
        
        # Se for tentado um método não permitido
        else: 
            return JsonResponse({"error": "Método não permitido"}, status=405)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        traceback.print_exc()
        return JsonResponse({"error": "Erro interno do servidor"}, status=500)
    

# Rota protegida para validação de token
@csrf_exempt
def protected_route(request):
    if request.method == "GET":
        token = request.META.get("HTTP_AUTHORIZATION")
        token = token.replace("Bearer ", "") if token else None
        if token:
            try:
                payload = decode(token.replace("Bearer ", ""))
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
    
# Método para criar o primeiro admin
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


def hello(request):
    return JsonResponse({"message": "Hello, World!"}, status=200)  