admin.controller('main_container', function ($scope, $q, $rootScope, $http) {
    $scope.$on('active', function (event, name, page_name) {
        var p = $('.profile');
        if (name == 'profile') {
            $('#sidebar-menu li.active').click();
            p.addClass('active');
            p.css('background-color', 'rgba(255,255,255,0.5)');
            p.css('border-right', '5px solid #1ABB9C');
        } else {
            if (p.hasClass('active')) {
                p.removeClass('active');
                p.css('background-color', 'rgba(255,255,255,0)');
                p.css('border-right', '');
            }
            var li = $('li[control="' + name + '"]');
            li.click();
            $('#sidebar-menu li').removeClass('current-page');
            li.addClass('current-page');
        }
        $scope.page_name = page_name;
        $scope.name = name;
    });
    $scope.$on('update', function (event, data) {
        for (var k in data) {
            if (k) {
                $scope[k] = data[k];
            }
        }
    });
    $scope.logout = function () {
        $http.post('/logout').success(function (data) {
            window.location = '/login?ref=/admin';
        });
    };
    $scope.request_permissions = function (func) {
        $http.put('/admin/', 'permissions').success(func);
    };
    $scope.request_permissions(function (data) {
        $scope.permissions = data;
    });
});

//admin.controller('profile', function ($scope, $q, $rootScope, $http) {
//    $scope.$emit("active", "profile", "管理员信息查看");
//    $http.get('/admin/profile').success(function (data) {
//        $scope.data = data;
//        $scope.nickname = data['nickname'];
//    });
//    $scope.modify_name = function () {
//        $http.post('/admin/profile', {'nickname': $scope.nickname}).success(function (data) {
//            if (data == 'success') {
//                $scope.$emit("update", {'username': $scope.nickname});
//                message('修改成功', '', 'success');
//            }
//        });
//    }
//});

