from marshmallow import Schema, fields, validate

class ExpenseSchema(Schema):
    """Schema for expense validation."""
    class Meta:
        unknown = 'exclude'
    
    id = fields.Str(dump_only=True)
    user_id = fields.Str(required=True)
    category_id = fields.Str(required=True)
    account_id = fields.Str(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(validate=validate.Length(max=200))
    # Видалено: created_at

class ExpenseQuerySchema(Schema):
    """Schema for expense query parameters."""
    user_id = fields.Str()
    category_id = fields.Str()
    account_id = fields.Str()
    start_date = fields.DateTime()
    end_date = fields.DateTime()