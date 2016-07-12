import requests
import string
import logging
import datetime
import traceback
from os import path as os_path
from tornado.web import RequestHandler
from tornado.web import HTTPError
from tornado.options import options
from kazoo.exceptions import NodeExistsError
from .mixins import RestMixin
from .exceptions import SchemaError


class SchemaHandler(RestMixin, RequestHandler):
    @staticmethod
    def list_all_schema():
        r = requests.get('{0}/_stats'.format(options.es))
        if r.status_code >= 300:
            raise SchemaError('list all schema error {0}'.format(r.text))
        return r.json().get('indices', {}).keys()

    @staticmethod
    def is_schema_exist(name):
        resp = requests.head('{0}/{1}'.format(options.es, name))
        return resp.status_code == 200

    @staticmethod
    def is_same_field(o, n):
        return o == n

    @staticmethod
    def get_schema(name):
        resp = requests.get('{0}/{1}/schema/{2}'.format(options.es, name, name))
        return resp.json().get('_source')

    @staticmethod
    def check_conflict(schema):
        origin = SchemaHandler.get_schema(schema['name'])
        if origin['pk'] != schema['pk']:
            raise SchemaError('pk can not modify')
        if not {field['name'] for field in schema['fields']}.issuperset(
                {field['name'] for field in origin.get('fields', [])}):
            raise SchemaError('conflict check fail')
        fields = {field['name']: field for field in schema['fields']}
        for field in origin.get('fields', []):
            if not SchemaHandler.is_same_field(field, fields[field['name']]):
                raise SchemaError('{0} not same origin'.format(field['name']))
        if schema['pk'] != origin['pk']:
            raise SchemaError('pk not same origin')

    @staticmethod
    def validate_name(name):
        if len(name) <= 0:
            raise SchemaError('name is require')
        charts = set(string.ascii_letters)
        charts.update(string.digits)
        if not set(name).issubset(charts):
            raise SchemaError('name error')

    @staticmethod
    def validate_field(field):
        SchemaHandler.validate_name(field['name'])
        if field['name'] in ('name', 'pk', 'version', 'timestamp', 'fields'):
            raise SchemaError('field name error')
        for key in ('require', 'multi', 'unique'):
            if field.get(key) is None or not isinstance(field.get(key), bool):
                field[key] = False
                logging.warning('field {0} {1} is nut set or is not a bool, set False'.format(field['name'], key))
        if field['type'] not in ('string', 'long', 'double', 'date', 'ip'):
            raise SchemaError('type error')
        if field.get('ref'):
            schema_name, field_name = field.get('ref').split('::')
            if not SchemaHandler.is_schema_exist(schema_name):
                raise SchemaError('reference schema {0} is not exist'.format(schema_name))
            schema = SchemaHandler.get_schema(schema_name)
            if field_name not in schema['fields']:
                raise SchemaError('reference field {0} is not exist'.format(field_name))
        return field

    @staticmethod
    def validate_schema(schema):
        SchemaHandler.validate_name(schema['name'])
        if len({field['name'] for field in schema['fields']}) != len(schema['fields']):
            raise SchemaError('field name must be unique')
        if SchemaHandler.is_schema_exist(schema['name']):
            SchemaHandler.check_conflict(schema)
        for field in schema['fields']:
            SchemaHandler.validate_field(field)
        for field in schema['fields']:
            if field['name'] == schema['pk']:
                if not (field['require'] is True and
                                field['unique'] is True and
                                field['multi'] is False and
                                field['type'] == string):
                    raise SchemaError('pk error')
                break
        else:
            raise  SchemaError('pk is not a field')

    @staticmethod
    def make_mapping(schema):
        properties = {}
        for field in schema['fields']:
            if field['type'] == 'string':
                properties[field['name']] = {
                    'type': 'string',
                    'index': 'not_analyzed'
                }
            else:
                properties[field['name']] = {
                    'type': field['type']
                }
        return {'properties': properties}

    @staticmethod
    def create_index(name):
        settings = {
            'index': {
                'number_of_shards': options.shards,
                'number_of_replicas': options.replicas
            }
        }
        mapping = {
            'properties': {
                'name': {'type': 'string', 'index': 'not_analyzed'},
                'pk': {'type': 'string', 'index': 'not_analyzed'},
                'version': {'type': 'long'},
                'timestamp': {'type': 'date'},
                'fields': {
                    'type': 'nested',
                    'properties': {
                        'name': {'type': 'string', 'index': 'not_analyzed'},
                        'type': {'type': 'string', 'index': 'not_analyzed'},
                        'require': {'type': 'boolean'},
                        'multi': {'type': 'boolean'},
                        'unique': {'type': 'boolean'},
                        'ref': {'type': 'string', 'index': 'not_analyzed'}
                    }
                }
            }
        }

        r = requests.put('{0}/{1}'.format(options.es, name), json={
            'settings': settings,
            'mappings': {
                'schema': mapping,
                'schema_history': mapping
            }
        })
        if r.status_code >= 300:
            raise HTTPError(status_code=500, reason='create index {0} error'.format(name))

    def post(self, *args, **kwargs):
        payload = self.get_payload()
        node = None
        try:
            node = os_path.join(options.root, payload['name'])
            self.application.zk.create(node)
            SchemaHandler.validate_schema(payload)
            payload['version'] = 0
            if SchemaHandler.is_schema_exist(payload['name']):
                payload['version'] = SchemaHandler.get_schema(payload['name'])['version'] + 1
            else:
                SchemaHandler.create_index(payload['name'])
            payload['timestamp'] = int(datetime.datetime.now().timestamp() * 1000)
            mapping = SchemaHandler.make_mapping(payload)
            r = requests.put('{0}/{1}/_mapping/entity_history'.format(options.es, payload['name']), json=mapping)
            if r.status_code >= 300:
                logging.error(r.text)
                raise HTTPError(status_code=500, reason='put mapping error, response code is {0}'.format(r.status_code))
            r = requests.put('{0}/{1}/_mapping/entity'.format(options.es, payload['name']), json=mapping)
            if r.status_code >= 300:
                logging.error(r.text)
                raise HTTPError(status_code=500, reason='put mapping error, response code is {0}'.format(r.status_code))
            r = requests.post('{0}/{1}/schema_history'.format(options.es, payload['name']), json=payload)
            if r.status_code >= 300:
                logging.error(r.text)
                raise HTTPError(status_code=500,
                                reason='put schema history error, response code is {0}'.format(r.status_code))
            r = requests.put('{0}/{1}/schema/{2}'.format(options.es, payload['name'], payload['name']), json=payload)
            if r.status_code >= 300:
                logging.error(r.text)
                raise HTTPError(status_code=500,
                                reason='put schema error, response code is {0}'.format(r.status_code))
            self.jsonify(code=200, schema=SchemaHandler.get_schema(payload['name']))
        except KeyError as e:
            logging.error(traceback.format_exc())
            logging.error(e)
            raise HTTPError(status_code=400, reason='schema name require')
        except NodeExistsError:
            node = None
            raise HTTPError(status_code=503, reason='schema {0} is locked'.format(payload['name']))
        except SchemaError as e:
            raise HTTPError(status_code=400, reason=str(e))
        finally:
            if node is not None:
                self.application.zk.delete(node)

    def get(self, name):
        if name == '_list':
            self.jsonify(code=200, schemas=list(SchemaHandler.list_all_schema()))
            return
        if not SchemaHandler.is_schema_exist(name):
            raise HTTPError(status_code=404, reason='schema {0} not exist'.format(name))
        self.jsonify(code=200, schema=SchemaHandler.get_schema(name))
