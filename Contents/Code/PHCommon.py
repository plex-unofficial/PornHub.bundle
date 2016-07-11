import urllib
import urlparse
from collections import OrderedDict

ROUTE_PREFIX =				'/video/pornhub'

BASE_URL =				'http://pornhub.com'
PH_VIDEO_URL =				BASE_URL + '/video'
PH_VIDEO_SEARCH_URL =		PH_VIDEO_URL + '/search?search=%s'

PH_PORNSTARS_HOVER_URL =	BASE_URL + '/pornstar/hover?id=%s'

MAX_VIDEOS_PER_PAGE =			32
MAX_VIDEOS_PER_SEARCH_PAGE =		20
MAX_VIDEOS_PER_CHANNEL_PAGE =	36
MAX_VIDEOS_PER_PORNSTAR_PAGE =	26
MAX_VIDEOS_PER_USER_PAGE =		48

SORT_ORDERS = OrderedDict([
	('Most Recent',					{'o':'mr'}),
	('Most Viewed - All Time',		{'o':'mv', 't':'a'}),
	('Most Viewed - This Month',		{'o':'mv', 't':'m'}),
	('Most Viewed - This Week',		{'o':'mv', 't':'w'}),
	('Most Viewed - Today',			{'o':'mv', 't':'t'}),
	('Top Rated - All Time',			{'o':'tr', 't':'a'}),
	('Top Rated - This Month',		{'o':'tr', 't':'m'}),
	('Top Rated - This Week',			{'o':'tr', 't':'w'}),
	('Top Rated - Today',			{'o':'tr', 't':'t'}),
	('Most Discussed - All Time',		{'o':'md', 't':'a'}),
	('Most Discussed - This Month',	{'o':'md', 't':'m'}),
	('Most Discussed - This Week',		{'o':'md', 't':'w'}),
	('Most Discussed - Today',		{'o':'md', 't':'t'}),
	('Being Watched',				{'o':'bw'}),
	('Longest',					{'o':'lg'})
])

CHANNEL_VIDEOS_SORT_ORDERS = OrderedDict([
	('Most Recent',					{'o':'da'}),
	('Most Viewed',					{'o':'vi'}),
	('Top Rated',					{'o':'ra'})
])

PORNSTAR_VIDEOS_SORT_ORDERS = OrderedDict([
	('Recently Featured',			{}),
	('Most Viewed',					{'o':'mv'}),
	('Top Rated',					{'o':'tr'}),
	('Longest',					{'o':'lg'}),
	('Newest',						{'o':'cm'})
])

@route(ROUTE_PREFIX + '/videos/browse')
def BrowseVideos(title=L("DefaultBrowseVideosTitle"), url = PH_VIDEO_URL, sortOrders = SORT_ORDERS):
	
	# If sorting channels, use a different dictionary of sort orders
	if ("/channels/" in url):
		sortOrders = CHANNEL_VIDEOS_SORT_ORDERS
	elif ("/pornstar/" in url):
		sortOrders = PORNSTAR_VIDEOS_SORT_ORDERS
	
	# Create a dictionary of menu items
	browseVideosMenuItems = OrderedDict()
	
	# Add the sorting options
	for sortTitle, urlParams in sortOrders.items():
		
		# Add a menu item for the category
		browseVideosMenuItems[sortTitle] = {'function':ListVideos, 'functionArgs':{'url':addURLParameters(url, urlParams)}}
	
	return GenerateMenu(title, browseVideosMenuItems)

