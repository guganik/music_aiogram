from aiogram import Bot, Dispatcher, F
import os
import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, URLInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
import requests
from bs4 import BeautifulSoup

import datetime
import time
import codecs
import json
import time
import multiprocessing
import logging

from idle import GetMusicList, GetListMusicText
import keyboards as k
import download as d

os.system("")

BOT_TOKEN = "7057005949:AAEqUsBerh_CeJBaWrzFv2h7mTeJttw51Zw"
# session = AiohttpSession(proxy='http://proxy.server:3128')

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

all_users = {}

class Form(StatesGroup):
	ymusic_list = State()
	list_name = State()
	up_list_name = State()
	select_page = State()
	new_playlist = State()

@dp.message(CommandStart())
async def Start(message: Message):
	await message.answer('<blockquote expandable>Привет! Этот бот разработан специально для тех, кого изрядно раздражает открывать приложение Яндекс Музыки, копировать оттуда ссылку на песню, отправлять ее другу, чтобы тот насладился этим творением, что занимает минимум 5 минут.\nСпециально для этого я создал бота, чтобы вы могли не переживать на этот счет.\n\nВсе, что нужно - отправить боту ссылку на свой плейлист из Яндекс Музыки и ждать, пока бот с помощью сторонних сервисов сможет найти и отправить вам необходимые аудиофайлы.</blockquote>\nНаслаждайтесь!\nНужна помощь с ботом? /help')
	with open('./Users/AllUsers.json', 'r') as file:
		all_users = json.load(file)
	list_users = [i for i, k in all_users.items()]
	if str(message.chat.id) not in list_users:
		print(f'\n\033[0;36m[log]\033[0m Пользователь впервые запустил бота!\n\033[0;35mID\033[0m: \033[0;32m{message.chat.id}\033[0m, \033[0;35mName\033[0m: \033[0;32m{message.from_user.username}\033[0m')
		all_users[message.chat.id] = message.from_user.username
		with open('./Users/AllUsers.json', 'w') as file:
			json.dump(all_users, file)

@dp.message(Command('say', prefix='!'))
async def Say(message: Message):
	if message.chat.id in [564605262, 419016539]:
		with open('./Users/AllUsers.json', 'r') as file:
			all_users = json.load(file)
		users_id = [i for i, k in all_users.items()]
		for i in users_id:
			if i != str(message.chat.id):
				await bot.send_message(text=message.text.split('!say')[1], chat_id=i)
		print(f'\n\033[0;36m[say]\033[0m Сообщение \033[0;33m"{message.text.split("!say")[1].strip()}"\033[0m было отправлено \033[0;32m{len(all_users)-1}\033[0m чел.\n\033[0;35mОтправитель\033[0m: \033[0;32m{message.chat.id}\033[0m')

@dp.message(Command(commands=['playlists', 'mymusic', 'плейлисты', 'музыка', 'моямузыка']))
async def GetLists(message: Message, state: FSMContext, callback='', delete='', user_name=None, add=''):
	if user_name == None:
		user_name = message.from_user.username
	try:
		dir = os.listdir(f'./Users/{user_name}')
	except:
		os.mkdir(f'./Users/{user_name}')
		dir = os.listdir(f'./Users/{user_name}')
	len_dir = len(dir)
	list_dir = []
	for i in range(len(dir)):
		if dir[i][:2] == 'r#':
			continue
		else:
			index = int(dir[i].split('_')[0])
			list_dir.insert(index, dir[i].split('.txt')[0])
	dir = list_dir[:10]
	await state.update_data(plus=0)
	plus = 0
	if len(dir) > 0:
		try:
			if callback == 'update':
				await message.message.answer(f'<b>Обновить плейлист</b>', reply_markup=await k.GetLists(dir, message.from_user.username, plus, len_dir, callback, delete, add))
			elif callback == 'add':
				await message.message.answer(f'<b>Выбери плейлист</b>', reply_markup=await k.GetLists(dir, message.from_user.username, plus, len_dir, callback, delete, add))
			else:
				await message.message.answer(f'<b>Плейлисты</b>', reply_markup=await k.GetLists(dir, message.from_user.username, plus, len_dir, callback, delete, add))
		except:
			if callback == 'update':
				await message.answer(f'<b>Обновить плейлист</b>', reply_markup=await k.GetLists(dir, message.from_user.username, plus, len_dir, callback, delete, add))
			elif callback == 'add':
				await message.answer(f'<b>Выбери плейлист</b>', reply_markup=await k.GetLists(dir, message.from_user.username, plus, len_dir, callback, delete, add))
			else:
				await message.answer(f'<b>Плейлисты</b>', reply_markup=await k.GetLists(dir, message.from_user.username, plus, len_dir, callback, delete, add))
	else:
		await message.answer('У тебя еще нет плейлистов. Загрузи первый!\n/help', reply_markup=await k.NewPlaylist())

