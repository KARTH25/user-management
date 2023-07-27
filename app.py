'''
    APIs to create new user / modify existing user info / delete user
'''

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dbUtils import db, create_db, seed_db, drop_db, Users
from schemaUtils import ma, user_schema

## Base Dir
baseDir = os.path.abspath(os.path.dirname(__file__))

## APP Configs
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'users.db')

## DB Configs
db.init_app(app)

## Schema configs
ma.init_app(app)

## CLI
@app.cli.command('createdb')
def create():
    create_db()

@app.cli.command('seeddb')
def seed():
    seed_db()

@app.cli.command('dropdb')
def drop():
    drop_db()

## Routes
@app.route('/health')
def health():
    return jsonify(status="healthy"), 200

## Get user Information based on userId
@app.route('/getUserInfo/<string:userName>')
def getUserInfo(userName : str):
    userInfo = Users.query.filter_by(firstName=userName).first()
    if userInfo:
      return jsonify(user_schema.dump(userInfo))
    else:
      return jsonify(error=(f'No UserInfo Available for userName : {userName}'))






