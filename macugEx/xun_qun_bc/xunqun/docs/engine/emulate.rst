设备模拟器
==========

简介
----

设备模拟器主要用于调试设备服务器的功能,使用 python 标准库来实现 tcp/ip 通信,
模拟设备与服务器的交互,并通过编程实现具体想要的模拟器所模拟的设备动作。

实现
----

`emulate.py` 主要实现了 Emulate 类,通过在创建该类时传进的参数,配置模拟器类的一些参数。

主要的初始化参数有:

* host

    模拟器连接的服务器地址

* port

    模拟器连接的服务器端口号

* imei

    模拟器所模拟的自身imei标识

* heartbeat

    模拟器定期发送心跳指令的时间

模拟器类有几个比较重要的函数定义:

* `emulate.Emulate.recv`:

    模拟器接受数据函数,返回的 data 是 socket 接收到的数据

* `emulate.Emulate.parse_data`:

    模拟器在收到服务器端发送过来的数据以后使用该函数解析成对应的参数列表

* `emulate.Emulate.action`:

    模拟器执行函数,如果自定义模拟器子类,需要在 action 动作中解析收到的 data 参数(使用`emulate.Emulate.parse_data`)。

示例
----

在初始化 `emulate.Emulate` 类后,模拟器已经发送登录到服务器了,登录的方法为 `emulate.Emulate.login`,
在服务器修改登录方式后,可以相对应修改模拟器类的 `login` 方法,并初始化模拟器类后即可测试连接成功与否。

模拟器的 `loop` 函数为:

.. code-block:: python

    def loop(self, block=True):
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        if block:
            self._loop()
        else:
            recv_thread = threading.Thread(target=self._loop)
            recv_thread.daemon = True
            recv_thread.start()

在模拟器的运行循环中,先启动处理心跳指令线程,再看模拟器是否在阻塞模式,如果 `block` 参数为真,
则接下来的处理指令循环会直接运行在主线程中,阻塞程序的执行,适用于一般情况下的简单运行。
如果需要在其他业务中集成使用 `emulate.Emulate` 类,可以使其运行在非阻塞模式下,这时候会开启
一个新的线程用于处理指令的接受与处理收到的指令,不会阻塞主线程的运行。

可以在模拟器连接上服务器后,发送自定义的数据至服务器,之后数据的解析则有 loop 函数进行处理,例如:

.. code-block:: python

    emulate = Emulate(host=host, port=port, imei=imei, customer_id=customer)

    # emulate.locate([[460, 0, 9475, 44901, -78], [460, 0, 9475, 17252, -87]])  # 科学城
    # emulate.locate(gps=(113.4395958, 23.1659372), Ltype=2)  # 科学城
    emulate.send('\x29', ['56909c5f0bdb823db41496a8']) # 发送 0x29 指令,并附带数据,指令数据格式见指令文档
    emulate.loop()

默认将阻塞主线程的运行,但在一般情况下,都作为测试用,用于快速验证服务器。

