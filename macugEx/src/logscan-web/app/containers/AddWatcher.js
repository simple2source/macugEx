/**
 * Created by comyn on 16-4-16.
 */
import React from 'react';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';
import { autobind } from 'core-decorators';
import * as WatcherActions from '../actions/watcher';

@connect(state => ({resp: state.resp}), {pushState, add: WatcherActions.add})
export default class AddWatcher extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      app: '',
      filename: ''
    };
    //this.handleSubmit = this.handleSubmit.bind(this);
  }

  @autobind
  handleSubmit() {
    this.props.add(this.state.app, this.state.filename);
  }

  componentWillReceiveProps(props) {
    if(props.resp.status.success) {
      this.props.pushState(null, '/watchers');
    }
  }

  render() {
    return (
      <div>
        <input type="text" value={this.state.app} onChange={e => this.setState({app: e.target.value})}/>
        <input type="text" value={this.state.filename} onChange={e => this.setState({filename: e.target.value})}/>
        <button onClick={this.handleSubmit}>submit</button>
      </div>
    )
  }
}