admin.controller('watch_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "watch_info", "腕表信息");
    $scope.field = ['_id', 'maketime', 'lasttime', 'mac', 'authcode', 'status', 'group_id', 'name', 'phone', 'customer_id', 'software_v', 'bluetooth_v'];
    $scope.searchRecords = function () {
        if (!$scope.imei) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = {'$regex': '.*' + $scope.imei + '.*'};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/device');
    $scope.record_handle = function (datas) {
        for (var i in datas) {
            if (datas[i]['alarms']) {
                datas[i]['alarms'] = JSON.stringify(datas[i]['alarms'], null, 2);
                if (datas[i]['alarms'] == '{}') {
                    delete datas[i]['alarms']
                }
            }
        }
    };
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/watch/count')
    validate_permission($scope, 'watch_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (imei) {
        var confirm = window.confirm("确定删除 " + imei + " ？");
        if (confirm) {
            $http.post('/admin/watch/delete', {
                'find': {'_id': imei}
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == imei) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('profile', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "user", "管理员管理");
    $scope.field = ['_id', 'maketime', 'lasttime', 'nickname', 'permissions'];
    $scope.searchRecords = function () {
        if (!$scope._id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = {'$regex': '.*' + $scope._id + '.*'};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/admin');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/admin/count');

    $scope.new_permissions = [];
    $scope.addPermissions = function (event) {
        var val = $(event.target).prev().val();
        if (!val) {
            return false;
        }
        for (var i in $scope.new_permissions) {
            if ($scope.new_permissions[i] == val) {
                return false;
            }
        }
        $scope.new_permissions.push(val);
    };
    $scope.delPermissions = function (event) {
        // var btn = $(event.target);
        // var val = btn.prev().prev().val();
        // new_permissions = [];
        // for (var i in $scope.new_permissions) {
        //     if ($scope.new_permissions[i] != val) {
        //         new_permissions.push($scope.new_permissions[i]);
        //     }
        // }
        // $scope.new_permissions = new_permissions;
        $scope.new_permissions.pop();
    };
    $scope.prepare_submit = function (form) {
        var _id = form.find('input[name="_id"]').val();
        if (!_id) {
            message('新账号id参数未填', '', 'error');
            return false;
        } else {
            try {
                JSON.parse(_id);
                if (isNaN(_id)) {
                    form.find('input[name="_id"]').val(_id);
                } else {
                    form.find('input[name="_id"]').val('"' + _id + '"');
                }
            }
            catch (err) {
                form.find('input[name="_id"]').val(JSON.stringify(_id));
            }
        }
        var nickname = form.find('input[name="nickname"]').val();
        if (nickname) {
            try {
                JSON.parse(nickname);
                if (isNaN(nickname)) {
                    form.find('input[name="nickname"]').val(nickname);
                } else {
                    form.find('input[name="nickname"]').val('"' + nickname + '"');
                }
            }
            catch (err) {
                form.find('input[name="nickname"]').val(JSON.stringify(nickname));
            }
        }
        if (!$scope.new_permissions.length) {
            message('新账号权限未添加', '', 'error');
            return false;
        }
        return true;
    };
    $scope.after_submit = function () {
        $scope.getRecords();
    };
    $scope.delete = function (_id) {
        var confirm = window.confirm("确定删除 " + _id + " ？");
        if (confirm) {
            $http.post('/admin/admin/delete', {'_id': _id}).success(function (data) {
                if (data == 'success') {
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == _id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                    message('操作成功', '', 'success');
                } else {
                    message(data, '', 'error');
                }
            });
        }
        ;
    };
    $scope.modify = function (_id) {
        var modal = $('#myModal2');
        modal.modal('show');
        id_text = modal.find('input[name="_id"]');
        id_text.val(_id);
        for (var i in $scope.datas) {
            if ($scope.datas[i]['_id'] == _id) {
                $scope.temp = {};
                for (var j in $scope.datas[i]) {
                    if (Object.prototype.toString.call($scope.datas[i][j]) === '[object Array]') {
                        $scope.temp[j] = $scope.datas[i][j].slice();
                    } else {
                        $scope.temp[j] = $scope.datas[i][j];
                    }
                }
            }
        }
    };
    $scope.addPermissions_temp = function (event) {
        var val = $(event.target).prev().val();
        if (!val) {
            return false;
        }
        for (var i in $scope.temp['permissions']) {
            if ($scope.temp['permissions'][i] == val) {
                return false;
            }
        }
        $scope.temp['permissions'].push(val);
    };
    $scope.delPermissions_temp = function (event) {
        // var btn = $(event.target);
        // var val = btn.prev().prev().val();
        // new_permissions = [];
        // for (var i in $scope.temp['permissions']) {
        //     if ($scope.temp['permissions'][i] != val) {
        //         new_permissions.push($scope.temp['permissions'][i]);
        //     }
        // }
        // $scope.temp['permissions'] = new_permissions;
        $scope.temp['permissions'].pop();
    };
    $scope.submit_temp = function () {
        $http.post('/admin/admin', {
            '_id': $scope.temp['_id'],
            'nickname': $scope.temp['nickname'],
            'permissions': $scope.temp['permissions']
        }).success(function (data) {
            if (data == 'success') {
                $scope.getRecords();
                message('修改成功', '', 'success');
            } else {
                message(data, '', 'error');
            }
        })
    };
    $scope.ajaxFormError = function (response, status) {
        if (response.status == 403) {
            message('没有权限', '', 'error');
        }
    };
    validate_permission($scope, 'admin', function (ok) {
        if (ok) $scope.isAdmin = true;
    });
});

admin.controller('user_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "user_info", "用户信息");
    $scope.field = ['_id', 'session', 'name', 'image_id', 'phone', 'share_locate', 'group_id', 'maketime'];
    $scope.searchRecords = function () {
        if (!$scope.user_id) {
            $scope.query = {};
        } else {
            if (!check_object_id($scope.user_id)) return false;
            $scope.query['_id'] = {'__type__': 'ObjectIdType', '__value__': $scope.user_id};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/user');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/user/count');
});

admin.controller('group_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "group_info", "圈子信息");
    $scope.field = ['_id', 'name', 'email', 'brief', 'users', 'devs', 'contacts', 'maketime'];
    $scope.searchRecords = function () {
        if (!$scope.group_id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = {
                '__type__': 'IntType',
                '__value__': $scope.group_id
            };
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/group');
    $scope.record_handle = function (datas) {
        for (var i in datas) {
            if (datas[i]['users']) {
                datas[i]['users'] = JSON.stringify(datas[i]['users'], null, 1);
                if (datas[i]['users'] == '{}') {
                    delete datas[i]['users']
                }
            }
            if (datas[i]['devs']) {
                datas[i]['devs'] = JSON.stringify(datas[i]['devs'], null, 1);
                if (datas[i]['devs'] == '{}') {
                    delete datas[i]['devs']
                }
            }
        }
        validate_permission($scope, 'admin', function (ok) {
            if (!ok) return false;
            $http.get('/admin/group', {
                params: {
                    find: JSON.stringify($scope.query),
                    field: JSON.stringify(['_id', 'password']),
                    page: $scope.current_page - 1,
                    num: $scope.num
                }
            }).success(function (new_datas) {
                for (var i = 0; i < new_datas.length; i++) {
                    for (var j = 0; j < datas.length; j++) {
                        if (j['_id'] == i['_id']) {
                            j['password'] = i['password']
                        }
                    }
                }
            });
        });
    };
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/group/count');
});

admin.controller('watch_locate_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "watch_locate_info", "腕表定位信息");
    $scope.field = ['imei', 'loc', 'raw_loc', 'timestamp', 'address', 'province', 'city', 'type', 'radius'];
    $scope.sort = ['timestamp', -1];
    $scope.searchRecords = function () {
        $scope.query = {};
        if ($scope.imei) {
            $scope.query['imei'] = $scope.imei;
        } else {
            if ($scope.query['imei']) {
                delete $scope.query['imei']
            }
        }
        if ($scope.type) {
            $scope.query['type'] = $scope.type;
        } else {
            if ($scope.query['type']) {
                delete $scope.query['type']
            }
        }
        var start = $scope.startDateTime ? $scope.startDateTime.getTime() : 0;
        var end = $scope.endDateTime ? $scope.endDateTime.getTime() : 0;
        $scope.query['timestamp'] = {};
        if (start) {
            $scope.query['timestamp']['$gt'] = start / 1000;
        } else {
            if ($scope.query['timestamp']['$gt']) {
                delete $scope.query['timestamp']['$gt'];
            }
        }
        if (end) {
            $scope.query['timestamp']['$lt'] = end / 1000;
        } else {
            if ($scope.query['timestamp']['$lt']) {
                delete $scope.query['timestamp']['$lt'];
            }
        }
        if (!start && !end) {
            delete $scope.query['timestamp']
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.numlist = [10, 20, 30, 50, 80, 100, 150, 200, 300, 500];
    $scope.getRecords = QueryRecord($scope, $http, '/admin/watch_locate');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/watch_locate/count');
    $scope.freshQuery = function () {
        $scope.datas = [];
        $scope.query = {};
        delete $scope.startDateTime;
        delete $scope.endDateTime;
        $scope.num = $scope.selectTimeRange ? 500 : 10;
    };
    var map = new AMap.Map('amap_container', {
        resizeEnable: true
    });
    AMap.plugin(['AMap.MapType', 'AMap.ToolBar', 'AMap.Scale'], function () {
        var toolbar = new AMap.ToolBar();
        map.addControl(toolbar);
        var scale = new AMap.Scale();
        map.addControl(scale);
        var type = new AMap.MapType({
            defaultType: 0 //使用2D地图
        });
        map.addControl(type);

    });
    $scope.map = map;
    $scope.mapShow = function () {
        $scope.mapShowed = true;
        $scope.paginate_style = {
            'padding-top': '20px'
        };
        $('#menu_toggle').click();
    };
    $scope.mapHide = function () {
        $scope.mapShowed = false;
        $scope.paginate_style = {};
        $('#menu_toggle').click();
    };
    $scope.record_handle = function (datas) {
        if (!datas.length) {
            return false;
        }
        $scope.filter_type = 'all';
        $scope.map.clearMap();
        $scope.map.setZoomAndCenter(15, datas[0]['loc']);

        var line = {};
        for (var i in datas) {
            var p = datas[i];
            if (!line[p['imei']]) {
                line[p['imei']] = {
                    'points': [],
                    'point_types': []
                };
            }
            var m = new AMap.Marker({
                position: p['loc'],
                title: p['imei'] + '(' + timeConverter(p['timestamp']) + ')',
                map: $scope.map,
                offset: new AMap.Pixel(-8, -8)
            });
            if (p['type'] == 1) {
                var icon = new AMap.Icon({
                    image: '/static/images/red.png',
                    size: new AMap.Size(17, 17)
                });
                m.setIcon(icon);
                line[p['imei']]['point_types'].push(1);
            } else {
                var icon = new AMap.Icon({
                    image: '/static/images/blue.png',
                    size: new AMap.Size(17, 17)
                });
                m.setIcon(icon);
                line[p['imei']]['point_types'].push(0);
            }
            line[p['imei']]['points'].push(p['loc']);
        }
        $scope.line = line;
    };
    $scope.curve_fitting = function () {
        var p = $scope.map.getAllOverlays('polyline');
        for (var i in p) {
            if (p[i].line_type != 'drawing') $scope.map.remove(p[i]);
        }
        for (var imei in $scope.line) {
            var points = $scope.line[imei]['points'];
            var slice = [];
            var i = 0;
            while (1) {
                var s = points.slice(i, i + $scope.slice_num);
                if (s.length == 0) {
                    break;
                }
                i += $scope.slice_num;
                var res = new PolyFitForcast().get(s, $scope.m);
                slice.push(res);
            }
            var polyline = [];
            for (var i in slice) polyline = polyline.concat(slice[i]);
            $.unique(polyline);
            // 去除无效点
            x_max = 0;
            x_min = 999;
            y_max = 0;
            y_min = 999;
            for (var i in points) {
                if (points[i][0] > x_max) x_max = points[i][0];
                if (points[i][0] < x_min) x_min = points[i][0];
                if (points[i][1] > y_max) y_max = points[i][1];
                if (points[i][1] < y_min) y_min = points[i][1];
            }
            var polyline_well = [];
            for (var i in polyline) {
                if ((polyline[i][0] > x_max) || (polyline[i][0] < x_min) || (polyline[i][1] > y_max) || (polyline[i][1] < y_min)) continue;
                polyline_well.push(polyline[i]);
            }
            new AMap.Polyline({
                path: polyline_well,
                strokeColor: getRandomColor(),
                map: $scope.map
            });
        }
    };
    $scope.line_draw = function () {
        var L = $scope.map.getAllOverlays('polyline');
        for (var i in L) {
            if (L[i].line_type == 'drawing') $scope.map.remove(L[i]);
        }
        for (var imei in $scope.line) {
            var points = $scope.line[imei]['points'];
            var polyline_point = [];
            for (var i in points) {
                polyline_point.push(points[i]);
            }
            var polyline = new AMap.Polyline({
                path: polyline_point,
                strokeColor: getRandomColor(),
                map: $scope.map
            });
            polyline.line_type = 'drawing';
        }
    };
    function copy_line(old_line) {
        // $scope.line = {'201615622711702': {
        //  'points': [[113.3626424, 23.1337272], [113.3626424, 23.1337272]],
        //  'point_types': [0, 1]
        // }}
        var line = {};
        for (var imei in old_line) {
            line[imei] = {};
            line[imei]['points'] = old_line[imei]['points'].slice();
            line[imei]['point_types'] = old_line[imei]['point_types'].slice();
        }
        return line;
    }

    $scope.point_filter = function () {
        if ($scope.filter_type == 'all') {
            if ($scope._stashed) {
                $scope.line = copy_line($scope._stash_line);
                $scope._stashed = false;
            }
            $scope.point_draw();
        }
        else {
            if (!$scope._stashed) {
                $scope._stash_line = copy_line($scope.line);
                $scope._stashed = true;
            }
            else {
                $scope.line = copy_line($scope._stash_line);
            }
            for (var imei in $scope.line) {
                var new_points = [];
                var new_types = [];
                for (var i in $scope.line[imei]['points']) {
                    if ($scope.filter_type == 'gps' && $scope.line[imei]['point_types'][i] == 1) {
                        new_points.push($scope.line[imei]['points'][i]);
                        new_types.push(1);
                    }
                    if ($scope.filter_type == 'lbs' && $scope.line[imei]['point_types'][i] != 1) {
                        new_points.push($scope.line[imei]['points'][i])
                        new_types.push(0);
                    }
                }
                $scope.line[imei]['points'] = new_points;
                $scope.line[imei]['point_types'] = new_types;
            }
            $scope.point_draw();
        }
    };
    $scope.point_draw = function () {
        var L = $scope.map.getAllOverlays('polyline');
        for (var i in L) {
            $scope.map.remove(L[i]);
        }
        var P = $scope.map.getAllOverlays('marker');
        for (var i in P) {
            $scope.map.remove(P[i]);
        }
        for (var imei in $scope.line) {
            for (var i in $scope.line[imei]['points']) {
                var loc = $scope.line[imei]['points'][i];
                var type = $scope.line[imei]['point_types'][i];
                var m = new AMap.Marker({
                    position: loc,
                    map: $scope.map,
                    offset: new AMap.Pixel(-8, -8)
                });
                if (type == 1) {
                    var icon = new AMap.Icon({
                        image: '/static/images/red.png',
                        size: new AMap.Size(17, 17)
                    });
                    m.setIcon(icon);
                } else {
                    var icon = new AMap.Icon({
                        image: '/static/images/blue.png',
                        size: new AMap.Size(17, 17)
                    });
                    m.setIcon(icon);
                }
            }
        }
    };
});

admin.controller('watch_locus_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "watch_locus_info", "腕表轨迹信息");
    $scope.field = ['imei', 'timestamp', 'address', 'lon', 'lat', 'type', 'radius'];
    $scope.searchRecords = function () {
        if (!$scope.imei) {
            $scope.query = {};
        } else {
            $scope.query['imei'] = $scope.imei;
        }
        if ($scope.type) {
            $scope.query['type'] = $scope.type;
        } else {
            if ($scope.query['type']) {
                delete $scope.query['type']
            }
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/watch_locus');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/watch_locus/count');
});

admin.controller('user_locate_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "user_locate_info", "用户定位信息");
    $scope.field = ['user_id', 'loc', 'timestamp', 'address', 'province', 'city', 'radius'];
    $scope.searchRecords = function () {
        if (!$scope.user_id) {
            $scope.query = {};
        } else {
            $scope.query['user_id'] = $scope.user_id;
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/user_locate');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/user_locate/count');
});

admin.controller('user_locus_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "user_locus_info", "用户轨迹信息");
    $scope.field = ['user_id', 'lat', 'lon', 'radius', 'timestamp'];
    $scope.searchRecords = function () {
        if (!$scope.user_id) {
            $scope.query = {};
        } else {
            $scope.query['user_id'] = $scope.user_id;
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/user_locus');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/user_locus/count');
});

admin.controller('devicetoken_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "devicetoken_info", "用户 devicetoken 信息查看");
    $scope.field = ['user_id'];
    $scope.searchRecords = function () {
        if (!$scope.user_id) {
            $scope.query = {};
        } else {
            $scope.query['user_id'] = $scope.user_id;
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/devicetoken');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/devicetoken/count');
});

admin.controller('watch_loger_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "watch_loger_info", "腕表指令日志查看");
    $scope.field = ['imei', 'event', 'itype', 'data', 'timestamp'];
    $scope.instruct_list = {
        '0x01': 1, '0x02': 2, '0x03': 3,
        '0x04': 4, '0x05': 5, '0x06': 6, '0x07': 7, '0x08': 8, '0x0a': 10, '0x0b': 11, '0x0c': 12, '0x0e': 14,
        '0x10': 16, '0x12': 18, '0x14': 20, '0x16': 22, '0x17': 23, '0x18': 24, '0x1a': 26, '0x1b': 27, '0x1c': 28,
        '0x1d': 29, '0x1e': 30, '0x1f': 31, '0x20': 32, '0x22': 34, '0x24': 36, '0x26': 38, '0x28': 40, '0x29': 41,
        '0x31': 49, '0x33': 51, '0x34': 52, '0x35': 53, '0x36': 54, '0x37': 55, '0x38': 56, '0x3a': 58, '0x3c': 60,
        '0x3d': 61, '0x3f': 63, '0x40': 64, '0x41': 65, '0x42': 66, '0x43': 67, '0x44': 68, '0x45': 69, '0x46': 70
    };
    $scope.searchRecords = function () {
        if (!$scope.imei) {
            $scope.query = {};
        } else {
            $scope.query['imei'] = $scope.imei;
        }
        if ($scope.instruct) {
            $scope.query['itype'] = $scope.instruct;
        } else {
            if ($scope.query['itype']) {
                delete $scope.query['itype']
            }
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/watch_loger');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/watch_loger/count');
});

admin.controller('story_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "story_info", "故事列表");
    $scope.field = ['_id', 'title', 'brief', 'image_id', 'category_id', 'audio_id', 'content_id'];
    $scope.searchRecords = function () {
        if (!$scope.story_id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = {'__ObjectId__': $scope.story_id};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/story');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/story/count');
    validate_permission($scope, 'story_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (story_id) {
        var confirm = window.confirm("确定删除 " + story_id + " ？");
        if (confirm) {
            $http.post('/admin/story/delete', {
                'find': {
                    '_id': {
                        '$in': [{
                            '__type__': 'ObjectIdType',
                            '__value__': story_id
                        }]

                    }
                }
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == story_id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('story_upload', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "story_upload", "上传腕表故事");
    $scope.category_list = [{'_id': 'story', 'name': '故事'}];
});

admin.controller('watch_online', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "watch_online", "在线腕表");
    $scope.searchRecords = function () {
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = function () {
        $http.get('/admin/watch/getlist', {
            params: {
                imei: $scope.imei,
                page: $scope.current_page - 1,
                num: $scope.num
            }
        }).success(function (imei_list) {
            $scope.imei_list = imei_list;
        });
    };
    $scope.jumpPage = JumpPage($scope);
    $scope.getLength = function () {
        var deferred = $q.defer();
        $http.get('/admin/watch/gettotal').success(function (data) {
            deferred.resolve(data);
        });
        return deferred.promise;
    };
    $scope.pagination = pagination($scope, $q);
});

admin.controller('watch_locate_analysis', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "watch_locate_analysis", "腕表地域信息统计");

    $scope.echart = echarts.init(document.getElementById('echat_container'));
    $http.get('/static/json/china.json').success(function (chinaJson) {
        echarts.registerMap('china', chinaJson);
    });
    $scope.option = {
        title: {text: '', subtext: '', x: 'center'},
        tooltip: {trigger: 'item', formatter: '{b} : {c}'},
        dataRange: {min: 0, max: 100, x: 'left', y: 'bottom', text: ['高', '低'], calculable: true},
        toolbox: {
            show: true, orient: 'vertical', x: 'right', y: 'center',
            feature: {
                mark: {show: true},
                dataView: {
                    show: true,
                    readOnly: false,
                    scroll: true
                },
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        roamController: {show: true, x: 'right', mapTypeControl: {'china': true}},
        series: [{
            name: '',
            type: 'map',
            mapType: 'china',
            roam: false,
            itemStyle: {normal: {label: {show: true}}, emphasis: {label: {show: true}}}
        }]
    };

    $scope.pipeline = [
        {'$match': {'province': {'$ne': '', '$exists': true}}},
        {'$group': {'_id': '$imei', 'province': {'$last': '$province'}}},
        {'$group': {'_id': '$province', 'value': {'$sum': 1}}}
    ];
    $scope.aggregateRecord = AggregateRecord($scope, $http, '/admin/watch_locate/aggregate');
    $scope.aggregateRecord();
    $scope.record_handle = function (datas) {
        var option = $scope.option;
        var max = 0;
        for (var i in datas) {
            if (datas[i]['value'] > max) {
                max = datas[i]['value']
            }
            datas[i]['name'] = datas[i]['_id'].slice(0, -1)
        }
        option['dataRange']['max'] = max;
        option['series'][0]['data'] = datas;
        $scope.echart.setOption(option);
    };
});

admin.controller('user_locate_analysis', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "user_locate_analysis", "用户地域信息统计");

    $scope.echart = echarts.init(document.getElementById('echat_container'));
    $http.get('/static/json/china.json').success(function (chinaJson) {
        echarts.registerMap('china', chinaJson);
    });
    $scope.option = {
        title: {text: '', subtext: '', x: 'center'},
        tooltip: {trigger: 'item', formatter: '{b} : {c}'},
        dataRange: {min: 0, max: 100, x: 'left', y: 'bottom', text: ['高', '低'], calculable: true},
        toolbox: {
            show: true, orient: 'vertical', x: 'right', y: 'center',
            feature: {
                mark: {show: true},
                dataView: {
                    show: true,
                    readOnly: false,
                    scroll: true,
                },
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        roamController: {show: true, x: 'right', mapTypeControl: {'china': true}},
        series: [{
            name: '',
            type: 'map',
            mapType: 'china',
            roam: false,
            itemStyle: {normal: {label: {show: true}}, emphasis: {label: {show: true}}}
        }]
    };

    $scope.pipeline = [
        {'$match': {'province': {'$ne': '', '$exists': true}}},
        {'$group': {'_id': '$user_id', 'province': {'$last': '$province'}}},
        {'$group': {'_id': '$province', 'value': {'$sum': 1}}}
    ];
    $scope.aggregateRecord = AggregateRecord($scope, $http, '/admin/user_locate/aggregate');
    $scope.aggregateRecord();
    $scope.record_handle = function (datas) {
        var option = $scope.option;
        var max = 0;
        for (var i in datas) {
            if (datas[i]['value'] > max) {
                max = datas[i]['value']
            }
            datas[i]['name'] = datas[i]['_id'].slice(0, -1)
        }
        option['dataRange']['max'] = max;
        option['series'][0]['data'] = datas;
        $scope.echart.setOption(option);
    };
});

admin.controller('user_create_analysis', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "user_create_analysis", "新建用户数量统计");

    $scope.echart = echarts.init(document.getElementById('echat_container'));
    $scope.baseOption = {
        timeline: {
            data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
            label: {
                formatter: function (s) {
                    return s + '月';
                }
            },
            autoPlay: false,
            currentIndex: 0
        },
        tooltip: {trigger: 'axis'},
        toolbox: {
            show: true,
            orient: 'vertical',
            x: 'right',
            y: 'center',
            feature: {
                mark: {show: true},
                dataView: {
                    show: true,
                    readOnly: true
                },
                dataZoom: {show: true},
                magicType: {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        calculable: true,
        grid: {y: 80, y2: 100},
        xAxis: [{
            type: 'category',
            axisLabel: {interval: 0},
            data: [
                '1号', '2号', '3号', '4号', '5号', '6号', '7号', '8号', '9号', '10号', '11号', '12号', '13号', '14号', '15号', '16号',
                '17号', '18号', '19号', '20号', '21号', '22号', '23号', '24号', '25号', '26号', '27号', '28号', '29号', '30号', '31号'
            ]
        }],
        yAxis: [{
            type: 'value',
            name: '用户数',
            max: 1000
        }],
        series: [{
            name: '人数',
            type: 'line'
        }]
    };
    $scope.pipeline = [
        {
            '$match': {
                'maketime': {'$exists': true, '$gt': {'__type__': 'YearType', '__value__': '2016'}}
            }
        },
        {
            '$project': {
                'month': {'$month': "$maketime"},
                'day': {'$dayOfMonth': "$maketime"}
            }
        },
        {
            '$group': {
                '_id': {'month': '$month', 'day': '$day'},
                'value': {'$sum': 1}
            }
        }
    ];
    $scope.aggregateRecord = AggregateRecord($scope, $http, '/admin/user/aggregate');
    $scope.aggregateRecord();
    $scope.record_handle = function (datas) {
        var base_option = $scope.baseOption;
        var now_month = new Date().getMonth();
        base_option['timeline']['currentIndex'] = now_month;
        data = [];
        for (var i = 0; i < 12; i++) {
            data[i] = [];
            for (var j = 0; j < 31; j++) {
                data[i][j] = {'value': 0}
            }
        }
        var max = 0;
        for (var i in datas) {
            var month = datas[i]['_id']['month'];
            var day = datas[i]['_id']['day'];
            var value = datas[i]['value'];
            if (value > max) max = value;
            data[month - 1][day - 1]['value'] = value;
        }
        options = [];
        for (var m = 0; m < 12; m++) {
            options[m] = {
                series: [{
                    data: data[m],
                    smooth: true
                }]
            }
        }
        base_option['yAxis'][0]['max'] = max;
        $scope.echart.setOption({baseOption: base_option, options: options});
    };
});

admin.controller('group_create_analysis', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "group_create_analysis", "新建圈子数量统计");

    $scope.echart = echarts.init(document.getElementById('echat_container'));
    $scope.baseOption = {
        timeline: {
            data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
            label: {
                formatter: function (s) {
                    return s + '月';
                }
            },
            autoPlay: false,
            currentIndex: 0
        },
        tooltip: {trigger: 'axis'},
        toolbox: {
            show: true,
            orient: 'vertical',
            x: 'right',
            y: 'center',
            feature: {
                mark: {show: true},
                dataView: {
                    show: true,
                    readOnly: true
                },
                dataZoom: {show: true},
                magicType: {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        calculable: true,
        grid: {y: 80, y2: 100},
        xAxis: [{
            type: 'category',
            axisLabel: {interval: 0},
            data: [
                '1号', '2号', '3号', '4号', '5号', '6号', '7号', '8号', '9号', '10号', '11号', '12号', '13号', '14号', '15号', '16号',
                '17号', '18号', '19号', '20号', '21号', '22号', '23号', '24号', '25号', '26号', '27号', '28号', '29号', '30号', '31号'
            ]
        }],
        yAxis: [{
            type: 'value',
            name: '圈子数',
            max: 1000
        }],
        series: [{
            name: '个数',
            type: 'line'
        }]
    };
    $scope.pipeline = [
        {
            '$match': {
                'maketime': {'$exists': true, '$gt': {'__type__': 'YearType', '__value__': '2016'}}
            }
        },
        {
            '$project': {
                'month': {'$month': "$maketime"},
                'day': {'$dayOfMonth': "$maketime"}
            }
        },
        {
            '$group': {
                '_id': {'month': '$month', 'day': '$day'},
                'value': {'$sum': 1}
            }
        }
    ];
    $scope.aggregateRecord = AggregateRecord($scope, $http, '/admin/group/aggregate');
    $scope.aggregateRecord();
    $scope.record_handle = function (datas) {
        var base_option = $scope.baseOption;
        var now_month = new Date().getMonth();
        base_option['timeline']['currentIndex'] = now_month;
        data = [];
        for (var i = 0; i < 12; i++) {
            data[i] = [];
            for (var j = 0; j < 31; j++) {
                data[i][j] = {'value': 0}
            }
        }
        var max = 0;
        for (var i in datas) {
            var month = datas[i]['_id']['month'];
            var day = datas[i]['_id']['day'];
            var value = datas[i]['value'];
            if (value > max) max = value;
            data[month - 1][day - 1]['value'] = value;
        }
        options = [];
        for (var m = 0; m < 12; m++) {
            options[m] = {
                series: [{
                    data: data[m],
                    smooth: true
                }]
            }
        }
        base_option['yAxis'][0]['max'] = max;
        $scope.echart.setOption({baseOption: base_option, options: options});
    };
});

admin.controller('admin_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit('active', 'admin_info', '管理员信息查看');
    $scope.field = ['_id', 'maketime', 'lasttime', 'nickname', 'permissions'];
    $scope.searchRecords = function () {
        if (!$scope._id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = {'$regex': '.*' + $scope._id + '.*'};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/admin');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/admin/count');

    $scope.new_permissions = [];
    $scope.addPermissions = function (event) {
        var val = $(event.target).prev().val();
        if (!val) {
            return false;
        }
        for (var i in $scope.new_permissions) {
            if ($scope.new_permissions[i] == val) {
                return false;
            }
        }
        $scope.new_permissions.push(val);
    };
    $scope.delPermissions = function (event) {
        var btn = $(event.target);
        var val = btn.prev().prev().val();
        new_permissions = [];
        for (var i in $scope.new_permissions) {
            if ($scope.new_permissions[i] != val) {
                new_permissions.push($scope.new_permissions[i]);
            }
        }
        $scope.new_permissions = new_permissions;
    };
    $scope.prepare_submit = function (form) {
        var _id = form.find('input[name="_id"]').val();
        if (!_id) {
            message('新账号id参数未填', '', 'error');
            return false;
        } else {
            try {
                JSON.parse(_id);
                if (isNaN(_id)) {
                    form.find('input[name="_id"]').val(_id);
                } else {
                    form.find('input[name="_id"]').val('"' + _id + '"');
                }
            }
            catch(err) {
                form.find('input[name="_id"]').val(JSON.stringify(_id));
            }
        }
        var nickname = form.find('input[name="nickname"]').val();
        if (nickname) {
            try {
                JSON.parse(nickname);
                if (isNaN(nickname)) {
                    form.find('input[name="nickname"]').val(nickname);
                } else {
                    form.find('input[name="nickname"]').val('"' + nickname + '"');
                }
            }
            catch(err) {
                form.find('input[name="nickname"]').val(JSON.stringify(nickname));
            }
        }
        if (!$scope.new_permissions.length) {
            message('新账号权限未添加', '', 'error');
            return false;
        }
        return true;
    };
    $scope.after_submit = function () {
        $scope.getRecords();
    };
    $scope.delete = function (_id) {
        var confirm = window.confirm("确定删除 " + _id + " ？");
        if (confirm) {
            $http.post('/admin/admin/delete', {'_id': _id}).success(function (data) {
                if (data == 'success') {
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == _id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                    message('操作成功', '', 'success');
                } else {
                    message(data, '', 'error');
                }
            });
        };
    };
    $scope.modify = function (_id) {
        var modal = $('#myModal2');
        modal.modal('show');
        id_text = modal.find('input[name="_id"]');
        id_text.val(_id);
        for (var i in $scope.datas) {
            if ($scope.datas[i]['_id'] == _id) {
                $scope.temp = {};
                for (var j in $scope.datas[i]) {
                    if (Object.prototype.toString.call($scope.datas[i][j]) === '[object Array]') {
                        $scope.temp[j] = $scope.datas[i][j].slice();
                    } else {
                        $scope.temp[j] = $scope.datas[i][j];
                    }
                }
            }
        }
    };
    $scope.addPermissions_temp = function (event) {
        var val = $(event.target).prev().val();
        if (!val) {
            return false;
        }
        for (var i in $scope.temp['permissions']) {
            if ($scope.temp['permissions'][i] == val) {
                return false;
            }
        }
        $scope.temp['permissions'].push(val);
    };
    $scope.delPermissions_temp = function (event) {
        var btn = $(event.target);
        var val = btn.prev().prev().val();
        new_permissions = [];
        for (var i in $scope.temp['permissions']) {
            if ($scope.temp['permissions'][i] != val) {
                new_permissions.push($scope.temp['permissions'][i]);
            }
        }
        $scope.temp['permissions'] = new_permissions;
    };
    $scope.submit_temp = function () {
        $http.post('/admin/admin', {
            '_id': $scope.temp['_id'],
            'nickname': $scope.temp['nickname'],
            'permissions': $scope.temp['permissions']
        }).success(function (data) {
            if (data == 'success') {
                $scope.getRecords();
                message('修改成功', '', 'success');
            } else {
                message(data, '', 'error');
            }
        })
    }
});

admin.controller('version_android', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "version_android", "安卓版本管理");
    $scope.field = ['number', 'name', 'platform', 'log', 'maketime', 'file_id'];
    $scope.searchRecords = function () {
        if (!$scope.number) {
            $scope.query = {};
        } else {
            $scope.query['number'] = {'__type__': 'IntType', '__value__': $scope.number};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/version');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/version/count');
    $scope.startSpinner = function () {
        spinner.start('spin');
    };
    $scope.stopSpinner = function () {
        spinner.stop('spin');
    };
    validate_permission($scope, 'version_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (number) {
        var confirm = window.confirm("确定删除 " + number + " ？");
        if (confirm) {
            $http.post('/admin/version/delete', {
                'number': {
                    '__type__': 'IntType',
                    '__value__': number
                }
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['number'] == number) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('appstore_category_info', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "appstore_category_info", "应用分类信息");
    $scope.field = ['_id', 'name', 'image_id', 'image_id2', 'sort'];
    $scope.sort = ['sort', 1];
    $scope.getRecords = QueryRecord($scope, $http, '/admin/appstore.category');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/appstore.category/count');
    validate_permission($scope, 'category_manage', function (ok) {
        if (ok) $scope.modifiable = true;
    });
    $scope.startSpinner = function () {
        spinner.start('spin');
    };
    $scope.stopSpinner = function () {
        spinner.stop('spin');
    };
    function change_category_image(category_id, image_name) {
        var form = $(".ImageForm");
        form.find('input[name=image_name]').val(image_name);
        form.find('input[name=category_id]').val(category_id);
        var input = form.find('input[name=image]');
        input.val('');
        input.unbind("change");
        input.change(function () {
            form.ajaxForm();
            form.ajaxForm();
            $scope.startSpinner();
            form.ajaxSubmit(function (data) {
                $scope.stopSpinner();
                $('input').enable();
                if (data == 'success') {
                    form.resetForm();
                    message('更新成功', '', 'success');
                    $scope.getRecords();
                } else {
                    message('错误', data, 'error')
                }
            })
        });
        input.click();
    }

    $scope.change_image = function (category_id) {
        change_category_image(category_id, 'image_id');
    };
    $scope.change_image2 = function (category_id) {
        change_category_image(category_id, 'image_id2');
    };
    $scope.upsort = function (category_id) {
        datas = $scope.datas;
        for (var i in datas) {
            if (datas[i]['_id'] == category_id) {
                var sort = datas[i]['sort'] ? datas[i]['sort'] - 1 : 0;
                var index = i;
            }
        }
        $http.post('/admin/appstore.category', {
            'find': {'_id': category_id},
            'update': {'$set': {'sort': sort}}
        }).success(function (data) {
            if (data == 'success') {
                $scope.datas[index]['sort'] = sort
            } else {
                message('错误', data, 'error')
            }
        })
    };
    $scope.downsort = function (category_id) {
        datas = $scope.datas;
        for (var i in datas) {
            if (datas[i]['_id'] == category_id) {
                var sort = datas[i]['sort'] ? datas[i]['sort'] + 1 : 1;
                var index = i;
            }
        }
        $http.post('/admin/appstore.category', {
            'find': {'_id': category_id},
            'update': {'$set': {'sort': sort}}
        }).success(function (data) {
            if (data == 'success') {
                $scope.datas[index]['sort'] = sort
            } else {
                message('错误', data, 'error')
            }
        })
    };
    validate_permission($scope, 'category_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (category_id) {
        var confirm = window.confirm("确定删除 " + category_id + " ？");
        if (confirm) {
            $http.post('/admin/appstore.category/delete', {
                'category_id': category_id
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == category_id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('plaza_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "plaza_info", "广场消息");
    $scope.field = ['_id', 'user_id', 'content', 'images', 'like_num', 'comment_num', 'timestamp'];
    $scope.searchRecords = function () {
        if (!$scope.post_id) {
            $scope.query = {};
        } else {
            if (!check_object_id($scope.post_id)) return false;
            $scope.query['_id'] = {'__type__': 'ObjectIdType', '__value__': $scope.post_id};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/plaza');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/plaza/count');
    validate_permission($scope, 'plaza_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (post_id) {
        var confirm = window.confirm("确定删除 " + post_id + " ？");
        if (confirm) {
            $http.post('/admin/plaza/delete', {
                'find': {
                    '_id': {
                        '$in': [{
                            '__type__': 'ObjectIdType',
                            '__value__': post_id
                        }]

                    }
                }
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == post_id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('submail_info', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "submail_info", "邮件信息");
    $scope.field = [];
    $scope.searchRecords = function () {
        $scope.query = {};
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/submail');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/submail/count')
});

admin.controller('bluetooth_info', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "bluetooth_info", "腕表蓝牙版本管理");
    $scope.field = ['_id', 'version', 'maketime'];
    $scope.searchRecords = function () {
        if (!$scope.number) {
            $scope.query = {};
        } else {
            $scope.query['version'] = {'__type__': 'IntType', '__value__': $scope.number};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/bluetooth');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/bluetooth/count');
    $scope.startSpinner = function () {
        spinner.start('spin');
    };
    $scope.stopSpinner = function () {
        spinner.stop('spin');
    };
    validate_permission($scope, 'version_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (_id) {
        var confirm = window.confirm("确定删除 " + _id + " ？");
        if (confirm) {
            $http.post('/admin/bluetooth/delete', {
                '_id': {
                    '__type__': 'ObjectIdType',
                    '__value__': _id
                }
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == _id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('banner_info', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "banner_info", "应用首页广告信息");
    $scope.field = ['_id', 'image_id'];
    $scope.getRecords = QueryRecord($scope, $http, '/admin/banner');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/banner/count');
    $scope.startSpinner = function () {
        spinner.start('spin');
    };
    $scope.stopSpinner = function () {
        spinner.stop('spin');
    };
    validate_permission($scope, 'story_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (_id) {
        var confirm = window.confirm("确定删除 " + _id + " ？");
        if (confirm) {
            $http.post('/admin/banner/delete', {
                '_id': {
                    '__type__': 'ObjectIdType',
                    '__value__': _id
                }
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == _id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('answer_game_info', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "answer_game_info", "答题游戏信息");
    $scope.field = ['_id', 'question', 'answer', 'category_id'];
    $scope.getRecords = QueryRecord($scope, $http, '/admin/answer_game');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/answer_game/count');
    $scope.searchRecords = function () {
        if (!$scope.game_id) {
            $scope.query = {};
        } else {
            if (!check_object_id($scope.game_id)) return false;
            $scope.query['_id'] = {'__type__': 'ObjectIdType', '__value__': $scope.game_id};
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.startSpinner = function () {
        spinner.start('spin');
    };
    $scope.stopSpinner = function () {
        spinner.stop('spin');
    };
    validate_permission($scope, 'game_manage', function (ok) {
        if (ok) $scope.deletable = true;
    });
    $scope.delete = function (_id) {
        var confirm = window.confirm("确定删除 " + _id + " ？");
        if (confirm) {
            $http.post('/admin/answer_game/delete', {
                '_id': {
                    '__type__': 'ObjectIdType',
                    '__value__': _id
                }
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == _id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
    $scope.getCategory = function () {
        $http.get('/admin/answer_game.category', {
            params: {
                find: JSON.stringify({}),
                field: JSON.stringify(['_id', 'name']),
                page: 0,
                num: 10,
                sort: JSON.stringify(['sort', 1])
            }
        }).success(function (category) {
            $scope.category_list = category;
        });
    };
});

admin.controller('answer_game_category_info', function ($scope, $q, $rootScope, $http, spinner) {
    $scope.$emit("active", "answer_game_category_info", "答题游戏分类信息");
    $scope.field = ['_id', 'name', 'image_id', 'sort'];
    $scope.sort = ['sort', 1];
    $scope.getRecords = QueryRecord($scope, $http, '/admin/answer_game.category');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/answer_game.category/count');
    validate_permission($scope, 'game_manage', function (ok) {
        if (ok) {
            $scope.modifiable = true;
            $scope.deletable = true;
        }
    });
    $scope.startSpinner = function () {
        spinner.start('spin');
    };
    $scope.stopSpinner = function () {
        spinner.stop('spin');
    };
    function change_category_image(category_id, image_name) {
        var form = $(".ImageForm");
        form.find('input[name=image_name]').val(image_name);
        form.find('input[name=category_id]').val(category_id);
        var input = form.find('input[name=image]');
        input.val('');
        input.unbind("change");
        input.change(function () {
            form.ajaxForm();
            form.ajaxForm();
            $scope.startSpinner();
            form.ajaxSubmit(function (data) {
                $scope.stopSpinner();
                $('input').enable();
                if (data == 'success') {
                    form.resetForm();
                    message('更新成功', '', 'success');
                    $scope.getRecords();
                } else {
                    message('错误', data, 'error')
                }
            })
        });
        input.click();
    }

    $scope.change_image = function (category_id) {
        change_category_image(category_id, 'image_id');
    };
    $scope.upsort = function (category_id) {
        datas = $scope.datas;
        for (var i in datas) {
            if (datas[i]['_id'] == category_id) {
                var sort = datas[i]['sort'] ? datas[i]['sort'] - 1 : 0;
                var index = i;
            }
        }
        $http.post('/admin/answer_game.category', {
            'find': {'_id': category_id},
            'update': {'$set': {'sort': sort}}
        }).success(function (data) {
            if (data == 'success') {
                $scope.datas[index]['sort'] = sort
            } else {
                message('错误', data, 'error')
            }
        })
    };
    $scope.downsort = function (category_id) {
        datas = $scope.datas;
        for (var i in datas) {
            if (datas[i]['_id'] == category_id) {
                var sort = datas[i]['sort'] ? datas[i]['sort'] + 1 : 1;
                var index = i;
            }
        }
        $http.post('/admin/answer_game.category', {
            'find': {'_id': category_id},
            'update': {'$set': {'sort': sort}}
        }).success(function (data) {
            if (data == 'success') {
                $scope.datas[index]['sort'] = sort
            } else {
                message('错误', data, 'error')
            }
        })
    };
    $scope.delete = function (category_id) {
        var confirm = window.confirm("确定删除 " + category_id + " ？");
        if (confirm) {
            $http.post('/admin/answer_game.category/delete', {
                'category_id': category_id
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == category_id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller('service_manage', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "service_manage", "客服管理");
    $scope.field = ['_id', 'password', 'maketime'];
    $scope.searchRecords = function () {
        if (!$scope.serv_id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = $scope.serv_id;
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/service');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/service/count');
    validate_permission($scope, 'service_manage', function (ok) {
        if (ok) {
            $scope.deletable = true;
        }
    });
    $scope.delete = function (id) {
        var confirm = window.confirm("确定删除 " + id + " ？");
        if (confirm) {
            $http.post('/admin/service/delete', {
                'find': {'_id': id}
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
});

admin.controller("question_manage", function($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "question_manage", "问题管理");
    $scope.field = ['_id', 'title', 'user_id', "serv_id", "status", "star", "timestamp"];
    $scope.searchRecords = function () {
        if (!$scope.serv_id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = $scope.serv_id;
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/questions');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/questions/count');
    validate_permission($scope, 'service_manage', function (ok) {
        if (ok) {
            $scope.deletable = true;
        }
    });
    $scope.delete = function (id) {
        var confirm = window.confirm("确定删除 " + id + " ？");
        if (confirm) {
            $http.post('/admin/question/delete', {
                'find': {'_id': id}
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
})

admin.controller("answer_manage", function($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "answer_manage", "答案管理");

    $scope.templates = [
    {"_id": "usually", "title": "常见问题"},
    {"_id": "sim", "title": "SIM卡"},
    {"_id": "app", "title": "APP下载与激活"},
    {"_id": "watch", "title": "手表开关机"}];

    $scope.field = ['_id', 'template_id', 'content', 'question'];
    $scope.searchRecords = function () {
        if (!$scope.serv_id) {
            $scope.query = {};
        } else {
            $scope.query['_id'] = $scope.serv_id;
        }
        $scope.current_page = 1;
        $scope.pagination();
        $scope.getRecords();
    };
    $scope.getRecords = QueryRecord($scope, $http, '/admin/answers');
    $scope.jumpPage = JumpPage($scope);
    $scope.pagination = pagination($scope, $q, $http, '/admin/answers/count');
    validate_permission($scope, 'service_manage', function (ok) {
        if (ok) {
            $scope.deletable = true;
        }
    });
    $scope.delete = function (id) {
        var confirm = window.confirm("确定删除 " + id + " ？");
        if (confirm) {
            $http.post('/admin/answer/delete', {
                'find': {'_id': id}
            }).success(function (data) {
                if (data == 'success') {
                    message('删除成功', '', 'success');
                    for (var i in $scope.datas) {
                        if ($scope.datas[i]['_id'] == id) {
                            $scope.datas.splice(i, 1);
                        }
                    }
                } else {
                    message('删除失败', data, 'error');
                }
            });
        };
    };
})