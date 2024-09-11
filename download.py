import requests
from bs4 import BeautifulSoup

async def Down(name):
	headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36"
	}

	punc = '''!()[]{};:'"\\<>./?@#$%^&*_~'''
	url_track = name
	for ele in url_track:
		if ele in punc:
			url_track = url_track.replace(ele, "")
	url_track = url_track.split()
	req = '+'.join(url_track)
	url_track_ptf = f"https://ru.patefon.cc/search/{req}"
	url_track_mstr = f"https://muz-monster.ru/?song={req}"

	try:
		request = requests.get(url_track_ptf, headers)
		soup = BeautifulSoup(request.text, "lxml")
		url = soup.find("main").find("a", class_="tracks-card__download-btn").get("href")
		track = f"https://ru.patefon.cc{url}"
		service = "Patefon"
	except:
		request = requests.get(url_track_mstr, headers)
		soup = BeautifulSoup(request.text, "lxml")
		url = soup.find(class_="results").find(class_="chkd").find(class_="link").get("href")
		track = f'https://muz-monster.ru/mp3/{url}'
		service = "Muz Monster"

	return track, service