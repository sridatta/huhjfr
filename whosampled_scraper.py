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


# this is where the page has the sampling information
def get_page_inner_content_list(soup, list_type):
	#list_type is either 0 or 1
		# 0: current song's original songs are. What does this current song sample from?
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
				if int(header.span.text.strip().split()[-2]) > 5:
					new_r = requests.get("http://whosampled.com" + str(header.find("a")['href']))
					new_soup = BeautifulSoup(new_r.text)
					new_inner_content =new_soup.body.find("div", {"id":"content"}).find("div", {"class":"leftContent"}).find("div", {"class":"innerContent"})
					new_items = new_inner_content.find("ul", {"class":"list"})
					return new_items 
				# if less than 6 songs, then they don't put it in another link
				return items
		return []


# current song we are looking at
def get_song(soup):
	song_title = soup.body.find("div", {"class": "trackWrap"}).h1.text
	return song_title

#current song we are looking at
def get_song_artist(soup):
	song_track = soup.body.find("div", {"class": "trackWrap"})
	song_artists = song_track.find("span", {"class" : "trackArtists"}).find_all("a")
	current_song_artist = song_artists[0].text
	return current_song_artist 


def get_songs(soup, list_type):
	#list_type is either 0 or 1
		# 0: current song's original songs are from? 
		# 1: list of songs that took from the current song
	song_items = get_page_inner_content_list(soup, list_type)
	if len(song_items) == 0:
		return []
	song_dicts = []
	for song_item in song_items.find_all("li", {"class": "listEntry sampleEntry"}):
		song_detail = song_item.find("span", {"class": "trackDetails"})
		song_name = song_detail.find("a", {"class":"trackName playIcon"}).text
		song_artist = song_detail.find("span", {"class": "trackArtist"}).find("a").text
		append_tuple = {"title":song_name, "artist":song_artist}
		song_dicts.append(append_tuple)
	return song_dicts


data_dict = {}
def run():
	filedir = "allowed_artists.json"
	data = load_json_data(filedir)

	data_dict = {}

	#change sample links to songs that jerry seeds for me
	for link in sample_links:
		r = requests.get(link)
		soup = BeautifulSoup(r.text)

		current_song_title = get_song(soup)
		current_song_artist = get_song_artist(soup)
		current_song_dict= {"title":current_song_title,"artist": current_song_artist}
		current_song_key = "%s +=+=+ %s" % (current_song_title, current_song_artist)

		sampled_from = get_songs(soup, 0)
		sampled_by = get_songs(soup, 1)

		data_dict[current_song_key] = {"song":current_song_dict,"sampled_from": sampled_from, "sampled_by": sampled_by}
	
	with open('whosampled_data.json', 'w') as outfile:
		json.dump(data_dict, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


if __name__ == "__main__":
	run()
