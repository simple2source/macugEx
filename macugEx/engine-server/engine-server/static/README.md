#### 静态文件处理模块

处理静态文件的请求,可以用nginx做本地文件请求代理,当文件还未生成时由static模块处理请求并生成文件;
static模块各flask端点函数,用于处理图片的压缩,不同尺寸图片静态文件的生成;
周期性更新星历文件;
假设项目路径为 /YK01;

##### 配置步骤

1. 复制项目默认头像至 **./misc/** 并编辑config.json;
2. 静态文件服务如果使用 nginx 的示例配置:

假设服务使用的域名为 www.example.com

```
server
{
    listen       80;
    server_name  www.example.com;
    root /YK01/cache; 
    
    location / {
        proxy_pass http://unix:/YK01/static/static.sock;
        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;
        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }
    
    location /almanac/current.alp {
        default_type application/octet-stream;
        try_files /current_almanac.alp $uri @server;
    }
    
    location ~ ^/android/(.*)\..*$ {
        default_type application/octet-stream;
        try_files /android/$1.apk $uri @server;
    }

    location ~ ^/bluetooth/(.*)\..*$ {
        default_type application/octet-stream;
        try_files /bluetooth/$1.bin $uri @server;
    }
    
    location ~ ^/banner/image/(.*)\..*$ {
        try_files /banner/$1.jpg $uri @server;
    }
    
    location ~ ^/category/image/(.*)\..*$ {
        try_files /category/$1.jpg $uri @server;
    }

    location ~ ^/game_category/image/(.*)\..*$ {
        try_files /category/$1.jpg $uri @server;
    }

    location ~ ^/group/image/(\w+)/(\w+)\..*$ {
        try_files /group/$2_$1.jpg $uri @server;
    }
    
    location ~ ^/user/image/(\w+)/(\w+)\..*$ {
        try_files /user/$2_$1.jpg $uri @server;
    }
    
    location ~ ^/watch/image/(\w+)/(\w+)\..*$ {
        try_files /watch/$2_$1.jpg $uri @server;
    }
    
    location ~ ^/plaza/image/(\w+)/(\w+)\..*$ {
        try_files /plaza/$2_$1.jpg $uri @server;
    }
    
    location ~ ^/story/image/(\w+)/(\w+)\..*$ {
        try_files /story/$2_$1.jpg $uri @server;
    }
    
    location ~ ^/story/audio/(\w+)\..*$ {
        try_files /story/$1.amr $uri @server;
    }

    location @server {
        proxy_pass http://unix:/YK01/static/static.sock;
        proxy_connect_timeout      90;
        proxy_send_timeout         90;
        proxy_read_timeout         90;
        proxy_buffer_size          4k;
        proxy_buffers              4 32k;
        proxy_busy_buffers_size    64k;
        proxy_temp_file_write_size 64k;
    }
    
    location /cache {
        internal;
        root /YK01/;
    }
}
```