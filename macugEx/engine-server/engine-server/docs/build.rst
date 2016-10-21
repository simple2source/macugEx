构建引擎项目
============

安装依赖
--------

运行项目前,需要先安装项目所使用到的python包依赖,项目 requirements.txt 文件内容为::


    flask==0.10.1
    gevent==1.2.1
    pyzmq==15.2.0
    paho-mqtt==1.2
    apns-client==0.2.1

如果项目使用了 Monogdb,还需要安装::

    pymongo==3.2.2

如果还需要安装项目文档,还需要安装::

    Sphinx==1.4.3

所有依赖都可以使用 `pip` 安装,pip的使用说明详见: `<https://pip.pypa.io/en/stable/quickstart/>`_, 运行::

    pip -r requirements.txt

对项目所需依赖进行安装。

如果系统为 centos:

* 可以直接通过修改 ~/.bashrc 文件,在文件中添加以下几行::

    cd /root/engine  # 本机的 engine 项目目录
    source activate
    cd - >/dev/null

* 或者每次在进入项目文件夹内后,执行::

    source activate

用于激活虚拟环境(类似virtualenv)

配置参数
--------

将项目源码中的 `conf.example.py` 复制为 `conf.py`::

    cp conf.py.sample conf.py

根据下面的参数解释,对一些数值进行修改,如程序运行端口、主机域名等。

参数解释
--------

在 conf.py 中有以下字典对象,分别被各个模块所使用:

conf.devices
^^^^^^^^^^^^^^

``devices['worker']``

设备服务开启的多进程数,因为 python 不能充分利用多线程的并发能力,
所以服务需要使用多线程来达到处理高并发的要求。

``devices['sock_port']``

设备TCP长服务socket程序占用的端口。

``devices['http_port']``

对设备提供http服务的程序占用的端口。

``devices['conf_port']``

对设备提供配置服务的程序占用的端口。

``devices['debug']``

设备TCP长连接服务是否在终端下打印输出,在 watch/socket/run.py 中有:

.. code-block:: python

    if conf.devices['debug']:
        printlog = logging.StreamHandler()
        printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
        printlog.setLevel(conf.devices['loglevel'])
        logger.addHandler(printlog)


``devices['uri']``

设备TCP长连接服务器的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``devices['sock_timeout']``

设备长连接服务器中tcp连接的默认超时时间

``devices['loglevel']``

设备TCP长连接服务程序所使用的日志级别,默认为调试级别。

``devices['logfile']``

设备TCP长连接服务程序所使用的日志文件。

conf.app
^^^^^^^^^^^

``app['debug']``

接口程序使用 `flask` 框架编写接口服务, conf.app['debug'] 参数被用于 app/run.py 的 FLask 对象中,有:

.. code-block:: python

    app.config['DEBUG'] = conf.app['debug']
    app.config['SESSION_COOKIE_NAME'] = 'secret'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = conf.app['debug']
    app.config['PROPAGATE_EXCEPTIONS'] = True


``app['port']``

接口程序占用的端口

``app['uri']``

接口程序部署服务器使用的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``app['loglevel']``

http RESTful接口程序使用的日志级别,默认为调试级别。

``app['logfile']``

接口程序所使用的日志文件

conf.admin
^^^^^^^^^^^^^

``admin['host']``

管理后台程序监听的地址,当前端用 `nginx` 处理 ssl 连接时,管理后台可使用本地局域网地址,
如只接受本机请求为'127.0.0.1',提供外网服务为'0.0.0.0'。

``admin['port']``

管理后台所监听的端口号。

``admin['debug']``

管理后台是否开启调试模式,如果 `debug = True`,会在终端打印日志消息,在 admin/run.py 中有:

.. code-block:: python

    if conf.admin['debug']:
        printlog = logging.StreamHandler()
        printlog.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(filename)s(%(lineno)s):%(message)s'))
        printlog.setLevel(conf.admin['loglevel'])
        logger.addHandler(printlog)

``admin['uri']``

管理后台程序所在服务器的主机名,在本机运行时例如为 '127.0.0.1',在线上运行时例如为 'www.example.com',
目前项目中未用到此配置参数。

``admin['salt']``

管理后台加密管理员账号密码的盐值。

``admin['loglevel']``

管理后台程序使用的日志级别,默认为调试级别。

``admin['logfile']``

管理后台程序所使用的日志文件。

conf.broker
^^^^^^^^^^^^^^

``broker['host']``

指令交互程序监听的地址,指令交互程序为项目内提供对特定设备发送指令的中转服务抽象,一般只使用局域网地址,
如只接受本机请求为'127.0.0.1',提供外网服务为'0.0.0.0'。

``broker['request_port']``

REQ模式的 router 监听的端口。

``broker['respond_port']``

REP模式的 router 监听的端口。

``broker['port']``

PUB/SUB模式所监听的端口,主要的用于甄别程序运行状态的端口。

``broker['loglevel']``

指令交互程序使用的日志级别,默认为调试级别。

``broker['logfile']``

指令交互程序所使用的日志文件。

conf.mongo
^^^^^^^^^^^^^

``mongo['host']``

Mongodb 服务器的主机地址

``mongo['port']``

Mongodb 服务程序的端口号

``mongo['database']``

项目使用到的数据库名

``mongo['username']``

连接 Mongodb 服务器使用的用户名,没有时填 `None`。

``mongo['password']``

连接 Mongodb 服务器使用的密码,没有时填 `None`。

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

在运行我们的程序之前,需要保证 `mongodb` 在程序运行之前已启动,
并且正确的连接方式已修改 `conf.py` 文件配置完成。

进程之间有一定服务依赖关系,增加在 `python run.py` 其后的参数是因为在 `ps -ef` 中可以看到原始的运行命令,便于在其中识别各个服务。

首先运行指令交互模块, `agent` 模块::

    cd agent/
    python run.py agent

运行管理后台::

    cd admin
    python run.py admin

运行接口服务程序::

    cd api
    python run.py api

运行设备TCP长连接程序::

    cd devices/
    python run.py devices
