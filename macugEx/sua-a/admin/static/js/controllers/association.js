admin.controller('association', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "association", "校友会");
    /**
     * 获取数据库校友会信息
     *
     */
    $scope.getRecords = function () {
        // $("#searchResult").hide()
        // $("#associationSet").show()
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/associations', {
            params: params
        }).success(function (data) {
            $scope.associationsShow = data.associations
        });
    }
    /***
     * 搜索校友会
     * @params:name:type
     */
    $scope.searchRecords = function () {
        $http.get($scope.server_uri +'/resource/associations/search',{
            params : {
                searchKey :$scope.searchKey
            }
        }).success(function (data) {
            if(data.code == 0){
                $scope.associationsShow = data.associationSet
                var resultLength = data.associationSet.length
                 $scope.totalPage = Math.ceil(resultLength / $scope.num);
                 var a= [];
                for (var i = 1; i < $scope.totalPage +1; i++) {
                a.push(i);
                if (i >= 10) break;
                }
                $scope.pagelist = a
                $scope.jumpPage = JumpPage();

            }
            else if(data.code == 1001){
                message(data.msg,'','error')
            }
        }).error(function () {
            message('搜索出错，请重新搜索','','error')
        })
    }
    /***
     * 页数跳转
     *
     */
    $scope.jumpPage = JumpPage();
    $scope.pagination = pagination($scope.server_uri + '/resource/associations/count', function (data) {
        return data.count;
    });
    /**
     *
     * 监听分页
     *
     */
    $scope.change = function (changeNum) {
        $scope.num = changeNum
        $scope.totalPage = Math.ceil($scope.length / $scope.num);
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/associations', {
            params: params
        }).success(function (data) {
            $scope.associationsShow = data.associations
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
     */
    $scope.delete = function (associationid, association) {
        var confirm = window.confirm("确定删除" + associationid + "?");
        if (confirm) {
            $http.delete($scope.server_uri + '/resource/association/' + associationid).success(function (data) {
                if (data.code == 0){
                    $scope.associationsShow.splice($scope.associationsShow.indexOf(association), 1);
                    message(data.msg,data.code,'success');
                }
                else if(data.code == 1001){
                    message(data.msg,data.code,'error');
                }
                }).error(function (data) {
                message(data.msg, data.code, 'error')

            })
        }
        else message('你取消了删除')
        console.log(associationid)

    };


    /**
     *
     * 修改校友会数据
     */
    $scope.modify = function (association) {
        $scope.association = association;
        if (association.content) $scope.quillChange.clipboard.dangerouslyPasteHTML(association.content);
    };

    function setFormField(form, name, value){
        form.find('input[name= "' + name + '"]').val(value);
    }


    $scope.submitModify = function () {
        var form = $('#editModal form');

//         获取编辑器里面内容
        var content = $scope.quillChange.root.innerHTML;
        setFormField(form, 'content', content);
        $scope.association.content = content;

        form.ajaxForm();

        function success(data) {
            if (data.code == 0) {
                message('修改成功', '', 'success');
            }else {
                message('修改出错', data.code);
            }
        }

        form.ajaxSubmit({
            url: $scope.server_uri + '/resource/association/' + $scope.association._id,
            dataType: 'json',
            success: success
        });

    };


    /**
     *
     * 添加校友会
     */
    $scope.submit = function () {
        var form = $('#myModal form');
        form.find('input[name="content"]').val($scope.associationQuill.root.innerHTML);
        form.ajaxForm();

        function success(data) {
            if (data.code == 0) {
                $scope.getRecords();
                form.find('input').val("");
                $scope.associationQuill.root.innerHTML = "";
                message('添加成功', '', 'success');
            }else {
                message('添加出错', data.code);
            }
        }

        form.ajaxSubmit({
            url: $scope.server_uri + '/resource/associations',
            dataType: 'json',
            success: success
        });
    };


    /**
     *
     * 初始化quill编辑器
     */
    $scope.associationQuill = new Quill('#editorAssociation', {
        modules: {
            toolbar: [
                [{header: [1, 2, false]}],
                ['bold', 'italic', 'underline'],
                ['image', 'code-block']
            ]
        },
        placeholder: '请输入相关简介和添加校友会二维码图片',
        theme: 'snow' // or 'bubble'
    });

    $scope.quillChange = new Quill("#editor_modify", {
        modules: {
            toolbar: [
                ['bold', 'italic'],
                ['link', 'blockquote', 'code-block', 'image'],
                [{list: 'ordered'}, {list: 'bullet'}]
            ]
        },
        placeholder: '请输入相关简介和添加校友会二维码图片',
        theme: 'snow' // or 'bubble'
    });
});
