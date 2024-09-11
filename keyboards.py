from aiogram.utils.keyboard import InlineKeyboardBuilder

async def GetLists(dir, user, plus, len_dir, callback='', delete='', add=''):
  builder = InlineKeyboardBuilder()
  row = []
  for i in dir:
    count_play = int(i.split('_')[2]) + 1
    name = i.split('_')[1]
    if count_play > 1: name = f'{name} {count_play}'
    else: name = name
    builder.button(text=name, callback_data=f'playlist$.${user}$.${i}$.${add}$.${callback}$.${delete}')
    row.append(1)
  
  if plus > 0 and len_dir >= 10:
    call_back = f'lists$.$back_page$.${callback}$.${delete}'
  else:
    call_back = "#"
  builder.button(text='<', callback_data=call_back)

  len_dir_ = len_dir % 10
  if len_dir_ > 0: len_dir_ = len_dir // 10 + 1
  else: len_dir_ = len_dir

  builder.button(text=f'{plus//10+1}/{len_dir_}', callback_data='#')

  if plus+10 < len_dir:
    call_next = f'lists$.$next_page$.${callback}$.${delete}'
  else:
    call_next = "#"
  builder.button(text='>', callback_data=call_next)
  row.append(3)
  builder.button(text='Создать новый', callback_data='lists$.$new_playlist')
  row.append(1)

  builder.adjust(*row)

  return builder.as_markup()

async def GetMusic(playlist, index_playlist, username, plus, len_list):
  builder = InlineKeyboardBuilder()
  k=0
  row = []
  for name in playlist:
    k+=1
    global index_music
    index_music = k+plus
    builder.button(text=name.split('|')[0], callback_data=f'music$.${username}$.${index_playlist}$.${index_music}')
    row.append(1)

  if plus > 0 and len_list >= 10:
    call_back=f'playlist$.$first_page$.${index_playlist}$.${plus}'
  else:
    call_back='#'
  builder.button(text='<<<', callback_data=call_back)

  if plus > 0:
    call_back=f'playlist$.$back_page$.${index_playlist}$.${plus}'
  else:
    call_back='#'
  builder.button(text='<', callback_data=call_back)

  len_list_ = len_list % 10
  if len_list_ > 0: len_list_ = len_list // 10 + 1
  else: len_list_ = len_list // 10
  builder.button(text=f'{plus//10+1}/{len_list_}', callback_data=f'playlist$.$select_page$.${index_playlist}$.${plus}')

  if plus+10 < len_list:
    call_next = f'playlist$.$next_page$.${index_playlist}$.${plus}'
  else:
    call_next = '#'
  builder.button(text='>', callback_data=call_next)

  if plus+10 < len_list:
    call_next = f'playlist$.$last_page$.${index_playlist}$.${plus}'
  else:
    call_next = '#'
  builder.button(text='>>>', callback_data=call_next)
  row.append(5)
  builder.button(text='Выйти в меню', callback_data='playlist$.$cancel')
  row.append(1)
  builder.button(text='Загрузить весь плейлист', callback_data=f'playlist$.${index_playlist}$.${username}$.$download_all')
  row.append(1)
  builder.adjust(*row)

  return builder.as_markup()

async def GetMusicText(playlist, plus, len_list, index_playlist, username):
  builder = InlineKeyboardBuilder()
  k=0
  row = []
  for name in playlist:
    k+=1
    global index_music
    index_music = k+plus
    builder.button(text=name.split('|')[0], callback_data=f'music$.${username}$.${index_playlist}$.${index_music}$.$responce')
    row.append(1)

  if plus > 0 and len_list >= 10:
    call_back=f'playlist$.$first_page$.${index_playlist}$.${plus}'
  else:
    call_back='#'
  builder.button(text='<<<', callback_data=call_back)

  if plus > 0:
    call_back=f'playlist$.$back_page$.${index_playlist}$.${plus}'
  else:
    call_back='#'
  builder.button(text='<', callback_data=call_back)

  len_list_ = len_list % 10
  if len_list_ > 0: len_list_ = len_list // 10 + 1
  else: len_list_ = len_list // 10
  builder.button(text=f'{plus//10+1}/{len_list_}', callback_data=f'playlist$.$select_page$.${index_playlist}$.${plus}')

  if plus+10 < len_list:
    call_next = f'playlist$.$next_page$.${index_playlist}$.${plus}'
  else:
    call_next = '#'
  builder.button(text='>', callback_data=call_next)

  if plus+10 < len_list:
    call_next = f'playlist$.$last_page$.${index_playlist}$.${plus}'
  else:
    call_next = '#'
  builder.button(text='>>>', callback_data=call_next)
  row.append(5)
  builder.button(text='Выйти в меню', callback_data='playlist$.$cancel')
  row.append(1)
  builder.button(text='Загрузить весь плейлист', callback_data=f'playlist$.${index_playlist}$.${username}$.$download_all')
  row.append(1)
  builder.adjust(*row)

  return builder.as_markup()

async def CancelLink():
  builder = InlineKeyboardBuilder()
  builder.button(text='Найти песню', callback_data='link$.$cancel')
  return builder.as_markup()

async def MusicKeyboard(music):
  builder = InlineKeyboardBuilder()
  builder.button(text='Добавить в плейлист', callback_data=f'music$.$add.{music}')
  return builder.as_markup()

async def NewPlaylist():
  builder = InlineKeyboardBuilder()
  builder.button(text='Создать новый', callback_data='lists$.$new_playlist')
  builder.adjust(1)
  return builder.as_markup()