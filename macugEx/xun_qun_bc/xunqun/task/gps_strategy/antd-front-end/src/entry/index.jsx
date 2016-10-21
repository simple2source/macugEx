import '../common/lib';
import React from 'react'; //注释掉会报 React is not defined
import {render} from 'react-dom';
import {Router, Route, Link, browserHistory, hashHistory} from 'react-router'
import IndexTable from './IndexTable';
import LogTable from './LogTable';


render((
  <Router history={hashHistory}>
    <Route path="/" component={IndexTable}/>
    <Route path="/log/:imei" component={LogTable}/>
    <Route path="*" component={IndexTable}/>
  </Router>
), document.getElementById('content'))

