from PHCommon import *

PH_DISCOVER_MEMBERS_URL =	BASE_URL + '/user/discover'
PH_SEARCH_MEMBERS_URL =		BASE_URL + '/user/search?username=%s'

PH_MAX_MEMBERS_PER_PAGE =			42
PH_MAX_MEMBER_CHANNELS_PER_PAGE =	8

@route(ROUTE_PREFIX + '/members')
def BrowseMembers(title=L("DefaultBrowseMembersTitle"), url=PH_DISCOVER_MEMBERS_URL):
	
	# Create a dictionary of menu items
	browseMembersMenuItems = OrderedDict([
		('Search Members', {'function':SearchMembers, 'search':True, 'directoryObjectArgs':{'prompt':'Search for...','summary':"Enter member's username"}})
	])
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of sort orders
	sortOrders = html.xpath("//div[contains(@class, 'members-page')]/div[contains(@class, 'sectionTitle')]")
	
	# Loop through all sort orders
	for sortOrder in sortOrders:
		
		# Use xPath to extract sort order details
		sortOrderTitle =	sortOrder.xpath("./h2/text()")[0]
		sortOrderURL =	BASE_URL + sortOrder.xpath("./div[contains(@class, 'filters')]/a/@href")[0]
		
		# Add a menu item for the sort order
		browseMembersMenuItems[sortOrderTitle] = {'function':ListMembers, 'functionArgs':{'url':sortOrderURL}}
	
	return GenerateMenu(title, browseMembersMenuItems)

@route(ROUTE_PREFIX + '/members/list')
def ListMembers(title, url=PH_DISCOVER_MEMBERS_URL, page=1):
	
	# Create a dictionary of menu items
	listMembersMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of members
	members = html.xpath("//ul[contains(@class, 'userWidgetWrapperGrid')]/li")
	
	# Loop through all members
	for member in members:
		
		# Use xPath to extract member details
		memberTitle =		member.xpath("./div[contains(@class, 'usernameWrap')]/a[contains(@class, 'usernameLink')]/text()")[0]
		memberURL =		BASE_URL + member.xpath("./div[contains(@class, 'usernameWrap')]/a[contains(@class, 'usernameLink')]/@href")[0]
		memberThumbnail =	member.xpath("./div[contains(@class, 'large-avatar')]/a[contains(@class, 'userLink')]/img/@src")[0]
		
		# Add a menu item for the member
		listMembersMenuItems[memberTitle] = {'function':MemberMenu, 'functionArgs':{'url':memberURL, 'username':memberTitle}, 'directoryObjectArgs':{'thumb':memberThumbnail}}
	
	# There is a slight change that this will break... If the number of members returned in total is divisible by PH_MAX_MEMBERS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(members) == PH_MAX_MEMBERS_PER_PAGE):
		listMembersMenuItems['Next Page'] = {'function':ListMembers, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, listMembersMenuItems)

@route(ROUTE_PREFIX + '/members/search')
def SearchMembers(query):
	
	# Format the query for use in PornHub's search
	formattedQuery = formatStringForSearch(query, "+")
	
	try:
		return ListMembers(title='Search Results for ' + query, url=PH_SEARCH_MEMBERS_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)

@route(ROUTE_PREFIX + '/members/menu')
def MemberMenu(title, url, username):
	
	# Create a dictionary of menu items
	memberMenuItems = OrderedDict([
		('Channels',			{'function':MemberChannels,			'functionArgs':{'title':username + "'s Channels",			'url':url + '/channels'}}),
		('Subscribed Channels',	{'function':MemberSubscribedChannels,	'functionArgs':{'title':username + "'s Subscribed Channels",	'url':url + '/channel_subscriptions'}}),
		('Public Videos',		{'function':ListVideos,				'functionArgs':{'title':username + "'s Public Videos",		'url':url + '/videos/public'}}),
		('Favorite Videos',		{'function':ListVideos,				'functionArgs':{'title':username + "'s Favorite Videos",		'url':url + '/videos/favorites'}}),
		('Watched Videos',		{'function':ListVideos,				'functionArgs':{'title':username + "'s Watched Videos",		'url':url + '/videos/recent'}}),
		('Public Playlists',		{'function':ListPlaylists,				'functionArgs':{'title':username + "'s Public Playlists",	'url':url + '/playlists/public'}}),
		('Favorite Playlists',	{'function':ListPlaylists,				'functionArgs':{'title':username + "'s Favorite Playlists",	'url':url + '/playlists/favorites'}})
	])
	
	return GenerateMenu(title, memberMenuItems)

@route(ROUTE_PREFIX + '/members/channels')
def MemberChannels(url, title="Member Channels", page=1):
	
	# Create a dictionary of menu items
	memberChannelMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = addURLParameters(url, {'page':str(page)})
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of channels
	channels = html.xpath("//div[contains(@class, 'sectionWrapper')]/div[contains(@class, 'topheader')]")
	
	for channel in channels:
		# Use xPath to extract channel details
		channelTitle =	channel.xpath("./div[contains(@class, 'floatLeft')]/div[contains(@class, 'title')]/a/text()")[0]
		channelURL =	BASE_URL + channel.xpath("./div[contains(@class, 'floatLeft')]/div[contains(@class, 'title')]/a/@href")[0] + "/videos"
		channelThumb =	channel.xpath("./div[contains(@class, 'avatarWrapper')]/a/img/@src")[0]
		
		# Add a menu item for the member
		memberChannelMenuItems[channelTitle] = {'function':BrowseVideos, 'functionArgs':{'url':channelURL, 'title':channelTitle}, 'directoryObjectArgs':{'thumb':channelThumb}}
	
	# There is a slight change that this will break... If the number of members returned in total is divisible by PH_MAX_MEMBER_CHANNELS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(channels) == PH_MAX_MEMBER_CHANNELS_PER_PAGE):
		memberChannelMenuItems['Next Page'] = {'function':MemberChannels, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, memberChannelMenuItems)

@route(ROUTE_PREFIX + '/members/channels/subscribed')
def MemberSubscribedChannels(url, title="Member's Subscribed Channels"):
	
	# Create a dictionary of menu items
	memberSubscribedChannelMenuItems = OrderedDict()
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of subscribed channels
	channels = html.xpath("//div[contains(@class, 'channelSubWidgetContainer')]/ul/li[contains(@class, 'channelSubChannelWig')]")
	
	for channel in channels:
		# Use xPath to extract channel details
		channelTitle =	channel.xpath("./div/div[contains(@class, 'wtitle')]/a/text()")[0]
		channelURL =	BASE_URL + channel.xpath("./div/div[contains(@class, 'wtitle')]/a/@href")[0] + "/videos"
		channelThumb =	channel.xpath("./div/div/a/img/@src")[0]
		
		# Add a menu item for the member
		memberSubscribedChannelMenuItems[channelTitle] = {'function':BrowseVideos, 'functionArgs':{'url':channelURL, 'title':channelTitle}, 'directoryObjectArgs':{'thumb':channelThumb}}
	
	return GenerateMenu(title, memberSubscribedChannelMenuItems)