import requests
from bs4 import BeautifulSoup
import time
import os

async def GetMusicList(message, tg_name, name=None):
	url = message.text
	try:
		os.mkdir(f'./Users/{tg_name}')
	except:
		pass
	url = url.split('/')
	y_name = url[4]
	playlist_id = url[6]
	url = f"https://music.yandex.ru/handlers/playlist.jsx?owner={y_name}&kinds={playlist_id}&light=false&withLikesCount=true&external-domain=music.yandex.ru"
	response = requests.get(url).json()
	stroke = ''
	for i in response["playlist"]["tracks"]:
		try:
			warning = i['contentWarning']
			warning = '🔞 | '
		except:
			warning = ''
		arts = []
		for j in i["artists"]:
			arts.append(j["name"])
		duraction = i['durationMs'] // 1000
		list_name = response['playlist']['title']
		stroke += f"{warning}{', '.join(arts)} - {i['title']} | {time.strftime('%M:%S', time.gmtime(duraction))}\n"
	
	list_user = os.listdir(f'./Users/{tg_name}')
	try: list_user.remove(f'r#{message.chat.id}.txt')
	except: pass
	music_indexs = []
	count_play = []
	if len(list_user)> 0:
		for music_index in list_user:
			music_indexs.append(int(music_index.split('_')[0]))
			if music_index.split('_')[1].split('.txt')[0] == list_name:
				count_play.append(int(music_index.split('_')[-1].split('.txt')[0]))
		for i in range(max(count_play)):
			print(i, sorted(count_play)[i])
			if i != sorted(count_play)[i]:
				count_play = i
				break
		if type(count_play) is list:
			count_play = sorted(count_play)[-1] + 1
		max_index = max(music_indexs)
		list_name = f"{int(max_index) + 1}_" + list_name + f"_{count_play}"
	else: list_name = "0_" + list_name + "_0"

	if name != None:
		list_name = name
	with open(f"./Users/{tg_name}/{list_name}.txt", "w", encoding="utf-8") as file:
		file.write(stroke)

	return list_name

async def GetListMusicText(name):
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
	
	musics = {}
	url_track_ptf = f"https://ru.patefon.cc/search/{req}"
	request = requests.get(url_track_ptf, headers)
	soup = BeautifulSoup(request.text, "lxml")
	max_page = len(soup.find('main').find_all('li', class_='pagination__item'))
	k=0
	service = "Patefon"
	musics[service] = {}
	for i in range(max_page):
		url_track_ptf = f"https://ru.patefon.cc/search/{req}?page={i+1}"
		request = requests.get(url_track_ptf, headers)
		soup = BeautifulSoup(request.text, "lxml")
		track_info = soup.find("main").find_all(class_='tracks-card')
		for info in track_info:
			k+=1
			link = f"https://ru.patefon.cc{info.find('a', class_='tracks-card__download-btn').get('href')}"
			try: artist = info.find(class_='tracks-card__desc').find('a').text
			except: artist = "Неизвестный"
			title = info.find('a', class_='tracks-card__title').text
			name = artist + ' - ' + title
			musics[service][k] = [name, link]

	url_track_mstr = f"https://muz-monster.ru/?song={req}"
	request = requests.get(url_track_mstr, headers)
	soup = BeautifulSoup(request.text, "lxml")
	track_info = soup.find(class_="results").find_all(class_="chkd")
	service = "Muz Monster"
	musics[service] = {}
	for info in track_info:
		k+=1
		link = f"https://muz-monster.ru/mp3/{info.find('a', 'link').get('href')}"
		title = info.find('span', class_='title').find_all('a')
		title = [i.text for i in title]
		name = title[0] + ' - ' + title[1]
		musics[service][k] = [name, link]

	return musics