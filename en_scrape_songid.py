import json
import urllib
import io
import time

APIKEY = "HAIKKE9E0URQNNYSN"
raw_output = {}
errors = []
wait_time = 60.0
num_requests = 0
num_found = 0

raw_data = open("data/songs_dump.json")
songs = json.load(raw_data)
print "Loading", str(len(songs)), "songs"

for song in songs:
  artist = urllib.quote(songs[song]['mainArtist'].encode("utf-8"))
  title = urllib.quote(songs[song]['songTitle'].encode("utf-8"))
  url = "http://developer.echonest.com/api/v4/song/search?api_key="+APIKEY+"&format=json&results=1&artist="+artist+"&title="+title+"&bucket=id:whosampled&limit=true&bucket=tracks"
  id = 0
  while(not id):
    raw_result = urllib.urlopen(url)
    result = json.loads(raw_result.read().decode("utf-8"))
    try:
      if result['response']['songs']:
        raw_id = result['response']['songs'][0]['tracks'][0]['foreign_id']
        id = raw_id.split(':')[2]
        raw_output[song] = id
        num_found += 1
      else:
        break
    except KeyError:
      if result['response']['status']['code'] == 4:
        errors.append(song)
        break
      print "Reached rate limit, waiting "+str(wait_time/60)+" minutes. " + str(num_requests) + " requested so far."
      # print result
      # print title
      # print artist
      time.sleep(wait_time)
      wait_time += 60.0
      print "Resuming queries"
    time.sleep(0.8)
  wait_time = max(60.0, wait_time/2)
  num_requests += 1
  if num_requests%100 == 0:
    with io.open('data/en_songid.json', 'w', encoding='utf-8') as f:
      f.write(unicode(json.dumps(raw_output, ensure_ascii=False)))
    print "Done with " + str(num_requests) + " songs"

with io.open('data/en_songid.json', 'w', encoding='utf-8') as f:
  f.write(unicode(json.dumps(raw_output, ensure_ascii=False)))

  
with io.open('data/errors.txt', 'w', encoding='utf-8') as f:
  for song in errors:
    f.write(song)

  
print str(num_found) + " songs were found in EchoNest"
