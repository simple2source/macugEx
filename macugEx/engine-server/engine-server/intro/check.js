content = $('#content');
total = 6;

pymongo = "check_module(\'pymongo\',\'无法找到 pymongo，执行 pip install pymongo 进行安装，完成后刷新页面重试.\')";
pymysql = "check_module(\'pymysql\',\'无法找到 pymysql，执行 pip install pymysql 进行安装，完成后刷新页面重试.\')";

function finish(){
    if(total == 0){
        content.append('<p>项目所需依赖包都已安装.</p>');
        content.append('<p>选择您所使用的数据库 <button onclick="'+pymongo+'">Mongodb</button> <s>或 <button disabled=true><s>Mysql</s></button></s>(暂不支持)。</p>');
    }
    if(total == -1){ //已选择数据库驱动并满足
        $("button").attr("onclick", "");
        content.append('<p>数据库驱动已满足，请继续完善配置文件.</p><br/><a class="button" href="./config.html">下一步</a>');
    }
}

function check_module(module, warning){
    $.ajax({
        url: "http://"+window.location.hostname+":5700/check/" + module,
        dataType: 'text'
    }).done(function(data) {
        if(data=='success')
        {
            content.append('<p class="italic">'+module+'已安装.</p>');
            total = total - 1;
            finish();
        }else{
            content.append('<p class="italic">'+warning+'</p>');
        }
    }).fail(function(xhr, status, error){
        content.append('<p>'+module+'<span class="error">检查失败</span>,请刷新页面<a href="javascript:window.location.reload(true);">重试</a>.</p>');
    });
}

setTimeout(function(){
    check_module('pip', '无法在您的系统中找到包管理工具 pip，请按 <a href="https://pip.pypa.io/en/stable/installing/" target="_blank">PIP INSTALL</a> 引导安装.');
},100);
setTimeout(function(){
    check_module('flask', '无法找到 flask，执行 pip install flask 进行安装，完成后刷新页面重试.');
},200);
setTimeout(function(){
    check_module('gevent', '无法找到 gevent，执行 pip install gevent 进行安装，完成后刷新页面重试.\
                    <br/>（windows机器需要从 <a href="http://www.lfd.uci.edu/~gohlke/pythonlibs/#gevent">gevent</a> 处下载）');
},300);
setTimeout(function(){
    check_module('zmq', '无法找到 pyzmq，pip install pyzmq 进行安装，完成后刷新页面重试.');
},400);
setTimeout(function(){
    check_module('paho-mqtt', '无法找到 paho-mqtt，pip install paho-mqtt 进行安装，完成后刷新页面重试.');
},500);
setTimeout(function(){
    check_module('apnsclient', '无法找到 apns-client，pip install apns-client 进行安装，完成后刷新页面重试.');
},600);








