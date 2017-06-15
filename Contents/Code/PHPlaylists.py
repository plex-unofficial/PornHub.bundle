from PHCommon import *

PH_PLAYLISTS_URL =			BASE_URL + AREA + '/playlists'
PH_PLAYLIST_URL =			BASE_URL + '/playlist'

MAX_PLAYLISTS_PER_PAGE =	36

@route(ROUTE_PREFIX + '/playlists')
def BrowsePlaylists(title=L("DefaultBrowsePlaylistsTitle")):
	
	# Create a dictionary of menu items
	browsePlaylistsMenuItems = OrderedDict([
		('Most Recent',				{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'mr'})}}),
		('Top Rated - All Time',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'a'})}}),
		('Top Rated - Monthly',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'m'})}}),
		('Top Rated - Weekly',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'w'})}}),
		('Top Rated - Daily',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'tr', 't':'t'})}}),
		('Most Viewed - All Time',	{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'a'})}}),
		('Most Viewed - Monthly',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'m'})}}),
		('Most Viewed - Weekly',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'w'})}}),
		('Most Viewed - Daily',		{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'mv', 't':'t'})}}),
		('Most Favorited',			{'function':ListPlaylists, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_PLAYLISTS_URL, {'o':'mf'})}})
	])
	
	return GenerateMenu(title, browsePlaylistsMenuItems)

@route(ROUTE_PREFIX + '/playlists/list')
def ListPlaylists(title, url = PH_PLAYLISTS_URL, page=1):
	
	# Create a dictionary of menu items
	listPlaylistsMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = SharedCodeService.PHCommon.AddURLParameters(url, {'page':str(page)})
	
	# Get list of playlists
	playlists = SharedCodeService.PHPlaylists.GetPlaylists(url)
	
	# Loop through all playlists
	for playlist in playlists:
		
		# Make sure Playlist isn't empty
		if (playlist["isEmpty"] == False):
			
			# Add a menu item for the playlist
			# TODO: I am currently using the playlist title as a key, however these aren't guarenteed to be unique. 
			listPlaylistsMenuItems[playlist["title"]] = {
				'function':			BrowseVideos,
				'functionArgs':			{'url': BASE_URL + playlist["url"]},
				'directoryObjectArgs':	{'thumb': playlist["thumbnail"]}
			}
	
	# There is a slight change that this will break... If the number of playlists returned in total is divisible by MAX_PLAYLISTS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(playlists) == MAX_PLAYLISTS_PER_PAGE):
		listPlaylistsMenuItems['Next Page'] = {'function':ListPlaylists, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, listPlaylistsMenuItems)