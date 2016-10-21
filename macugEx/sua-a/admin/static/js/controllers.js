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

    $scope.logout = function () {
        $http.post('/logout').success(function (data) {
            window.location = '/login';
        });
    };
});

admin.controller('profile', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "profile", "欢迎管理员登陆");
    $http.get('http://127.0.0.1:8081/profile').success(function(data){
        $scope.profile_data = data;
        });
    $scope.modify_name = function() {

        var modify_password = $('#modify_password').val()
        $http({
      url: 'http://127.0.0.1:8081/modify',
      method: "POST",
      data: $.param({'_id': $scope.profile_data._id, 'password': modify_password}),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).success(function(data){
        message('修改成功', '', 'success')
        $('#modify_password').val('')
    });
    };


    $scope.adminSubmit = function() {
        function error(data){
            if(data.responseText == 'success'){
                console.log('sssssaaaaa')
                message('添加成功', '', 'success');
            }
            else{
                message(data.responseText,'','error')

            }

            console.log(data.responseText)
        }

        var form = $('#newModal form');
        form.ajaxForm();
        form.ajaxSubmit({
            url: 'http://127.0.0.1:8081/create',
            dataType: 'json',
            error: error
        });
        form.find('input').val("")
        // window.location.reload()

    };
});
admin.controller('users', function ($scope, $q, $rootScope, $http, $routeParams) {
    $scope.$emit("active", "users", "校友");
    /**
     * 获取数据
     */
    $scope.getRecords = function () {
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/users', {
            params: params
        }).success(function (data) {
            $scope.users = data.users
        });
    }
    /**
     *
     * 页面跳转
     */
    $scope.jumpPage = JumpPage();
    $scope.pagination = pagination($scope.server_uri + '/resource/users/count', function (data) {
        return data.count;
    });
     /**
     * 监听$scope.num
     *
     */
    $scope.change = function (changeNum) {
        $scope.num = changeNum
        $scope.totalPage = Math.ceil($scope.length / $scope.num);
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/users', {
            params: params
        }).success(function (data) {
            $scope.users = data.users
        });
        var a= [];
        for (var i = 1; i < $scope.totalPage +1; i++) {
            a.push(i);
            if (i >= 10) break;
        }
        $scope.pagelist = a
        $scope.jumpPage = JumpPage();
    }
    /**
     *
     * 删除数据
     *
     */
    $scope.delete = function (userid, user) {
        var confirm = window.confirm("确定删除" + userid + "?");
        if (confirm) {
            $http.delete($scope.server_uri + '/resource/user/' + userid).success(function (data) {
                if (data.code == 0){
                    $scope.users.splice($scope.users.indexOf(user), 1);
                    message(data.msg, data.code,'success')
                    console.log(data.msg + '<<<<---data.msg--->>>>>'+ data.code + '<<---data.code-->>')
                }
                else if (data.code == 1001){
                    message(data.msg, data.code,'error')
                    console.log(data.msg + '<<<<---data.msg--->>>>>'+ data.code + '<<---data.code-->>')
                }
                else if(data.code != 0 || data.code!= 1001){
                    message('删除失败', '','error');
                    console.log(data.msg + '<<<<---data.msg--->>>>>'+ data.code + '<<---data.code-->>')
                }
                }).error(function (data) {
                console.log(data.msg + '<<<<---data.msg--ERROR PART!!!!!!->>>>>'+ data.code + '<<---data.code-->>')
                message(data.msg,'error function','')
            });
        }
        else message('你取消了删除')
    };

    /**
     *
     *获取单个用户信息
     * @param userid
     */
    $scope.getUserInfo = function (userid) {
        console.log(userid)
    };

    /**
     *
     * 修改单个用户信息
     * @param user
     */
    $scope.modify = function (user) {
        $scope.currUser = user;
        var gender = $scope.currUser.gender
        if(gender == "男"){
            $('#man').attr("checked", true);
        }
        else if (gender == "女"){
            $('#lady').attr("checked",true);
        }
    }

    /**
     * 提交修改用户信息
     *
     */
    $scope.submitModify = function () {
        var form = $('#editModal form');
        form.find('input[name="gender"]:checked').val()
        form.ajaxForm();
        console.log(form.find('input[name="gender"]:checked').val(), '<<<----gender value--->>>>')
        function success(data) {
            if (data.code == 0) {
                message('修改成功', '', 'success');
                $http.get($scope.server_uri + '/resource/users').success(function (data) {
                    $scope.users = data.users
                });
            } else {
                message('修改出错', data.code, 'error');
            }
        }
        form.ajaxSubmit({
            url: $scope.server_uri + '/resource/user/' + $scope.currUser._id,
            dataType: 'json',
            success: success
        });
    }
        /**
         *
         * 搜索功能
         * click事件
         *
         */
    $scope.search = function () {
        var searchkey = $("#inputField").val()
        // $("#searchResult").show();
        // $("#userSet").hide();
        console.log(searchkey,'<<------searchKey---->>>>>')
        $http.get($scope.server_uri + '/resource/users/search', {
            params: {
                searchKey: searchkey
            }
        }).success(function (data) {
            if (data.code == 0) {
                $scope.users = data.userSet;
               var resultLength = data.userSet.length
                console.log($scope.users)
                console.log($scope.resultLength,'<<---length-->>>')
                $scope.totalPage = Math.ceil(resultLength / $scope.num);
                 var a= [];
                for (var i = 1; i < $scope.totalPage +1; i++) {
                a.push(i);
                if (i >= 10) break;
                }
                $scope.pagelist = a
                $scope.jumpPage = JumpPage();
            }
            else if (data.code == 1001) {
                message(data.msg, '', 'error')
            }
        }).error(function () {
            message('未知错误，请换个关键字重新搜索', '', 'error')
        })
    }
});

admin.controller('activity', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "activity", "活动");
});
admin.controller('group', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "group", "圈子");
});
admin.controller('topic', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "topic", "圈子话题");
});

admin.controller('worksheet', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "worksheet", "工单");
});

