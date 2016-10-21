#### watch.socket模块的通信代理

用 `zmq` 实现用于各个 watch.socket 模块之间通信的 hub;
项目内各处请求与 watch.socket 通信时,由 hub 广播请求,并返回结果;

![通信流程](./architecture.png)