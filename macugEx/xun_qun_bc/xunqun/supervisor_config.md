supervisord 配置文件示例:

YK01 为项目代号,示例中,假设 python2.7 的执行路径为 /usr/local/python27/bin/python ,
假设项目源码放置在 /YK01 目录下。

```
[program:YK01-agent]
command=/usr/local/python27/bin/python run.py agent
directory=/YK01/agent
user=root
autostart=true
autorestart=true
priority=100

[program:YK01-push]
command=/usr/local/python27/bin/python run.py push
directory=/YK01/push
user=root
autostart=true
autorestart=true
priority=100

[program:YK01-watch-LocateProxy]
command=/usr/local/python27/bin/python run.py watch.LocateProxy
directory=/YK01/watch/LocateProxy
user=root
autostart=true
autorestart=true
priority=100

[program:YK01-static]
command=/usr/local/python27/bin/python run.py static
directory=/YK01/static
user=root
autostart=true
autorestart=true
priority=120

[program:YK01-admin]
command=/usr/local/python27/bin/python run.py admin
directory=/YK01/admin
user=root
autostart=true
autorestart=true
priority=150

[program:YK01-app]
command=/usr/local/python27/bin/python run.py app
directory=/YK01/app
user=root
autostart=true
autorestart=true
priority=150

[program:YK01-watch-socket]
command=/usr/local/python27/bin/python run.py watch.socket
directory=/YK01/watch/socket
user=root
autostart=true
autorestart=true
priority=200
stopasgroup=true

[program:YK01-watch-http]
command=/usr/local/python27/bin/python run.py watch.http
directory=/YK01/watch/http
user=root
autostart=true
autorestart=true
priority=200

[program:YK01-task-submail]
command=/usr/local/python27/bin/python submail_hook.py task.submail
directory=/YK01/task
user=root
autostart=true
autorestart=true
priority=200

[program:YK01-gps-strategy]
command=/usr/local/python27/bin/python run.py task.gps.strategy
directory=/YK01/task/gps_strategy
user=root
autostart=true
autorestart=true
priority=200

[program:YK01-watch-config]
command=/usr/local/python27/bin/python run.py watch.configServe
directory=/YK01/watch/configServe
user=root
autostart=true
autorestart=true
priority=200
```