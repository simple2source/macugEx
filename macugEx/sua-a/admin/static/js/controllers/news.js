/**
 * Created by junerlam on 16-9-30.
 */


admin.controller('news', function ($scope, $q, $rootScope, $http) {

    $scope.$emit("active", "news", "校友资讯");


    /*
     *  获取数据库所有资讯
     * */
    $scope.getRecords = function () {
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/news', {
            params: params
        }).success(function (data) {
            $scope.newsShow = data.news
        });
    }
    $scope.jumpPage = JumpPage();
    $scope.pagination = pagination($scope.server_uri + '/resource/news/count', function (data) {
        return data.count;
    });

    /**
     * 搜索功能
     * 关键字段：quote表中的title
     *
     */
    $scope.searchRecords = function(){
        $http.get($scope.server_uri + '/resource/news/search',{
            params : {title : $scope.title}
        }).success(function (data) {
            if (data.code == 0){
                $scope.newsShow = data.titles;
                var resultLength = data.titles.length
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
            message('未知错误，请重新搜索','','error')
        })
    }

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
        $http.get($scope.server_uri + '/resource/news', {
            params: params
        }).success(function (data) {
            $scope.newsShow = data.news
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
     * 删除一条资讯
     * */
    $scope.delete = function (newid, aNew) {
        var confirm = window.confirm("确定删除" + newid + "?");
        if (confirm) {
            $http.delete($scope.server_uri + '/resource/news/' + newid).success(function (data) {
                if(data.code== 0){
                    message(data.msg,'','success');
                    $scope.newsShow.splice($scope.newsShow.indexOf(aNew), 1);
                }
                else if (data.code!=0){
                    message(data.msg,'','error')
                }
            }).error(function (data) {
                message(data.msg, '', 'error')
                console.log('fail to delete!')
                });

        }
        else message('你取消了删除')
    };

    /**
     * 设置表单字段
     *
     * @param form
     * @param name
     * @param value
     */
    function setFormField(form, name, value) {
        form.find('input[name="' + name + '"]').val(value);
    }

    /*
     * 得到单条资讯信息
     * */
    $scope.getNewInfo = function (newid) {
        $http.get($scope.server_uri + '/resource/news/' + newid)
    }

    /*
     * 修改单条资讯信息
     *
     * */
    $scope.modify = function (news) {
        $scope.formatData = news;
        if (news.content) $scope.newsChange.clipboard.dangerouslyPasteHTML(news.content);
    };

    /*
     * 资讯修改成功时触发方法
     * */
    $scope.submitModify = function () {
        var form = $("#editModal form");

        var content = $scope.newsChange.root.innerHTML;
        setFormField(form,'content' ,content);
        $scope.formatData.content = content;

        form.ajaxForm();
        setFormField(form, 'title', $scope.formatData.title)
        setFormField(form, 'source', $scope.formatData.source)

        function success(data) {
            if (data.code == 0) {
                $http.get($scope.server_uri + '/resource/news').success(function (data) {
                    $scope.newsShow = data.news
                });
                message('修改成功', '', 'success');
            }
        }

        function error(data) {
            if(data.code!==0){
                message(data.msg, '','error');
            }
        }
        var content = $scope.newsChange.root.innerHTML;
        var form = $("#editModal form");
        form.ajaxForm();
        setFormField(form,'content' ,content);
        form.ajaxSubmit({
            url: $scope.server_uri +'/resource/news/' + $scope.formatData._id,
            method: 'POST',
            dataType: 'json',
            success: success,
            error: error

        });
    };

    /*
     * 添加资讯
     * */
    $scope.newSubmit = function () {

        var form  = $("#myModal form");
        form.find('input[name="content"]').val($scope.newsQuill.root.innerHTML);
        form.ajaxForm();
        function success(data) {
            if (data.code == 0) {
                form.find('input').val("");
                $scope.newsQuill.root.innerHTML = "";
                $scope.getRecords();
                message(data.msg, '', 'success');

            }
        }
        function error(data) {
            if(data.code!== 0){
                message(data.msg, '','error');
            }
        }
        form.ajaxForm();
        form.ajaxSubmit({
            url: $scope.server_uri + '/resource/news',
            method: 'POST',
            dataType: 'json',
            success: success,
            error:error

        });
    };

    /**
     *
     * 初始化quill编辑器
     */
    $scope.newsQuill = new Quill('#newsEditor', {
        modules: {
            toolbar: [
                [{header: [1, 2, false]}],
                ['bold', 'italic', 'underline'],
                ['image', 'code-block']
            ]
        },
        placeholder: '请输入资讯相关内容',
        theme: 'snow' // or 'bubble'
    });



    $scope.newsChange = new Quill("#quillModify", {
        modules: {
            toolbar: [
                ['bold', 'italic'],
                ['link', 'blockquote', 'code-block', 'image'],
                [{list: 'ordered'}, {list: 'bullet'}]
            ]
        },
        placeholder: '请输入资讯相关内容',
        theme: 'snow' // or 'bubble'
    });
});


