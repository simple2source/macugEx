import os
import socket
import datetime
import logging
import requests
import farmhash
from tornado.web import RequestHandler
from tornado.web import HTTPError
from tornado.options import options
from kazoo.exceptions import NodeExistsError
from .mixins import RestMixin
from .schema import SchemaHandler
from .exceptions import EntityError


def is_ip(s):
    try:
        socket.inet_aton(s)
        return True
    except OSError:
        return False


type_mapping = {
    'string': lambda x: isinstance(x, str),
    'long': lambda x: isinstance(x, int),
    'double': lambda x: isinstance(x, float),
    'date': lambda x: isinstance(x, int),
    'ip': is_ip
}


class EntityHandler(RestMixin, RequestHandler):
    @staticmethod
    def get_entity(schema_name, key, source=True):
        resp = requests.get('{0}/{1}/entity/{2}'.format(options.es, schema_name, farmhash.hash64(key)))
        if resp.status_code >= 300 and resp.status_code != 404:
            raise EntityError('get entity {0} error: {1}'.format(key, resp.text))
        if source:
            return resp.json().get('_source')
        return resp.json()

    @staticmethod
    def term_query(schema_name, field_name, value):
        query = {
            'term': {field_name: value}
        }
        resp = requests.get('{0}/{1}/entity/_search'.format(options.es, schema_name), json={'query': query})
        if resp.status_code >= 300:
            raise HTTPError(status_code=500, reason=resp.text)
        return resp.json()

    @staticmethod
    def validate_type(tp, value):
        return type_mapping.get(tp)(value)

    @staticmethod
    def validate_unique(schema, field, value, key):
        resp = EntityHandler.term_query(schema['name'], field['name'], value)
        total = resp.get('hits', {}).get('total', 0)
        if total == 1:
            entity = EntityHandler.get_entity(schema['name'], key, False)
            o = resp.get('hits').get('hits')[0]
            if o['_id'] == entity['_id']:
                return
        if total <= 0:
            return
        raise EntityError('{0}:{1} is exist'.format(field['name'], value))

    @staticmethod
    def validate_reference(schema, field, value, key):
        if field.get('ref') is not None:
            schema_name, field_name = field['ref'].split('::')
            resp = EntityHandler.term_query(schema_name, field_name, value)
            if resp.get('hits', {}).get('total', 0) < 1:
                raise EntityError('field {0} reference check error'.format(field['name']))
        entity = EntityHandler.get_entity(schema['name'], key, False)
        if entity['found']:
            if entity.get(field['name']) is None:
                return
            if entity[field['name']] == value:
                return
            for s in SchemaHandler.list_all_schema():
                for f in SchemaHandler.get_schema(s).get('fields'):
                    if f.get('ref') is not None and f['ref'] == '{0}::{1}'.format(schema['name'], field['name']):
                        resp = EntityHandler.term_query(s, f['name'], entity[field['name']])
                        if resp.get('hits', {}).get('total', 0) > 0:
                            raise EntityError('it is reference by {0}::{1}'.format(s, f['name']))

    @staticmethod
    def validate_field(schema, field, value, key):
        if field['multi']:
            if not isinstance(value, list):
                raise EntityError('{0} not multi'.format(field['name']))
            if not all((EntityHandler.validate_type(field['type'], v) for v in value)):
                raise EntityError('{0} type check error, require {1}, but {2}'.format(field['name'],
                                                                                      field['type'],
                                                                                      type(value)))
            for v in value:
                EntityHandler.validate_unique(schema, field, v, key)
                EntityHandler.validate_reference(schema, field, v, key)

        else:
            if not EntityHandler.validate_type(field['type'], value):
                raise EntityError('{0} type check error, require {1}, but {2}'.format(field['name'],
                                                                                      field['type'],
                                                                                      type(value)))
            EntityHandler.validate_unique(schema, field, value, key)
            EntityHandler.validate_reference(schema, field, value, key)

    @staticmethod
    def validate_entity(schema, entity):
        if '_meta' in entity.keys():
            entity.pop('_meta')
        if set(entity.keys()) != {field['name'] for field in schema['fields']}:
            raise EntityError('field list not match')
        for field in schema['fields']:
            EntityHandler.validate_field(schema, field, entity[field['name']], entity[schema['pk']])

    def post(self, schema_name):
        node = os.path.join(options.root, schema_name)
        try:
            self.application.zk.create(node)
            schema = SchemaHandler.get_schema(schema_name)
            payload = self.get_payload()
            EntityHandler.validate_entity(schema, payload)
            entity = EntityHandler.get_entity(schema_name, payload[schema['pk']])
            if entity is None:
                payload['_meta'] = {
                    'schema': schema_name,
                    'version': 0,
                    'timestamp': int(datetime.datetime.now().timestamp() * 1000)
                }
            else:
                payload['_meta'] = {
                    'schema': schema_name,
                    'version': entity['_meta']['version'] + 1,
                    'timestamp': int(datetime.datetime.now().timestamp() * 1000)
                }
            r = requests.post('{0}/{1}/entity_history'.format(options.es, schema_name), json=payload)
            if r.status_code >= 300:
                logging.error('put entity history error: {0}'.format(r.text))
                raise HTTPError(status_code=500, reason='put entity history error: {0}'.format(r.text))
            key = farmhash.hash64(payload[schema['pk']])
            r = requests.put('{0}/{1}/entity/{2}'.format(options.es,
                                                         schema_name,
                                                         key), json=payload)
            if r.status_code >= 300:
                logging.error('put entity error: {0}'.format(r.text))
                raise HTTPError(status_code=500, reason='put entity error: {0}'.format(r.text))
            self.jsonify(code=200, entity=EntityHandler.get_entity(schema_name, payload[schema['pk']]))
        except NodeExistsError:
            node = None
            raise HTTPError(status_code=422, reason='schema {0} is locked'.format(schema_name))
        finally:
            if node is not None:
                self.application.zk.delete(node)

    def get(self, schema_name, pk):
        entity = EntityHandler.get_entity(schema_name, pk)
        if entity is not None:
            self.jsonify(code=200, entity=entity)
        else:
            self.jsonify(code=404, message='{0}::{0} not found'.format(schema_name, pk))


