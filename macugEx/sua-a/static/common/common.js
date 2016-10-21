function getCookie(c_name) {
    var i, x, y, ARRcookies = document.cookie.split(";");
    for (i = 0; i < ARRcookies.length; i++) {
        x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
        y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
        x = x.replace(/^\s+|\s+$/g, "");
        if (x == c_name) {
            return decodeURIComponent(y);
        }
    }
}

function setCookie(c_name, value, expire_second) {
    if (!expire_second) expire_second = 10;
    var exdate = new Date();
    exdate.setSeconds(exdate.getSeconds() + expire_second);
    var c_value = decodeURIComponent(value) + "; expires=" + exdate.toUTCString() + "; path=/";
    document.cookie = c_name + "=" + c_value;
}

function getUserId() {
    return getCookie('userid');
}

function getUser(func) {
    if (func) {
        var userid = getUserId();
        if (!userid) {
            func();
            return false;
        }
        $.get("/resource/user/" + userid, function (result) {
            if (result.code == 0) {
                setUser(result);
                func(result)
            } else {
                func();
            }
        });
    }
    return {
        'id': getCookie('userid'),
        'name': getCookie('user_name'),
        'grade': getCookie('user_grade'),
        'career': getCookie('user_career'),
        'phone': getCookie('user_phone')
    }
}

function setUser(user) {
    if (user.name) setCookie('user_name', user.name);
    if (user.grade) setCookie('user_grade', user.grade);
    if (user.career) setCookie('user_career', user.career);
    if (user.phone) setCookie('user_phone', user.phone);
}

function getJsTicket() {
    return getCookie('jsticket');
}

function generate_signature(nonce, timestamp) {
    var url = window.location.href.split('#')[0];
    var str = 'jsapi_ticket=' + getJsTicket() + '&noncestr=' + nonce + '&timestamp=' + timestamp + '&url=' + url;
    var defer = $.Deferred();
    $.getScript("/static/common/sha1.js", function (data, textStatus, jqxhr) {
        shaObj = new jsSHA(str, 'TEXT');
        var signature = shaObj.getHash('SHA-1', 'HEX');
        defer.resolve(signature);
    });
    // return defer
    return defer.promise(); // safe promise object
}

var _d = $.Deferred();
var complete = _d.promise(); // 微信jssdk可用时触发的全局 promise 对象

$.getScript("https://res.wx.qq.com/open/js/jweixin-1.0.0.js", function (data, textStatus, jqxhr) {
    var now = Math.round(new Date().getTime() / 1000);
    var nonce = Math.random().toString(36).substr(2, 15);

    $.when(generate_signature(nonce, now)).done(function (signature) {
        wx.config({
            debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
            appId: 'wxee9484c48bdb3464', // 必填，企业号的唯一标识，此处填写企业号corpid
            timestamp: now, // 必填，生成签名的时间戳
            nonceStr: nonce, // 必填，生成签名的随机串
            signature: signature,// 必填，签名，见附录1
            jsApiList: [
                'checkJsApi',
                'openLocation',
                'getLocation',
                'chooseImage',
                'previewImage',
                'uploadImage',
                'downloadImage',
                'scanQRCode'
            ] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
        });
    });

    wx.ready(function () {
        _d.resolve();
    });

});


complete.then(function () {
    var cache = getCookie('has-located');
    var userid = getUserId();
    if (!cache) {
        wx.getLocation({
            type: 'gcj02', // 默认为wgs84的gps坐标，如果要返回直接给openLocation用的火星坐标，可传入'gcj02'
            success: function (res) {
                var latitude = res.latitude; // 纬度，浮点数，范围为90 ~ -90
                var longitude = res.longitude; // 经度，浮点数，范围为180 ~ -180。
                var speed = res.speed; // 速度，以米/每秒计
                var accuracy = res.accuracy; // 位置精度
                $.post("/resource/user/" + userid, {
                    'lon': longitude,
                    'lat': latitude
                }, function (result) {
                    console.log('upload locating status: ' + result.code);
                    setCookie('has-located', '1', 300);
                })
            }
        });
    }
});



