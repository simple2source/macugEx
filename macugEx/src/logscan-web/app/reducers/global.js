import { OrderedSet } from 'immutable';
import * as Notification from '../actions/notification';


const initialState = {
  notifications: OrderedSet()
};

export default function global(state = initialState, action = {}) {
  switch (action.type) {
    case Notification.ADD_NOTIFICATION:
      return Object.assign({}, state, {
        notifications: state.notifications.add(
          Object.assign({},
            action.notification,
            {id: action.notification.key ? action.notification.key: state.notifications.size + 1}))
      });
    case Notification.REMOVE_NOTIFICATION:
      return Object.assign({}, state, {
        notifications: state.notifications.delete(action.notification)
      });
    default:
      return state;
  }
}
