import urllib
import urlparse
from collections import OrderedDict

ROUTE_PREFIX =			'/video/pornhub'

BASE_URL =			'http://pornhub.com'
PH_VIDEO_URL =			BASE_URL + '/video'
PH_VIDEO_SEARCH_URL =	PH_VIDEO_URL + '/search?search=%s'

MAX_VIDEOS_PER_PAGE =			28
MAX_VIDEOS_PER_SEARCH_PAGE =		20
MAX_VIDEOS_PER_CHANNEL_PAGE =	36
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

@route(ROUTE_PREFIX + '/list')
def ListVideos(title, url, page=1, pageLimit = MAX_VIDEOS_PER_PAGE):
	
	# Create the object to contain all of the videos
	oc = ObjectContainer(title2 = title)
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	if ("/channels/" in url):
		pageLimit =	MAX_VIDEOS_PER_CHANNEL_PAGE
	elif ("/video/search" in url):
		pageLimit =	MAX_VIDEOS_PER_SEARCH_PAGE
	elif ("/users/" in url):
		pageLimit =	MAX_VIDEOS_PER_USER_PAGE
	
	# Get the HTML of the site
	html = HTML.ElementFromURL(url)
	
	Log(HTML.StringFromElement(html))
	
	# Use xPath to extract a list of divs that contain videos
	videos = html.xpath("//li[contains(@class,'videoblock')]")
	
	# This piece of code is ridiculous. From the best I can gether, the poorly formed HTML on PornHub makes xPath choke at 123 videos. So I rounded it down to 120 and limited the videos to that. This should only affect playlists, but it is a really ridiculous problem
	if (len(videos) >= 120):
		videos =	videos[0:119]
	
	Log ('There are ' + str(len(videos)) + ' videos')
	
	# Loop through the videos in the page
	for video in videos:
		
		#Log (HTML.StringFromElement(video))
		
		# Get the link of the video
		videoURL = video.xpath("./div/div/a/@href")[0]
		
		# Check for relative URLs
		if (videoURL.startswith('/')):
			videoURL = BASE_URL + videoURL
		
		# Make sure the last step went smoothly (this is probably redundant but oh well)
		if (videoURL.startswith(BASE_URL)):
			# Get the video details
			videoTitle =	video.xpath("./div/div/a/div[contains(@class, 'thumbnail-info-wrapper')]/span[@class='title']/a/text()")[0]
			thumbnail =	video.xpath("./div/div/a/div[@class='img']/img/@data-mediumthumb")[0]
			
			# Create a Video Clip Object for the video
			vco = VideoClipObject(
				url =		videoURL,
				title =	videoTitle,
				thumb =	thumbnail
			)
			
			# Get the duration of the video
			durationString =	video.xpath("./div/div/a/div[@class='img']/div[@class='marker-overlays']/var[@class='duration']/text()")[0]
			
			# Split it into a list separated by colon
			durationArray =	durationString.split(":")
			
			if (len(durationArray) == 2):
				# Dealing with MM:SS
				minutes =	int(durationArray[0])
				seconds =	int(durationArray[1])
				
				vco.duration = (minutes*60 + seconds) * 1000
				
			elif (len(durationArray) == 3):
				# Dealing with HH:MM:SS... PornHub doesn't do this, but I'll keep it as a backup anyways
				hours =	int(durationArray[0])
				minutes =	int(durationArray[1])
				seconds =	int(durationArray[2])
				
				vco.duration = (hours*3600 + minutes * 60 + seconds) * 1000
			else:
				# WTF
				pass
			
			# Add the Video Clip Object to the Object Container
			oc.add(vco)
	
	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(videos) == int(pageLimit)):
		oc.add(NextPageObject(
			key =	Callback(ListVideos, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))

	return oc

@route(ROUTE_PREFIX + '/sort')
def SortVideos(title, url = PH_VIDEO_URL, sortOrders = SORT_ORDERS):
	
	# Create the object to contain all of the sorting options
	oc = ObjectContainer(title2 = title)
	
	if ("/channels/" in url):
		sortOrders = CHANNEL_VIDEOS_SORT_ORDERS
	
	# Add the sorting options
	for sortTitle, urlParams in sortOrders.items():
		
		oc.add(DirectoryObject(
			key =	Callback(ListVideos, title=sortTitle, url=addURLParameters(url, urlParams)),
			title =	title + ' - ' + sortTitle
		))
	
	return oc

@route(ROUTE_PREFIX + '/search')
def SearchVideos(query, title):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "+")
	
	try:
		return ListVideos(title='Search Results for ' + query, url=PH_VIDEO_SEARCH_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)

# I stole this function from http://stackoverflow.com/questions/2506379/add-params-to-given-url-in-python. It works.
def addURLParameters (url, params):
	
	urlParts =	list(urlparse.urlparse(url))
	
	urlQuery =	dict(urlparse.parse_qsl(urlParts[4]))
	urlQuery.update(params)
	
	# So... PornHub requires that it's query string parameters are set in the right order... for some reason. This piece of code handles that. It's retarded, but it has to be done
	urlQueryOrder = ['c', 'channelSearch', 'search', 'o', 't', 'page']
	
	urlQueryOrdered = OrderedDict()
	
	for i in urlQueryOrder:
		if i in urlQuery:
			urlQueryOrdered[i] = urlQuery[i] 

	urlParts[4] = urllib.urlencode(urlQueryOrdered)

	return urlparse.urlunparse(urlParts)

def formatStringForSearch(query, delimiter):
	query = String.StripTags(str(query))
	query = query.replace('%20',' ')
	query = query.replace('  ',' ')
	query = query.strip(' \t\n\r')
	query = delimiter.join(query.split())
	
	return query