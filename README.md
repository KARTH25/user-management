# user-management

Repository holds the user management related APIs

# Technologies used

  1. Python Flask for exposing APIs

  2. Docker for Deployment

  3. JWT for authentication and access management

  4. Sqlite DB for data management

# Deals with

  1. Creating a new user

  2. Logining in a existing user to allow access for other resources

  3. Retrieve forgotten password based on email authentication

  4. Get logged in user information

  5. Update information of logged in user

  6. Delete existing user

# Working with application

## Running application as a docker

  1. Build a docker image using command -> docker image build <image_name> .

  2. Using built docker image run a container using command -> docker run -it -d -p 5000:5000 <image_name>

  3. Access the routes of the application using http://localhost:5000 check /healcheck for application health check

## Running application as flask app 

  1. Install required dependencies using requirements.txt file using command -> pip install -r requirements.txt (or) pip3 install -r requirements.txt

  2. All env variables required to start flask app is scripted in file start-app.sh

  3. Start the flask app using the command -> sh start-app.sh

  4. Access the routes of the application using http://localhost:5000 check /healcheck for application health check
