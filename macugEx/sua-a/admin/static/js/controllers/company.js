admin.controller('company', function ($scope, $q, $rootScope, $http) {
    $scope.$emit("active", "companys", "校企");

    /**
     * 模态框地图操作
     *
     */
    $scope.newCompanyMap = function () {
        AMap = $scope.AMap;
        var map = new AMap.Map('newContainer', {
            zoom: 17
        });
        map.plugin(["AMap.ToolBar"], function () {
            map.addControl(new AMap.ToolBar());
        });
        map.plugin('AMap.Geolocation', function () {
            var geolocation = new AMap.Geolocation({
                enableHighAccuracy: true,//是否使用高精度定位，默认:true
                timeout: 30000,          //超过10秒后停止定位，默认：无穷大
                noIpLocate: true,
                maximumAge: 0,           //定位结果缓存0毫秒，默认：0
                convert: true,           //自动偏移坐标，偏移后的坐标为高德坐标，默认：true
                showButton: false,        //显示定位按钮，默认：true
                showMarker: false,        //定位成功后在定位到的位置显示点标记，默认：true
                showCircle: false,        //定位成功后用圆圈表示定位精度范围，默认：true
                zoomToAccuracy: true      //定位成功后调整地图视野范围使定位位置及精度范围视野内可见，默认：false
            });

            function complete(result) {
                if (result.isConverted) {
                    map.setCenter(result.position);
                } else {
                    console.log('convert locate fail', result)
                }
            }

            function error() {
                console.log('Amap locate fail', error)
            }

            AMap.event.addListener(geolocation, 'complete', complete);
            AMap.event.addListener(geolocation, 'error', error);
            if (geolocation.isSupported()) geolocation.getCurrentPosition()
        });
        var marker = new AMap.Marker();
        marker.setMap(map);
        AMap.event.addListener(map, 'dragend', function () {
            marker.setPosition(map.getCenter())
        });
        AMap.event.addListener(map, 'moveend', function () {
            marker.setPosition(map.getCenter())
        });
        $scope.newCompanyMap.map = map;
        $scope.newCompanyMap.marker = marker;
    };

    $scope.editCompanyMap = function () {
        AMap = $scope.AMap;
        var map = new AMap.Map('editContainer', {
            zoom: 17
        });
        map.plugin(["AMap.ToolBar"], function () {
            map.addControl(new AMap.ToolBar());
        });
        var marker = new AMap.Marker();
        marker.setMap(map);
        AMap.event.addListener(map, 'dragend', function () {
            marker.setPosition(map.getCenter())
        });
        AMap.event.addListener(map, 'moveend', function () {
            marker.setPosition(map.getCenter())
        });
        $scope.editCompanyMap.map = map;
        $scope.editCompanyMap.marker = marker;
    };

    $.getScript("https://webapi.amap.com/maps?v=1.3&key=608d75903d29ad471362f8c58c550daf", function () {
        $scope.AMap = AMap;
        $scope.newCompanyMap();
        $scope.editCompanyMap();
    });

    $scope.mapResolveAddress = function (lat, lon) {
        var deferred = $q.defer();
        $scope.newCompanyMap.map.plugin(["AMap.Geocoder"], function () {
            var geo = new $scope.AMap.Geocoder({
                radius: 1000,
                extensions: "all"
            });
            var loc = new $scope.AMap.LngLat(lat, lon);
            geo.getAddress(loc, function (status, result) {
                if (status == 'complete') {
                    deferred.resolve(result);
                } else {
                    console.log('map geo fail:', lat, lon, result);
                    message('获取地图错误', lat, lon, result)
                    deferred.reject(result);
                }
            });
        });
        return deferred.promise;
    };

    /**
     * 获取数据库校企信息
     *
     */
    $scope.getRecords = function () {
        var params = {
            page: $scope.current_page - 1,
            num: $scope.num
        };
        $http.get($scope.server_uri + '/resource/companys', {
            params: params
        }).success(function (data) {
            $scope.companysShow = data.companys
        });
    };
    /**
     * 搜索校企
     * @param:name:address:type
     *
     */
    $scope.searchRecords = function () {

        $http.get($scope.server_uri + '/resource/companys/search',{
            params: {
                searchKey : $scope.searchKey
            }
        }).success(function (data) {
            if(data.code == 0){
                $scope.companysShow = data.companySet
                var resultLength = data.companySet.length
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
            message('未知错误，请换个关键字重新搜索', '','error')
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
        $http.get($scope.server_uri + '/resource/companys', {
            params: params
        }).success(function (data) {
            $scope.companysShow = data.companys
        });
        var a= [];
        for (var i = 1; i < $scope.totalPage +1; i++) {
            a.push(i);
            if (i >= 10) break;
        }
        $scope.pagelist = a
        $scope.jumpPage = JumpPage();
    }
    /***
     * 页数跳转
     *
     */
    $scope.jumpPage = JumpPage();
    $scope.pagination = pagination($scope.server_uri + '/resource/companys/count', function (data) {
        return data.count;
    })._pagination ;
    /**
     *
     * 删除数据
     * @param companyid
     */
    $scope.delete = function (companyid, aCompany) {
        var confirm = window.confirm("确定删除" + companyid + "?");
        if (confirm) {
            $http.delete($scope.server_uri + '/resource/company/' + companyid).success(function (data) {
                if (data.code == 0){
                    $scope.companysShow.splice($scope.companysShow.indexOf(aCompany), 1);
                    message(data.msg, data.code, 'success');
                }
                else if (data.code == 1001){
                    message(data.msg, data.code, 'error');
                }
            }).error(function (data) {
                message(data.msg, '', 'error')
            })
        }
        else message('你取消了删除')
        console.log(companyid)
    };
    /**
     *
     * 修改校企数据
     * @param company
     */
    $scope.modify = function (company) {
        $scope.company = company;
        if (company.content) $scope.quillChange.clipboard.dangerouslyPasteHTML(company.content);
        if (company.loc) {
            var loc = new $scope.AMap.LngLat(company.loc[0], company.loc[1]);
            $scope.editCompanyMap.marker.setPosition(loc);
            $scope.editCompanyMap.map.setCenter(loc);
        }
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
     * 确认修改触发方法
     *
     */
    $scope.submitModify = function () {
        var form = $('#editModal form');

        var content = $scope.quillChange.root.innerHTML;
        setFormField(form, 'content', content);
        $scope.company.content = content;

        form.ajaxForm();

        function success(data) {
            if (data.code == 0) {
                message('修改成功', '', 'success')
            }else {
                message('修改出错', data.code)
            }
        }
        var loc = $scope.editCompanyMap.marker.getPosition();
        var lon = loc.getLng();
        var lat = loc.getLat();
        $scope.mapResolveAddress(lon, lat).then(function (data) {
            console.log(data);
            if (data.info == 'OK') {
                setFormField(form, 'lon', lon);
                setFormField(form, 'lat', lat);
                setFormField(form, 'province', data.regeocode.addressComponent.province);
                setFormField(form, 'city', data.regeocode.addressComponent.city);
                setFormField(form, 'citycode', data.regeocode.addressComponent.citycode);
                setFormField(form, 'district', data.regeocode.addressComponent.district);
                setFormField(form, 'adcode', data.regeocode.addressComponent.adcode);
                setFormField(form, 'address', data.regeocode.formattedAddress);

                form.ajaxSubmit({
                    url: $scope.server_uri + '/resource/company/' + $scope.company._id,
                    dataType: 'json',
                    success: success
                });
            } else {
                console.log('geo loc fail:', data);
            }
        });
    };
    /**
     *
     * 添加校企
     */
    $scope.companySubmit = function () {
        var form = $('#newModal form');
        form.find('input[name="content"]').val($scope.companyQuill.root.innerHTML);
        form.ajaxForm();

        function success(data) {
            if (data.code == 0) {
                $scope.getRecords();
                message('添加成功', '', 'success');
                form.find('input').val("");
                $scope.companyQuill.root.innerHTML = "";
                console.log(form,'<<<<----form----->>>>')
            }
            else {
                message('添加出错', data.code, 'error');

            }
        }
        var loc = $scope.newCompanyMap.marker.getPosition();
        var lon = loc.getLng();
        var lat = loc.getLat();
        $scope.mapResolveAddress(lon, lat).then(function (data) {
            if (data.info == 'OK') {
                setFormField(form, 'lon', lon);
                setFormField(form, 'lat', lat);
                setFormField(form, 'province', data.regeocode.addressComponent.province);
                setFormField(form, 'city', data.regeocode.addressComponent.city);
                setFormField(form, 'citycode', data.regeocode.addressComponent.citycode);
                setFormField(form, 'district', data.regeocode.addressComponent.district);
                setFormField(form, 'adcode', data.regeocode.addressComponent.adcode);
                setFormField(form, 'address', data.regeocode.formattedAddress);
                form.ajaxSubmit({
                    url: $scope.server_uri + '/resource/companys',
                    dataType: 'json',
                    success: success
                });
            } else {
                message('添加出错', data);
                console.log('geo loc fail:', data);
            }
        });
    };
    /**
     *
     * 初始化quill编辑器
     */
    $scope.companyQuill = new Quill('#newCompany', {
        modules: {
            toolbar: [
                [{header: [1, 2, false]}],
                ['bold', 'italic', 'underline'],
                ['image', 'code-block']
            ]
        },
        placeholder: '请输入校企详情页面内容',
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
        placeholder: '请输入校企详情页面内容',
        theme: 'snow' // or 'bubble'
    });
});