class EntitySearchHandler(RestMixin, RequestHandler):
    @staticmethod
    def search(query, schemas=None, size=50, page=1, sort=None):
        if schemas is None or len(schemas) <= 0:
            index = '_all'
        else:
            index = ','.join(schemas)
        query = {
            "query_string": {
                "query": query
            }
        }
        if sort is None:
            _sort = [{'_meta.timestamp': {'order': 'desc'}}]
        else:
            _sort = [{k: {'order': v}} for k, v in sort]
        r = requests.get('{0}/{1}/entity/_search'.format(options.es, index), json={
            'from': (page -1) * size,
            'size': size,
            'sort': _sort,
            'query': query
        })
        if r.status_code >= 300:
            raise HTTPError(status_code=500, reason=r.text)
        entities = {
            'total': r.json().get('hits').get('total'),
            'size': size,
            'page': page,
            'sort': sort,
            'entities': [x.get('_source') for x in r.json().get('hits').get('hits')]
        }
        return entities

    def get(self, *args, **kwargs):
        schemas = self.get_arguments('schema')
        query = self.get_argument('q', default='*')
        try:
            page =  int(self.get_argument('page', default=1))
        except Exception as e:
            logging.warning(e)
            page = 1
        try:
            size = int(self.get_argument('size', default=50))
        except Exception as e:
            logging.warning(e)
            size = 50
        sort = [x.split(':') for x in self.get_arguments('sort')]
        entities = EntitySearchHandler.search(query, page=page, size=size, sort=sort, schemas=schemas)
        self.jsonify(code=200, entities=entities)