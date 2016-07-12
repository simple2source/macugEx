/**
 * Created by comyn on 16-4-16.
 */
import React from 'react';
import {connect} from 'react-redux';
import * as WatcherActions from '../actions/watcher';

@connect(state => ({
  watchers: state.watchers
}), {list: WatcherActions.get})
export default class Watchers extends React.Component {
  constructor(props) {
    super(props);
    this.props.list('test');
  }

  render() {
    if (!this.props.watchers.status.success) {
      return <div>loading...</div>
    }
    return (
      <div>
        <ul>
          {this.props.watchers.res.files.map(file => <li key={file}>{file}</li>)}
        </ul>
      </div>
    )
  }
}
