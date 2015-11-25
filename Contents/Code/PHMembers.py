from PHCommon import *

PH_DISCOVER_MEMBERS_URL =	BASE_URL + '/user/discover'
PH_SEARCH_MEMBERS_URL =		BASE_URL + '/user/search?username=%s'

PH_MAX_MEMBERS_PER_PAGE =	42

@route(ROUTE_PREFIX + '/members')
def BrowseMembers(title, url=PH_DISCOVER_MEMBERS_URL):
	
	oc = ObjectContainer(title2=title)
	
	oc.add(InputDirectoryObject(
		key =	Callback(SearchMembers, title='Search Results'),
		title =	"Search Members",
		prompt =	"Search for...",
		summary =	"Enter member's username"
	))
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of sort orders
	sortOrders = html.xpath("//div[contains(@class, 'members-page')]/div[contains(@class, 'sectionTitle')]")
	
	# Loop through all sort orders
	for sortOrder in sortOrders:
		
		sortOrderTitle =	sortOrder.xpath("./h2/text()")[0]
		sortOrderURL =	BASE_URL + sortOrder.xpath("./div[contains(@class, 'filters')]/a/@href")[0]
		
		oc.add(DirectoryObject(
			key =	Callback(ListMembers, title=sortOrderTitle, url=sortOrderURL),
			title =	sortOrderTitle
		))
	
	return oc

@route(ROUTE_PREFIX + '/members/list')
def ListMembers(title, url=PH_DISCOVER_MEMBERS_URL, page=1):
	
	# Create the object to contain all of the members
	oc = ObjectContainer(title2=title)
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of members
	members = html.xpath("//ul[contains(@class, 'userWidgetWrapperGrid')]/li")
	
	# Loop through all members
	for member in members:
		
		memberTitle =		member.xpath("./div[contains(@class, 'usernameWrap')]/a[contains(@class, 'usernameLink')]/text()")[0]
		memberURL =		BASE_URL + member.xpath("./div[contains(@class, 'usernameWrap')]/a[contains(@class, 'usernameLink')]/@href")[0]
		memberThumbnail =	member.xpath("./div[contains(@class, 'large-avatar')]/a[contains(@class, 'userLink')]/img/@src")[0]
		
		# Add a Directory Object for the members
		oc.add(DirectoryObject(
			key =	Callback(MemberMenu, title=memberTitle, url=memberURL, username=memberTitle),
			title =	memberTitle,
			thumb =	memberThumbnail
		))
	
	# There is a slight change that this will break... If the number of members returned in total is divisible by PH_MAX_MEMBERS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(members) == PH_MAX_MEMBERS_PER_PAGE):
		oc.add(NextPageObject(
			key =	Callback(ListMembers, title=title, url=url, page = int(page)+1),
			title =	'Next Page'
		))
	
	return oc

@route(ROUTE_PREFIX + '/members/menu')
def MemberMenu(title, url, username):
	
	# Create the object to contain all of the member options
	oc = ObjectContainer(title2=title)
	
	# TODO: Use some data structure to make this into a loop... A simple dictionary won't do, will need to ponder this. First change to be made for v1.3
	
	# Directory Object for Member's Public Videos
	oc.add(DirectoryObject(
		key =	Callback(ListVideos, title=username + "'s Public Videos", url=url + '/videos/public'),
		title =	'Public Videos'
	))
	
	# Directory Object for Member's Favorite Videos
	oc.add(DirectoryObject(
		key =	Callback(ListVideos, title=username + "'s Favorite Videos", url=url + '/videos/favorites'),
		title =	'Favorite Videos'
	))
	
	# Directory Object for Member's Watched Videos
	oc.add(DirectoryObject(
		key =	Callback(ListVideos, title=username + "'s Watched Videos", url=url + '/videos/recent'),
		title =	'Watched Videos'
	))
	
	# Directory Object for Member's Public Playlists
	oc.add(DirectoryObject(
		key =	Callback(ListPlaylists, title=username + "'s Public Playlists", url=url + '/playlists/public'),
		title =	'Public Playlists'
	))
	
	# Directory Object for Member's Favorite Playlists
	oc.add(DirectoryObject(
		key =	Callback(ListPlaylists, title=username + "'s Favorite Playlists", url=url + '/playlists/favorites'),
		title =	'Favorite Playlists'
	))
	
	return oc

@route(ROUTE_PREFIX + '/members/search')
def SearchMembers(query, title):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "+")
	
	try:
		return ListMembers(title='Search Results for ' + query, url=PH_SEARCH_MEMBERS_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)