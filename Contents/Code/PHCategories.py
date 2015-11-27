from PHCommon import *

PH_CATEGORIES_URL =				BASE_URL + '/categories'
PH_CATEGORIES_ALPHABETICAL_URL =	PH_CATEGORIES_URL + '?o=al'

@route(ROUTE_PREFIX + '/categories')
def BrowseCategories(title=PH_DEFAULT_BROWSE_CATEGORIES_TITLE, url = PH_CATEGORIES_ALPHABETICAL_URL):
	
	# Create a dictionary of menu items
	browseCategoriesMenuItems = OrderedDict()
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of catgegories
	categories = html.xpath("//div[@id='categoriesStraightImages']/ul[contains(@class, 'categories-list')]/li/div")
	
	# Loop through all categories
	for category in categories:
		
		# Use xPath to extract category details
		categoryTitle =		category.xpath("./h5/a/strong/text()")[0]
		categoryURL =		BASE_URL + category.xpath("./h5/a/@href")[0]
		categoryThumbnail =	category.xpath("./a/img/@src")[0]
		
		# Add a menu item for the category
		browseCategoriesMenuItems[categoryTitle] = {'function':SortVideos, 'functionArgs':{'url':categoryURL}, 'directoryObjectArgs':{'thumb':categoryThumbnail}}
	
	return GenerateMenu(title, browseCategoriesMenuItems)