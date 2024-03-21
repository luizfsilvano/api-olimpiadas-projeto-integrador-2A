from marshmallow import Schema, fields, pre_load

class BaseSchema(Schema):
    @pre_load
    def lower_case(self, data, **kwargs):
        for key in data.keys():
            if isinstance(data[key], str):
                data[key] = data[key].lower()
            return data

class EsportesSchema(BaseSchema):
    nome = fields.Str(required=True)

class PaisSchema(BaseSchema):
    nome = fields.Str(required=True)
    sigla = fields.Str(required=True)
    continente = fields.Str(required=True)

class AtletasSchema(BaseSchema):
    nome = fields.Str(required=True)
    idade = fields.Int(required=True)
    pais = fields.Str(required=True)
    esporte = fields.Str(required=True)

class MedalhasSchema(BaseSchema):
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