@dp.message(Command(commands=['update']))
async def UpdatePlaylist(message: Message, state: FSMContext):
	await GetLists(message, state, callback='update')

@dp.message(Command(commands=['delete']))
async def DeletePlaylist(message: Message, state: FSMContext):
	await GetLists(message, state, delete='delete')

@dp.message(Command(commands=['cancel']))
async def CancelDownloadPlaylist(message: Message, state: FSMContext):
	await state.update_data(download_all=False)

async def SendMusic(message: Message, chat_id, music):
	data = await d.Down(music)
	try:
		await bot.send_chat_action(chat_id=chat_id, action='upload_document')
		await bot.send_audio(chat_id=chat_id, caption=f"Музыкальный сервис: {data[1]}", audio=URLInputFile(url=data[0], filename=music, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.10.0.0 Safari/537.36"}))
		print(f'\n\033[0;36m[log] Трек \033[0;33m"{music}"\033[0m с сервиса \033[0;33m"{data[1]}"\033[0m был отправлен пользователю\n\033[0;35mID\033[0m: \033[032;m{chat_id}\033[0m\n\033[0;35mСсылка\033[0m:\033[0;32m{data[0]}\033[0m\n')
	except:
		await bot.send_message(chat_id=chat_id, text='Песня не найдена :(')

@dp.message(Form.up_list_name)
async def UpdateListName(message: Message, state: FSMContext):
	if message.text[:24] == 'https://music.yandex.ru/':
		await YMusicGetMusic(message, state)
	else:
		await state.set_state(Form.up_list_name)
		await message.answer('Отправьте ссылку!')

@dp.message(Form.ymusic_list)
async def YMusicGetMusic(message: Message, state: FSMContext):
	try:
		data = await state.get_data()
		name = data['update_name']
	except:
		name = None
	list_name = await GetMusicList(message, message.from_user.username, name)
	await state.clear()
	if int(list_name.split("_")[2].split(".txt")[0]) > 0: count_play = f' {int(list_name.split("_")[2].split(".txt")[0])+1}'
	else: count_play = ''
	await message.answer(f'Плейлист \"{list_name.split("_")[1]}{count_play}\" создан!')
	print(f'\n\033[0;36m[log]\033[0m Пользователь \033[4mсоздал\033[0m плейлист \033[0;33m"{list_name}"\033[0m!\n\033[0;35mID\033[0m: \033[0;32m{message.chat.id}\033[0m, \033[0;35mName\033[0m: \033[0;32m{message.from_user.username}\033[0m\n\033[0;35mПуть к файлу\033[0m: \033[0;32m"./Users/{message.from_user.username}/{list_name}.txt"\033[0m\n\033[0;35mСсылка\033[0m: \033[0;32m{message.text}\033[0m\n')

@dp.message(Form.select_page)
async def SelectPlaylistPage(message: Message, state: FSMContext):
	data = await state.get_data()
	index_playlist = data['index_playlist']
	playlist = codecs.open(f'./Users/{message.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
	len_list = len(playlist)
	if int(message.text) > len_list // 10:
		await message.answer('Введенное число слишком большое')
	elif int(message.text) <= 0:
		await message.answer('Введите число больше нуля')
	else:
		play_plus = int(message.text) * 10 - 10
		await state.update_data(play_plus=play_plus)
		data = await state.get_data()
		play_plus = data['play_plus']
		if len(playlist) >= 10:
			playlist = playlist[play_plus:play_plus+10]
		else:
			playlist = playlist[play_plus:]
		message_id = data['message_id']
		await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id, reply_markup=await k.GetMusic(playlist, index_playlist, message.from_user.username, play_plus, len_list))
	await bot.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id, message.message_id-1])

