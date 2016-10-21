import '../common/lib';
import React from 'react';
import {Form, Input, Button, Select, Checkbox, Table, message} from 'antd';
import reqwest from 'reqwest';
import {Link} from 'react-router';

const FormItem = Form.Item;
const InputGroup = Input.Group;
const Option = Select.Option;

let Head = React.createClass({
  getInitialState: function () {
    return {
      operateValue: 'add',
      imei: ''
    };
  },
  handleSubmit(e) {
    e.preventDefault();
    if (!this.state.imei || this.state.imei.length != 15) {
      message.error('imei长度不够');
      return false;
    }
    reqwest({
      url: '/tasking_operate',
      method: 'post',
      data: {imei: this.state.imei, operate: this.state.operateValue},
      success: (msg) => {
        if (msg == 'success') {
          message.success('操作成功');
        } else {
          message.error(msg);
        }
        this.setState({'imei': ''});
      }
    });
  },
  setOperate(value){
    this.setState({'operateValue': value});
  },
  setImei(e){
    this.setState({'imei': e.target.value});
  },
  render() {
    return (
      <Form inline onSubmit={this.handleSubmit} style={{ margin: 16 }}>
        <FormItem
          label="imei：">
          <Input placeholder="请输入imei" value={this.state.imei} onChange={this.setImei}/>
          <Select value={this.state.operateValue} style={{ width: 70 }} onChange={this.setOperate}>
            <Option value="add">添加</Option>
            <Option value="del">删除</Option>
          </Select>
          <Button type="primary" htmlType="submit">确定</Button>
        </FormItem>
      </Form>
    );
  }
});

Head = Form.create()(Head);

const columns = [{
  title: 'imei',
  dataIndex: 'imei',
  render(imei) {
    return <Link to={`/log/${imei}`}>{imei}</Link>;
  }
}, {
  title: '策略',
  dataIndex: 'strategy',
}, {
  title: '状态',
  dataIndex: 'status',
}];


const IndexTable = React.createClass({
  getInitialState() {
    reqwest({
      url: '/tasking_count',
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
      loading: false
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
      url: '/tasking_watch',
      method: 'get',
      data: params,
      type: 'json',
      success: (data) => {
        this.setState({
          loading: false,
          data: data,
        });
      }
    });
  },
  componentDidMount() {
    this.fetch();
  },
  render() {
    return (
      <div>
        <Head />
        <Table columns={columns}
               dataSource={this.state.data}
               pagination={this.state.pagination}
               loading={this.state.loading}
               rowKey={record => record.imei}
               onChange={this.handleTableChange}/>
      </div>
    );
  }
});

export default IndexTable
