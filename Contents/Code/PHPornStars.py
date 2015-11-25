from PHCommon import *

PH_PORNSTARS_URL =			BASE_URL + '/pornstars'
PH_PORNSTARS_SEARCH_URL =	PH_PORNSTARS_URL + '/search?search=%s'
MAX_PORNSTARS_PER_PAGE =	28

@route(ROUTE_PREFIX + '/pornstars')
def BrowsePornStars(title):
	
	oc = ObjectContainer(title2=title)
	
	oc.add(InputDirectoryObject(
		key =	Callback(SearchPornStars, title='Search Results'),
		title =	"Search Porn Stars",
		prompt =	"Search for...",
		summary =	"Enter Porn Star Search Terms"
	))
	
	pornStarSortOrders = OrderedDict([
		('Most Popular',	{}),
		('Most Viewed',		{'o':'mv'}),
		('Top Trending',	{'o':'t'}),
		('Most Subscribed',	{'o':'ms'}),
		('Alphabetical',	{'o':'a'}),
		('Number of Videos',	{'o':'nv'})
	])
	
	for pornStarSortOrder, urlParams in pornStarSortOrders.items():
		oc.add(DirectoryObject(
			key =	Callback(ListPornStars, title=pornStarSortOrder, url=addURLParameters(PH_PORNSTARS_URL, urlParams)),
			title =	pornStarSortOrder
		))
	
	return oc

@route(ROUTE_PREFIX + '/pornstars/list')
def ListPornStars(title, url = PH_PORNSTARS_URL, page=1):
	
	# Create the object to contain all of the porn stars
	oc = ObjectContainer(title2=title)
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of porn stars
	pornStars = html.xpath("//ul[contains(@class, 'pornstarIndex')]/li")
	
	# Loop through all channels
	for pornStar in pornStars:
		
		pornStarName =		pornStar.xpath("./div/div[contains(@class, 'thumbnail-info-wrapper')]/a/text()")[0]
		pornStarURL =		BASE_URL + pornStar.xpath("./div/div[contains(@class, 'thumbnail-info-wrapper')]/a/@href")[0]
		pornStarThumbnail =	pornStar.xpath("./div/a/img/@src")[0]
		
		# Add a Directory Object for the channels
		oc.add(DirectoryObject(
			key =	Callback(SortVideos, title=pornStarName, url=pornStarURL),
			title =	pornStarName,
			thumb =	pornStarThumbnail
		))
	
	# There is a slight change that this will break... If the number of videos returned in total is divisible by MAX_VIDEOS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(pornStars) == MAX_PORNSTARS_PER_PAGE):
		oc.add(NextPageObject(
			key =	Callback(ListPornStars, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))
	
	return oc

@route(ROUTE_PREFIX + '/pornstars/search')
def SearchPornStars(query, title):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "+")
	
	try:
		return ListPornStars(title='Search Results for ' + query, url=PH_PORNSTARS_SEARCH_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)