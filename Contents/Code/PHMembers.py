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
	
	# Get list of sort orders
	sortOrders = SharedCodeService.PHMembers.GetMemberSortOrders(url)
	
	# Loop through all sort orders
	for sortOrder in sortOrders:
		
		# Add a menu item for the sort order
		browseMembersMenuItems[sortOrder["title"]] = {
			'function':	ListMembers,
			'functionArgs':	{'url': BASE_URL + sortOrder["url"]}
		}
	
	return GenerateMenu(title, browseMembersMenuItems)

@route(ROUTE_PREFIX + '/members/list')
def ListMembers(title, url=PH_DISCOVER_MEMBERS_URL, page=1, pageLimit=PH_MAX_MEMBERS_PER_PAGE):
	
	# Create a dictionary of menu items
	listMembersMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = SharedCodeService.PHCommon.AddURLParameters(url, {'page':str(page)})
	
	# Get list of members
	members = SharedCodeService.PHMembers.GetMembers(url)
	
	# Loop through all members
	for member in members:
		
		# Add a menu item for the member
		listMembersMenuItems[member["title"]] = {
			'function':			MemberMenu,
			'functionArgs':			{'url': BASE_URL + member["url"], 'username':member["title"]},
			'directoryObjectArgs':	{'thumb': member["thumbnail"]}
		}
	
	# There is a slight change that this will break... If the number of members returned in total is divisible by pageLimit with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(members) == int(pageLimit)):
		listMembersMenuItems['Next Page'] = {'function':ListMembers, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1, 'pageLimit':int(pageLimit)}, 'nextPage':True}
	
	return GenerateMenu(title, listMembersMenuItems)

@route(ROUTE_PREFIX + '/members/search')
def SearchMembers(query):
	
	# Format the query for use in PornHub's search
	formattedQuery = SharedCodeService.PHCommon.FormatStringForSearch(query, "+")
	
	try:
		return ListMembers(title='Search Results for ' + query, url=PH_SEARCH_MEMBERS_URL % formattedQuery)
	except:
		return ObjectContainer(header='Search Results', message="No search results found", no_cache=True)