@dp.message(Form.new_playlist)
async def CreateNewPlaylist(message: Message, state: FSMContext):
	list_name = message.text
	list_user = os.listdir(f'./Users/{message.from_user.username}')
	try: list_user.remove(f'r#{message.chat.id}.txt')
	except: pass
	music_indexs = []
	count_play = []
	if len(list_user)> 0:
		for music_index in list_user:
			music_indexs.append(int(music_index.split('_')[0]))
			if music_index.split('_')[1].split('.txt')[0] == list_name:
				count_play.append(int(music_index.split('_')[-1].split('.txt')[0]))
		if len(count_play) > 0:
			for i in range(max(count_play)):
				if i != sorted(count_play)[i]:
					count_play = i
					break
			if type(count_play) is list:
				count_play = sorted(count_play)[-1] + 1
		else: count_play = 0
		max_index = max(music_indexs)
		list_name = f"{int(max_index) + 1}_" + list_name + f"_{count_play}"
	else:
		list_name = "0_" + list_name + "_0"
		count_play = 0
	await state.clear()
	if count_play > 1: count_play = f' {count_play}'
	else: count_play = ''
	await message.answer(f'Плейлист \"{message.text}{count_play}\" создан!')
	await GetLists(message, state, user_name=message.from_user.username)

@dp.message(Command('help'))
async def Help(message: Message, state: FSMContext):
	await state.set_state(Form.ymusic_list)
	await message.answer('Скинь ссылку на плейлист Я. Музыки. Она должна выглядить так:\nhttps://music.yandex.ru/users/<i><b>your_username</b></i>/playlists/<i><b>playlist_id</b></i>\nЛибо отправь мне название трека, который хочешь найти.\n\nЧтобы посмотреть свои плейлисты: /playlists\nЧтобы обновить плейлист: /update\nЧтобы удалить плейлист: /delete\n\n!! Чтобы выбрать определенную страницу нажмите на нумерацию страниц внутри плейлиста и введите нужную страницу.')

@dp.message(F.text)
async def FindMusicOrError(message: Message, state: FSMContext):
	if message.text[:24] == 'https://music.yandex.ru/':
		await YMusicGetMusic(message, state)
	elif message.text[:7] == 'https://':
		await message.answer('Бот еще не умеет искать музыку по ссылкам, кроме Я. Музыки :(')
	else:
		# try:
			musics_split = await GetListMusicText(message.text)
			if len(musics_split['Patefon']) + len(musics_split['Muz Monster']) > 0:
				plus = 0
				index_playlist = f'r#{message.chat.id}'
				await state.update_data(index_playlist=index_playlist)
				await state.update_data(plus=0)
				musics = []
				for service, music in musics_split.items():
					for index, title in music.items():
						musics.append(f'{title[0]} | {title[1]}')
				if len(musics) >= 10:
					musics_short = musics[plus:plus+10]
				else:
					musics_short = musics[plus:]
				with open(f'./Users/{message.from_user.username}/{index_playlist}.txt', 'w', encoding="utf-8") as file:
					file.write('\n'.join(musics))
				await message.answer(f'Вот, что удалось найти по запросу <b>{message.text}</b>', reply_markup=await k.GetMusicText(musics_short, plus, len(musics), index_playlist, message.from_user.username))
		# except:
		# 	await message.answer('Песня не найдена :(')

