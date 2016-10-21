构建引擎项目
============

安装依赖
--------

运行项目前,需要先安装项目所使用到的python包依赖,项目 requirements.txt 文件内容为::

    flask==0.10.1
    gevent==1.1.1
    pyzmq==15.2.0
    pymongo==3.2.2
    paho-mqtt==1.1
    hiredis==0.2.0
    redis==2.10.5
    pillow==3.1.1
    apns-client==0.2.1
    msgpack-python==0.4.7
    pycrypto==2.6.1
    ujson==1.35
    mkdocs==0.15.3
    flask-scrypt==0.1.3.6
    requests==2.10.0

如果还需要安装项目文档,还需要安装::

    Sphinx==1.4.3

所有依赖都可以使用 `pip` 安装,pip的使用说明详见: `<https://pip.pypa.io/en/stable/quickstart/>`_, 运行::

    pip -r requirements.txt

对项目所需依赖进行安装。

配置参数
--------

将项目源码中的 `setting.py.sample` 复制为 `setting.py`::

    cp setting.py.sample setting.py

根据下面的参数解释,对一些数值进行修改,如程序运行端口、主机域名等。

参数解释
--------

在 setting.py 中有以下字典对象,分别被各个模块所使用:

setting.server
^^^^^^^^^^^^^^

``setting.server['worker']``

设备服务开启的多进程数,因为 python 不能充分利用多线程的并发能力,
所以服务需要使用多线程来达到处理高并发的要求。

``setting.server['sock_port']``

设备TCP长服务socket程序占用的端口。

``setting.server['http_port']``

对设备提供http服务的程序占用的端口。

``setting.server['conf_port']``

对设备提供配置服务的程序占用的端口。

``setting.server['debug']``

设备TCP长连接服务是否在终端下打印输出,在 watch/socket/run.py 中有:

.. code-block:: python

    if setting.server['debug']:
        printlog = logging.StreamHandler()
        printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
        printlog.setLevel(setting.server['loglevel'])
        logger.addHandler(printlog)


``setting.server['sock_uri']``

设备TCP长连接服务器的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``setting.server['http_uri']``

设备http接口服务器的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``setting.server['sock_timeout']``

设备长连接服务器中tcp连接的默认超时时间

``setting.server['almanac_timeout']``

设备GPS辅助定位用星历文件超时时间,为一小时,星历文件从 u-blox 官网中下载(由静态文件服务程序下载)。

``setting.server['loglevel']``

设备TCP长连接服务程序所使用的日志级别,默认为调试级别。

``setting.server['logfile']``

设备TCP长连接服务程序所使用的日志文件。

setting.app
^^^^^^^^^^^

``setting.app['debug']``

接口程序使用 `flask` 框架编写接口服务, setting.app['debug'] 参数被用于 app/run.py 的 FLask 对象中,有:

.. code-block:: python

    app.config['DEBUG'] = setting.app['debug']
    app.config['SESSION_COOKIE_NAME'] = 'secret'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = setting.app['debug']
    app.config['PROPAGATE_EXCEPTIONS'] = True


``setting.app['port']``

接口程序占用的端口

``setting.app['uri']``

接口程序部署服务器使用的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``setting.app['loglevel']``

http RESTful接口程序使用的日志级别,默认为调试级别。

``setting.app['logfile']``

接口程序所使用的日志文件

setting.static
^^^^^^^^^^^^^^

``setting.static['use_nginx']``

静态文件服务程序是否使用nginx处理文件传输,
这会影响是否在访问静态文件服务程序后返回的http头部中加入 `X-Accel-Redirect` 标识。
在 static/run.py 中有:

.. code-block:: python

    if use_nginx:
        headers.append(('X-Accel-Redirect', '/cache/story/%s_%s.jpg' % (story_image_id, pattern)))
        response = Response(headers=headers)
    else:
        response = Response(image_data, headers=headers)

``setting.static['use_local']``

静态文件服务程序如果与 `nginx` 部署在同一台主机上,可以选择让程序监使用unix域socket提供服务。

``use_port``

静态文件服务程序若不使用unix域socket,需要设置使用tcp socket时所绑定的端口。

.. _hello:

``setting.static['debug']``

静态文件服务程序使用 `flask` 框架进行对各个静态文件 url 的处理,
setting.static['debug'] 参数用于配置 `Flask` 该对象的一些参数,
在 static/run.py 中有:

.. code-block:: python

    static.config['DEBUG'] = setting.static['debug']
    static.config['PROPAGATE_EXCEPTIONS'] = True

``setting.static['uri']``

静态文件服务程序部署的服务器使用的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
例如在 admin/admin.py 中,有:

.. code-block:: python

    return render_template('admin.html', menubar=user_menubar, username=session['nickname'], server_uri=static_uri)