@route(ROUTE_PREFIX + '/videos/list')
def ListVideos(title=L("DefaultListVideosTitle"), url=PH_VIDEO_URL, page=1, pageLimit = MAX_VIDEOS_PER_PAGE):
	
	# Create the object to contain all of the videos
	oc = ObjectContainer(title2 = title)
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# This could definitely be handled more gracefully. But it works for now
	if ("/video/search" in url):
		pageLimit =	MAX_VIDEOS_PER_SEARCH_PAGE
	elif ("/channels/" in url):
		pageLimit =	MAX_VIDEOS_PER_CHANNEL_PAGE
	elif ("/pornstar/" in url):
		pageLimit =	MAX_VIDEOS_PER_PORNSTAR_PAGE
	elif ("/users/" in url):
		pageLimit =	MAX_VIDEOS_PER_USER_PAGE
	
	# Get the HTML of the site
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of divs that contain videos
	videos = html.xpath("//li[contains(@class,'videoblock')]")
	
	# This piece of code is ridiculous. From the best I can gether, the poorly formed HTML on PornHub makes xPath choke at 123 videos. So I rounded it down to 120 and limited the videos to that. This should only affect playlists, but it is a really ridiculous problem
	if (len(videos) >= 120):
		videos =	videos[0:119]
	
	# Loop through the videos in the page
	for video in videos:
		
		# Get the link of the video
		videoURL = video.xpath("./div/div/a/@href")[0]
		
		# Check for relative URLs
		if (videoURL.startswith('/')):
			videoURL = BASE_URL + videoURL
		
		# Make sure the last step went smoothly (this is probably redundant but oh well)
		if (videoURL.startswith(BASE_URL)):
			# Use xPath to extract video details
			videoTitle =	video.xpath("./div/div/a/div[contains(@class, 'thumbnail-info-wrapper')]/span[@class='title']/a/text()")[0]
			thumbnail =	video.xpath("./div/div/a/div[@class='img']/img/@data-mediumthumb")[0]
			
			# Get the duration of the video
			durationString =	video.xpath("./div/div/a/div[@class='img']/div[@class='marker-overlays']/var[@class='duration']/text()")[0]
			
			# Split it into a list separated by colon
			durationArray =	durationString.split(":")
			
			# Set a default duration of 0
			duration = 0
			
			if (len(durationArray) == 2):
				# Dealing with MM:SS
				minutes =	int(durationArray[0])
				seconds =	int(durationArray[1])
				
				duration = (minutes*60 + seconds) * 1000
				
			elif (len(durationArray) == 3):
				# Dealing with HH:MM:SS... PornHub doesn't do this, but I'll keep it as a backup anyways
				hours =	int(durationArray[0])
				minutes =	int(durationArray[1])
				seconds =	int(durationArray[2])
				
				duration = (hours*3600 + minutes * 60 + seconds) * 1000
			else:
				# WTF
				pass
			
			# Add a Directory Object for the video to the Object Container
			oc.add(DirectoryObject(
				key =	Callback(VideoMenu, url=videoURL, title=videoTitle, duration=duration),
				title =	videoTitle,
				thumb =	thumbnail
			))
	
	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(videos) == int(pageLimit)):
		oc.add(NextPageObject(
			key =	Callback(ListVideos, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))

	return oc

@route(ROUTE_PREFIX + '/videos/menu')
def VideoMenu(url, title=L("DefaultVideoMenuTitle"), duration=0):
	# Create the object to contain all of the videos options
	oc = ObjectContainer(title2 = title)
	
	# Create the Video Clip Object
	vco =	URLService.MetadataObjectForURL(url)
	
	# As I am calling MetadataObjectForURL from the URL Service, it only returns the metadata, it doesn't contain the URL
	vco.url =	url
	
	if (int(duration) > 0):
		vco.duration = int(duration)
	
	# Add the Video Clip Object
	oc.add(vco)
	
	# Get the HTML of the site
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of porn stars in the video
	pornStars = html.xpath("//div[contains(@class, 'pornstarsWrapper')]/a[contains(@class, 'pstar-list-btn')]")
	
	# Check how any porn stars are returned.
	# If just one, then display a Directory Object pointing to the porn star
	if (len(pornStars) == 1):
		oc.add(GenerateVideoPornStarDirectoryObject(pornStars[0]))
		
	# If more than one, create a Directory Object to another menu where all porn stars will be listed
	elif (len(pornStars) > 1):
		oc.add(DirectoryObject(
			key =	Callback(GenerateVideoPornStarMenu, url=url),
			title =	"Porn Stars"
		))
	
	return oc

@route(ROUTE_PREFIX + '/search')
def SearchVideos(query):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "+")
	
	try:
		return ListVideos(title='Search Results For ' + query, url=PH_VIDEO_SEARCH_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)

