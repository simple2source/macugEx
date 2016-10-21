
admin.controller('donate', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "donate", "校友捐赠");

    /**
     * 获取所有捐赠信息
     */
    $scope.getRecords = function () {
        // $("#donateSet").show()
        // $("#searchResult").hide()
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/foundations', {
            params: params
        }).success(function (data) {
            $scope.foundations = data.foundations
        });
    }
    $scope.jumpPage = JumpPage();
    $scope.pagination = pagination(
        $scope.server_uri + '/resource/donate/count',
        function (data) {
            return data.count;
        })

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
        $http.get($scope.server_uri + '/resource/foundations', {
            params: params
        }).success(function (data) {
            $scope.foundations = data.foundations
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
     * 搜索
     * 关键字：基金会名称（name in table donate）
     *
     */
    $scope.searchRecords = function () {
        $("#donateSet").hide()
        $("#searchResult").show()
        $http.get($scope.server_uri +'/resource/foundations/search',{
            params: {
                queryName : $scope.foundationsName
            }
        }).success(function (data) {
            if(data.code == 0){
                $scope.foundations = data.nameSet
                var resultLength = data.nameSet.length
                $scope.totalPage = Math.ceil(resultLength / $scope.num);
                 var a= [];
                for (var i = 1; i < $scope.totalPage +1; i++) {
                a.push(i);
                if (i >= 10) break;
                }
                $scope.pagelist = a
                $scope.jumpPage = JumpPage();
            }
            else if (data.code == 1001){
                message(data.msg,'','error')
            }

        }).error(function () {
            message('未知错误，请换个关键字重新输入','','error')

        })
    }
    /**
     * 编辑单条捐赠信息
     */
    $scope.modify = function (donate) {
        $scope.donate = donate;
        if (donate.content) $scope.donateChange.clipboard.dangerouslyPasteHTML(donate.content);


    }
    /**
     * 编辑捐赠信息成功时触发方法
     */
    $scope.modifySubmit = function () {
        function success(data) {
            if (data.code == 0) {
                message(data.msg, '', 'success');
                 $http.get($scope.server_uri + '/resource/foundation/' + $scope.donate._id)
                     .success(function (data) {
                         $scope.donate.content = data.content
                     });
            }
        }
        var form = $("#editModal form");
        var content = $scope.donateChange.root.innerHTML;
        setFormField(form, 'content', content)
        form.ajaxForm();
        setFormField(form, 'create_time', $scope.donate.create_time)
        form.ajaxSubmit({
            url: $scope.server_uri + '/resource/foundation/' + $scope.donate._id,
            dataType: 'json',
            success: success
        })
    }

    /**
     * 增加一条捐赠信息
     *
     */
    $scope.submit = function () {
    var form = $("#myModal form");
    form.find('input[name="content"]').val($scope.donateQuill.root.innerHTML);
    form.ajaxForm();
    function success(data) {
        if (data.code == 0) {
            $scope.getRecords();
            form.find('input').val("");
            $scope.donateQuill.root.innerHTML = "";
            message(data.msg, '', 'success');
        }
    }
    function error(data) {
        if (data.code == e)
        {
            message(data.msg, '', 'error')
        }
    }
    setFormField(form, 'create_time', new Date().toLocaleString())
    setFormField(form, 'acount', 0)
    setFormField(form, 'amount', 0)
    form.ajaxSubmit({
        url: $scope.server_uri + '/resource/foundations',
        dataType: 'json',
        success: success,
        error: error
    })
}

    /**
     * 删除一条捐赠信息
     */

    $scope.delete = function (foundid,found) {
        $http.delete($scope.server_uri + '/resource/foundation/' + foundid).success(function (data) {
            var confirm = window.confirm("确定删除" + foundid + "?");
            if (confirm &&data.code== 0) {
                message(data.msg, '', 'success')
                $scope.foundations.splice($scope.foundations.indexOf(found), 1);
            }
            else if(confirm && data.code!=0){
                message(data.msg,'' ,'error');
            }
            else message('数据没有删除')
        }).error(function (data) {
            message(data.msg,'','error')

        })


    }


     /**
     * 设置表单字段
     * @param form
     * @param name
     * @param value
     */
    function setFormField(form, name, value) {
        form.find('input[name="' + name + '"]').val(value);
    }

    /**
     *
     * 初始化quill编辑器
     */

        $scope.donateQuill = new Quill('#donateEditor', {
        modules: {
            toolbar: [
                [{ header: [1, 2, false] }],
                ['bold', 'italic', 'underline'],
                ['image', 'code-block']
            ]
        },
        placeholder: '请输入相关捐赠信息...',
        theme: 'snow' // or 'bubble'
    });

     $scope.donateChange = new Quill("#modifyDonate",{
            modules: {
                toolbar: [
                    ['bold', 'italic'],
                    ['link', 'blockquote', 'code-block', 'image'],
                    [{ list: 'ordered' }, { list: 'bullet' }]
                ]
            },
            placeholder: 'Compose an epic...',
            theme: 'snow' // or 'bubble'
        });
});