@dp.callback_query(F.data.split('$.$')[0] == 'lists')
async def Lists(call: CallbackQuery, state: FSMContext):
	if call.data.split('$.$')[1] == 'new_playlist':
		await call.message.delete()
		await call.message.answer('Напиши название для нового плейлиста')
		await state.set_state(Form.new_playlist)
	else:
		dir = os.listdir(f'./Users/{call.from_user.username}')
		try: dir.remove(f'r#{call.message.chat.id}.txt')
		except: pass
		len_dir = len(dir)
		plus = await state.get_data()
		plus = plus['plus']
		if call.data.split('$.$')[1] == 'next_page':
			await state.update_data(plus=plus+10)
			data = await state.get_data()
			plus = data['plus']
			list_dir = []
			for i in range(len(dir)):
				index = int(dir[i].split('_')[0])
				list_dir.insert(index, dir[i].split('.txt')[0])
			dir = list_dir
			if len(dir) >= 10:
				dir = dir[plus:plus+10]
			else:
				dir = dir[plus:-1]
		elif call.data.split('$.$')[1] == 'back_page':
			await state.update_data(plus=plus-10)
			data = await state.get_data()
			plus = data['plus']
			list_dir = []
			for i in range(len(dir)):
				index = int(dir[i].split('_')[0])
				list_dir.insert(index, dir[i].split('.txt')[0])
			dir = list_dir
			if len(dir) >= 10:
				dir = dir[plus:plus+10]
			else:
				dir = dir[plus:-1]
		await call.message.edit_reply_markup(reply_markup=await k.GetLists(dir, call.from_user.username, plus, len_dir=len_dir, callback=call.data.split('$.$')[-2], delete=call.data.split('$.$')[-1]))

