from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """Schema for user validation."""
    class Meta:
        unknown = 'exclude'  # Ігнорувати невідомі поля
    
    id = fields.Str(dump_only=True)
    name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100)
    )

class UserQuerySchema(Schema):
    """Schema for user query parameters."""
    name = fields.Str(validate=validate.Length(max=100))