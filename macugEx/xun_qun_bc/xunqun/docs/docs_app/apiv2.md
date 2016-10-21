### 服务器地址

接口访问url前缀:

> **<https://app.ios16.com:8080/v2>**

> **<https://app.mobilebrother.net:8080/v2>**

接口访问方式为 POST 请求

接口返回参数格式：

* {
    * status : int, //一定存在
    * object: object, //返回字典时存在
    * array: list, //返回数组时存在
    * error: int, //出错时存在
    * errorKey: str, //因为请求中的某个键值出错时存在,为出错的该键值
    * debug: str //出错且服务器为调试模式时存在,返回具体错误信息
* }

接口返回数据object说明:

* {
    * 'key' : type(*), //comment
* }
* key为字典键名,type为该键数据类型;
* '(*)'表示该类型值可能为空;
* enum 为可选值元组;

#### 获取最新版本信息
* URL: **/last_version**

* 如果服务器没有最新版本信息,返回空数据,请求:

    参数名|必填|默认值|限制|描述
    --|--|--|--|--
**session**|Y| |12|用户session
**platform**|Y| |('android','ios')|查询对应app平台
**model**|Y| |1~50|查询对应机型
**current_version**|Y| |number|当前版本号
**identify**| | | |APP应用包名

* 返回数据:

```
{
    'status': enum(200, 300),
    'object': {
        'version': int(*), //版本号
        'name': str(*), //版本名称
        'url': str(*), //下载url
        'log': str(*) //版本更新日志
    }
}
```
