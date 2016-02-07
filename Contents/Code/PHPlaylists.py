from PHCommon import *

PH_PLAYLISTS_URL =			BASE_URL + '/playlists'
PH_PLAYLIST_URL =			BASE_URL + '/playlist'

MAX_PLAYLISTS_PER_PAGE =	36

@route(ROUTE_PREFIX + '/playlists')
def BrowsePlaylists(title=L("DefaultBrowsePlaylistsTitle")):
	
	# Create a dictionary of menu items
	browsePlaylistsMenuItems = OrderedDict([
		('Most Recent',				{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'mr'})}}),
		('Top Rated - All Time',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'a'})}}),
		('Top Rated - Monthly',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'m'})}}),
		('Top Rated - Weekly',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'w'})}}),
		('Top Rated - Daily',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'t'})}}),
		('Most Viewed - All Time',	{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'a'})}}),
		('Most Viewed - Monthly',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'m'})}}),
		('Most Viewed - Weekly',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'w'})}}),
		('Most Viewed - Daily',		{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'d'})}}),
		('Most Favorited',			{'function':ListPlaylists, 'functionArgs':{'url':addURLParameters(PH_PLAYLISTS_URL, {'o':'mf'})}})
	])
	
	return GenerateMenu(title, browsePlaylistsMenuItems)

@route(ROUTE_PREFIX + '/playlists/list')
def ListPlaylists(title, url = PH_PLAYLISTS_URL, page=1):
	
	# Create a dictionary of menu items
	listPlaylistsMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of playlists
	playlists = html.xpath("//ul[contains(@class, 'user-playlist')]/li[contains(@id, 'playlist')]")
	
	# Loop through all playlists
	for playlist in playlists:
		
		# Use xPath to extract playlist details
		playlistTitle =		playlist.xpath("./div/div[contains(@class, 'thumbnail-info-wrapper')]/span[contains(@class, 'title')]/a[contains(@class, 'title')]/text()")[0]
		playlistURL =		BASE_URL + playlist.xpath("./div/div[contains(@class, 'thumbnail-info-wrapper')]/span[contains(@class, 'title')]/a[contains(@class, 'title')]/@href")[0]
		playlistThumbnail =	playlist.xpath("./div/div[contains(@class, 'linkWrapper')]/img[contains(@class, 'largeThumb')]/@data-mediumthumb")[0]
		
		# Add a menu item for the playlist
		listPlaylistsMenuItems[playlistTitle] = {'function':BrowseVideos, 'functionArgs':{'url':playlistURL}, 'directoryObjectArgs':{'thumb':playlistThumbnail}}
	
	# There is a slight change that this will break... If the number of playlists returned in total is divisible by MAX_PLAYLISTS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(playlists) == MAX_PLAYLISTS_PER_PAGE):
		listPlaylistsMenuItems['Next Page'] = {'function':ListPlaylists, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, listPlaylistsMenuItems)