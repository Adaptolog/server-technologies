from marshmallow import Schema, fields, validate

class AccountSchema(Schema):
    """Schema for account validation."""
    class Meta:
        unknown = 'exclude'
    
    id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    balance = fields.Float(dump_only=True)
    # Видалено: created_at та updated_at

class AccountQuerySchema(Schema):
    """Schema for account query parameters."""
    user_id = fields.Str()

class IncomeSchema(Schema):
    """Schema for income validation."""
    class Meta:
        unknown = 'exclude'
    
    id = fields.Str(dump_only=True)
    account_id = fields.Str(dump_only=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(validate=validate.Length(max=200))
    # Видалено: created_at

class IncomeQuerySchema(Schema):
    """Schema for income query parameters."""
    start_date = fields.DateTime()
    end_date = fields.DateTime()