import * as constants from '../constants/index';
import * as notification from '../actions/notification';

export function check(store, notify = null) {
  if (!store) {
    return false;
  }
  let _notify = notify;
  if (notify === null || typeof(notify) !== 'function') {
    _notify = () => null;
  }
  if (store.status.failure) {
    let redirect = null;
    if (store.error.status === 401 || store.error.status === 403) {
      if (typeof constants.LOGIN_PAGE === 'function') {
        redirect = constants.LOGIN_PAGE(window.location.href, store);
      } else {
        redirect = constants.LOGIN_PAGE;
      }
    }
    let title = null;
    if (store.error.status === 401) {
      title = '未登录';
    }
    if (store.error.status === 403) {
      title = '未授权';
    }
    _notify(notification.ERROR, store.error.message, {title, key: store.error.status, redirect});
    return false;
  }
  return store.status.request || store.status.success;
}
