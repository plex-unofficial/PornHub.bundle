from PHCommon import *

PH_PLAYLISTS_URL =			BASE_URL + '/playlists'
PH_PLAYLIST_URL =			BASE_URL + '/playlist'
MAX_PLAYLISTS_PER_PAGE =	36

@route(ROUTE_PREFIX + '/playlists')
def BrowsePlaylists(title):
	
	oc = ObjectContainer(title2=title)
	
	playlistSortOrders = OrderedDict([
		('Top Rated',		{}),
		('Most Viewed',		{'o':'mv'}),
		('Most Recent',		{'o':'mr'}),
		('Most Favorited',	{'o':'mf'})
	])
	
	for playlistSortOrder, urlParams in playlistSortOrders.items():
		oc.add(DirectoryObject(
			key =	Callback(ListPlaylists, title=playlistSortOrder, url=addURLParameters(PH_PLAYLISTS_URL, urlParams)),
			title =	playlistSortOrder
		))
	
	return oc

@route(ROUTE_PREFIX + '/playlists/list')
def ListPlaylists(title, url = PH_PLAYLISTS_URL, page=1):
	
	# Create the object to contain all of the playlists
	oc = ObjectContainer(title2=title)
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of playlists
	playlists = html.xpath("//ul[contains(@class, 'user-playlist')]/li[contains(@id, 'playlist')]")
	
	# Loop through all playlists
	for playlist in playlists:
		
		playlistTitle =		playlist.xpath("./div/div[contains(@class, 'thumbnail-info-wrapper')]/span[contains(@class, 'title')]/a[contains(@class, 'title')]/text()")[0]
		playlistURL =		BASE_URL + playlist.xpath("./div/div[contains(@class, 'thumbnail-info-wrapper')]/span[contains(@class, 'title')]/a[contains(@class, 'title')]/@href")[0]
		playlistThumbnail =	playlist.xpath("./div/div[contains(@class, 'linkWrapper')]/img[contains(@class, 'largeThumb')]/@data-mediumthumb")[0]
		
		# Add a Directory Object for the playlists
		oc.add(DirectoryObject(
			key =	Callback(SortVideos, title=playlistTitle, url=playlistURL),
			title =	playlistTitle,
			thumb =	playlistThumbnail
		))
	
	# There is a slight change that this will break... If the number of playlists returned in total is divisible by MAX_PLAYLISTS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(playlists) == MAX_PLAYLISTS_PER_PAGE):
		oc.add(NextPageObject(
			key =	Callback(ListPlaylists, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))
	
	return oc