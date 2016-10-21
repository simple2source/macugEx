(function(){
    $.ajax({
        url: "/conf.example",
    }).done(function(data) {
        $("textarea").val(data);
    });
})()

$('.reload').click(function(){
    window.location.reload(true);
});

function start_clocktick(){
    var outtime = parseInt($('#outtime').text());
    if(outtime > 0){
        $('#outtime').text(outtime - 1);
        setTimeout(start_clocktick, 1000);
    }
}

function stop_clocktick(){
    $('#outtime').text(0);
}

$('.next').click(function(){
    $.ajax({
        url: "http://"+window.location.hostname+":5700/config/example",
        method: 'POST',
        data: $("textarea").val(),
        dataType: 'json'
    }).done(function(result) {
        if(result.status == 'success'){
            $('.result').html('<p>编辑成功，正在检测数据库是否正确配置...<span id="outtime">60</span></p>');
            start_clocktick();
            test_mongo_connect();
        }else{
            $('.result').html('<p>配置文件有误，请重试</p><pre>'+result.data+'</pre>');
        }
    });
})

function test_mongo_connect(){
    $.ajax({
        url: "http://"+window.location.hostname+":5700/test_mongo/",
        method: 'GET',
        dataType: 'text'
    }).done(function(result){
        if(result == 'success'){
            $('.result').html('<p>配置完成，连接数据库成功，正在跳转...</p>')
            setTimeout(function(){
                location = './finish.html';
            }, 3000);
        }else{
            $('.result').append('<p>无法连接上数据库，请编辑 mongo 变量后重试。</p>' + '<pre>'+ result + '</pre>');
        }
        stop_clocktick();
    }).fail(function(xhr, status, error){
        $('.result').append('<p>检测数据库连接失败,请刷新页面重试.</p>');
        stop_clocktick();
    });
}
