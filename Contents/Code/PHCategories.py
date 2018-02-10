from PHCommon import *

PH_CATEGORIES_URL =				BASE_URL + AREA + '/categories'
PH_CATEGORIES_ALPHABETICAL_URL =	PH_CATEGORIES_URL + '?o=al'

@route(ROUTE_PREFIX + '/categories')
def BrowseCategories(title=L("DefaultBrowseCategoriesTitle"), url = PH_CATEGORIES_ALPHABETICAL_URL):
	
	# Create a dictionary of menu items
	browseCategoriesMenuItems = OrderedDict()
	
	# Get list of categories
	categories = SharedCodeService.PHCategories.GetCategories(url)
	
	# Loop through all categories
	for category in categories:
		
		# Add a menu item for the category
		browseCategoriesMenuItems[category["title"]] = {
			'function':			BrowseVideos,
			'functionArgs':			{'url': BASE_URL + category["url"]},
			'directoryObjectArgs':	{'thumb': category["thumbnail"]}
		}
	
	return GenerateMenu(title, browseCategoriesMenuItems)