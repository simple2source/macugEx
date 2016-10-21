#### Admin模块

讯群项目后台管理界面

##### 项目部署修改

使用 nginx 使用 ssl 加密 admin 连接:

假设服务器使用的域名为 www.example.com,后台源码目录 admin 路径为 /YK01/admin;

```
server
{
    listen       443;
    server_name  www.example.com;
    ssl on;
    ssl_certificate /etc/letsencrypt/live/www.example.com/cert.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:46123;
        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;
        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }

    location /static {
        root /YK01/admin/;
    }
}
server
{
    listen 80;
    server_name www.example.com;

    rewrite ^(.*) https://$server_name$1 permanent;
}
```

执行 setup.py 创建默认管理菜单,管理账号

###### 数据库model定义:

menubar (菜单):

* _id < str >
    * 菜单id,链接的angularjs controller
* name < str >
    * 菜单名字
* permissions < int >
    * 所需权限
* submenubar < dict >
    * _id < str >
    * {
        * name < str > 子菜单名字
        * level < int > 子菜单权限级别
    * }

admin (管理员):

* _id < str >
    * 管理员id
* password < str >
    * 密码
* permissions < int >
    * 用户拥有权限种类
        * admin: 超级管理员
        * guest: 访客
        * debug: 调试人员
        * story_manage: 故事管理员
        * category_manage: 
        * version_manage: Android版本管理员
        * document: 文档查看员
        * plaza_manage: 广场管理员
        * watch_manage: 腕表管理员
        * game_manage: 游戏管理员
        * service_manage: 客服管理员
* maketime < datetime >
    * 创建日期
* lasttime < datetime >
    * 最后登陆日期

