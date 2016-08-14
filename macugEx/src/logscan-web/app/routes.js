import React from 'react';
import { Route } from 'react-router';
import App from './containers/App';
import Watchers from './containers/Watchers';
import AddWatcher from './containers/AddWatcher'

const routes = (
  <Route>
    <Route path="/" component={App}>
      <Route path="/watchers" component={Watchers} />
      <Route path="/watcher/add" component={AddWatcher} />
    </Route>
  </Route>
);

export default routes;
