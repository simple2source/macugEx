import '../common/lib';
import React from 'react';
import {Table} from 'antd';
import reqwest from 'reqwest';
import {Link} from 'react-router';

const columns = [{
  title: '操作',
  dataIndex: 'status'
}, {
  title: '时间',
  dataIndex: 'timestamp',
  render(text, item){
    return <span>{timeConverter(item['timestamp'])}</span>;
  }
}, {
  title: '结果',
  dataIndex: 'result',
  render(text, item) {
    text = null;
    if (item['status'] == 'request') {
      let spend = null;
      let locate = null;
      if (item['recv_timestamp'] && item['spendtime']) {
        spend = <span>
          {timeConverter(item['recv_timestamp'])} 收到,总计 <span style={{'color': 'blue'}}>{item['spendtime']}</span>秒
        </span>;
      }
      if (item['loc'] && item['address']) {
        locate = <span>, <span style={{'color': 'blue'}}>{item['loc'][0]},{item['loc'][1]}</span> ,[{item['address']}]</span>;
      }
      text = <span>{spend}{locate}</span>;
    }
    if (item['status'] == 'close') {
      text = <span>发送gps省电策略</span>;
    }
    return text;
  }
}
];


function timeConverter(UNIX_timestamp) {
  var a = new Date(UNIX_timestamp * 1000);
  var year = a.getFullYear();
  var month = a.getMonth() + 1;
  month = month >= 10 ? month : '0' + month;
  var date = a.getDate();
  var hour = a.getHours();
  hour = hour >= 10 ? hour : '0' + hour;
  var min = a.getMinutes();
  min = min >= 10 ? min : '0' + min;
  var sec = a.getSeconds();
  sec = sec >= 10 ? sec : '0' + sec;
  var time = year + '-' + month + '-' + date + ' ' + hour + ':' + min + ':' + sec;
  return time;
}


const LogTable = React.createClass({
  getInitialState() {
    let {imei}  = this.props.params;
    reqwest({
      url: `/tasking_record_count/${imei}`,
      method: 'get',
      type: 'json',
      success: (total) => {
        const pagination = this.state.pagination;
        pagination.total = total;
        this.setState({pagination: pagination});
      }
    });
    return {
      data: [],
      pagination: {
        total: 0,
        current: 1,
        showSizeChanger: true,
        onShowSizeChange(current, pageSize) {
          console.log('Current: ', current, '; PageSize: ', pageSize);
        },
        onChange(current) {
          console.log('Current: ', current);
        }
      },
      loading: false,
      imei: imei
    };
  },
  handleTableChange(pagination, filters, sorter) {
    const pager = this.state.pagination;
    // 如果当前有翻页的话
    pager.current = pagination.current;
    pager.pageSize = pagination.pageSize;
    this.setState({
      pagination: pager
    });
    this.fetch({
      num: pagination.pageSize,
      page: pagination.current - 1,
      sortField: sorter.field,
      sortOrder: sorter.order,
      ...filters
    });
  },
  fetch(params = {}) {
    this.setState({loading: true});
    reqwest({
      url: `/tasking_record/${this.state.imei}`,
      method: 'get',
      data: params,
      type: 'json',
      success: (data_list) => {
        this.setState({
          loading: false,
          data: data_list,
        });
      }
    });
  },
  componentDidMount() {
    this.fetch();
  },
  render() {
    return (
      <Table columns={columns}
             dataSource={this.state.data}
             pagination={this.state.pagination}
             loading={this.state.loading}
             rowKey={record => record.timestamp}
             onChange={this.handleTableChange}/>
    );
  }
});

// ReactDOM.render(<MyTable />, document.getElementById('content'));

export default LogTable;
