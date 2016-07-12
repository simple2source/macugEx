/**
 * Created by comyn on 16-4-16.
 */
import { createTypes } from './utils';
import { PAYLOAD } from '../middleware/api';

export const GET = createTypes('GET');

function makeGetPayload(app) {
  return {
    [PAYLOAD]: {
      types: [GET.REQUEST, GET.SUCCESS, GET.FAILURE],
      endpoint: '/watcher',
      params: {app: app}
    }
  };
}

export function get(app) {
  return dispatch => dispatch(makeGetPayload(app));
}


export const ADD = createTypes('ADD');

function makeAddPayload(app, filename) {
  return {
    [PAYLOAD]: {
      types: [ADD.REQUEST, ADD.SUCCESS, ADD.FAILURE],
      endpoint: '/watcher',
      options: {
        method: 'POST',
        body: JSON.stringify({app_id: app, filename})
      }
    }
  }
}

export function add(app, filename) {
  return dispatch => dispatch(makeAddPayload(app, filename));
}
