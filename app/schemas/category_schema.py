from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    """Schema for category validation."""
    class Meta:
        unknown = 'exclude'
    
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    is_global = fields.Boolean(load_default=True)
    user_id = fields.Str(allow_none=True)

class CategoryQuerySchema(Schema):
    """Schema for category query parameters."""
    name = fields.Str(validate=validate.Length(max=50))
    is_global = fields.Boolean()
    user_id = fields.Str()