export const ADD_NOTIFICATION = 'ADD_NOTIFICATION';
export const REMOVE_NOTIFICATION = 'REMOVE_NOTIFICATION';

export const INFO = 'info';
export const SUCCESS = 'success';
export const WARNING = 'warning';
export const ERROR = 'error';


export function add(level = INFO, message = '', options = {}) {
  return dispatch => {
    return dispatch({
      type: ADD_NOTIFICATION,
      notification: Object.assign({}, options, {
        level: level,
        message
      })
    });
  };
}

export function remove(notification) {
  return dispatch => {
    return dispatch({
      notification,
      type: REMOVE_NOTIFICATION
    });
  };
}