用于在管理页面中,显示用户头像等其他静态资源。

``setting.static['normal_size']``

静态文件服务程序对头像类图像缩略图的一般大小。

``setting.static['small_size']``

静态文件服务程序对头像类图像缩略图的较小大小,在静态文件服务程序中头像的大小分类有: `origin`、`normal`、`small`。

``setting.static['loglevel']``

静态文件服务程序使用的日志级别,默认为调试级别。

``setting.static['logfile']``

静态文件服务程序所使用的日志文件。

setting.admin
^^^^^^^^^^^^^

``setting.admin['host']``

管理后台程序监听的地址,当前端用 `nginx` 处理 ssl 连接时,管理后台可使用本地局域网地址,
如只接受本机请求为'127.0.0.1',提供外网服务为'0.0.0.0'。

``setting.admin['port']``

管理后台所监听的端口号。

``setting.admin['debug']``

管理后台是否开启调试模式,如果 `debug = True`,会在终端打印日志消息,在 admin/run.py 中有:

.. code-block:: python

    if setting.admin['debug']:
        printlog = logging.StreamHandler()
        printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
        printlog.setLevel(setting.server['loglevel'])
        logger.addHandler(printlog)

``setting.admin['uri']``

管理后台程序所在服务器的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``setting.admin['salt']``

管理后台加密管理员账号密码的盐值。

``setting.admin['loglevel']``

管理后台程序使用的日志级别,默认为调试级别。

``setting.admin['logfile']``

管理后台程序所使用的日志文件。

setting.push
^^^^^^^^^^^^

``setting.push['host']``

推送代理程序监听的地址,推送代理程序为项目内提供对特定用户的推送服务抽象,一般只使用局域网地址,
如只接受本机请求为'127.0.0.1',提供外网服务为'0.0.0.0'。

``setting.push['port']``

推送代理程序监听的端口号。

``setting.push['loglevel']``

推送代理程序使用的日志级别,默认为调试级别。

``setting.push['logfile']``

推送代理程序所使用的日志文件。

setting.broker
^^^^^^^^^^^^^^

``setting.broker['host']``

指令交互程序监听的地址,指令交互程序为项目内提供对特定设备发送指令的中转服务抽象,一般只使用局域网地址,
如只接受本机请求为'127.0.0.1',提供外网服务为'0.0.0.0'。

``setting.broker['request_port']``

REQ模式的 router 监听的端口。

``setting.broker['respond_port']``

REP模式的 router 监听的端口。

``setting.broker['channel_port']``

PUB/SUB模式所监听的端口。

``setting.broker['loglevel']``

指令交互程序使用的日志级别,默认为调试级别。

``setting.broker['logfile']``

指令交互程序所使用的日志文件。

setting.mqtt
^^^^^^^^^^^^

``setting.mqtt['host']``

mqtt 服务器的主机地址,用于推送代理程序连接 mqtt 服务器。

``setting.mqtt['port']``

mqtt 服务程序的端口号,用于推送代理程序连接 mqtt 服务器。

``setting.mqtt['username']``

推送代理程序推送连接 mqtt 服务器时使用的用户名

``setting.mqtt['password']``

推送代理程序推送连接 mqtt 服务器时使用的密码

``setting.mqtt['cli_username']``

其他客户端连接 mqtt 服务器时使用的用户名,在 `docs/app/build.py` 中有:

.. code-block:: python

    template = Template(open('./docs/push.tpl', 'r').read().decode('utf-8-sig'))
    md = template.render(username=mqtt['cli_username'], password=mqtt['cli_password'], prefix=mqtt['prefix'])
    with open('./docs/push.md', 'w') as push_md:
        push_md.write(md.encode('utf-8'))

用于生成客户端查看的文档,下面两个参数同理。

``setting.mqtt['cli_password']``

其他客户端连接 mqtt 服务器时使用的密码

``setting.mqtt['prefix']``

项目中订阅 mqtt 所使用到的频道前缀

setting.mongo
^^^^^^^^^^^^^

``setting.mongo['host']``

Mongodb 服务器的主机地址

``setting.mongo['port']``

Mongodb 服务程序的端口号

``setting.mongo['database']``

项目使用到的数据库名

``setting.mongo['username']``

连接 Mongodb 服务器使用的用户名,没有时填 `None`。

``setting.mongo['password']``

连接 Mongodb 服务器使用的密码,没有时填 `None`。

setting.redis
^^^^^^^^^^^^^

``setting.redis['host']``

redis 服务器的主机地址

``setting.redis['port']``

redis 服务程序的端口号

``setting.redis['password']``

连接 redis 服务器使用的密码,没有时填 `None`。

setting.LocateProxy
^^^^^^^^^^^^^^^^^^^

``setting.LocateProxy['host']``

