from marshmallow import Schema, fields

class ErrorSchema(Schema):
    """Schema for error responses."""
    error = fields.Str()
    message = fields.Str()
    errors = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()), allow_none=True)