import { createStore, applyMiddleware, compose } from 'redux';
import { reduxReactRouter } from 'redux-router';
import { devTools } from 'redux-devtools';
import { default as createHistory } from 'history/lib/createBrowserHistory';
import thunk from 'redux-thunk';
import createLogger from 'redux-logger';
import api from '../middleware/api';
import rootReducer from '../reducers';
import routes from '../routes';

const finalCreateStore = compose(
  applyMiddleware(thunk, api),
  reduxReactRouter({ routes, createHistory }),
  applyMiddleware(createLogger()),
  devTools()
)(createStore);

export default function configureStore(initialState) {
  const store = finalCreateStore(rootReducer, initialState);

  if (module.hot) {
    module.hot.accept('../reducers', () => {
      const nextRootReducer = require('../reducers');
      store.replaceReducer(nextRootReducer);
    });
  }
  return store;
}
