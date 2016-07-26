from PHCommon import *

PH_DISCOVER_MEMBERS_URL =	BASE_URL + '/user/discover'
PH_SEARCH_MEMBERS_URL =		BASE_URL + '/user/search?username=%s'

# Only the Members search results page has 42 results. The other Member pages have 48 results, but don't feature pagination
PH_MAX_MEMBERS_PER_PAGE =					42
PH_MAX_MEMBERS_PER_MEMBER_SUBSCRIBERS_PAGE =	100
PH_MAX_MEMBERS_PER_MEMBER_SUBSCRIPTIONS_PAGE =	100
PH_MAX_MEMBERS_PER_MEMBER_FRIENDS_PAGE =		100
PH_MAX_MEMBER_CHANNELS_PER_PAGE =			8

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
def ListMembers(title, url=PH_DISCOVER_MEMBERS_URL, page=1, pageLimit=PH_MAX_MEMBERS_PER_PAGE):
	
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
	
	# There is a slight change that this will break... If the number of members returned in total is divisible by pageLimit with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(members) == int(pageLimit)):
		listMembersMenuItems['Next Page'] = {'function':ListMembers, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1, 'pageLimit':int(pageLimit)}, 'nextPage':True}
	
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
	
	# Get the HTML of the Member's spash page, as well as their Video and Playlist pages
	memberHTML =		HTML.ElementFromURL(url)
	memberVideosHTML =	HTML.ElementFromURL(url + '/videos')
	memberPlaylistsHTML =	HTML.ElementFromURL(url + '/playlists')
	
	# Create a dictionary of menu items
	memberMenuItems = OrderedDict([
		('Public Videos',			{'function':ListVideos,				'functionArgs':{'title':username + "'s Public Videos",			'url':url + '/videos/public'}}),
		('Favorite Videos',			{'function':ListVideos,				'functionArgs':{'title':username + "'s Favorite Videos",			'url':url + '/videos/favorites'}}),
		('Watched Videos',			{'function':ListVideos,				'functionArgs':{'title':username + "'s Watched Videos",			'url':url + '/videos/recent'}}),
		('Public Playlists',			{'function':ListPlaylists,				'functionArgs':{'title':username + "'s Public Playlists",		'url':url + '/playlists/public'}}),
		('Favorite Playlists',		{'function':ListPlaylists,				'functionArgs':{'title':username + "'s Favorite Playlists",		'url':url + '/playlists/favorites'}}),
		('Channels',				{'function':MemberChannels,			'functionArgs':{'title':username + "'s Channels",				'url':url + '/channels'}}),
		('Channel Subscriptions',		{'function':MemberSubscribedChannels,	'functionArgs':{'title':username + "'s Channel Subscriptions",	'url':url + '/channel_subscriptions'}}),
		('Porn Star Subscriptions',	{'function':MemberSubscribedPornStars,	'functionArgs':{'title':username + "'s Porn Star Subscriptions",	'url':url + '/pornstar_subscriptions'}}),
		('Subscribers',				{'function':ListMembers,				'functionArgs':{'title':username + "'s Subscribers",			'url':url + '/subscribers',			'pageLimit':PH_MAX_MEMBERS_PER_MEMBER_SUBSCRIBERS_PAGE}}),
		('Member Subscriptions',		{'function':ListMembers,				'functionArgs':{'title':username + "'s Member Subscriptions",		'url':url + '/subscriptions',			'pageLimit':PH_MAX_MEMBERS_PER_MEMBER_SUBSCRIPTIONS_PAGE}}),
		('Friends',				{'function':ListMembers,				'functionArgs':{'title':username + "'s Friends",				'url':url + '/friends',				'pageLimit':PH_MAX_MEMBERS_PER_MEMBER_FRIENDS_PAGE}})
	])
	
	# This dictionary will hold the conditons on which we want to display Member menu options
	memberMenuChecks = {
		"Public Videos": {
			"xpath":		"//section[@id='videosTab']//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Public']",
			"htmlElement":	memberVideosHTML
		},
		"Favorite Videos": {
			"xpath":		"//section[@id='videosTab']//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Favorites']",
			"htmlElement":	memberVideosHTML
		},
		"Watched Videos": {
			"xpath":		"//section[@id='videosTab']//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Watched']",
			"htmlElement":	memberVideosHTML
		},
		"Public Playlists": {
			"xpath":		"//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Public']",
			"htmlElement":	memberPlaylistsHTML
		},
		"Favorite Playlists": {
			"xpath":		"//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Favorites']",
			"htmlElement":	memberPlaylistsHTML
		},
		"Channels": {
			"xpath":		"//div[contains(@class,'channelSubWidgetContainer')]/ul/li[contains(@class,'channelSubChannelWig')]",
			"htmlElement":	memberHTML
		},
		"Channel Subscriptions": {
			"xpath":		"//div[contains(@class,'userWidgetContainer')]/ul/li[contains(@class,'userChannelWig')]",
			"htmlElement":	memberHTML
		},
		"Porn Star Subscriptions": {
			"xpath":		"//section[@id='sidebarPornstars']//ul[contains(@class,'pornStarSideBar')]/li[contains(@class,'pornstarsElements')]",
			"htmlElement":	memberHTML
		},
		"Subscribers": {
			"xpath":		"//ul[contains(@class,'subViewsInfoContainer')]/li[a[span[contains(@class,'connections')][contains(text(),'subscriber')]]]/a/span[contains(@class,'number')][not(text()='0')]",
			"htmlElement":	memberHTML
		},
		"Member Subscriptions": {
			"xpath":		"//section[@id='profileSubscriptions']//ul/li[contains(@class,'subscriptionsElement')]",
			"htmlElement":	memberHTML
		},
		"Friends": {
			"xpath":		"//ul[contains(@class,'subViewsInfoContainer')]/li[a[span[contains(@class,'connections')][contains(text(),'friend')]]]/a/span[contains(@class,'number')][not(text()='0')]",
			"htmlElement":	memberHTML
		}
	}
	
	# Loop through Member menu option conditons
	for memberMenuCheck in memberMenuChecks:
		# Attempt to get the element from the page
		elements = memberMenuChecks[memberMenuCheck]["htmlElement"].xpath(memberMenuChecks[memberMenuCheck]["xpath"])
		
		if (len(elements) == 0):
			# If no elements are found, do not display the Member menu option
			del memberMenuItems[memberMenuCheck]
	
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
	
	# Use xPath to extract a list of Channels
	channels = html.xpath("//div[contains(@class, 'sectionWrapper')]/div[contains(@class, 'topheader')]")
	
	for channel in channels:
		# Use xPath to extract Channel details
		channelTitle =	channel.xpath("./div[contains(@class, 'floatLeft')]/div[contains(@class, 'title')]/a/text()")[0]
		channelURL =	BASE_URL + channel.xpath("./div[contains(@class, 'floatLeft')]/div[contains(@class, 'title')]/a/@href")[0] + "/videos"
		channelThumb =	channel.xpath("./div[contains(@class, 'avatarWrapper')]/a/img/@src")[0]
		
		# Add a menu item for the Channel
		memberChannelMenuItems[channelTitle] = {'function':BrowseVideos, 'functionArgs':{'url':channelURL, 'title':channelTitle}, 'directoryObjectArgs':{'thumb':channelThumb}}
	
	# There is a slight change that this will break... If the number of Channels returned in total is divisible by PH_MAX_MEMBER_CHANNELS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(channels) == PH_MAX_MEMBER_CHANNELS_PER_PAGE):
		memberChannelMenuItems['Next Page'] = {'function':MemberChannels, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, memberChannelMenuItems)

