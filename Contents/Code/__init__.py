from PHCommon import *
from PHCategories import *
from PHChannels import *
from PHPornStars import *
from PHPlaylists import *
from PHMembers import *

NAME =		'PornHub'

ART =		'art-default.jpg'
ICON =		'icon-default.jpg'

def Start():
	
	# Set the defaults for Object Containers
	#ObjectContainer.art =		R(ART)
	ObjectContainer.title1 =	NAME
	
	# Set the defaults of Directory Objects
	DirectoryObject.thumb =	R(ICON)
	
	# Set the cache lifespan
	HTTP.CacheTime = CACHE_1HOUR * 2
	
	# Set the user agent
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'

@handler(ROUTE_PREFIX, NAME, thumb=ICON, art=ART)
def MainMenu():
	
	# Create the object to contain the main menu options
	oc = ObjectContainer()
	
	# Directory Object for Browse All Videos
	oc.add(DirectoryObject(
		key =	Callback(SortVideos, title='Browse All Videos'),
		title =	'Browse All Videos'
	))
	
	oc.add(DirectoryObject(
		key =	Callback(BrowseCategories, title='Categories'),
		title =	'Categories'
	))
	
	oc.add(DirectoryObject(
		key =	Callback(BrowseChannels, title='Channels'),
		title =	'Channels'
	))
	
	oc.add(DirectoryObject(
		key =	Callback(BrowsePornStars, title='Porn Stars'),
		title =	'Porn Stars'
	))
	
	oc.add(DirectoryObject(
		key =	Callback(BrowsePlaylists, title='Playlists'),
		title =	'Playlists'
	))
	
	oc.add(DirectoryObject(
		key =	Callback(BrowseMembers, title='Members'),
		title =	'Members'
	))
	
	oc.add(InputDirectoryObject(
		key =	Callback(SearchVideos, title='Search'),
		title =	'Search'
	))
	
	return oc