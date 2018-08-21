from collections import OrderedDict

ROUTE_PREFIX =				'/video/pornhub'

BASE_URL =				'http://pornhub.com'
PH_VIDEO_URL =				BASE_URL + '/video'
PH_VIDEO_SEARCH_URL =		PH_VIDEO_URL + '/search?search=%s'

PH_USER_HOVER_URL =		BASE_URL + '/user/hover?id=%s'

MAX_VIDEOS_PER_PAGE =			44
MAX_VIDEOS_PER_PAGE_PAGE_ONE =	32
MAX_VIDEOS_PER_SEARCH_PAGE =		20
MAX_VIDEOS_PER_CHANNEL_PAGE =	36
MAX_VIDEOS_PER_PORNSTAR_PAGE =	36
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
		browseVideosMenuItems[sortTitle] = {'function':ListVideos, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(url, urlParams)}}

	return GenerateMenu(title, browseVideosMenuItems)

@route(ROUTE_PREFIX + '/videos/list')
def ListVideos(title=L("DefaultListVideosTitle"), url=PH_VIDEO_URL, page=1, pageLimit = MAX_VIDEOS_PER_PAGE_PAGE_ONE):

	# Create the object to contain all of the videos
	oc = ObjectContainer(title2 = title)

	# Add the page number into the query string
	if (int(page) != 1):
		url = SharedCodeService.PHCommon.AddURLParameters(url, {'page':str(page)})

	# This could definitely be handled more gracefully. But it works for now
	if ("/video/search" in url):
		pageLimit =	MAX_VIDEOS_PER_SEARCH_PAGE
	elif ("/channels/" in url):
		pageLimit =	MAX_VIDEOS_PER_CHANNEL_PAGE
	elif ("/pornstar/" in url):
		pageLimit =	MAX_VIDEOS_PER_PORNSTAR_PAGE
	elif ("/users/" in url):
		pageLimit =	MAX_VIDEOS_PER_USER_PAGE
	elif ("/video" in url and page > 1):
		# In the Browse All Videos and Categories menus, they display MAX_VIDEOS_PER_PAGE_PAGE_ONE on page one, and MAX_VIDEOS_PER_PAGE from page two onward
		pageLimit =	MAX_VIDEOS_PER_PAGE

	# Get list of categories
	videos = SharedCodeService.PHCommon.GetVideos(url)

	# Loop through the videos in the page
	for video in videos:

		# Check for relative URLs
		if (video["url"].startswith('/')):
			video["url"] = BASE_URL + video["url"]

		# Make sure the last step went smoothly (this is probably redundant but oh well)
		if (video["url"].startswith(BASE_URL)):

			# Add a Directory Object for the video to the Object Container
			oc.add(DirectoryObject(
				key =	Callback(VideoMenu, url=video["url"], title=video["title"], duration=video["duration"]),
				title =	video["title"],
				thumb =	video["thumbnail"],
				duration =	video["duration"]
			))

	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(videos) == int(pageLimit)):
		oc.add(NextPageObject(
			key =	Callback(ListVideos, title=title, url=url, page = int(page)+1, pageLimit=int(pageLimit)),
			title =	'Next Page'
		))

	return oc

@route(ROUTE_PREFIX + '/videos/menu')
def VideoMenu(url, title=L("DefaultVideoMenuTitle"), duration=0):
	# Create the object to contain all of the videos options
	oc = ObjectContainer(title2 = title, no_cache=True)

	# Create the Video Clip Object
	vco =	URLService.MetadataObjectForURL(url)

	# As I am calling MetadataObjectForURL from the URL Service, it only returns the metadata, it doesn't contain the URL
	vco.url =	url

	# Overide the title
	vco.title =	"Play Video"

	if (int(duration) > 0):
		vco.duration = int(duration)

	# Add the Video Clip Object
	oc.add(vco)

	# Get the HTML of the site
	html =		HTML.ElementFromURL(url)

	# Get the video meta data
	videoMetaData = SharedCodeService.PHCommon.GetVideoMetaDataJSON(htmlElement=html)

	# Check to see if Thumbnails are enabled in the video sub menu in the Preferences, and also if the Thumbnail metadata exists
	if (Prefs["videoMenuShowThumbnails"] and videoMetaData["thumbs"] and videoMetaData["thumbs"]["urlPattern"]):
		oc.add(PhotoAlbumObject(
			key =		Callback(VideoThumbnails, url=url),
			rating_key =	url + " - Thumbnails",
			title =		"Thumbnails",
			summary =		"Tiled thumbnails from this video"
		))

	# Check to see if Uploaders are enabled in the video sub menu in the Preferences
	if (Prefs["videoMenuShowUploader"]):
		# Use xPath to extract the uploader of the video
		uploader = html.xpath("//div[contains(@class, 'video-info-row')]/div[contains(@class, 'usernameWrap')]")

		# Make sure one is returned
		if (len(uploader) > 0):
			# Get the link within
			uploaderLink =	uploader[0].xpath("./a")

			# Make sure it exists
			if (len(uploaderLink) > 0):
				uploaderURL =	BASE_URL + uploaderLink[0].xpath("./@href")[0]
				uploaderName =	uploaderLink[0].xpath("./text()")[0]

				uploaderType = uploader[0].xpath("./@data-type")[0]

				# Check to see if the video is listed under a channel or a user
				if (uploaderType == "channel"):
					channelID =	uploader[0].xpath("./@data-channelid")[0]

					# Get the porn star hover meta data
					channelHoverMetaData = SharedCodeService.PHChannels.GetChannelHoverMetaData(channelID)

					oc.add(DirectoryObject(
						key =	Callback(BrowseVideos, url=uploaderURL + '/videos', title=uploaderName),
						title =	uploaderName,
						summary =	"Channel this video appears in",
						thumb =	channelHoverMetaData["thumbnail"]
					))
				elif (uploaderType == "user"):
					pass

	# Check to see if Porn Stars are enabled in the video sub menu in the Preferences
	if (Prefs["videoMenuShowPornStars"]):
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
				title =	"Porn Stars",
				summary =	"Porn Stars that appear in this video"
			))


	# Check to see if Related Videos are enabled in the video sub menu in the Preferences
	if (Prefs["videoMenuShowRelatedVideos"]):
		# Use xPath to extract the related videos
		relatedVideos = html.xpath("//ul[@id='relatedVideosCenter' or @id='relateRecommendedItems']//li[contains(@class, 'videoblock')]/div[contains(@class, 'wrap')]/div[contains(@class, 'phimage')]")

		if (len(relatedVideos) > 0):
			relatedVideosThumb =	relatedVideos[0].xpath("./div[contains(@class, 'img')]/a/img/@data-mediumthumb")[0]

			# Add the Related Videos Directory Object
			oc.add(DirectoryObject(
				key =	Callback(RelatedVideos, url=url),
				title =	"Related Videos",
				summary =	"Videos related to this video",
				thumb =	relatedVideosThumb
			))


	# Check to see if Playlists are enabled in the video sub menu in the Preferences
	if (Prefs["videoMenuShowPlaylists"]):
		# Fetch playlists containing the video (if any)
		playlists = html.xpath("//ul[contains(@class, 'playlist-listingSmall')]/li/div[contains(@class, 'wrap')]")

		if (len(playlists) > 0):
			playlistsThumb =	playlists[0].xpath("./div[contains(@class, 'linkWrapper')]/img/@data-mediumthumb")[0]

			oc.add(DirectoryObject(
				key =	Callback(PlaylistsContainingVideo, url=url),
				title =	"Playlists",
				summary =	"Playlists that contain this video",
				thumb =	playlistsThumb
			))

	# Check to see if Action is enabled in the video sub menu in the Preferences
	if (Prefs["videoMenuShowAction"]):
		if (videoMetaData["actionTags"]):
			oc.add(DirectoryObject(
				key =	Callback(VideoActions, url=url),
				title =	"Action",
				summary =	"Timestamps of when actions (e.g. different positions) happen in this video"
			))

	return oc

