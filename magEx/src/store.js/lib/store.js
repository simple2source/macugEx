(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define("store", [], factory);
	else if(typeof exports === 'object')
		exports["store"] = factory();
	else
		root["store"] = factory();
})(this, function() {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;
/******/
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports) {

	"use strict";
	
	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	
	var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();
	
	function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
	
	var Store = function () {
	  function Store() {
	    _classCallCheck(this, Store);
	  }
	
	  _createClass(Store, null, [{
	    key: "get",
	    value: function get(key) {
	      var origin = localStorage.getItem(key);
	      var now = new Date();
	      if (origin) {
	        var value = JSON.parse(origin);
	        if (value.expireAt <= 0) {
	          return value.data;
	        }
	        if (now.valueOf() >= value.expireAt) {
	          localStorage.removeItem(key);
	          return null;
	        }
	        return value.data;
	      }
	      return null;
	    }
	  }, {
	    key: "set",
	    value: function set(key, data) {
	      var expire = arguments.length <= 2 || arguments[2] === undefined ? 0 : arguments[2];
	      var expireAt = arguments.length <= 3 || arguments[3] === undefined ? null : arguments[3];
	
	      var now = new Date().valueOf();
	      var _expireAt = 0;
	      var _expire = 0;
	      if (expireAt) {
	        _expireAt = expireAt.valueOf();
	        _expire = _expireAt - now;
	      } else {
	        _expireAt = expire === 0 ? 0 : now + expire;
	        _expire = expire;
	      }
	      var value = {
	        expireAt: _expireAt,
	        expire: _expire,
	        data: data
	      };
	      localStorage.setItem(key, JSON.stringify(value));
	    }
	  }, {
	    key: "remove",
	    value: function remove(key) {
	      localStorage.removeItem(key);
	    }
	  }, {
	    key: "getset",
	    value: function getset(key) {
	      var origin = localStorage.getItem(key);
	      if (origin) {
	        var value = JSON.parse(origin);
	        if (value.expireAt <= 0) {
	          return value.data;
	        }
	        if (new Date().valueOf() >= value.expireAt) {
	          localStorage.removeItem(key);
	          return null;
	        }
	        Store.set(key, value.data, value.expire);
	        return value.data;
	      }
	      return null;
	    }
	  }]);
	
	  return Store;
	}();

	exports.default = Store;
	module.exports = exports['default'];

/***/ }
/******/ ])
});
;
//# sourceMappingURL=store.js.map