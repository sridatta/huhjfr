var request = require('request');
var express = require("express");
var path = require('path');

var shortestPathQuery = "MATCH (a:Artist { name:{startName} }),(b:Artist { name:{endName}}), p = shortestPath((a)-[*]->(b)) RETURN extract(x in nodes(p) | x.name), extract(x in relationships(p) | x.song),  extract(x in relationships(p) | x.start_role),  extract(x in relationships(p) | x.end_role)"

var app = express();
app.set('views', __dirname + '/views');
app.engine('html', require('ejs').renderFile);
app.use(express.static(path.join(__dirname, 'public')));
app.use(app.router);

app.get("/", function(req, res) {
  res.render('index.html');
});

app.get("/api/path", function(req, res) {
  getPath(req.query.start, req.query.end, function(err, path){
    res.json(path);
  });
});

app.listen(8000);

function getPath(startName, endName, cb) {
  var queryBody = {
    query: shortestPathQuery,
    params : {
      startName: startName,
      endName: endName
    }
  }
  var data = {
    uri: "http://localhost:7474/db/data/cypher",
    headers: {
      "Accept": "application/json; charset=UTF-8",
      "Content-Type":  "application/json"
    },
    body: JSON.stringify(queryBody)
  }
  request.post(data, function(err, res, data){
    if(err) cb(err);
    data = JSON.parse(data);
    var path = [];
    if(data.data.length == 0) return [];
    
    var artists = data.data[0][0];
    var songs = data.data[0][1];
    var startRoles = data.data[0][2];
    var endRoles = data.data[0][3];

    for(var i = 0; i < artists.length - 1; i++) {
      path.push({start: artists[i], end: artists[i+1], startRole: startRoles[i], endRole: endRoles[i], song: songs[i]});
    }
    cb(null, path);
  });
}

