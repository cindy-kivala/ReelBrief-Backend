"""
User Schema
Owner: Ryan
Description: Marshmallow schema for serializing and validating User data.
"""

from app.extensions import ma
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True  # Deserialize into model instances
        include_fk = True     # Include foreign keys if present
        ordered = True
        exclude = ("password_hash", "verification_token", "reset_token", "reset_token_expires")

    # Optional: custom field formatting (example)
    # created_at = ma.Method("format_created_at")

    # def format_created_at(self, obj):
    #     return obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else None


# Single and multiple-user schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
