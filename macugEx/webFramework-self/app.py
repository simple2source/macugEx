import jwt
import logging
import datetime
from m import Router, Application, Filter
from m.utils import jsonfy
from m.security import AuthenticationProvider, AuthenticationFilter, Require
from webob import Response
from functools import wraps
from webob.exc import HTTPUnauthorized

KEY = 'dsjfhjkaSFHJKHSA'

logging.basicConfig(level=logging.INFO)


class Principal:
    def __init__(self, name, roles):
        self.name = name
        self.roles = roles


class AccessLogFilter(Filter):
    def __init__(self):
        pass

    def before_request(self, ctx, request):
        request.start = datetime.datetime.now()
        return request

    def after_request(self, ctx, request, response):
        now = datetime.datetime.now()
        time = (now - request.start).total_seconds()
        logging.info(str(time))
        return response


class JWTAuthenticationProvider(AuthenticationProvider):
    def __init__(self, request):
        super().__init__(request)
        token = request.headers.get('X-Authorization-Token')
        if token is None:
            raise HTTPUnauthorized()
        try:
            decoded = jwt.decode(token.encode(), KEY, ['HS512'])
            user = decoded.get('user')
            if user is None:
                raise HTTPUnauthorized()
            self.__principal = Principal('comyn', ['admin'])
        except Exception as e:
            logging.error(e)
            raise HTTPUnauthorized()

    @property
    def principal(self):
        return self.__principal


router = Router(filters=[AccessLogFilter(),
                         AuthenticationFilter(JWTAuthenticationProvider, ['/login'])])


@router.before_request
def audit(ctx, request):
    logging.info(request.path)
    return request


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
#@Require(permissions=['admin', 'root'])
def main(ctx, request):
    with Require(['root'], request):
        return Response('hello world')


@router.route('/login', methods=['POST'])
def login(ctx, request):
    payload = request.json()
    if payload.get('username') == 'comyn' and payload.get('password') == 'pass':
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        token = jwt.encode({'user': 'comyn', 'exp': exp}, KEY, 'HS512').decode()
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
