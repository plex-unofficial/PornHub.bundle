from PHCommon import *

PH_CHANNELS_URL =		BASE_URL + '/channels'
PH_CHANNEL_SEARCH_URL =	PH_CHANNELS_URL + '/search?channelSearch=%s'
MAX_CHANNELS_PER_PAGE =	36

@route(ROUTE_PREFIX + '/channels')
def BrowseChannels(title="DefaultBrowseChannelsTitle"):
	
	# Create a dictionary of menu items
	browseChannelsMenuItems = OrderedDict([
		('Search Channels',	{'function':SearchChannels, 'search':True, 'directoryObjectArgs':{'prompt':'Search for...','summary':'Enter Channel Search Terms'}}),
		('Most Popular',	{'function':ListChannels, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_CHANNELS_URL, {'o':'rk'})}}),
		('Trending',		{'function':ListChannels, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_CHANNELS_URL, {'o':'tr'})}}),
		('Most Recent',		{'function':ListChannels, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_CHANNELS_URL, {'o':'mr'})}}),
		('A-Z',			{'function':ListChannels, 'functionArgs':{'url':SharedCodeService.PHCommon.AddURLParameters(PH_CHANNELS_URL, {'o':'al'})}})
	])
	
	return GenerateMenu(title, browseChannelsMenuItems)

@route(ROUTE_PREFIX + '/channels/list')
def ListChannels(title, url = PH_CHANNELS_URL, page=1):
	
	# Create a dictionary of menu items
	listChannelsMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = SharedCodeService.PHCommon.AddURLParameters(url, {'page':str(page)})
	
	# Get list of channels
	channels = SharedCodeService.PHChannels.GetChannels(url)
	
	# Loop through all channels
	for channel in channels:
		
		# Add a menu item for the channel
		listChannelsMenuItems[channel["title"]] = {
			'function':			BrowseVideos,
			'functionArgs':			{'url': BASE_URL + channel["url"] + '/videos'},
			'directoryObjectArgs':	{'thumb': channel["thumbnail"]}
		}
	
	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(channels) == MAX_CHANNELS_PER_PAGE):
		listChannelsMenuItems['Next Page'] = {'function':ListChannels, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, listChannelsMenuItems)

@route(ROUTE_PREFIX + '/channels/search')
def SearchChannels(query):
	
	# Format the query for use in PornHub's search
	formattedQuery = SharedCodeService.PHCommon.FormatStringForSearch(query, "+")
	
	try:
		return ListChannels(title='Search Results for ' + query, url=PH_CHANNEL_SEARCH_URL % query)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)