@dp.callback_query(F.data.split('$.$')[0] == 'playlist')
async def CallGetMusicFromPlaylist(call: CallbackQuery, state: FSMContext):
	if 'update' in call.data.split('$.$'):
		name = call.data.split('$.$')[2]
		await state.update_data(update_name=name)
		await state.set_state(Form.up_list_name)
		data = await state.get_data()
		await call.message.answer('Отправь ссылку на обновленный плейлист!')
		print(f'\n\033[0;36m[log]\033[0m Пользователь \033[4mизменил\033[0m плейлист \033[0;33m"{call.data.split("$.$")[2]}"\033[0m!\n\033[0;35mID\033[0m: \033[0;32m{call.message.chat.id}\033[0m, \033[0;35mName\033[0m: \033[0;32m{call.from_user.username}\033[0m\n')
	elif 'download_all' in call.data.split('$.$'):
		global playlist
		playlist = codecs.open(f'./Users/{call.data.split("$.$")[2]}/{call.data.split("$.$")[1]}.txt', 'r', 'utf_8_sig').read().replace('\r', '').split('\n')[:-1]
		headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36"
		}
		down_bool = True
		time_s = int(round(len(playlist) * 4.5))
		if time_s >= 60*60:
			time_h = time_s // 3600
			time_m = (time_s - 3600) // 60
			time_s = (time_s - 3600) % 60
			time_h_text = f'{time_h}:'
			time_m_text = f'{time_m}:'
			time_s_text = f'{time_s}:'
			if time_h < 10: time_h_text = f'0{time_h}:'
			if time_m < 10: time_m_text = f'0{time_m}:'
			if time_s < 10: time_s_text = f'0{time_s}'
		elif time_s >= 60:
			time_m = time_s // 60
			time_s = time_s % 60
			time_h_text = ''
			time_m_text = f'{time_m}:'
			time_s_text = f'{time_s}:'
			if time_m < 10: time_m_text = f'0{time_m}:'
			if time_s < 10: time_s_text = f'0{time_s}'
		else:
			time_h_text = ''
			time_m_text = ''
			time_s_text = f'{time_s} сек.'
		await call.message.edit_text(f'Плейлист будет скачан примерно за {time_h_text}{time_m_text}{time_s_text}')
		for name in playlist:
			data = await state.get_data()
			try:
				down_bool = data['download_all']
			except:
				down_bool = down_bool
			if down_bool == False:
				await state.update_data(download_all=True)
				break
			else:
				if name.split('|')[0].strip() == '🔞': name = f'{name.split("|")[1].strip()} | E'
				else: name = name.split('|')[0].strip()
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
					try:
						request = requests.get(url_track_ptf, headers)
						soup = BeautifulSoup(request.text, "lxml")
						url = soup.find("main").find("a", class_="tracks-card__download-btn").get("href")
						track = f"https://ru.patefon.cc{url}"
						service = "Patefon"
						await call.bot.send_chat_action(call.message.chat.id, action='upload_document')
						await call.message.answer_audio(caption=f"Музыкальный сервис: {service}", audio=URLInputFile(url=track, filename=name, headers=headers), disable_notification=True)
					except:
						request = requests.get(url_track_mstr, headers)
						soup = BeautifulSoup(request.text, "lxml")
						url = soup.find(class_="results").find(class_="chkd").find(class_="link").get("href")
						track = f'https://muz-monster.ru/mp3/{url}'
						service = "Muz Monster"
						await call.bot.send_chat_action(call.message.chat.id, action='upload_document')
						await call.message.answer_audio(caption=f"Музыкальный сервис: {service}", audio=URLInputFile(url=track, filename=name, headers=headers), disable_notification=True)
				except:
					await call.message.answer(f'Трек <b>{name}</b> не найден', disable_notification=True)
		await call.message.answer(f'Скачивание плейлиста <b>{call.data.split("$.$")[1].split("_")[1]}</b> завершено!')
	elif 'delete' in call.data.split('$.$'):
		os.remove(f'./Users/{call.data.split("$.$")[1]}/{call.data.split("$.$")[2]}.txt')
		if int(call.data.split("$.$")[2].split('_')[2]) > 0: count_play = f' {int(call.data.split("$.$")[2].split("_")[2])+1}'
		else: count_play = ''
		await call.message.answer(f'Плейлист \"{call.data.split("$.$")[2].split("_")[1]}{count_play}\" удален!')
		await call.message.delete()
		await GetLists(message=call, state=state)
		print(f'\n\033[0;36m[log]\033[0m Пользователь \033[4mудалил\033[0m плейлист \033[0;33m"{call.data.split("$.$")[2]}"\033[0m!\n\033[0;35mID\033[0m: \033[0;32m{call.message.chat.id}\033[0m, \033[0;35mName\033[0m: \033[0;32m{call.from_user.username}\033[0m\n')
	elif 'add' in call.data.split('$.$'):
		data = await state.get_data()
		music = data['add_music']
		duration = data['duration']
		index_playlist = call.data.split('$.$')[2]
		playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().replace('\r', '')[:-1]
		with open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'w', encoding="utf-8") as file:
			file.write(f'{music} | {duration}\n{playlist}')
		await call.message.answer(f'Трек \"{music}\" добавлен в плейлист \"{index_playlist.split("_")[1]}\"')
		await call.message.delete()
	else:
		if call.data.split('$.$')[1] == 'cancel':
			await state.update_data(play_plus=0)
			await state.update_data(plus=0)
			await call.message.delete()
			name = call.from_user.username
			await GetLists(call, user_name=name, state=state)
		else:
			try:
				data = await state.get_data()
				try:
					index_playlist = call.data.split('$.$')[2]
					try:
						play_plus = int(call.data.split('$.$')[-1])
					except:
						play_plus = 0
				except:
					index_playlist = data['index_playlist']
					play_plus = int(data['play_plus'])
				if call.data.split('$.$')[1] == 'next_page':
					playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
					len_list = len(playlist)
					await state.update_data(play_plus=play_plus+10)
					data = await state.get_data()
					play_plus = data['play_plus']
					if len(playlist) >= 10:
						playlist = playlist[play_plus:play_plus+10]
					else:
						playlist = playlist[play_plus:]
					await call.message.edit_reply_markup(reply_markup=await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list))
				elif call.data.split('$.$')[1] == 'back_page':
					playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
					len_list = len(playlist)
					await state.update_data(play_plus=play_plus-10)
					data = await state.get_data()
					play_plus = data['play_plus']
					if len(playlist) >= 10:
						playlist = playlist[play_plus:play_plus+10]
					else:
						playlist = playlist[play_plus:]
					await call.message.edit_reply_markup(reply_markup=await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list))
				elif call.data.split('$.$')[1] == 'first_page':
					playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
					len_list = len(playlist)
					await state.update_data(play_plus=0)
					data = await state.get_data()
					play_plus = data['play_plus']
					if len(playlist) >= 10:
						playlist = playlist[play_plus:play_plus+10]
					else:
						playlist = playlist[play_plus:]
					await call.message.edit_reply_markup(reply_markup=await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list))
				elif call.data.split('$.$')[1] == 'last_page':
					playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
					len_list = len(playlist)
					if len_list % 10 > 0: play_plus = len_list - len_list % 10
					else: play_plus = len_list - len_list % 10 - 10
					await state.update_data(play_plus=play_plus)
					data = await state.get_data()
					play_plus = data['play_plus']
					if len(playlist) >= 10:
						playlist = playlist[play_plus:play_plus+10]
					else:
						playlist = playlist[play_plus:]
					await call.message.edit_reply_markup(reply_markup=await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list))
				elif call.data.split('$.$')[1] == 'select_page':
					playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
					len_list = len(playlist)
					len_list_ = len_list % 10
					if len_list_ > 0: len_list_ = len_list // 10 + 1
					else: len_list_ = len_list
					await call.message.answer(f'Напиши номер страницы от 0 до {len_list_ // 10}')
					await state.set_state(Form.select_page)
					await state.update_data(message_id=call.message.message_id)
					await state.update_data(index_playlist=call.data.split('$.$')[2])
				else:
					playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
					len_list = len(playlist)
					if len(playlist) >= 10:
						playlist = playlist[:10]
					else:
						playlist = playlist[:]
					await state.update_data(index_playlist=index_playlist)
					play_plus = 0
					await state.update_data(play_plus=0)
					await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list)
					await call.message.edit_text(f'<b>{index_playlist.split("_")[1]}</b>', reply_markup=await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list))
			except:
				try:
					index_playlist = data['index_playlist']
				except:
					index_playlist = call.data.split('$.$')[2]
				playlist = codecs.open(f'./Users/{call.from_user.username}/{index_playlist}.txt', 'r', 'utf_8_sig').read().split('\r\n')[:-1]
				len_list = len(playlist)
				if len(playlist) >= 10:
					playlist = playlist[:10]
				await state.update_data(index_playlist=index_playlist)
				play_plus = 0
				await state.update_data(play_plus=0)
				await call.message.edit_text(f'<b>{index_playlist.split("_")[1]}</b>', reply_markup=await k.GetMusic(playlist, index_playlist, call.from_user.username, play_plus, len_list))

