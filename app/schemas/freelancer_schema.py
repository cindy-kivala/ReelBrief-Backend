# app/schemas/freelancer_schema.py
from marshmallow import Schema, fields

class FreelancerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    bio = fields.Str()
    cv_url = fields.Str()
    portfolio_url = fields.Str()
    years_experience = fields.Int()
    hourly_rate = fields.Float()
    application_status = fields.Str()
    rejection_reason = fields.Str()
    created_at = fields.DateTime()
