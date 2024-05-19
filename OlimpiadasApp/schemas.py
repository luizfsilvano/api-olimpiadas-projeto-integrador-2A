from marshmallow import Schema, fields, pre_load, validate
from marshmallow_enum import EnumField
import enum

class FaseEnum(enum.Enum):
    OUTROS = "outros"
    CLASSIFICACAO = "classificacao"
    OITAVAS = "oitavas"
    QUARTAS = "quartas"
    SEMI = "semi"
    FINAL = "final"

class BaseSchema(Schema):
    @pre_load
    def lower_case(self, data, **kwargs):
        for key in data.keys():
            if isinstance(data[key], str):
                data[key] = data[key].lower()
        return data

class EsportesSchema(BaseSchema):
    nome = fields.Str(required=True)
    coletivo = fields.Bool(required=True)

class PaisSchema(BaseSchema):
    nome = fields.Str(required=True)
    sigla = fields.Str(required=True)
    continente = fields.Str(required=True)

class AtletasSchema(BaseSchema):
    pais_id = fields.Str(required=True)
    pais = fields.Str(required=True)
    esporte_id = fields.Str(required=True)
    esporte = fields.Str(required=True)
    nome = fields.Str(required=True)
    idade = fields.Int(required=True)

class MedalhasSchema(BaseSchema):
    pais_id = fields.Str(required=True)
    pais = fields.Str(required=True)
    esporte = fields.Str()
    atleta = fields.Str()
    ouro = fields.Int(default=0, missing=0)
    prata = fields.Int(default=0, missing=0)
    bronze = fields.Int(default=0, missing=0)
    total = fields.Int(default=0, missing=0)

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    user_type = fields.Str(required=True)

class ResultadoSchema(BaseSchema):
    atleta_id_ouro = fields.Str()
    atleta_id_prata = fields.Str()
    atleta_id_bronze = fields.Str()
    ouro = fields.Str(required=True)
    prata = fields.Str(required=True)
    bronze = fields.Str(required=True)

class PartidasSchema(BaseSchema):
    esporte_id = fields.Str(required=True)
    esporte = fields.Str(required=True)
    data = fields.Str(required=True)
    local = fields.Str(required=True)
    fase = EnumField(FaseEnum, by_value=True, required=True)
    resultado = fields.Nested(ResultadoSchema, required=False)
    detalhes = fields.Dict(required=True)

