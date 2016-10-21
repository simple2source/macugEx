### 腕表配置服务

> <http://getway.watch.ios16.com:9892>

腕表根据出厂时设置的客户号或经由指令设置的最新客户号请求该地址,<br/>
使用客户号的十进制形式作为`customid`参数的值,获取该客户号所属的域名等配置.

示例请求: <http://getway.watch.ios16.com:9892?customid=1>

返回数据:

    > HTTP/1.1 200
    > Content-Type: application/json
    > Date: Tue, 17 May 2016 06:23:36 GMT
    > Content-Length: 162

    {
        "name":"disney",
        "http_url":["h.mobilebrother.net",8001],
        "tcp_url":["s.mobilebrother.net",8000],
        "static_url":["static.mobilebrother.net",80]
    }

返回字段:

    name: 该客户标识(未用到)
    http_url: 腕表http服务所用域名,端口号
    tcp_url: 腕表tcp长连接所用域名,端口号
    static_url: 腕表所下载静态文件域名,端口号

内测地址：

> s.ios16.com:8000

> h.ios16.com:8001

> static.ios16.com:80


代理商版本地址：

> s.mobilebrother.net:8000

> h.mobilebrother.net:8001

> static.mobilebrother.net:80