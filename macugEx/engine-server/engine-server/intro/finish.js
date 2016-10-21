function runing(program, success, error){
    $.ajax({
        url: "http://"+window.location.hostname+":5700/runing/"+program,
        dataType: 'json'
    }).done(function(data) {
        if(data.status == 'success'){
            success(data.port);
        }else{
            error();
        }
    });
}

function start(program, success, error){
    $.ajax({
        url: "http://"+window.location.hostname+":5700/start/"+program,
    }).done(function(data) {
        if(data == 'success'){
            success()
        }else{
            error()
        }
    });
}

function server_success(){
    $("#result").append('<p>设备服务已经启动, 阅读 <a href="../docs/_build/html/emulate.html" target="_blank">模拟器</a> 文档进行测试使用。</p>');
};
function server_error(){
    var p = $('<p>设备服务未能启动 <button class="button">立即启动</button></p>');
    $("#result").append(p);
    p.find('button').click(function(){
        start('devices',
            function(){
                p.remove();
                setTimeout(function(){
                    runing('server', server_success, server_error);
                },3000);
            },
            function(){
                p.remove();
                server_error();
            }
        );
    });
};
runing('server', server_success, server_error);

function api_success(api_port){
    $("#result").append('<p>api服务已经启动, 打开示例链接测试：<a href="http://'+window.location.hostname+':'+api_port+'/online?num=0&page=10" target="_blank">查看在线设备接口</a>。</p>');
}
function api_error(){
    var p = $('<p>api服务未能启动 <button class="button">立即启动</button></p>');
    $("#result").append(p);
    p.find('button').click(function(){
        start('apis',
            function(){
                p.remove();
                setTimeout(function(){
                    runing('api', api_success, api_error);
                },3000);
            },
            function(){
                p.remove();
                api_error();
            }
        );
    });

}
runing('api', api_success, api_error);

function agent_success(){
    $("#result").append('<p>agent服务已经启动, 其他三个服务可以使用了。</p>');
}
function agent_error(){
    var p = $('<p>agent服务未能启动 <button class="button">立即启动</button></p>');
    $("#result").append(p);
    p.find('button').click(function(){
        start('agent',
            function(){
                p.remove();
                setTimeout(function(){
                    runing('broker', agent_success, agent_error);
                },3000);
            },
            function(){
                p.remove();
                agent_error();
            }
        );
    });

}
runing('broker', agent_success, agent_error);

function admin_success(port){
    $("#result").append('<p>admin服务已经启动, 登录<a href="http://'+window.location.hostname+':'+port+'/admin/" target="_blank">后台界面</a>（默认账号：admin 密码：admin）。</p>');
}
function admin_error(){
    var p = $('<p>admin服务未能启动 <button class="button">立即启动</button></p>');
    $("#result").append(p);
    p.find('button').click(function(){
        start('admin',
            function(){
                p.remove();
                setTimeout(function(){
                    runing('admin', admin_success, admin_error);
                },3000);
            },
            function(){
                p.remove();
                admin_error();
            }
        );
    });

}
runing('admin', admin_success, admin_error);





















