from PHCommon import *

PH_CHANNELS_URL =		BASE_URL + '/channels'
PH_CHANNEL_SEARCH_URL =	PH_CHANNELS_URL + '/search?channelSearch=%s'
MAX_CHANNELS_PER_PAGE =	36

@route(ROUTE_PREFIX + '/channels')
def BrowseChannels(title):
	
	oc = ObjectContainer(title2=title)
	
	oc.add(InputDirectoryObject(
		key =	Callback(SearchChannels, title='Search Results'),
		title =	"Search Channels",
		prompt =	"Search for...",
		summary =	"Enter Channel Search Terms"
	))
	
	channelSortOrders = OrderedDict([
		('Most Popular',	{'o':'rk'}),
		('Trending',		{'o':'tr'}),
		('Most Recent',		{'o':'mr'}),
		('A-Z',			{'o':'al'})
	])
	
	for channelSortOrder, urlParams in channelSortOrders.items():
		oc.add(DirectoryObject(
			key =	Callback(ListChannels, title=channelSortOrder, url=addURLParameters(PH_CHANNELS_URL, urlParams)),
			title =	channelSortOrder
		))
	
	return oc

@route(ROUTE_PREFIX + '/channels/list')
def ListChannels(title, url = PH_CHANNELS_URL, page=1):
	
	# Create the object to contain all of the channels
	oc = ObjectContainer(title2=title)
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of channels
	channels = html.xpath("//div[contains(@class, 'listChannelsWrapper')]/ul/li/div")
	
	# Loop through all channels
	for channel in channels:
		
		channelTitle =		channel.xpath("./div[contains(@class, 'description')]/div[contains(@class, 'descriptionContainer')]/ul/li/a[contains(@class, 'usernameLink')]/text()")[0]
		channelURL =		BASE_URL + channel.xpath("./div[contains(@class, 'description')]/div[contains(@class, 'descriptionContainer')]/ul/li/a[contains(@class, 'usernameLink')]/@href")[0]
		channelThumbnail =	channel.xpath("./div[contains(@class,'description')]/div[contains(@class, 'avatar')]/a/img/@src")[0]
		
		# Add a Directory Object for the channels
		oc.add(DirectoryObject(
			key =	Callback(SortVideos, title=channelTitle, url=channelURL + '/videos'),
			title =	channelTitle,
			thumb =	channelThumbnail
		))
	
	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(channels) == MAX_CHANNELS_PER_PAGE):
		oc.add(NextPageObject(
			key =	Callback(ListChannels, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))
	
	return oc

@route(ROUTE_PREFIX + '/channels/search')
def SearchChannels(query, title):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "+")
	
	try:
		return ListChannels(title='Search Results for ' + query, url=PH_CHANNEL_SEARCH_URL % query)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)