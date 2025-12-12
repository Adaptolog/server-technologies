from marshmallow import Schema, fields, validate, validates_schema
from marshmallow.exceptions import ValidationError

class UserSchema(Schema):
    """Schema for user validation."""
    class Meta:
        unknown = 'exclude'  # Ігнорувати невідомі поля
    
    id = fields.Str(dump_only=True)
    name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, 
        validate=validate.Length(min=6),
        load_only=True
    )
    confirm_password = fields.Str(
        required=True,
        load_only=True
    )
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validate that password and confirm_password match."""
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise ValidationError('Passwords do not match', 'confirm_password')

class UserQuerySchema(Schema):
    """Schema for user query parameters."""
    name = fields.Str(validate=validate.Length(max=100))
    email = fields.Email()

class LoginSchema(Schema):
    """Schema for user login."""
    class Meta:
        unknown = 'exclude'
    
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)