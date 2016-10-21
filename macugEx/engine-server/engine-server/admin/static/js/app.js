var admin = angular.module('admin', ['ngRoute', 'angular-spinner', 'ui.bootstrap', 'ui.bootstrap.datetimepicker']);

admin.config(['$routeProvider', '$interpolateProvider', '$locationProvider', function ($routeProvider, $interpolateProvider, $locationProvider) {
    $routeProvider
        .when('/', {
            //FIXME 暂时转至profile页面
            templateUrl: "/static/views/profile.html",
            controller: "profile"
        })
        .when('/watch_info', {
            templateUrl: "/static/views/watch_info.html",
            controller: "watch_info"
        })
        .when('/user_info', {
            templateUrl: "/static/views/user_info.html",
            controller: "user_info"
        })
        .when('/group_info', {
            templateUrl: "/static/views/group_info.html",
            controller: "group_info"
        })
        .when('/watch_locate_info', {
            templateUrl: "/static/views/watch_locate_info.html",
            controller: "watch_locate_info"
        })
        .when('/watch_locus_info', {
            templateUrl: "/static/views/watch_locus_info.html",
            controller: "watch_locus_info"
        })
        .when('/user_locate_info', {
            templateUrl: "/static/views/user_locate_info.html",
            controller: "user_locate_info"
        })
        .when('/user_locus_info', {
            templateUrl: "/static/views/user_locus_info.html",
            controller: "user_locus_info"
        })
        .when('/devicetoken_info', {
            templateUrl: "/static/views/devicetoken_info.html",
            controller: "devicetoken_info"
        })
        .when('/watch_loger_info', {
            templateUrl: "/static/views/watch_loger_info.html",
            controller: "watch_loger_info"
        })
        .when('/story_info', {
            templateUrl: "/static/views/story_info.html",
            controller: "story_info"
        })
        .when('/story_upload', {
            templateUrl: "/static/views/story_upload.html",
            controller: "story_upload"
        })
        .when('/watch_online', {
            templateUrl: "/static/views/watch_online.html",
            controller: "watch_online"
        })
        .when('/watch_locate_analysis', {
            templateUrl: "/static/views/watch_locate_analysis.html",
            controller: "watch_locate_analysis"
        })
        .when('/user_locate_analysis', {
            templateUrl: "/static/views/user_locate_analysis.html",
            controller: "user_locate_analysis"
        })
        .when('/profile', {
            templateUrl: "/static/views/profile.html",
            controller: "profile"
        })
        .when('/user_create_analysis', {
            templateUrl: "/static/views/user_create_analysis.html",
            controller: "user_create_analysis"
        })
        .when('/group_create_analysis', {
            templateUrl: "/static/views/group_create_analysis.html",
            controller: "group_create_analysis"
        })
        .when('/admin_info', {
            templateUrl: '/static/views/admin_info.html',
            controller: 'admin_info'
        })
        .when('/version_android', {
            templateUrl: "/static/views/version_android.html",
            controller: "version_android"
        })
        .when('/appstore_category_info', {
            templateUrl: "/static/views/appstore_category_info.html",
            controller: "appstore_category_info"
        })
        .when('/plaza_info', {
            templateUrl: "/static/views/plaza_info.html",
            controller: "plaza_info"
        })
        .when('/submail_info', {
            templateUrl: "/static/views/submail_info.html",
            controller: "submail_info"
        })
        .when('/bluetooth_info', {
            templateUrl: "/static/views/bluetooth_info.html",
            controller: "bluetooth_info"
        })
        .when('/banner_info', {
            templateUrl: "/static/views/banner_info.html",
            controller: "banner_info"
        })
        .when('/answer_game_info', {
            templateUrl: "/static/views/answer_game_info.html",
            controller: "answer_game_info"
        })
        .when('/answer_game_category_info', {
            templateUrl: "/static/views/answer_game_category_info.html",
            controller: "answer_game_category_info"
        })
        .when('/service_manage', {
            templateUrl: "/static/views/service_manage.html",
            controller: "service_manage"
        })
        .when('/question_manage', {
            templateUrl: "/static/views/question_manage.html",
            controller: "question_manage"
        })
        .when('/answer_manage', {
            templateUrl: "/static/views/answer_manage.html",
            controller: "answer_manage"
        })
        .otherwise({
            templateUrl: '/static/views/profile.html',
            controller: 'profile'
        });

    $locationProvider.html5Mode({
        enabled: false,
        requireBase: true
    });

    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

function pagination(scope, q, http, url) {
    if (!scope.getLength) {
        // scope.getLength is function return the Promise
        if (http && url) {
            scope.getLength = function () {
                var deferred = q.defer();
                http.get(url, {
                    params: {
                        'find': JSON.stringify(scope.query)
                    }
                }).success(function (data) {
                    deferred.resolve(data);
                });
                return deferred.promise;
            }
        } else {
            throw Error('$scope undefinition "getLength" Method before pagination')
        }
    }
    var _pagination = function () {
        scope.getLength().then(function (data) {
            scope.length = parseInt(data);
            scope.totalPage = Math.ceil(scope.length / scope.num);
            var a = [];
            for (var i = 1; i < scope.totalPage + 1; i++) {
                a.push(i);
                if (i >= 10) break;
            }
            scope.pagelist = a;
        });
        scope._prev_num = scope.num;
        scope._prev_query = scope.query;
    };
    if (!scope._has_pagination) {
        _pagination();
        scope._has_pagination = true;
    }
    return _pagination
}

function JumpPage(scope) {
    if (!scope.getRecords) {
        throw Error('$scope undefinition "getRecords" Method before jumpPage');
    }
    if (!scope.numlist) scope.numlist = [10, 20, 30, 50, 100, 200, 300];
    if (!scope._paginateTotal) scope._paginateTotal = 10;
    if (!scope.length) scope.length = 0;
    if (!scope.num) scope.num = scope.numlist[0];
    if (!scope.pagelist) scope.pagelist = [];
    if (!scope.current_page) scope.current_page = 1;

    return function (page) {
        var k = 0;
        for (var i = 0; i < scope.pagelist.length; i++) {
            if (page == scope.pagelist[i]) k = 1;
        }
        var ignore = 0;
        if (!k && page == 1) {
            var a = [];
            for (var i = 0; i < this._paginateTotal; i++) {
                if (i >= scope.totalPage) break;
                a.push(i + 1);
            }
            scope.pagelist = a;
            ignore = 1;
        }
        if (!k && page == scope.totalPage) {
            var a = [];
            for (var i = 0; i < this._paginateTotal; i++) {
                var value = scope.totalPage - i;
                if (value <= 0) break;
                a.unshift(value);
            }
            scope.pagelist = a;
            ignore = 1;
        }
        if (!ignore && !k && page < scope.pagelist[0]) {
            var a = [];
            var last = scope.pagelist[0] - 1;
            for (var i = 0; i < this._paginateTotal; i++) {
                var value = last - i;
                if (value <= 0) break;
                a.unshift(value);
            }
            scope.pagelist = a;
        }
        if (!ignore && !k && page > scope.pagelist[scope.pagelist.length - 1]) {
            var a = [];
            var first = scope.pagelist[scope.pagelist.length - 1] + 1;
            for (var i = 0; i < this._paginateTotal; i++) {
                var value = first + i;
                if (value > scope.totalPage) break;
                a.push(value);
            }
            scope.pagelist = a;
        }
        scope.current_page = page;
        scope.getRecords();
    };
}

function QueryRecord(scope, http, url) {
    if (!scope.field) {
        throw Error('QueryRecord need $scope.field explicit');
    }
    scope.query = {};
    return function () {
        var params = {
            find: JSON.stringify(scope.query),
            field: JSON.stringify(scope.field),
            page: scope.current_page - 1,
            num: scope.num
        };
        if (scope.sort) {
            params['sort'] = JSON.stringify(scope.sort);
        }
        http.get(url, {
            params: params
        }).success(function (datas) {
            if (scope.record_handle) {
                scope.record_handle(datas)
            }
            scope.datas = datas;
        });
    }
}

function AggregateRecord(scope, http, url) {
    if (!scope.pipeline) {
        throw Error('AggregateRecord need $scope.pipeline explicit');
    }
    return function () {
        http.get(url, {
            params: {'pipeline': JSON.stringify(scope.pipeline)}
        }).success(function (datas) {
            if (scope.record_handle) {
                scope.record_handle(datas)
            }
            scope.datas = datas;
        });
    }
}

function validate_permission(scope, permission, func) {
    if (scope.permissions === undefined) {
        scope.request_permissions(function (data) {
            scope.permissions = data;
            var condition = data.indexOf('admin') != -1 || data.indexOf(permission) != -1;
            if (func) {
                func(condition);
            }
        });
    } else {
        var condition = scope.permissions.indexOf('admin') != -1 || scope.permissions.indexOf(permission) != -1;
        if (func) {
            func(condition)
        }
        return condition;
    }
}

admin.directive('submitForm', [function () {
    return {
        restrict: 'C',
        link: function ($scope, iElm, iAttrs, controller) {
            if ($(iElm).attr('form')) {
                var form_ident = $(iElm).attr('form');
            } else {
                var form_ident = '.Form';
            }
            iElm.bind("click", function () {
                var form = $(form_ident);
                if ($scope.prepare_submit) {
                    if (!$scope.prepare_submit(form)) {
                        return false;
                    }
                }
                form.ajaxForm();
                if ($scope.startSpinner) {
                    $scope.startSpinner();
                }
                if ($scope.ajaxFormSuccess) {
                    var success = $scope.ajaxFormSuccess;
                } else {
                    var success = function (data) {
                        if ($scope.stopSpinner) {
                            $scope.stopSpinner();
                        }
                        form.find('input').enable();
                        form.find('select').enable();
                        form.find('textarea').enable();
                        if (data == 'success') {
                            form.resetForm();
                            form.find('.i_image').remove();
                            form.find('.i_index').remove();
                            message('创建成功', '', 'success');
                            if ($scope.after_submit) {
                                $scope.after_submit(form);
                            }
                        } else {
                            message('错误', data, 'error')
                        }
                    }
                }
                if ($scope.ajaxFormError) {
                    var error = $scope.ajaxFormError;
                } else {
                    var error = function (resp, status) {
                        if ($scope.stopSpinner) {
                            $scope.stopSpinner();
                        }
                        console.log(resp, status);
                    }
                }
                form.ajaxSubmit({
                    success: success,
                    error: error
                });
            })
        }
    };
}]);

function getRandomColor() {
    var letters = '0123456789abcdef'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function timeConverter(UNIX_timestamp) {
    var a = new Date(UNIX_timestamp * 1000);
    var year = a.getFullYear();
    var month = a.getMonth() + 1;
    month = month >= 10 ? month : '0' + month;
    var date = a.getDate();
    var hour = a.getHours();
    hour = hour >= 10 ? hour : '0' + hour;
    var min = a.getMinutes();
    min = min >= 10 ? min : '0' + min;
    var sec = a.getSeconds();
    sec = sec >= 10 ? sec : '0' + sec;
    var time = year + '-' + month + '-' + date + ' ' + hour + ':' + min + ':' + sec;
    return time;
}

function PolyFitForcast() {
    /**
     * <p>
     * 函数功能：最小二乘法曲线拟合
     * </p>
     * <p>
     * 方程:Y = a(0) + a(1) * (X - X1)+ a(2) * (X - X1)^2 + ..... .+ a(m) * (X -
     * X1)^m X1为X的平均数
     * </p>
     *
     * @param x
     *            实型一维数组,长度为 n. 存放给定 n 个数据点的 X 坐标
     * @param y
     *            实型一维数组,长度为 n.存放给定 n 个数据点的 Y 坐标
     * @param n
     *            变量。给定数据点的个数
     * @param a
     *            实型一维数组，长度为 m.返回 m-1 次拟合多项式的 m 个系数
     * @param m
     *            拟合多项式的项数，即拟合多项式的最高次数为 m-1. 要求 m<=n 且m<=20。若 m>n 或 m>20
     *            ，则本函数自动按 m=min{n,20} 处理.
     *            <p>
     *            Date:2007-12-25 16:21 PM
     *            </p>
     * @author qingbao-gao
     * @return 多项式系数存储数组
     */
    function PolyFit(x, y, n, a, m) {
        var i, j, k;
        var z, p, c, g, q = 0, d1, d2;
        var s = new Array(20);
        var t = new Array(20);
        var b = new Array(20);
        var dt = new Array(3);
        for (i = 0; i <= m - 1; i++) {
            a[i] = 0.0;
        }
        if (m > n) {
            m = n;
        }
        if (m > 20) {
            m = 20;
        }
        z = 0.0;
        for (i = 0; i <= n - 1; i++) {
            z = z + x[i] / (1.0 * n);
        }
        b[0] = 1.0;
        d1 = 1.0 * n;
        p = 0.0;
        c = 0.0;
        for (i = 0; i <= n - 1; i++) {
            p = p + (x[i] - z);
            c = c + y[i];
        }
        c = c / d1;
        p = p / d1;
        a[0] = c * b[0];
        if (m > 1) {
            t[1] = 1.0;
            t[0] = -p;
            d2 = 0.0;
            c = 0.0;
            g = 0.0;
            for (i = 0; i <= n - 1; i++) {
                q = x[i] - z - p;
                d2 = d2 + q * q;
                c = c + y[i] * q;
                g = g + (x[i] - z) * q * q;
            }
            c = c / d2;
            p = g / d2;
            q = d2 / d1;
            d1 = d2;
            a[1] = c * t[1];
            a[0] = c * t[0] + a[0];
        }
        for (j = 2; j <= m - 1; j++) {
            s[j] = t[j - 1];
            s[j - 1] = -p * t[j - 1] + t[j - 2];
            if (j >= 3)
                for (k = j - 2; k >= 1; k--) {
                    s[k] = -p * t[k] + t[k - 1] - q * b[k];
                }
            s[0] = -p * t[0] - q * b[0];
            d2 = 0.0;
            c = 0.0;
            g = 0.0;
            for (i = 0; i <= n - 1; i++) {
                q = s[j];
                for (k = j - 1; k >= 0; k--) {
                    q = q * (x[i] - z) + s[k];
                }
                d2 = d2 + q * q;
                c = c + y[i] * q;
                g = g + (x[i] - z) * q * q;
            }
            c = c / d2;
            p = g / d2;
            q = d2 / d1;
            d1 = d2;
            a[j] = c * s[j];
            t[j] = s[j];
            for (k = j - 1; k >= 0; k--) {
                a[k] = c * s[k] + a[k];
                b[k] = t[k];
                t[k] = s[k];
            }
        }
        dt[0] = 0.0;
        dt[1] = 0.0;
        dt[2] = 0.0;
        for (i = 0; i <= n - 1; i++) {
            q = a[m - 1];
            for (k = m - 2; k >= 0; k--) {
                q = a[k] + q * (x[i] - z);
            }
            p = q - y[i];
            if (Math.abs(p) > dt[2]) {
                dt[2] = Math.abs(p);
            }
            dt[0] = dt[0] + p * p;
            dt[1] = dt[1] + Math.abs(p);
        }
        return a;
    }// end

    /**
     * <p>
     * 对X轴数据节点球平均值
     * </p>
     *
     * @param x
     *            存储X轴节点的数组
     *            <p>
     *            Date:2007-12-25 20:21 PM
     *            </p>
     * @author qingbao-gao
     * @return 平均值
     */
    function average(x) {
        var ave = 0;
        var sum = 0;
        if (x !== null) {
            for (var i = 0; i < x.length; i++) {
                sum += x[i];
            }
            ave = sum / x.length;
        }
        return ave;
    }

    /**
     * <p>
     * 由X值获得Y值
     * </p>
     * @param x
     *            当前X轴输入值,即为预测的月份
     * @param xx
     *            当前X轴输入值的前X数据点
     * @param a
     *            存储多项式系数的数组
     * @param m
     *            存储多项式的最高次数的数组
     *            <p>
     *            Date:2007-12-25 PM 20:07
     *            </p>
     * @return 对应X轴节点值的Y轴值
     */
    function getY(x, xx, a, m) {
        var y = 0;
        var ave = average(xx);

        var l = 0;
        for (var i = 0; i < m; i++) {
            l = a[0];
            if (!(a[i] < 0) && !(a[i] > 0)) {
                a[i] = 0;
            }
            if (i > 0) {
                y += a[i] * Math.pow((x - ave), i);
            }
        }
        return (y + l);
    }

    /**
     * 返回拟合后的点坐标数组
     * @param  {Array} arr 点坐标数组
     * @return {Array}     拟合后的点坐标数组
     */
    this.get = function (arr, m) {
        var arrX = [], arrY = [];

        for (var i = 0; i < arr.length; i++) {
            arrX.push(arr[i][0]);
            arrY.push(arr[i][1]);
        }

        var len = arrY.length;
        var a = new Array(arrX.length);
        var aa = PolyFit(arrX, arrY, len, a, m);
        var arrRes = [];
        for (var i = 0; i < len; i++) {
            arrRes.push([arrX[i], getY(arrX[i], arrX, aa, m)]);
        }

        return arrRes;
    };
}

function check_object_id(object_id) {
    if (object_id.length < 24) {
        message('id长度不够', 'ObjectId为24位长', 'info');
        return false;
    } else if (object_id.length > 24) {
        message('id长度超过', 'ObjectId为24位长', 'info');
        return false;
    }
    var ValidChar = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 97, 98, 99, 100, 101, 102];
    for (var i in object_id) {
        var a = object_id[i].charCodeAt(0);
        var s = ValidChar.indexOf(a);
        if (s == -1) {
            message('含有非0x0~0xF字符', 'ObjectId格式不正确', 'info');
            return false;
        }
    }
    return true;
}

