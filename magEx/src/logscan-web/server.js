var _ = require("lodash");
var express = require('express');
var httpProxy = require('http-proxy');
var proxyConfig = require('./proxy.config');

var app = new express();
var port = 3000;

var proxy = httpProxy.createProxyServer({});

//app.use()
app.use('/static', express.static(__dirname+'/static'));

app.use(function(req, res){
  var service = req.get('x-service');
  if(proxyConfig.hasOwnProperty(service)) {
    var backend = proxyConfig[service];
    var timeout = backend.timeout?backend.timeout:30;
    proxy.web(req, res, {target: _.sample(backend.servers), xfwd:true}, function(error){
      console.log(error);
      res.status(502).json({code:502, error: error});
    });
  }else{
    res.sendFile(__dirname + '/index.html');
  }
});

app.listen(port, function(error) {
  if (error) {
    console.error(error);
  } else {
    console.info("Listening on port %s. Open up http://localhost:%s/ in your browser.", port, port);
  }
});


function Stack() {

}

Stack.pro