@route(ROUTE_PREFIX + '/members/channels/subscribed')
def MemberSubscribedChannels(url, title="Member's Subscribed Channels"):
	
	# Create a dictionary of menu items
	memberSubscribedChannelMenuItems = OrderedDict()
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of subscribed Channels
	channels = html.xpath("//div[contains(@class, 'channelSubWidgetContainer')]/ul/li[contains(@class, 'channelSubChannelWig')]")
	
	for channel in channels:
		# Use xPath to extract Channel details
		channelTitle =	channel.xpath("./div/div[contains(@class, 'wtitle')]/a/text()")[0]
		channelURL =	BASE_URL + channel.xpath("./div/div[contains(@class, 'wtitle')]/a/@href")[0] + "/videos"
		channelThumb =	channel.xpath("./div/div/a/img/@src")[0]
		
		# Add a menu item for the Channel
		memberSubscribedChannelMenuItems[channelTitle] = {'function':BrowseVideos, 'functionArgs':{'url':channelURL, 'title':channelTitle}, 'directoryObjectArgs':{'thumb':channelThumb}}
	
	return GenerateMenu(title, memberSubscribedChannelMenuItems)

@route(ROUTE_PREFIX + '/members/pornstars')
def MemberSubscribedPornStars(url, title="Member's Subscribed Porn Stars"):
	
	# Create a dictionary of menu items
	memberSubscribedPornStarsMenuItems = OrderedDict()
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of subscribed Porn Stars
	pornStars = html.xpath("//ul[contains(@class,'pornStarGrid')]/li/div[contains(@class,'user-flag')]/div[contains(@class,'avatarWrap')]/a")
	
	for pornStar in pornStars:
		# Use xPath to extract Porn Star details
		pornStarTitle =	pornStar.xpath("./img/@alt")[0]
		pornStarURL =	BASE_URL + pornStar.xpath("./@href")[0]
		pornStarThumb =	pornStar.xpath("./img/@src")[0]
		
		# Add a menu item for the Porn Star
		memberSubscribedPornStarsMenuItems[pornStarTitle] = {'function':BrowseVideos, 'functionArgs':{'url':pornStarURL, 'title':pornStarTitle}, 'directoryObjectArgs':{'thumb':pornStarThumb}}
	
	return GenerateMenu(title, memberSubscribedPornStarsMenuItems)