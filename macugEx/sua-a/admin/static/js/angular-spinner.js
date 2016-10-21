(function(module) {
try { module = angular.module("angular-spinner.templates"); }
catch(err) { module = angular.module("angular-spinner.templates", []); }
module.run(["$templateCache", function($templateCache) {
  "use strict";
  $templateCache.put("spinner.tpl.html",
    "<div ng-class=\"spinnerClass()\">\n" +
    "  <span ng-transclude></span>\n" +
    "</div>");
}]);
})();

angular.module('angular-spinner', [  
  'angular-spinner.templates'
])

.directive("spinner", function() {
  return {
    restrict: 'A',
    controller: 'SpinnerController',
    scope: {
      spinnerName: '=?'
    },
    templateUrl: 'spinner.tpl.html',
    transclude: true
  }
})


.provider('spinner', function(){
  var options = {};

  this.setOptions = function(o){
    options = o;
  }

  this.$get = function($q, $timeout){
    this.spinners = {};
    var _this = this;

    this.start = function(name){
      $timeout(function(){
        _this.spinners[name] = true;
      })
    }

    this.stop = function(name){
      $timeout(function(){
        _this.spinners[name] = false;
      })

    }

    this.isSpinning = function(name){
      return this.spinners[name] === true;
    }

    this.stopAll = function(){
      this.spinners = {};
    }


    this.options = function(){
      return options;
    }


    this.disableFormFields = function (container, isDisabled) {
      if(!container) return;
      var tagNames = ["INPUT", "SELECT", "TEXTAREA"];
      for (var i = 0; i < tagNames.length; i++) {
        var elems = container.getElementsByTagName(tagNames[i]);
        for (var j = 0; j < elems.length; j++) {
          elems[j].disabled = isDisabled;
        }
      }
    }

    return this;
  }
})


.controller('SpinnerController', function($scope, $element, spinner, $timeout, $attrs){
  var spinnerName = $scope.spinnerName;
  if(!spinnerName) spinnerName = $attrs.spinnerName;

  spinner.spinners[spinnerName] = false;

  $scope.spinnerOptions = JSON.parse($attrs.spinnerOptions || null)  || spinner.options().spinnerConfig || {
    lines: 9, // The number of lines to draw
    length: 10, // The length of each line
    width: 4, // The line thickness
    radius: 6, // The radius of the inner circle
    corners: 1, // Corner roundness (0..1)
    rotate: 0, // The rotation offset
    direction: 1, // 1: clockwise, -1: counterclockwise
    color: '#000', // #rgb or #rrggbb or array of colors
    speed: 1, // Rounds per second
    trail: 60, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9
  };


  $scope.backgroundClass = $attrs.backgroundClass || spinner.options().backgroundClass || 'opaque';

  $scope.spinnerEl;  
  $scope.spinner = spinner;

  $scope.spinnerClass = function(){
    if($scope.spinner.spinners[spinnerName]){
      return $scope.backgroundClass;
    }
  }

  $scope.spinnerOn = function(){
    $scope.spinnerEl = new Spinner($scope.spinnerOptions).spin($element[0]);
    $scope.spinner.disableFormFields($element[0], true)
  }

  $scope.spinnerOff = function(){
    $scope.spinnerEl.stop();
  }

  $scope.$watch(function(){
    return $scope.spinner.spinners[spinnerName];
  }, function(newVal, oldVal){
    if(newVal !== oldVal){
      if(newVal ){
        $scope.spinnerOn();
      }
      else{
        $scope.spinnerOff()
      }
    }
  }, true);
})
angular.module("angular-spinner.config", [])

.constant("ENV", {})

;