定位数据处理程序所在服务器的主机地址

``setting.LocateProxy['port']``

定位数据处理程序的端口号

``setting.LocateProxy['loglevel']``

定位数据处理程序使用的日志级别,默认为调试级别。

``setting.LocateProxy['logfile']``

定位数据处理程序所使用的日志文件。

项目静态文件
------------

``app/api/new_group.html``

用户创建圈子时,发送给用户邮件所用的html模板。

``app/api/config.json``

设备配置服务器中与客户号相关的APP包名,为各个接口中的 `identify` 参数。

``app/cert/``

接口服务器与APP之间访问https所用的证书

``push/cert/``

推送代理服务与APNs交互时使用的ios推送证书

``push/config.json``

推送代理服务配置的用户 `identify` (即APP包名)与所用证书的关系。

``static/misc/*.jpg``

静态文件处理程序所处理的用户等默认头像

``static/conifg.json``

静态文件处理程序配置的客户号与用户头像之间的关系,由 `static/define.py` 所使用。

测试环境
--------

在运行程序前,可以进入 `test` 目录,对项目的一些代码在正式环境中进行测试。
有一些测试用例的正确执行需要模块服务的支持,如 test/test_agent.py 中测试指令交互程序是否正确运行,
需要提前运行 `agent` 模块完成测试。

具体使用方法是运行 `testrunner.py 模块` 来测试某些模块的正确性,或者执行::

    > python testrunner.py

在所有测试都通过后, 可以运行项目。

开始运行
--------

在运行我们的程序之前,需要保证 `mongodb` 与 `redis` 在程序运行之前已启动,
并且正确的连接方式已修改 `setting.py` 文件配置完成。

supervisord
^^^^^^^^^^^

使用 supervisor 运行项目,将源码目录下的 `supervisor_config.md` 打开,复制并按实际情况编辑其中的示例。
需要先用 pip 安装 supervisor 模块。

按照示例编辑好 supervisord 的配置文件之后,
就可以启动 supervisord 了,具体的用法参考: `<http://supervisord.org/>`_ 。

直接运行
^^^^^^^^^^^^

手动管理进程的启动,进程之间有一定服务依赖关系,在 supervisord 的示例配置文件的 `priority` 参数中有所体现。
`python run.py` 其后的参数是因为在 `ps -ef` 中可以看到原始的运行命令,便于在其中识别各个服务。

首先运行指令交互模块, `agent` 模块::

    cd agent/
    python run.py agent

运行推送代理程序, `push` 模块::

    cd push/
    python run.py push

运行定位数据处理程序, `LocateProxy` 模块::

    cd watch/locateProxy/
    python run.py watch.LocateProxy

运行静态文件处理程序::

    cd static/
    python run.py static

运行管理后台::

    cd admin
    python run.py admin

运行接口服务程序::

    cd app
    python run.py app

运行设备TCP长连接程序::

    cd watch/socket/
    python run.py watch.socket

运行设备http接口程序::

    cd watch/http/
    python run.py watch.http


。。。

手动运行程序和 supervisor_config.md 中的配置文件的作用是一样的,都是按一定顺序,
启动程序, `supervisord` 启动的优势更大些。

维护代码
--------

在修改了某些模块的代码后,比如增加了一个APP的接口在 `app/api/apiv1.py` :

.. code-block:: python

    def api_test():
        return 'hello world'

如果用 `supervisord` 启动的(一般是在服务器上,本地测试一般直接运行),在修改文件后,
重启 app 接口程序::

    supervisorctl restart xxx-app

源码中 `xxx-app` 为 `YK01-app`,可自行修改。
(其他管理 supervisord 进程的方法参见 supervisord 官网)

之后可以使用 curl 测试是否生效::

    curl http://{uri}:{port}/v1/test -d ''

uri 为 `setting.py` 中 setting.app['uri'] 的值,为APP接口程序的 uri,为 APP接口程序所在的服务器地址。
port 为 APP接口程序运行时占用的端口号。

* 注:

.. code-block:: python

    API_PREFIX = 'api_'

    def add_view_func(module, pattern):
        for funcname in dir(module):
            if funcname.startswith(API_PREFIX):
                endpoint = funcname.split(API_PREFIX, 1)[1]
                raw_view_func = getattr(module, funcname)
                view_func = debuging(raw_view_func, module.failed) if setting.app['debug'] else raw_view_func
                app.add_url_rule(pattern % endpoint, endpoint, view_func, methods=['POST'])

    add_view_func(apiv1, '/v1/%s')
    add_view_func(apiv2, '/v2/%s')

在 `app/run.py` 中有视图函数挂载到特定的url的操作,可以按图索骥进行修改。
所有的接口请求都为 POST 方法(由 add_view_func 函数限定)。
