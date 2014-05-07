# original song, sampler song, orig, sampler artist
import json
import requests
from bs4 import BeautifulSoup
import re

sample_links = ["http://www.whosampled.com/track/view/3898",
			"http://www.whosampled.com/track/view/4000",]


# given json filename, return the set
def load_json_data(filedir):
	json_data = open(filedir).read()
	data = json.loads(json_data)
	return data

def is_match(regex, text):
    pattern = re.compile(regex, text)
    return pattern.search(text) is not None

# this is where the page has the sampling information
def get_page_inner_content_list(soup, list_type):
	#list_type is either 0 or 1
		# 0: current song's original songs are
		# 1: list of songs that took from the current song
	inner_content = soup.body.find("div", {"id":"content"}).find("div", {"class": "innerContent"})
	item_list = inner_content.find_all("ul", {"class":"list"})
	header_list = inner_content.find_all("div", {"class": "sectionHeader"})
	if list_type == 0:
		for header, items in zip(header_list, item_list):
			if re.match("Contains samples of .*", header.span.text.strip()) is not None:
				return items
		return []
	elif list_type == 1:
		for header, items in zip(header_list, item_list):
			if re.match("Was sampled in .*", header.span.text.strip()) is not None:
				return items
		return []


# current song we are looking at
def get_song(soup):
	song_title = soup.body.find("div", {"class": "trackWrap"}).h1.text
	return song_title

#current song we are looking at
def get_song_artists(soup):
	song_track = soup.body.find("div", {"class": "trackWrap"})
	song_artists = song_track.find("span", {"class" : "trackArtists"}).find_all("a")
	main_artist = song_artists[0]
	return main_artist 


# this is the list of original song sources
# returns = list of tuples = [(song name, song artist),...]
def get_sampled_from(soup):
	song_items = get_page_inner_content_list(soup, 0)
	if len(song_items) == 0:
		return []
	sampled_from = []
	for song_item in song_items.find_all("li", {"class": "listEntry sampleEntry"}):
		song_detail = song_item.find("span", {"class": "trackDetails"})
		song_name = song_detail.find("a", {"class":"trackName playIcon"}).text
		song_artist = song_detail.find("span", {"class": "trackArtist"}).find("a").text
		append_tuple = (song_name, song_artist)
		sampled_from.append(append_tuple)
	return sampled_from



# this is the song sampled the current 
def get_sampled_by_songs(soup):
	pass

# song sampled by
def get_sampled_by_artists(soup):
	pass


def run():
	filedir = "allowed_artists.json"
	data = load_json_data(filedir)

	#change sample links to songs that jerry seeds for me
	for link in sample_links:
		r = requests.get(link)
		soup = BeautifulSoup(r.text)

		current_song_title = get_song(soup)
		main_artist = get_song_artists(soup)



soup = ""
if __name__ == "__main__":
	r = requests.get("http://www.whosampled.com/track/view/4000")
	soup = BeautifulSoup(r.text)
