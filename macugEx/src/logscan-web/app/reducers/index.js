import { combineReducers } from 'redux';
import { routerStateReducer as router } from 'redux-router';
import * as utils from './utils';
import global from './global';
import * as Watcher from '../actions/watcher';

const watchers = utils.createReduce(Watcher.GET);
const resp = utils.createReduce(Watcher.ADD);

const rootReducer = combineReducers({
  global,
  watchers,
  resp,
  router
});

export default rootReducer;
