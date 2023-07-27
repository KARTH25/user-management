from flask_marshmallow import Marshmallow

ma = Marshmallow()

## Schema Class for Users
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email')

## Schema accessors for Users
user_schema = UserSchema() ## Schema to serialize single user info
users_schema = UserSchema(many=True) ## Schema to serialize multiple user info

## Schema Class with Password
class UserSchemaWithPassword(ma.Schema):
    class Meta:
        fields = ('id','first_name','last_name','email','password')

## Schema accessors for Users with password
user_schema_with_password = UserSchemaWithPassword()