@route(ROUTE_PREFIX + '/members/menu')
def MemberMenu(title, url, username):
	
	# Get the HTML of the Member's spash page, as well as their Video and Playlist pages
	memberHTML =		HTML.ElementFromURL(url)
	
	# Create a dictionary of menu items
	memberMenuItems = OrderedDict([
		('Public Videos',			{'function':ListVideos,				'functionArgs':{'title':username + "'s Public Videos",			'url':url + '/videos/public'}}),
		('Favorite Videos',			{'function':ListVideos,				'functionArgs':{'title':username + "'s Favorite Videos",			'url':url + '/videos/favorites'}}),
		('Watched Videos',			{'function':ListVideos,				'functionArgs':{'title':username + "'s Watched Videos",			'url':url + '/videos/recent'}}),
		('Public Playlists',			{'function':ListPlaylists,				'functionArgs':{'title':username + "'s Public Playlists",		'url':url + '/playlists/public'}}),
		('Favorite Playlists',		{'function':ListPlaylists,				'functionArgs':{'title':username + "'s Favorite Playlists",		'url':url + '/playlists/favorites'}}),
		('Channels',				{'function':ListMemberChannels,			'functionArgs':{'title':username + "'s Channels",				'url':url + '/channels'}}),
		('Channel Subscriptions',		{'function':ListMemberSubscribedChannels,	'functionArgs':{'title':username + "'s Channel Subscriptions",	'url':url + '/channel_subscriptions'}}),
		('Porn Star Subscriptions',	{'function':ListMemberSubscribedPornStars,	'functionArgs':{'title':username + "'s Porn Star Subscriptions",	'url':url + '/pornstar_subscriptions'}}),
		('Subscribers',				{'function':ListMembers,				'functionArgs':{'title':username + "'s Subscribers",			'url':url + '/subscribers',			'pageLimit':PH_MAX_MEMBERS_PER_MEMBER_SUBSCRIBERS_PAGE}}),
		('Member Subscriptions',		{'function':ListMembers,				'functionArgs':{'title':username + "'s Member Subscriptions",		'url':url + '/subscriptions',			'pageLimit':PH_MAX_MEMBERS_PER_MEMBER_SUBSCRIPTIONS_PAGE}}),
		('Friends',				{'function':ListMembers,				'functionArgs':{'title':username + "'s Friends",				'url':url + '/friends',				'pageLimit':PH_MAX_MEMBERS_PER_MEMBER_FRIENDS_PAGE}})
	])
	
	# This dictionary will hold the conditons on which we want to display Member menu options
	memberMenuChecks = {
		"Public Videos": {
			"xpath":		"//section[@id='profileVideos']//ul[contains(@class,'videos')]/li[contains(@class,'videoblock')]",
			"htmlElement":	memberHTML
		},
		"Favorite Videos":		None,
		"Watched Videos":		None,
		"Public Playlists": {
			"xpath":		"//section[@id='playlistsSidebar']//ul[contains(@class,'user-playlist')]/li[contains(@id,'playlist_')]",
			"htmlElement":	memberHTML
		},
		"Favorite Playlists":	None,
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
	
	# These overrides perform a more accurate check, however they all require an extra HTTP request
	memberMenuPreferenceOverrides =	{
		"memberMenuAccurateVideos": {
			'urlSuffix':	'/videos',
			'checks':		[
				{'key':'Public Videos',		'xpath':"//section[@id='videosTab']//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Public']"},
				{'key':'Favorite Videos',		'xpath':"//section[@id='videosTab']//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Favorites']"},
				{'key':'Watched Videos',		'xpath':"//section[@id='videosTab']//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Watched']"}
			]
		},
		"memberMenuAccuratePlaylists": {
			'urlSuffix':	'/playlists',
			'checks':		[
				{'key':'Public Playlists',	'xpath':"//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Public']"},
				{'key':'Favorite Playlists',	'xpath':"//nav[contains(@class,'sectionMenu')]/ul/li/a[text()='Favorites']"}
			]
		},
		"memberMenuAccurateSubscribers": {
			'urlSuffix':	'/subscribers',
			'checks':		[
				{'key':'Subscribers',		'xpath':"//ul[contains(@class, 'userWidgetWrapperGrid')]/li"}
			]
		},
		"memberMenuAccurateMemberSubscriptions": {
			'urlSuffix':	'/subscriptions',
			'checks':		[
				{'key':'Member Subscriptions',	'xpath':"//ul[contains(@class, 'userWidgetWrapperGrid')]/li"}
			]
		},
		"memberMenuAccurateFriends": {
			'urlSuffix':	'/friends',
			'checks':		[
				{'key':'Friends',			'xpath':"//ul[contains(@class, 'userWidgetWrapperGrid')]/li"}
			]
		}
	}
	
	# Loop through Preference overrides
	for key in memberMenuPreferenceOverrides:
		# Check to see if the Preference is set
		if (Prefs[key]):
			# Get the HTML of the page
			memberMenuPreferenceOverrideHTML = HTML.ElementFromURL(url + memberMenuPreferenceOverrides[key]["urlSuffix"])
			
			# Loop through the checks
			for check in memberMenuPreferenceOverrides[key]["checks"]:
				# Override the menu check
				memberMenuChecks[check['key']] = {
					"xpath":		check['xpath'],
					"htmlElement":	memberMenuPreferenceOverrideHTML
				}
	
	# Loop through Member menu option conditons
	for key in memberMenuChecks:
		# Make sure the check exists
		if (memberMenuChecks[key] is not None):
			# Attempt to get the element from the page
			elements = memberMenuChecks[key]["htmlElement"].xpath(memberMenuChecks[key]["xpath"])
			
			if (len(elements) == 0):
				# If no elements are found, do not display the Member menu option
				del memberMenuItems[key]
		else:
			del memberMenuItems[key]
	
	return GenerateMenu(title, memberMenuItems, no_cache=True)

@route(ROUTE_PREFIX + '/members/channels')
def ListMemberChannels(url, title="Member Channels", page=1):
	
	# Create a dictionary of menu items
	memberChannelMenuItems = OrderedDict()
	
	# Add the page number into the query string
	if (int(page) != 1):
		url = SharedCodeService.PHCommon.AddURLParameters(url, {'page':str(page)})
	
	# Get list of channels
	channels = SharedCodeService.PHMembers.GetMemberChannels(url)
	
	for channel in channels:
		
		# Add a menu item for the channel
		memberChannelMenuItems[channel["title"]] = {
			'function':			BrowseVideos,
			'functionArgs':			{'url': BASE_URL + channel["url"], 'title':channel["title"]},
			'directoryObjectArgs':	{'thumb': channel["thumbnail"]}
		}
	
	# There is a slight change that this will break... If the number of Channels returned in total is divisible by PH_MAX_MEMBER_CHANNELS_PER_PAGE with no remainder, there could possibly be no additional page after. This is unlikely though and I'm too lazy to handle it.
	if (len(channels) == PH_MAX_MEMBER_CHANNELS_PER_PAGE):
		memberChannelMenuItems['Next Page'] = {'function':ListMemberChannels, 'functionArgs':{'title':title, 'url':url, 'page':int(page)+1}, 'nextPage':True}
	
	return GenerateMenu(title, memberChannelMenuItems)

@route(ROUTE_PREFIX + '/members/channels/subscribed')
def ListMemberSubscribedChannels(url, title="Member's Subscribed Channels"):
	
	# Create a dictionary of menu items
	memberSubscribedChannelMenuItems = OrderedDict()
	
	# Get list of channels
	channels = SharedCodeService.PHMembers.GetMemberSubscribedChannels(url)
	
	for channel in channels:
		
		# Add a menu item for the Channel
		memberSubscribedChannelMenuItems[channel["title"]] = {
			'function':			BrowseVideos,
			'functionArgs':			{'url': BASE_URL + channel["url"], 'title':channel["title"]},
			'directoryObjectArgs':	{'thumb': channel["thumbnail"]}
		}
	
	return GenerateMenu(title, memberSubscribedChannelMenuItems)

@route(ROUTE_PREFIX + '/members/pornstars')
def ListMemberSubscribedPornStars(url, title="Member's Subscribed Porn Stars"):
	
	# Create a dictionary of menu items
	memberSubscribedPornStarsMenuItems = OrderedDict()
	
	# Get list of porn stars
	pornStars = SharedCodeService.PHMembers.GetMemberSubscribedPornStars(url)
	
	for pornStar in pornStars:
		
		# Add a menu item for the Porn Star
		memberSubscribedPornStarsMenuItems[pornStar["title"]] = {
			'function':			BrowseVideos,
			'functionArgs':			{'url': BASE_URL + pornStar["url"], 'title':pornStar["title"]},
			'directoryObjectArgs':	{'thumb': pornStar["thumbnail"]}
		}
	
	return GenerateMenu(title, memberSubscribedPornStarsMenuItems)