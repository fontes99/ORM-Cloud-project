#!/bin/bash

sudo apt update; sudo apt install nodejs build-essential -y

echo  """#!/usr/bin/env nodejs
var http = require('http');
var os = require('os');
var crypto = require('crypto');
http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    var nonce = 1;
    var seed = Math.random();
    var h = crypto.createHash('sha256');
    h.update(new Buffer(nonce + ""'Hello World '"" + seed));
    while (h.digest(""'hex'"").substr(0,3)!='000') {
        h = crypto.createHash('sha256');
        nonce++;
        h.update(new Buffer(nonce + "" 'Hello World' "" + seed));
    }
    res.end(""'""{ "'"'"host"'"'": ' + os.hostname() + ', "'"'"nonce"'"'": ' + nonce + '}');
}).listen(8080, '');
console.log('Server running at http://localhost:8080/');
"""> server.js

chmod +x ./server.js
./server.js

