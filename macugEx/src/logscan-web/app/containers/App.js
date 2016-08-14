import React from 'react';
import {connect} from 'react-redux';
import {pushState} from 'redux-router';
import NotificationSystem from 'react-notification-system';
import * as Notification from '../actions/notification';

@connect(state => ({global: state.global}), {pushState, remove: Notification.remove})
export default class App extends React.Component {
  static propTypes = {
    global: React.PropTypes.object.isRequired,
    pushState: React.PropTypes.func.isRequired,
    children: React.PropTypes.node.isRequired,
    remove: React.PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.ns = null;
  }

  componentDidMount() {
    this.ns = this.refs.ns;
  }

  render() {
    const { children } = this.props;
    this.props.global.notifications.map(notification => {
      const {
        title = null,
        message,
        level = Notification.INFO,
        position = 'tc',
        autoDismiss = 5
      } = notification;
      let onRemove = () => this.props.remove(notification);
      let action = null;
      if (notification.redirect) {
        onRemove = () => {
          this.props.remove(notification);
          this.props.pushState(null, notification.redirect);
        };
        action = {
          label: '跳转',
          callback: () => this.props.pushState(null, notification.redirect)
        };
      }
      const msg = {title, message, level, position, autoDismiss, onRemove, action, uid: notification.id};
      if (this.ns) {
        this.ns.addNotification(msg);
      }
    });
    return (
      <div>
        {children}
        <NotificationSystem ref="ns" />
      </div>
    );
  }
}
