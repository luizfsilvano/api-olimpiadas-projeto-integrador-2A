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
from .views_esportes import check_refeer_permissions, check_admin_permissions

# Conexão com o banco de dados
uri = "mongodb+srv://luizfsilvano:luiz1605@olimpiadas.f0rs1ml.mongodb.net/?retryWrites=true&w=majority&appName=Olimpiadas"
db_handle, client = get_db_handle('Olimpiadas', uri)

load_dotenv('../../secret_key.env')
# Definição de Chave Secreta
SECRET_KEY = str(os.getenv("SECRET_KEY"))

# Definição de Logger
logger = logging.getLogger(__name__)

# Definição de Contexto de Senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Definição de Encoder JSON
class JSONEncoder(json.JSONEncoder):
    def default (self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# Método para criar um Pais
@csrf_exempt
def create_pais(request):
    # Criar um pais
    if request.method == "POST":
        logger.info(SECRET_KEY)


        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        data = json.loads(request.body)
        schema = PaisSchema()
        errors = schema.validate(data)

        # Verificar se o país já existe
        pais = db_handle.paises.find_one({"nome": data["nome"]})
        if pais:
            return JsonResponse({"error": "409 - País já existe"}, status=409)
        
        # Verificar se há erros
        if errors:
            return JsonResponse(errors, status=400)
        else: # Inserir o país
            result = db_handle.paises.insert_one(data)
            response_data = {
                "_id": str(result.inserted_id),
                "message": "201 - País criado com sucesso!"
            }
            return JsonResponse(response_data, safe=False, status=201)
        
    # Obter todos os países ou um país específico
    if request.method == "GET":
        if not check_refeer_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        pais_id = request.GET.get('_id')
        if pais_id:
            pais = db_handle.paises.find_one({'_id': ObjectId(pais_id)})
            if pais:
                response_data = {
                    "_id": str(pais["_id"]),
                    "nome": pais["nome"],
                    "sigla": pais["sigla"],
                    "continente": pais["continente"],
                    "mensagem": "200 - País obtido com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "País não encontrado"}, status=404)
        else:
            paises = db_handle.paises.find()
            paises_list = []
            for pais in paises:
                response_data = {
                    "_id": str(pais["_id"]),
                    "nome": pais["nome"],
                    "sigla": pais["sigla"],
                    "continente": pais["continente"]
                }
                paises_list.append(response_data)
            return JsonResponse(paises_list, safe=False, status=200)
    
    # Atualizar um país
    if request.method == "PATCH":
        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        schema = PaisSchema()
        data = schema.load(json.loads(request.body), partial=True)
        pais_id = request.GET.get("_id")
        if pais_id:
            db_handle.paises.update_one({"_id": ObjectId(pais_id)}, {"$set": data})
            response_data = {
                "_id": pais_id,
                "message": "200 - País atualizado com sucesso!"
            }
            return JsonResponse(response_data, status=200)
        else:
            return JsonResponse({"error": "400 - Bad Request - Você forneceu o id?"}, status=400)
        
    # Deletar um país
    if request.method == "DELETE":
        if not check_admin_permissions(request):
            return JsonResponse({"error": "403 - Acesso negado"}, status=403)
        pais_id = request.GET.get("_id")
        try:
            pais_id = ObjectId(pais_id)
        except InvalidId:
            return JsonResponse({"error": "400 - Bad Request - ID informado inválido!"}, status=400)
        if pais_id:
            pais = db_handle.paises.find_one({"_id": ObjectId(pais_id)})
            if pais:
                db_handle.paises.delete_one({"_id": ObjectId(pais_id)})
                response_data = {
                    "_id": str(pais_id),
                    "message": "200 - País deletado com sucesso!"
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": "404 - País não encontrado"}, status=404)
        else:
            return JsonResponse({"error": "400 - Bad Request - Você forneceu o id?"}, status=400)
        
    # Se for tentado um método não permitido
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)