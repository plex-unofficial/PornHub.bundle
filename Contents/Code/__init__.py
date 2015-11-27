from PHCommon import *
from PHCategories import *
from PHChannels import *
from PHPornStars import *
from PHPlaylists import *
from PHMembers import *

NAME =	'PornHub'

ART =	'art-default.jpg'
ICON =	'icon-default.jpg'

def Start():
	
	# Set the defaults for Object Containers
	ObjectContainer.art =		R(ART)
	ObjectContainer.title1 =	NAME
	
	# Set the defaults of Directory Objects
	DirectoryObject.thumb =	R(ICON)
	
	# Set the cache lifespan
	HTTP.CacheTime = CACHE_1HOUR * 2
	
	# Set the user agent
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'

@handler(ROUTE_PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():
	
	# Create a dictionary of menu items
	mainMenuItems = OrderedDict([
		('Browse All Videos',	{'function':BrowseVideos}),
		('Categories',			{'function':BrowseCategories}),
		('Channels',			{'function':BrowseChannels}),
		('Porn Stars',			{'function':BrowsePornStars}),
		('Playlists',			{'function':BrowsePlaylists}),
		('Members',			{'function':BrowseMembers}),
		('Search',				{'function':SearchVideos, 'search':True, 'directoryObjectArgs':{'prompt':'Search for...','summary':'Enter Search Terms'}})
	])
	
	return GenerateMenu(NAME, mainMenuItems)