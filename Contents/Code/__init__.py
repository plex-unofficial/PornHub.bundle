from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
from urlparse import urljoin
import time
from exceptions import IndexError
####################################################################################################

PLUGIN_TITLE = 'Pornhub'
STEALTH_TITLE = 'System Stats'
PLUGIN_PREFIX = '/video/pornhub'

BASE_URL = 'http://www.pornhub.com'
CATEGORIES = '%s/categories' % BASE_URL
AMFPROXY = 'http://amfproxy.plexapp.net/pornhub/%s.xml'
SORT_ORDER = [
  ['Most Recent', 'o=mr'],
  ['Most Viewed - All Time', 'o=mv&t=a'],
  ['Most Viewed - This Month', 'o=mv&t=m'],
  ['Most Viewed - This Week', 'o=mv&t=w'],
  ['Most Viewed - Today', 'o=mv&t=t'],
  ['Top Rated - All Time', 'o=tr&t=a'],
  ['Top Rated - This Month', 'o=tr&t=m'],
  ['Top Rated - This Week', 'o=tr&t=w'],
  ['Top Rated - Today', 'o=tr&t=t'],
  ['Most Discussed - All Time', 'o=md&t=a'],
  ['Most Discussed - This Month', 'o=md&t=m'],
  ['Most Discussed - This Week', 'o=md&t=w'],
  ['Most Discussed - Today', 'o=md&t=t'],
  ['Being Watched', 'o=bw'],
  ['Longest', 'o=lg']]

# Default artwork and icons
PLUGIN_ARTWORK = 'art-default.png'
PLUGIN_ICON_DEFAULT = 'icon-default.png'
STEALTH_ARTWORK = 'art-stealth.png'
STEALTH_ICON = 'icon-stealth.png'

####################################################################################################
  
# Lazy Loader
global pages
pages = list()
global dirItems
dirItems = MediaContainer()
global parseThread
parseThread = None
global noMorePages
noMorePages = True
global noMoreMeta
noMoreMeta = True
global metaThread
global lastMatchKey
lastMatchKey = None

####################################################################################################

def LL(sender,  pageGetter, parser, metaGetter, url, matchKey, title1=None, title2=None, viewGroup=None, contextMenu=None, replaceParent=False, **kwargs):
  global pages, dirItems, parseThread, metaThread, noMorePages, noMoreMeta, lastMatchKey, parseThreadShouldDie, metaThreadShouldDie
  Log(matchKey)
  Log(lastMatchKey)
  
  if pageGetter == 'getURLs':
    pageHnd = getURLs
  elif pageGetter == 'getVideos':
    pageHnd = getVideos
  else:
    raise
    
  if parser == 'getVideos':
    parseHnd = getVideos
  else:
    raise
  
  if metaGetter == 'getMeta':
    metaHnd = getMeta
  elif metaGetter == 'NOP':
    metaHnd = NOP
    
  
  if matchKey != lastMatchKey:
    lastMatchKey = matchKey
    parseThreadShouldDie = True
    metaThreadShouldDie = True
    while (parseThreadShouldDie and not noMorePages) or (metaThreadShouldDie and not noMoreMeta):
      Log('Waiting for old threads to die')
      Log([parseThreadShouldDie, noMorePages, metaThreadShouldDie, noMoreMeta])
      time.sleep(1)
    Log('Threads are all dead')
    pages = list()
    dirItems = MediaContainer(title1=title1, title2=title2, viewGroup=viewGroup, contextMenu=contextMenu, replaceParent=replaceParent)
    parseThread = None
  if parseThread == None:
    parseThreadShouldDie = False
    metaThreadShouldDie = False
    pages = pageHnd(url, **kwargs)
    noMorePages = False
    noMoreMeta = False
    dirItems.autoRefresh=5
    parseThread = Thread.Create(parseEach, parseHnd, **kwargs)
    metaThread = Thread.Create(getMetaEach, metaHnd)
    time.sleep(3)
  return(dirItems)

def parseEach(parser, **kwargs):
  global pages, dirItems, noMorePages, parseThread, parseThreadShouldDie
  while True:
    if parseThreadShouldDie:
      parseThreadShouldDie = False
      return
    try:
      url = pages[0]
      del pages[0]
    except:
      Log('Out of pages')
      noMorePages = True
      return
    else:
      try:
        parser(url, **kwargs)
      except:
        Log('parser raised an exception')

