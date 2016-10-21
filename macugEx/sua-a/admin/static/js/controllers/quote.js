admin.controller('quote', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "quote", "诚哥语录");
    /**
     * 获取所有语录
     */
    $scope.getRecords = function () {
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        }
        $http.get('http://127.0.0.1:8080/resource/quotes', {
            params: params
        }).success(function (data) {
            $scope.quoteShow = data.quotes
        })
    }
    /**
     * 搜索功能
     * 关键字段：quote表中的title
     *
     */
    $scope.searchRecords = function(){
        $http.get($scope.server_uri + '/resource/quote',{
            params : {title : $scope.title}
        }).success(function (data) {
            if(data.code == 0){
                $scope.quoteShow = data.titles;
                var resultLength = data.titles.length
                console.log(data.titles.length,'--length')
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
    $scope.jumpPage = JumpPage();
    $scope.pagination = pagination($scope.server_uri + '/resource/quote/count', function (data) {
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
        $http.get($scope.server_uri + '/resource/quotes', {
            params: params
        }).success(function (data) {
            $scope.quoteShow = data.quotes
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
     * 编辑单条语录
     */
    $scope.modify = function (quoteShow) {
        $scope.quote = quoteShow
        if(quoteShow.brief) $scope.quoteChange.clipboard.dangerouslyPasteHTML(quoteShow.brief);
    }
    /**
     * 编辑成功时触发方法
     */
    $scope.modifySubmit = function () {
        var qid = $scope.quote._id;
        function success(data) {
            if (data.code == 0) {
                message(data.msg, '', 'success');
            }
        }
        var form = $("#editModal form")
        var brief = $scope.quoteChange.root.innerHTML
        setFormField(form,'brief', brief)
        $scope.quote.brief = brief
        form.ajaxForm();
        setFormField(form, 'timestamp', $scope.quote.timestamp)
        form.ajaxSubmit({
            url:$scope.server_uri + '/resource/quote/'+ qid,
            dataType: 'json',
            success: success
        })
    }
    /**
     * 增加一条语录
     *
     */
    $scope.addQuote = function () {
        function success(data) {
            if (data.code == 0) {
                $scope.getRecords();
                form.find('input').val("");
                $scope.quoteQuill.root.innerHTML = "";
                message(data.msg, '', 'success');
            }
        }
        function error(data) {
            if(data.code==1001){
                message(data.msg, data.code,'error');
            }
        }
        var form = $('#myModal form');
        form.find('input[name="brief"]').val($scope.quoteQuill.root.innerHTML);
        form.ajaxForm();
        setFormField(form, 'timestamp', new Date().toLocaleString())
        form.ajaxSubmit({
            url: $scope.server_uri + '/resource/quotes',
            dataType: 'json',
            success: success,
            error: error
        });
    }
    /**
     * 删除一条语录
     */
    $scope.delete = function (quoteid, quote) {
        var confirm = window.confirm("确定删除" + quoteid + "?");
        if (confirm) {

            $http.delete($scope.server_uri + '/resource/quote/' + quoteid).success(function (data) {
                if (data.code == 0){
                    $scope.quoteShow.splice($scope.quoteShow.indexOf(quote), 1);
                    message(data.msg, '', 'success');
                }
                else if (data.code!= 0){
                    message(data.msg,'','error');
                }
                console.log(quoteid)
            }).error(function (data) {
                message(data.msg, '', 'error')
            })

        }
        else message('你取消了删除')
    };



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

        $scope.quoteQuill = new Quill('#editorQuote', {
            modules: {
                toolbar: [
                    [{header: [1, 2, false]}],
                    ['bold', 'italic', 'underline'],
                    ['image', 'code-block']
                ]
            },
            placeholder: '请输入语录...',
            theme: 'snow' // or 'bubble'
        });

    $scope.quoteChange = new Quill("#quillQuote", {
            modules: {
                toolbar: [
                    ['bold', 'italic'],
                    ['link', 'blockquote', 'code-block', 'image'],
                    [{list: 'ordered'}, {list: 'bullet'}]
                ]
            },
            placeholder: 'Compose an epic...',
            theme: 'snow' // or 'bubble'
        });


});