@route(ROUTE_PREFIX + '/search')
def SearchVideos(query):

	# Format the query for use in PornHub's search
	formattedQuery = SharedCodeService.PHCommon.FormatStringForSearch(query, "+")

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

	# Get the porn star hover meta data
	pornStarHoverMetaData = SharedCodeService.PHPornStars.GetPornStarHoverMetaData(pornStarID)

	return DirectoryObject(
		key =	Callback(BrowseVideos, url=pornStarURL, title=pornStarName),
		title =	pornStarName,
		summary =	"Porn Star appearing in this video",
		thumb =	pornStarHoverMetaData["thumbnail"]
	)

@route(ROUTE_PREFIX + '/video/thumbnails')
def VideoThumbnails(url, title="Thumbnails"):
	# Create the object to contain the thumbnails
	oc = ObjectContainer(title2=title)

	# Get the video thumbnail URLs
	thumbnailURLs = SharedCodeService.PHCommon.GetVideoThumbnailURLs(url)

	for i, thumbnailURL in enumerate(thumbnailURLs):

		oc.add(PhotoObject(
			key =		thumbnailURL,
			rating_key =	thumbnailURL,
			title =		"Thumbnail #" + str(i + 1),
			thumb =		thumbnailURL
		))

	return oc

@route(ROUTE_PREFIX + '/video/related')
def RelatedVideos(url, title="Related Videos"):
	# Create the object to contain the related videos
	oc = ObjectContainer(title2=title)

	# Get the video thumbnail URLs
	relatedVideos = SharedCodeService.PHCommon.GetRelatedVideos(url)

	# Loop through related videos
	for relatedVideo in relatedVideos:

		oc.add(DirectoryObject(
			key =	Callback(VideoMenu, url=BASE_URL + relatedVideo["url"], title=relatedVideo["title"]),
			title =	relatedVideo["title"],
			summary =	relatedVideo["title"],
			thumb =	relatedVideo["thumbnail"]
		))

	return oc

@route(ROUTE_PREFIX + '/video/playlists')
def PlaylistsContainingVideo(url, title="Playlists Containing Video"):
	# Create the object to contain the playlists
	oc = ObjectContainer(title2=title)

	# Get the playlists containing the video
	playlists = SharedCodeService.PHCommon.GetPlaylistsContainingVideo(url)

	# Loop through playlists
	for playlist in playlists:

		oc.add(DirectoryObject(
			key =	Callback(BrowseVideos, url=BASE_URL + playlist["url"], title=playlist["title"]),
			title =	playlist["title"],
			thumb =	playlist["thumbnail"]
		))

	return oc

@route(ROUTE_PREFIX + '/video/actions')
def VideoActions(url, title="Actions", header=None, message=None, replace_parent=None):
	# Create the object to contain the actions
	oc = ObjectContainer(title2=title)

	if (header):
		oc.header =		header
	if (message):
		oc.message =		message
	if (replace_parent):
		oc.replace_parent =	replace_parent

	# Get the playlists containing the video
	actions = SharedCodeService.PHCommon.GetVideoActions(url)

	for action in actions:

		actionSummary = action["title"] + " starts at " + action["timestamp"]

		oc.add(DirectoryObject(
			key =	Callback(VideoActions, url=url, title=title, header=action["title"], message=actionSummary, replace_parent=True),
			title =	action["timestamp"] + ": " + action["title"],
			summary =	actionSummary
		))

	return oc

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