def getMetaEach(metaGetter):
  global dirItems, noMorePages, noMoreMeta, metaThreadShouldDie
  itemIndex = 0
  while True:
    if metaThreadShouldDie:
      metaThreadShouldDie = False
      return
    try:
      dirItem = dirItems[itemIndex]
    except IndexError:
      if noMorePages:
        Log('No more videos')
        del dirItems.autoRefresh
        noMoreMeta = True
        return
      else:
        Log('Waiting for videos')
        time.sleep(1)
    else:
      itemIndex += 1
      try:
        metaGetter(dirItem)
      except:
        Log('metaGetter raised an exception')

####################################################################################################

def P(pref, default=''):
  p = Prefs.Get(pref)
  if p == None:
    return default
  else:
    return p

def V(val, default=''):
  if val == None:
    return default
  else:
    return val
####################################################################################################

def Start():
  if P('Stealth', False):
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, STEALTH_TITLE, STEALTH_ICON, STEALTH_ARTWORK)
  else:
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1 = PLUGIN_TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(PLUGIN_ARTWORK)

  Plugin.AddViewGroup('_List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('_InfoList', viewMode='InfoList', mediaType='items')
  Plugin.AddViewGroup('_Pictures', viewMode='Pictures', mediaType='items')
  Plugin.AddViewGroup('_Wall Stream', viewMode='WallStream', mediaType='items')
  Plugin.AddViewGroup('_Cover Flow', viewMode='Coverflow', mediaType='items')

  # Set the default cache time
  HTTP.SetCacheTime(CACHE_1HOUR)

####################################################################################################

def CreatePrefs():
  Prefs.Add(id='Stealth', type='bool', default=False, label='Stealth Mode')
  Prefs.Add(id='catView', type='enum', default='List', label='Default Category View', values='List|InfoList|Pictures|Wall Stream|Cover Flow')
  Prefs.Add(id='videoView', type='enum', default='List', label='Default Video View', values='List|InfoList|Pictures|Wall Stream|Cover Flow')
  sortValues = ''
  for sort, key in SORT_ORDER:
    sortValues += sort + '|'
  sortValues = sortValues + 'Prompt'
  Prefs.Add(id='pageCount', type='text', default='1', label='Pages (26 videos each)')
  Prefs.Add(id='sortOrder', type='enum', default='Prompt', label='Default Sort Order', values=sortValues)
  for category in XML.ElementFromURL(CATEGORIES, isHTML=True, cacheTime=CACHE_1DAY, errors='ignore').xpath('//li[@class="cat_pic"]//strong/text()'):
    Prefs.Add(id=category.strip().replace(' ', '_').replace('/', '_'), type='bool', default=True, label='Show ' + category.strip())

def CreateDict():
  Dict.Set('oldStealthSetting', False)

####################################################################################################

def getURLs(url, sortURL, **kwargs):
  if url.find('?') == -1:
    totalUrl = urljoin(BASE_URL, url + '?' + sortURL)
  else:
    totalUrl = urljoin(BASE_URL, url + '&' + sortURL)
  videoPage = XML.ElementFromURL(totalUrl, isHTML=True, errors='ignore')
  try:
    pageCount = int(videoPage.xpath('//span[text()="Last"]/parent::*')[0].get('href').split('=')[-1])
  except:
    pageCount = len(videoPage.xpath('//ul[@class="pagination"]/li')) - 1
    if pageCount == -1:
      pageCount = 1
  pages = list()
  for p in range(1, pageCount + 1):
    pages.append(totalUrl +  '&page=' + str(p))
  return pages

def getVideos(url, **kwargs):
  global dirItems
  Log('getVideos for ' + url)
  for video in XML.ElementFromURL(url, isHTML=True, errors='ignore').xpath('//div[@class="wrap"]'):
    title = video.xpath('.//a[@class="title"]')[0].text.strip()
    duration = TimeToSeconds(video.xpath('.//var[@class="duration"]')[0].text) * 1000
    thumb = video.xpath('.//img')[0].get('src')
    rating = float(video.xpath('.//div[starts-with(@class,"rating-container")]/div[@class="value"]')[0].text.split('%')[0]) * 2

    added = L('Added: %s') % video.xpath('.//var[@class="added"]')[0].text
    views = L('Views: %s views') % video.xpath('.//span[@class="views"]/var')[0].text

    viewkey = video.xpath('.//a')[0].get('href').split('viewkey=')
    premium = video.xpath('.//a')[0].get('href').find('view_video_2.php')
    private = thumb.find('private-video')

    if len(viewkey) > 1 and premium < 0 and private < 0:
      videoURL = 'http://www.pornhub.com/view_video.php?viewkey=' + viewkey[1]
      dirItems.Append(Function(VideoItem(getVideo, title=title, summary=added + '\n' + views, duration=duration, thumb=thumb, art=None, rating=rating), videoURL=videoURL))

def getMeta(dirItem):
  Log(dirItem.__dict__)
  metaURL = dirItem._Function__kwargs['videoURL']
  Log('Getting metadata for ' + metaURL)

  metaPage = None
  tries = 3
  while metaPage == None and tries != 0:
    metaPage = XML.ElementFromURL(metaURL, True, errors='ignore', cacheTime=CACHE_1MONTH)
    tries -= 1
  if metaPage == None:return

  summary = dirItem.summary + '\n'
  users = metaPage.xpath('//a[starts-with(@href,"/user/")]')
  if len(users) != 0:
    summary += 'From: ' + V(users[0].text) + '\n'
  stars = metaPage.xpath('//a[starts-with(@href,"/video/search?pornstar")]')
  if len(stars) != 0:
    summary += 'Pornstars: '
    for star in stars:
      summary += V(star.text) +', '
    summary = summary[:-2] + '\n'
  tags = metaPage.xpath('//a[starts-with(@href,"/video/search?search=")]')
  if len(tags) != 0:
    summary += 'Tags: '
    for tag in tags:
      summary += V(tag.text) + ', '
    summary = summary[:-2] + '\n'
  dirItem.summary = summary

def getVideo(sender, videoURL):
  js = XML.ElementFromURL(videoURL, True).xpath('//div[@id="playerDiv_1"]/following-sibling::script')[0].text
  for line in js.split('\n'):
    if '"video_url"' in line:
      url = line.split('"')[-2]
  return Redirect(url)  

def MainMenu():
  stealthSetting = Prefs.Get('Stealth')
  if Dict.Get('oldStealthSetting') != stealthSetting:
    Dict.Set('oldStealthSetting', stealthSetting)
    time.sleep(5)
    Log('Stealth Mode toggled, Restarting')
    Plugin.Restart()

  dir = MediaContainer(noCache=True)
  dir.viewGroup = '_' + Prefs.Get('catView')

  sortName, sortURL = getSort()
  # 'All' item
  if sortName == '':
    dir.Append(Function(DirectoryItem(SortOrder, title='All', thumb=R(PLUGIN_ICON_DEFAULT)), url='/video?c=', title2='All'))
  else:
    dir.Append(Function(DirectoryItem(LL, title='All', thumb=R(PLUGIN_ICON_DEFAULT)), pageGetter='getURLs', parser='getVideos', metaGetter='getMeta', title1=PLUGIN_TITLE, title2='All', url='/video?c=', sortURL=sortURL, matchKey=['/video?c=', sortURL]))

  for category in XML.ElementFromURL(CATEGORIES, isHTML=True, cacheTime=CACHE_1DAY, errors='ignore').xpath('//li[@class="cat_pic"]'):
    url = category.xpath('./a')[0].get('href')

    title = category.xpath('.//strong')[0].text.strip()
    thumb = category.xpath('./a/img')[0].get('src')
    if Prefs.Get(title.strip().replace(' ', '_').replace('/', '_')):
      if sortName == '':
        dir.Append(Function(DirectoryItem(SortOrder, title=title, thumb=thumb), url=url, title2=title, viewGroup='_' + Prefs.Get('videoView')))
      else:
        dir.Append(Function(DirectoryItem(LL, title=title, thumb=thumb), pageGetter='getURLs', parser='getVideos', metaGetter='getMeta', title1=PLUGIN_TITLE, title2=title, url=url, sortURL=sortURL, viewGroup='_' + Prefs.Get('videoView'), matchKey=[url, sortURL]))
  #dir.Append(Function(DirectoryItem(LL, title=L('Users')), pageGetter=getURLs, parser=getUsers, metaGetter=NOP, title1=PLUGIN_TITLE, title2='Users', url='http://www.pornhub.com/user/search', sortURL='o=recent_users', viewGroup='_' + Prefs.Get('videoView'), matchKey=['http://www.pornhub.com/user/search', sortURL]))

  dir.Append(Function(InputDirectoryItem(InputVideoList, title=L("Search Videos ..."), prompt=L("Search on Pornhub"), subtitle = L('Search by keyword in pornhub archive'), summary = 'You can type in any word you want to search content for. This can be tags, names, ...' ), title1 = PLUGIN_TITLE, title2 = 'Search - "%s"', url = 'http://www.pornhub.com/video/search?search=%s', sortURL=sortURL))
   #Add search item
  #dir.Append(Function(InputDirectoryItem(InputUserList, title=L("Search Users ..."), prompt=L("Search User by name"), subtitle = L('Search by name in pornhub user list')), title1 = PLUGIN_TITLE, title2 = 'Search User - "%s"', url = BASE_URL + '/user/search?username=%s', sortURL=sortURL))
  dir.Append(PrefsItem('Preferences', thumb=R('icon-prefs.png')))
  return dir

####################################################################################################

def SortOrder(sender, url, title2, viewGroup):
  dir = MediaContainer(title2=title2)

  for (sortTitle,sortURL) in SORT_ORDER:
    dir.Append(Function(DirectoryItem(LL, title=sortTitle, thumb=R(PLUGIN_ICON_DEFAULT)), pageGetter='getURLs', parser='getVideos', metaGetter='getMeta', title1=title2, title2=sortTitle, url=url, sortURL=sortURL, viewGroup=viewGroup, matchKey=[url, sortURL]))

  return dir

####################################################################################################

def InputVideoList(sender, query, title1, title2, url, sortURL, page=1):
  Log('(PLUG-IN) **==> ENTER Search on PornHub')
  title2 = title2 % query
  query = String.Quote(query, usePlus=True)
  url = url % query
  return LL(sender, title1=title1, title2=title2, url=url, sortURL=sortURL, pageGetter=getURLs, parser=getVideos, metaGetter=getMeta, matchKey=['searchVideos', query])

####################################################################################################

def TimeToSeconds(timecode):
  seconds  = 0
  duration = timecode.split(':')
  duration.reverse()

  for i in range(0, len(duration)):
    seconds += int(duration[i]) * (60**i)

  return seconds

####################################################################################################

def getSort():
  sort = Prefs.Get('sortOrder')
  for name, url in SORT_ORDER:
    if sort == name: return [name, url]
  return ['','']

####################################################################################################

# TODO: write user metadata getter

def getUsers(url, **kwargs):
  global dirItems
  for user in XML.ElementFromURL(url, isHTML=True, errors='ignore').xpath('//div[@class="user-box"]'):
    name = user.xpath('./a/span')[0].text
    link = user.xpath('./a')[0].get('href')
    thumb = user.xpath('./a/img')[0].get('src')
    #userid = link.split('user/')[1]

    if len(link) > 1:
      userURL = BASE_URL + link #+ '/videos/recent?'
      dirItems.Append(Function(DirectoryItem(getUsers2, title=name, thumb=thumb), title1=PLUGIN_TITLE, userName=name, url=userURL, viewGroup='_' + Prefs.Get('videoView')))

def getUsers2(sender, url, title1, userName, viewGroup):
  dir = MediaContainer(title1=title1, title2=userName, viewGroup=viewGroup)
  dir.Append(Function(DirectoryItem(LL, title='Favourites'), pageGetter='getURLs', parser='getVideos', metaGetter='NOP', title1=PLUGIN_TITLE, title2='Favourites - ' + userName, url=url + '/videos/favorites', sortURL='o=mr', viewGroup='_' + Prefs.Get('videoView'), matchKey=['getUsersFaves', userName]))
  dir.Append(Function(DirectoryItem(LL, title='Recents'), pageGetter='getURLs', parser='getVideos', metaGetter='NOP', title1=PLUGIN_TITLE, title2='Recents - ' + userName, url=url + '/videos/recent?', sortURL='', viewGroup='_' + Prefs.Get('videoView'), matchKey=['getUsersRecents', userName]))
  return dir

def NOP(*args, **kwargs):
  pass

####################################################################################################

def InputUserList(sender, query, title1, title2, url, sortURL, page=1):
  Log('(PLUG-IN) **==> ENTER Search on PornHub')
  title2 = title2 % query
  query = String.Quote(query, usePlus=True)
  url = url % query
  return LL(sender, url=url, pageGetter=getURLs, parser=getUsers, metaGetter=NOP, title1=PLUGIN_TITLE, title2=query, sortURL='', viewGroup='_' + Prefs.Get('videoView'), matchKey=['searchUsers', query])