@route(ROUTE_PREFIX + '/video/pornstars')
def GenerateVideoPornStarMenu(url, title="Porn Stars"):
	# Create the object to contain all of the porn stars in the video
	oc = ObjectContainer(title2 = title)
	
	# Get the HTML of the site
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of porn stars in the video
	pornStars = html.xpath("//div[contains(@class, 'pornstarsWrapper')]/a[contains(@class, 'pstar-list-btn')]")
	
	if (len(pornStars) > 0):
		for pornStar in pornStars:
			oc.add(GenerateVideoPornStarDirectoryObject(pornStar))
	
	return oc

# This function takes markup of a porn star from a video page and creates a Directory Object for it
def GenerateVideoPornStarDirectoryObject(pornStarElement):
	pornStarID =	pornStarElement.xpath("./@data-id")[0]
	pornStarURL =	BASE_URL + pornStarElement.xpath("./@href")[0]
	pornStarName =	pornStarElement.xpath("./text()")[0]
	
	# Fetch the thumbnail
	pornStarHoverHTML = HTML.ElementFromURL(PH_PORNSTARS_HOVER_URL % pornStarID)
	
	pornStarThumbnail = pornStarHoverHTML.xpath("//div[@id='psBoxPictureContainer']/img/@src")[0]
	
	return DirectoryObject(
		key =	Callback(BrowseVideos, url=pornStarURL, title=pornStarName),
		title =	pornStarName,
		thumb =	pornStarThumbnail
	)

def GenerateMenu(title, menuItems, no_cache=False):
	# Create the object to contain the menu items
	oc = ObjectContainer(title2=title, no_cache=no_cache)
	
	# Loop through the menuItems dictionary
	for menuTitle, menuData in menuItems.items():
		# Create empty dictionaries to hold the arguments for the Directory Object and the Function
		directoryObjectArgs =	{}
		functionArgs =		{}
		
		# See if any Directory Object arguments are present in the menu data
		if ('directoryObjectArgs' in menuData):
			# Merge dictionaries
			directoryObjectArgs.update(menuData['directoryObjectArgs'])
		
		# Check to see if the menu item is a search menu item
		if ('search' in menuData and menuData['search'] == True):
			directoryObject = InputDirectoryObject(title=menuTitle, **directoryObjectArgs)
		# Check to see if the menu item is a next page item
		elif ('nextPage' in menuData and menuData['nextPage'] == True):
			directoryObject = NextPageObject(title=menuTitle, **directoryObjectArgs)
		# Otherwise, use a basic Directory Object
		else:
			directoryObject = DirectoryObject(title=menuTitle, **directoryObjectArgs)
			functionArgs['title'] = menuTitle
		
		# See if any Function arguments are present in the menu data
		if ('functionArgs' in menuData):
			# Merge dictionaries
			functionArgs.update(menuData['functionArgs'])
		
		# Set the Directory Object key to the function from the menu data, passing along any additional function arguments
		directoryObject.key =	Callback(menuData['function'], **functionArgs)
		
		# Add the Directory Object to the Object Container
		oc.add(directoryObject)
	
	return oc

# I stole this function from http://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python. It works.
def addURLParameters (url, params):
	
	urlParts =	list(urlparse.urlparse(url))
	
	urlQuery =	dict(urlparse.parse_qsl(urlParts[4]))
	urlQuery.update(params)
	
	# So... PornHub requires that it's query string parameters are set in the right order... for some reason. This piece of code handles that. It's retarded, but it has to be done
	urlQueryOrder = ['c', 'channelSearch', 'search', 'username', 'o', 't', 'page']
	
	urlQueryOrdered = OrderedDict()
	
	for i in urlQueryOrder:
		if i in urlQuery:
			urlQueryOrdered[i] = urlQuery[i] 

	urlParts[4] = urllib.urlencode(urlQueryOrdered)

	return urlparse.urlunparse(urlParts)

# I stole this function (and everything I did for search basically) from the RedTube Plex Plugin, this file specifically https://github.com/flownex/RedTube.bundle/blob/master/Contents/Code/PCbfSearch.py
def formatStringForSearch(query, delimiter):
	query = String.StripTags(str(query))
	query = query.replace('%20',' ')
	query = query.replace('  ',' ')
	query = query.strip(' \t\n\r')
	query = delimiter.join(query.split())
	
	return query