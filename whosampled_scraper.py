# original song, sampler song, orig, sampler artist
import json
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

CHECK_IN_ALLOWED=False


# this method was made to get past json dump errors with accents and shit
def text_normalize(text):
    try:
        return unicodedata.normalize('NFKD', unicode(text, 'utf-8'))
    except:
        return unicodedata.normalize('NFKD', text)

# given json filename, return the set
def load_json_data(filedir):
    json_data = open(filedir).read()
    data = json.loads(json_data)
    return data

sample_links = load_json_data("data/en_songid.json")
allowed_artists = load_json_data("allowed_artists_expanded.json")

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
                if int(header.span.text.strip().split()[-2]) > 5: #number of things it was sampled in
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
    try:
        return text_normalize(song_title)
    except:
        return song_title

#current song we are looking at
def get_song_artist(soup):
    song_track = soup.body.find("div", {"class": "trackWrap"})
    song_artists = song_track.find("span", {"class" : "trackArtists"}).find_all("a")
    current_song_artist = song_artists[0].text
    try:
        # if can be converted, then convert u'\xe8'
        current_song_artist = text_normalize(current_song_artist)
    except:
        pass
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
        if CHECK_IN_ALLOWED and song_artist not in allowed_artists:
            print "sampl(ed)/(er) song artist not in there: %s"%song_artist
            continue

        try:
            song_name = text_normalize(song_name)
        except Exception, e:
            print "#####"
            print str(e)
            print "#####"

        try:
            song_artist = text_normalize(song_artist)
        except Exception, e:
            print "#####"
            print str(e)
            print "#####"


        append_tuple = {"title":song_name, "artist":song_artist}
        song_dicts.append(append_tuple)
    return song_dicts


data_dict = {}
def run():
    filedir = "allowed_artists_expanded.json"
    allowed_artists = load_json_data(filedir)

    data_dict = {}

    #change sample links to songs that jerry seeds for me
    i = 0
    for rgId, wsId in sample_links.items():
        try:
            i += 1
            link = "http://www.whosampled.com/track/view/%s" % wsId
            print link
            r = requests.get(link)
            soup = BeautifulSoup(r.text)

            current_song_title = get_song(soup)
            current_song_artist = get_song_artist(soup)
            if CHECK_IN_ALLOWED and current_song_artist not in allowed_artists:
                print "current song artist not in there: %s" %current_song_artist
                continue
            current_song_dict= {"title":current_song_title,"artist": current_song_artist}
            current_song_key = rgId

            sampled_from = []
            try:
                sampled_from = get_songs(soup, 0)
            except Exception,e:
                print "=========="
                print "problem 1"
                print str(e)
                print "=========="

            sampled_by = []
            try:
                sampled_by = get_songs(soup, 1)
            except Exception,e:
                print "**********"
                print "problem 2"
                print str(e)
                print "**********"

            data_dict[current_song_key] = {"song":current_song_dict,"sampled_from": sampled_from, "sampled_by": sampled_by}

            if i % 200 == 0:
                with open('whosampled_data_no_checks.json', 'w') as outfile:
                    json.dump(data_dict, outfile, sort_keys = True, indent = 4, ensure_ascii=True)
        except Exception, e:
            print "++++++++++"
            print "problem 3"
            print str(e)
            print "++++++++++"
            print sampled_from
            print sampled_by
            print "++++++++++"

    with open('whosampled_data.json', 'w') as outfile:
        json.dump(data_dict, outfile, sort_keys = True, indent = 4, ensure_ascii=True, encoding='utf-8')


if __name__ == "__main__":
    run()
