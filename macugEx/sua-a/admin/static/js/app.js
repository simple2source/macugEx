var admin = angular.module('admin', ['ngRoute', 'angular-spinner', 'ui.bootstrap', 'ui.bootstrap.datetimepicker']);

admin.config(['$routeProvider', '$interpolateProvider', '$locationProvider', function ($routeProvider, $interpolateProvider, $locationProvider) {
    $routeProvider
        .when('/', {
            templateUrl: "/static/views/profile.html",
            controller: "profile"
        });

    $('#menubar .control').each(function (index, li) {
        var control = $(li).attr('control');
        if (control) {
            $routeProvider
                .when('/' + control, {
                    templateUrl: "/static/views/" + control + ".html",
                    controller: control
                });
        }
    });


    //.otherwise({
    //    templateUrl: '/static/views/watch_info.html',
    //    controller: 'watch_info'
    //});

    $locationProvider.html5Mode({
        enabled: false,
        requireBase: true
    });

    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

function pagination(url, func) {
    var $scope = angular.element('#ng-view').scope();
    var inject = angular.element('#ng-view').injector();
    var $q = inject.get('$q');
    var $http = inject.get('$http');

    if (!$scope.getLength) {
        // $scope.getLength is function return the Promise
        if ($http && url) {
            $scope.getLength = function () {
                var deferred = $q.defer();
                $http.get(url).success(function (data) {
                    if (func) {
                        deferred.resolve(func(data));
                    } else {
                        deferred.resolve(data);
                    }
                });
                return deferred.promise;
            }
        } else {
            throw Error('$scope undefinition "getLength" Method before pagination')
        }
    }
    var _pagination = function () {
        $scope.getLength().then(function (data) {
            $scope.length = parseInt(data);
            $scope.totalPage = Math.ceil($scope.length / $scope.num);
            var a = [];
            for (var i = 1; i < $scope.totalPage + 1; i++) {
                a.push(i);
                if (i >= 10) break;
            }
            $scope.pagelist = a;
        });
        $scope._prev_num = $scope.num;
        $scope._prev_query = $scope.query;
    };
    if (!$scope._has_pagination) {
        _pagination();
        $scope._has_pagination = true;
    }
    return _pagination
}

function JumpPage() {
    var $scope = angular.element('#ng-view').scope();
    if (!$scope.getRecords) {
        throw Error('$scope undefinition "getRecords" Method before jumpPage');
    }
    if (!$scope.numlist)$scope.numlist = [10, 20, 30, 50, 100, 200, 300];
    if (!$scope._paginateTotal) $scope._paginateTotal = 10;
    if (!$scope.length) $scope.length = 0;
    if (!$scope.num) $scope.num = $scope.numlist[0];
    if (!$scope.pagelist) $scope.pagelist = [];
    if (!$scope.current_page) $scope.current_page = 1;

    return function (page) {
        var k = 0;
        for (var i = 0; i < $scope.pagelist.length; i++) {
            if (page == $scope.pagelist[i]) k = 1;
        }
        var ignore = 0;
        if (!k && page == 1) {
            var a = [];
            for (var i = 0; i < this._paginateTotal; i++) {
                if (i >= $scope.totalPage) break;
                a.push(i + 1);
            }
            $scope.pagelist = a;
            ignore = 1;
        }
        if (!k && page == $scope.totalPage) {
            var a = [];
            for (var i = 0; i < this._paginateTotal; i++) {
                var value = $scope.totalPage - i;
                if (value <= 0) break;
                a.unshift(value);
            }
            $scope.pagelist = a;
            ignore = 1;
        }
        if (!ignore && !k && page < $scope.pagelist[0]) {
            var a = [];
            var last = $scope.pagelist[0] - 1;
            for (var i = 0; i < this._paginateTotal; i++) {
                var value = last - i;
                if (value <= 0) break;
                a.unshift(value);
            }
            $scope.pagelist = a;
        }
        if (!ignore && !k && page > $scope.pagelist[$scope.pagelist.length - 1]) {
            var a = [];
            var first = $scope.pagelist[$scope.pagelist.length - 1] + 1;
            for (var i = 0; i < this._paginateTotal; i++) {
                var value = first + i;
                if (value > $scope.totalPage) break;
                a.push(value);
            }
            $scope.pagelist = a;
        }
        $scope.current_page = page;
        $scope.getRecords();
    };
}


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

