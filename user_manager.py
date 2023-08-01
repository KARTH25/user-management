from flask import Flask, jsonify, request
from dbUtils import db, create_db, seed_db, drop_db, Users
from schemaUtils import ma, user_schema, users_schema, user_schema_with_password
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, decode_token
from flask_mail import Mail, Message
from flask_migrate import Migrate
import random
import os

## Base Dir
baseDir = os.path.abspath(os.path.dirname(__file__))

## Initializing APP
app = Flask(__name__)
## APP config for SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'users.db')
## App config for JWT Secret Key
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') if os.environ.get('JWT_SECRET_KEY') else os.environ['JWT_SECRET_KEY']
## App config for Mail server
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') if os.environ.get('MAIL_SERVER') else os.environ['MAIL_SERVER']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') if os.environ.get('MAIL_USERNAME') else os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') if os.environ.get('MAIL_PASSWORD') else os.environ['MAIL_PASSWORD']
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT') if os.environ.get('MAIL_PORT') else os.environ['MAIL_PORT']
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') if os.environ.get('MAIL_USE_TLS') else os.environ['MAIL_USE_TLS']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL') if os.environ.get('MAIL_USE_SSL') else os.environ['MAIL_USE_SSL']

## Precheck Exception
precheck_exception_routes = ['/healthCheck','/createUser','/login'] 

## Initializing DB 
db.init_app(app)

## Initializing Marshmallow
ma.init_app(app)

## Initialozing JWT
jwt = JWTManager(app)

## Initializing mail
mail = Mail(app)

## Initializing configurations for database upgrade
migrate = Migrate(app, db)

'''
     CLI Commands for Database creation / seed / drop
'''
@app.cli.command('createdb')
def create():
    create_db()

@app.cli.command('seeddb')
def seed():
    seed_db()

@app.cli.command('dropdb')
def drop():
    drop_db()

'''
    APP Routes
'''

## Healthcheck for APIs
@app.route('/healthCheck')
def home():
    print("checking health status")
    return jsonify(status="healthy")

## Route for creating new user
'''
   @route /createUser
   @methods POST
   @requestBody { "first_name" : <str>, "last_name" : <str>, "email" : <str>, "password" : <str> }
'''
@app.route('/createUser', methods=['POST'])
def createUser():
    ## checking if request body is json
    if request.json:
        ## request body info
        requestBody = request.json
        ## fetching userInfo from UserInfo table and filtering by email 
        userInfo = Users.query.filter_by(email=requestBody['email']).first()
        ## If user does not exists creating new user to userInfo table
        if not(userInfo):
            newUser = Users(first_name=requestBody['first_name'], last_name=requestBody['last_name'], email=requestBody['email'], password=requestBody['password'])
            db.session.add(newUser)
            db.session.commit()
            return jsonify(message=(f"User created successfully with email {requestBody['email']}"))
        ## If user email already exists returing error message to user
        else:
            return jsonify(error=(f"User already exists for email {requestBody['email']}")), 403

## Route for Login
'''
   @route /login
   @methods POST
   @requestBody { "email" : <str>, "password" : <str> }
'''
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        ## request body info
        requestBody = request.json
        ## fetching userInfo from userInfo table and filtering by email
        userInfo = Users.query.filter_by(email=requestBody['email'], password=requestBody['password']).first()
        if userInfo:
            access_token = create_access_token(identity={"email" : requestBody['email']})
            return jsonify(message="User login successful", access_token=access_token)
        else:
            return jsonify(error="User login failed bad user credentials"), 401

