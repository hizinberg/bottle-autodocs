from bottle import Bottle, request, HTTPError, run
import functools
from bottle_autodocs import bottle_autodocs
app = Bottle()
app.install(bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description=" API Docs basic auth"))
USERS = {
    'admin': 'secret',
    'user': 'password'
}


def is_authenticated_user(user, password):
    return USERS.get(user) == password


def auth_basic(check, realm="private", text="Access denied"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a, **ka):
            user, password = request.auth or (None, None)
            if user is None or not check(user, password):
                err = HTTPError(401, text)
                err.add_header('WWW-Authenticate', 'Basic realm="%s"' % realm)
                return err
            return func(*a, **ka)
        return wrapper
    return decorator


@app.route('/protected',summary='This is protected route',description='cannot access without logging in ')
@auth_basic(is_authenticated_user)
def protected():
    return {'status': 'success', 'message': f'Hello, {request.auth[0]}! You are authenticated.'}


# run the app and click on authorize and enter the following credentials 
# username = admin
# password = secret
# subsequent request will be automatically called with the credentials 
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
