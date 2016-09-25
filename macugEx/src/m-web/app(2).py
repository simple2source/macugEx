import jwt
import json
import datetime
from m import Router, Application
from m.utils import jsonfy
from webob import Response
from functools import wraps
from webob.exc import HTTPUnauthorized

__KEY = 'dsjfhjkaSFHJKHSA'

router = Router()


def authenticated(fn):
    @wraps(fn)
    def wrap(ctx, request):
        token = request.headers.get('X-Authorization-Token')
        if token is None:
            raise HTTPUnauthorized()
        try:
            decoded = jwt.decode(token.encode(), __KEY, ['HS512'])
            user = decoded.get('user')
            if user is None:
                raise HTTPUnauthorized()
            request.user = user
            return fn(ctx, request)
        except Exception:
            raise HTTPUnauthorized()
    return wrap


@router.route('/')
@authenticated
def main(ctx, request):
    return Response('hello world')


@router.route('/login', methods=['POST'])
def login(ctx, request):
    payload = request.json()
    if payload.get('username') == 'comyn' and payload.get('password') == 'pass':
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        token = jwt.encode({'user': 'comyn', 'exp': exp}, __KEY, 'HS512').decode()
        return jsonfy(code=200, token=token)
    return jsonfy(code=401, message='username or password not match')

app = Application([router])


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3001, app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
