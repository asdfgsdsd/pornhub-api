# -*- coding: UTF-8 -*-

from .core import *
import re

class Videos(object):
    
    def __init__(self, ProxyDictionary, keywords=None, pro=False, home=False, sort=None, timeframe="a", country=None, hd=False, category=None, *args):
        """

        :param ProxyDictionary:
        :param keywords: The keywords to search, if keyword searching. Defaults to not searching.
        :param pro: Whether to only show professional videos. Defaults to false.
        :param home: Whether to only show home videos. Defaults to false.
        :param sort: How to sort. Options are mr for Featured Recently, mv for Most Viewed, tr for Top Rated, ht for Hottest, lg for Longest, and cm for newest. Defaults to Most Relevant.
        :param timeframe: The timescale to restrict mv or tr to. Options are t for daily, w for weekly, m for monthly, y for yearly, and a for all time. Defaults to all time.
        :param country: The country to restrict mv or ht to. Defaults to global. Too many options to list, sorry.
        :param hd: Whether to limit to only HD video. Defaults to false.
        :param args:
        """
        if keywords is None:
            keywords = []
        self.keywords = keywords
        self.ProxyDictionary = ProxyDictionary
        self.pro = pro
        self.home = home
        self.sort = sort
        self.timeframe = timeframe
        self.country = country
        self.hd = hd
        self.category = category

    def _craftVideoURL(self, page_num=1):
        # url example:
        # pornhub.com/video/search?search=arg1+arg2
        # pornhub.com/video/search?search=arg1+arg2&p=professional
        # pornhub.com/video/search?search=arg1+arg2&p=professional&page=3

        payload = {}

        if len(self.keywords) > 0:
            payload["search"] = ""
            for item in self.keywords:
                payload["search"] += (item + " ")

        if self.pro:
            payload["p"] = "professional"
        elif self.home:
            payload["p"] = "homemade"

        if self.category is not None:
            payload["c"] = self.category

        if not (self.sort is None or (len(self.keywords) > 0 and (self.sort == "ht" or self.sort == "cm"))):
            payload["o"] = self.sort
            if self.sort == "mv" or self.sort == "tr":
                payload["t"] = self.timeframe
            if (self.sort == "mv" or self.sort == "ht") and self.country is not None:
                payload["cc"] = self.country

            if self.hd:
                payload["hd"] = "1"

            payload["page"] = page_num

        return payload

    def _loadVideosPage(self, page_num):
        if len(self.keywords) > 0:
            URL_str = BASE_URL + VIDEOS_SEARCH_URL
        else:
            URL_str = BASE_URL + VIDEOS_URL
        # print(URL_str)
        # print(self._craftVideoURL())
        r = requests.get(URL_str, params=self._craftVideoURL(page_num), headers=HEADERS, proxies=self.ProxyDictionary)
        html = r.text

        return BeautifulSoup(html, "lxml")

    def _scrapLiVideos(self, soup_data):
        return soup_data.find("ul", {"class":re.compile(".*search-video-thumbs.*")}).find_all("li", { "class" : re.compile(".*videoblock videoBox.*") } )

    def _scrapVideoInfo(self, div_el):
        data = {
            "name"          : None,     # string
            "url"           : None,     # string
            "rating"        : None,     # integer
            "duration"      : None,     # string
            "background"    : None      # string
        }

        # scrap url, name
        for a_tag in div_el.find_all("a", href=True):
            try:
                url = a_tag.attrs["href"]
                if isVideo(url):
                    data["url"] = BASE_URL + url
                    data["name"] = a_tag.attrs["title"]
                    break
            except Exception as e:
                pass

        # scrap background photo url
        for img_tag in div_el.find_all("img", src=True):
            try:
                url = img_tag.attrs["data-thumb_url"]
                if isVideoPhoto(url):
                    data["background"] = url
                    break
            except Exception as e:
                pass

        # scrap duration
        for var_tag in div_el.find_all("var", { "class" : "duration" } ):
            try:
                data["duration"] = str(var_tag).split(">")[-2].split("<")[-2]
                break
            except Exception as e:
                pass

        # scrap rating
        for div_tag in div_el.find_all("div", { "class" : "value" } ):
            try:
                data["rating"] = int( str(div_tag).split(">")[1].split("%")[0] )
                break
            except Exception as e:
                pass

        # return
        return data if None not in data.values() else False

    def getVideos(self, quantity = 1, page = 1, infinity = False):
        """
        Get videos basic informations.

        :param quantity: number of videos to return
        :param page: starting page number
        :param infinity: never stop downloading
        """

        quantity = quantity if quantity >= 1 else 1
        page = page if page >= 1 else 1
        found = 0

        while True:

            for possible_video in self._scrapLiVideos(self._loadVideosPage(page)):
                data_dict = self._scrapVideoInfo(possible_video)

                if data_dict:
                    yield data_dict

                    if not infinity:
                        found += 1
                        if found >= quantity: return

            page += 1