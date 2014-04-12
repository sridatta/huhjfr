var allowedArtists = require("./artists.json");
var rapgeniusClient = require("rapgenius-js");

var fs = require('fs');
var async = require('async');
var songs = {};
var visitedArtists = {};
var visitedSongs = {};

var q = async.queue(function fetchArtist(artistName, cb) {
  console.log("Started artist:", artistName);
  visitedArtists[artistName] = true;
  rapgeniusClient.searchArtist(artistName, "rap", function(err, artist){
    if(err){
      console.log("Error: " + err);
      cb();
    }else{
      async.each(artist.songs, function(song, callback) {
        if(!(song.link in visitedSongs)) { 
          fetchSong(song.link, callback);
        } else {
          callback();
        }
      }, function(err) {
        console.log("Finished artist:", artistName);
        cb();
      });
    }
  });
}, 10);

q.drain = function() {
  console.log("FINISHED WITH ENTIRE RUN");
  fs.writeFileSync("songs.dump", JSON.stringify(visitedSongs));
  fs.writeFileSync("artists.dump", JSON.stringify(visitedArtists));
};


// Seed the queue with popular artists
var seed = ["Kanye West", "Diddy", "Jay-Z", "Dre", "Birdman", "50 Cent", "Lil Wayne"];
seed.forEach(function(a) { q.push(a) });

function concat(a, b) {
  return Array.prototype.push.apply(a, b);
}

function fetchSong(songLink, cb) {
  console.log("Started song", songLink);
  rapgeniusClient.searchLyricsAndExplanations(songLink , "rap", function(err, res) {
    if(err) return cb();

    var song = res.lyrics;
    //console.log(song.songId, song.songTitle, song.mainArtist, song.featuringArtists, song.producingArtists);
    visitedSongs[songLink] = song;
    var relatedArtists = [song.mainArtist];
    concat(relatedArtists, song.featuringArtists);
    concat(relatedArtists, song.producingArtists);
    relatedArtists.forEach(function(art) {
      if(!(art in visitedArtists) && art in allowedArtists) {
        visitedArtists[art] = true;
        console.log("q-ing", art);
        q.push(art);
      }
    });

    console.log("Done with song", songLink);
    cb();
  });
}

setInterval(function() {
  console.log("QUEUE LENGHT", q.tasks.length, "COMPLETED", Object.keys(visitedArtists).length);
  fs.writeFileSync("songs.dump", JSON.stringify(visitedSongs));
  fs.writeFileSync("artists.dump", JSON.stringify(visitedArtists));
}, 60000);

process.on('uncaughtException', function(err) { 
  fs.writeFileSync("songs.dump", JSON.stringify(visitedSongs));
  fs.writeFileSync("artists.dump", JSON.stringify(visitedArtists));
});
