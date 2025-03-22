import jwt
import datetime
import os
from bottle import request, run, HTTPResponse, Bottle
from bottle_autodocs import bottle_autodocs


SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

app = Bottle()
app.install(bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description=" API Docs auth bearer"))


def generate_token(user):
    payload = {
        'user': user,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


def auth_bearer(func):
    def wrapper(*args, **kwargs):
        auth_header = request.get_header('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = decode_token(token)
            if isinstance(payload, dict) and 'user' in payload:
                request.user = payload['user']
                return func(*args, **kwargs)
            else:
                return HTTPResponse(
                    status=401, 
                    body={'status': 'error', 'message': payload.get('error', 'Unauthorized')}
                )
        else:
            return HTTPResponse(
                status=401, 
                body={'status': 'error', 'message': 'Missing token'}
            )
    return wrapper


@app.route('/login', method='POST',summary='login route',description='used for loggin user in credentails are username=admin, password=secret')
def login():
    username = request.forms.get('username')
    password = request.forms.get('password')

   
    if username == 'admin' and password == 'secret':
        token = generate_token(username)
        return {'status': 'success', 'token': token}
    else:
        return HTTPResponse(
            status=401, 
            body={'status': 'error', 'message': 'Invalid credentials'}
        )


@app.route('/protected',summary='This is protected route',description='cannot access without logging in ')
@auth_bearer
def protected():
    return {'status': 'success', 'message': f'Hello, {request.user}! You are authorized.'}
@app.route('/protected/<id:int>',summary='This is protected route',description='cannot access without logging in ')
@auth_bearer
def protected(id):
    return {'status': 'success', 'message': f'Hello, {request.user}! You are authorized. and id is {id}'}

@app.route('/public',summary='this is public route',description='no need to log in to access this route')
def public():
    return 'no auth required for this route'


# run the app and go to login and enter the following credentials 
# username = admin
# password = secret
# copy the bearer token and paste it in the bearer field of authorize modal 
# subsequent request will be automatically with the bearer token
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)

