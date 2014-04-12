var fs = require("fs");
var artists = fs.readFileSync("./artists.dump");
var songs = fs.readFileSync("./songs_dump.json");

artists = JSON.parse(artists);
artists = Object.keys(artists);
songs = JSON.parse(songs);

function doArtists() {
  console.log('name');
  Object.keys(artists).forEach(function(a){
    console.log(a);
  });
}

var artmap = {};
function doSongs() {

  Object.keys(songs).forEach(function(k) {
    var song = songs[k];
    artmap[song.mainArtist] = true
    song.featuringArtists.forEach(function(feat) {
      artmap[feat] = true
    });
    song.producingArtists.forEach(function(prod) {
      artmap[prod] = true
    });
  });
  //Object.keys(artmap).forEach(function(a){
    //a = a.replace(/\"/g, "'");
    //console.log("CREATE ({name: \"" + a + "\"});");
  //});
  //return

  artmap = Object.keys(artmap);

  Object.keys(songs).forEach(function(k) {
    var song = songs[k];
    // mainArtist v everyone else
    song.featuringArtists.forEach(function(feat) {
      printCypher(song.mainArtist, feat, "main artist", "featuring artist", song.songTitle);
      printCypher(feat, song.mainArtist, "featuring artist", "main artist", song.songTitle)
    });
    song.producingArtists.forEach(function(prod) {
      printCypher(song.mainArtist, prod, "main artist", "producer", song.songTitle);
      printCypher(prod, song.mainArtist,"producer", "main artist", song.songTitle);

      song.featuringArtists.forEach(function(feat) {
        printCypher(prod, feat, "producer", "featuring artist", song.songTitle);
        printCypher(feat, prod, "featuring artist", "producer", song.songTitle);
      });
    });
  });

}

function printCypher(nodea, nodeb, rolea, roleb, title) {
  console.log("MATCH (a {name:'"+nodea+"'}), (b {name:'"+nodeb+"'}) CREATE (a)-[:COLLABORATED {start_role: '"+rolea+"', end_role:'"+roleb+"', song:'"+title+"'}]->(b);")
}

doSongs();
