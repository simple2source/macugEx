import fetch from 'isomorphic-fetch';
import { encode } from 'querystring';
import Store from 'store';
import * as constants from '../constants/index';

export const PAYLOAD = Symbol('API_PAYLOAD');

function call(endpoint, params, options) {
  let headers = new Headers(options.headers || constants.DEFAULT_HEADERS);
  const token = Store.get(constants.TOKEN_KEY || 'token');
  if (!token && constants.ENABLE_AUTH) {
    return Promise.reject({status: 401, message: constants.UNAUTHORIZED_MESSAGE || 'Unauthorized'});
  }
  if (constants.ENABLE_AUTH) {
    headers.set(constants.TOKEN_HEADER, token);
  }
  return fetch(`${endpoint}?${encode(params)}`, Object.assign({}, options, {headers}));
}

export default store => next => action => {
  const payload = action[PAYLOAD];
  if (typeof payload === 'undefined') {
    next(action);
    return;
  }

  let { endpoint, params, options, post} = payload;
  const {types, initialAction} = payload;

  if (typeof endpoint === 'function') {
    endpoint = endpoint(store.getState());
  }

  params = params || {};
  options = options || {};

  if (typeof post !== 'function') {
    post = data => data;
  }

  if (typeof endpoint !== 'string') {
    throw new Error('Specify a string endpoint URL.');
  }

  if (!Array.isArray(types) || types.length !== 3) {
    throw new Error('Expected an array of three action types.');
  }

  if (!types.every(type => typeof type === 'string')) {
    throw new Error('Expected action types to be strings.');
  }

  function actionWith(data) {
    let finalAction = Object.assign({}, action, data);
    delete finalAction[PAYLOAD];
    return finalAction;
  }
  const [ REQUEST, SUCCESS, FAILURE ] = types;
  next(actionWith(Object.assign({}, initialAction, {type: REQUEST})));
  return call(endpoint, params, options)
    .then(res => {
      if (res.ok) {
        res.json().then(json => next(actionWith({
          res: post(json),
          type: SUCCESS
        })));
      } else {
        res.json().then(json => {
          switch (res.status) {
            case 401:
              next(actionWith({
                error: {status: 401, message: constants.UNAUTHORIZED_MESSAGE || 'Unauthorized'},
                type: FAILURE
              }));
              break;
            case 403:
              next(actionWith({
                error: {status: 403, message: constants.FORBIDDEN_MESSAGE || 'Forbidden'},
                type: FAILURE
              }));
              break;
            default:
              next(actionWith({
                error: json,
                type: FAILURE
              }));
          }
        });
      }
    }).catch(err => next(actionWith({
      error: err,
      type: FAILURE
    })));
};