@dp.callback_query(F.data.split('$.$')[0] == 'music')
async def CallSendMusic(call: CallbackQuery, state: FSMContext, music=None):
	if 'add' in call.data.split('$.$'):
		duration = time.strftime('%M:%S', time.gmtime(call.message.audio.duration))
		await state.update_data(add_music=f"{call.message.audio.performer} - {call.message.audio.title}")
		await state.update_data(duration=duration)
		await GetLists(message=call.message, state=state, add='add', user_name=call.from_user.username)
	elif 'responce' in call.data.split('$.$'):
		track = codecs.open(f'./Users/{call.from_user.username}/r#{call.message.chat.id}.txt', 'r', 'utf-8-sig').read().split('\r\n')[int(call.data.split('$.$')[3])-1]
		if track.split('|')[1].split('/')[2] == 'ru.patefon.cc': service = 'Patefon'
		else: service = 'Muz Monster'
		title = track.split('|')[0]
		link = track.split('|')[1].strip()
		await call.bot.send_chat_action(call.message.chat.id, action='upload_document')
		await call.message.answer_audio(caption=f"Музыкальный сервис: {service}", audio=URLInputFile(url=link, filename=title, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.10.0.0 Safari/537.36"}))
		print(f'\n\033[0;36m[log]\033[0m Трек \033[0;33m"{title}"\033[0m с сервиса \033[0;33m"{service}"\033[0m был отправлен пользователю\n\033[0;35mID\033[0m: \033[0;32m{call.message.chat.id}\033[0m\n\033[0;35mСсылка\033[0m: \033[0;32m{link}\033[0m\n')
	else:
		music_full = codecs.open(f'./Users/{call.data.split("$.$")[1]}/{call.data.split("$.$")[2]}.txt', 'r', 'utf_8_sig').read().split('\r\n')[int(call.data.split('$.$')[3])-1]
		if music_full.split('|')[0].strip() == '🔞':
			music = music_full.split('|')[1].strip()
			data = await d.Down(music)
			music = f'{music_full.split("|")[1].strip()} (E)'
		else:
			music = music_full.split('|')[0].strip()
			data = await d.Down(music)
		try:
			await call.bot.send_chat_action(call.message.chat.id, action='upload_document')
			await call.message.answer_audio(caption=f"Музыкальный сервис: {data[1]}", audio=URLInputFile(url=data[0], filename=music, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.10.0.0 Safari/537.36"}))
			print(f'\n\033[0;36m[log]\033[0m Трек \033[0;33m"{music}"\033[0m с сервиса \033[0;33m"{data[1]}"\033[0m был отправлен пользователю\n\033[0;35mID\033[0m: \033[0;32m{call.message.chat.id}\033[0m\n\033[0;35mСсылка\033[0m: \033[0;32m{data[0]}\033[0m\n')
		except:
			await call.message.answer('Песня не найдена :(')

@dp.callback_query(F.data.split('$.$')[0] == 'link')
async def CallLinkCommands(call: CallbackQuery, state: FSMContext):
	if call.data.split('$.$')[1] == 'cancel':
		await call.message.delete()
		await call.message.answer('Введи название своей песни')
		await state.clear()

async def Spam(time_now):
	with open('./Users/AllUsers.json', 'r') as file:
		all_users = json.load(file)
	users_id = [i for i, k in all_users.items()]
	for i in users_id:
		await bot.send_message(text=f'Уже <u>{time_now}</u>, а бот еще не на хостинге :(\n<blockquote>Чтобы бот быстрее вышел в штатный режим делитесь им со своими знакомыми и если прирост будет удовлетворительным, то будет введена реферальная система!</blockquote>', chat_id=i)

async def scheduler():
	while True:
		time_now = datetime.datetime.now().strftime('%H:%M %d.%m.%Y')
		if time_now.split(' ')[0] in ['00:00', '12:00', '18:00', '06:00']:
			await Spam(time_now)
		await asyncio.sleep(60)

def worker():
	asyncio.run((scheduler()))

async def main():
	process = multiprocessing.Process(target=worker)
	process.start()
	logging.basicConfig(level=logging.INFO)
	await dp.start_polling(bot)
	process.join()

if __name__ == '__main__':
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("\033[0;31m[err]\033[0m Бот остановлен!\n")