## Route for generating OTP for retrieving lost password to email
'''
   @route /generateOtp/<email>
   @methods GET
'''
@app.route('/generateOtp/<string:email>', methods=['GET'])
def generateOtp(email : str):
    ## Querying data from userInfo table and filtering based on email
    userInfo = Users.query.filter_by(email=email).first()
    ## If userInfo for the email exists returning response
    if userInfo:
        otp = str(random.randint(100000, 999999))
        userInfo.otp = otp
        db.session.commit()
        msg = Message("Your OTP to reset the password is : " + otp, sender="admin@streetshoppe.com", recipients=[email])
        print("forming message " , msg)
        mail.send(msg)
        print("message sent")
        return jsonify(message="OTP for retrieving your password has been send to : " + email)
    ## If no userInfo exists for the email returning error message
    else:
        return jsonify(error="User for this mail id does not exists")

## Route for retrieving lost password to email
'''
   @route /retrievePassword/<email>
   @methods GET
'''
@app.route('/retrievePassword/<string:email>', methods=['POST'])
def retrievePassword(email : str):
    requestBody = request.json
    ## Querying data from userInfo table and filtering based on email
    userInfo = Users.query.filter_by(email=email, otp=requestBody['otp']).first()
    ## If userInfo for the email exists returning response
    if userInfo:
        msg = Message("your lost password is : " + userInfo.password, sender="admin@streetshoppe.com", recipients=[email])
        mail.send(msg)
        return jsonify(message="your password has been sent to mail : " + email)
    ## If no userInfo exists for the email returning error message
    else:
        return jsonify(error="Invalid credentials")

## Route for get user information based on email
'''
   @route /getUserInfo/<email>
   @methods GET
'''
@app.route('/getUserInfo/<string:email>', methods=['GET'])
@jwt_required()
def getUserInfo(email : str):
    ## Querying data from userInfo table and filtering based on email
    userInfo = Users.query.filter_by(email=email).first()
    ## If userInfo for the email exists returning response
    if userInfo:
        return jsonify(user_schema.dump(userInfo))
    ## If no userInfo exists for the email returning error message
    else:
        return jsonify(error=(f'No User Info available for the user name {email}'))

## Route to update existing user information
'''
   @route /updateUserInfo/<email>
   @method POST
   @requestBody <UserInfo>
'''
@app.route('/updateUserInfo/<string:email>', methods=['PUT'])
@jwt_required()
def updateUserInfo(email:str):
    requestBody = request.json
    ## Querying data from userInfo table and filtering based on email
    userInfo = Users.query.filter_by(email=email).first()
    ## If userInfo for the email exists updating info to table and returning response
    if userInfo:
      updatedUserInfo = (user_schema_with_password.dump(userInfo))
      updatedUserInfo.update(requestBody)
      userInfo.first_name = updatedUserInfo['first_name']
      userInfo.last_name = updatedUserInfo['last_name']
      userInfo.email = updatedUserInfo['email']
      userInfo.password = updatedUserInfo['password']
      db.session.commit()
      return jsonify(message=(f"User Information updated successfully for user {email}"))
    ## If no userInfo exists for the email returning error message
    else:
        return jsonify(error=(f"No User Information found for user {email}")), 404


## Route to delete existing user information
'''
   @route /deleteUserInfo/<email>
   @method DELETE
'''
@app.route('/deleteUserInfo/<string:email>',methods=['DELETE'])
@jwt_required()
def deleteUserInfo(email:str):
    userInfo = Users.query.filter_by(email=email).first()
    if userInfo:
        db.session.delete(userInfo)
        db.session.commit()
        return jsonify(message=(f"User deleted successfully with email {email}")), 200
    else:
        return jsonify(message=(f"User not found with mail {email}")), 400



@app.before_request
def router_precheck():
    if(request.path not in precheck_exception_routes) and (request.headers['Authorization']):
       print("validating token")
       encoded_jwt_token = request.headers['Authorization'].split(' ')[1]
       decoded_jwt_token = decode_token(encoded_token=encoded_jwt_token, csrf_value=None, allow_expired=False)
       if(decoded_jwt_token['sub']['email'] != request.headers['email']):
           return jsonify(error="Invalid Token to access resources")
    else:
        print("valid user")
          

