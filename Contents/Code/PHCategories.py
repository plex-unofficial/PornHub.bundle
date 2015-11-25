from PHCommon import *

PH_CATEGORIES_URL =				BASE_URL + '/categories'
PH_CATEGORIES_ALPHABETICAL_URL =	PH_CATEGORIES_URL + '?o=al'

@route(ROUTE_PREFIX + '/categories')
def BrowseCategories(title, url = PH_CATEGORIES_ALPHABETICAL_URL):
	
	# Create the object to contain all of the categories
	oc = ObjectContainer(title2=title)
	
	# Get the HTML of the page
	html = HTML.ElementFromURL(url)
	
	# Use xPath to extract a list of catgegories
	categories = html.xpath("//div[@id='categoriesStraightImages']/ul[contains(@class, 'categories-list')]/li/div")
	
	# Loop through all categories
	for category in categories:
		
		categoryTitle =		category.xpath("./h5/a/strong/text()")[0]
		categoryURL =		BASE_URL + category.xpath("./h5/a/@href")[0]
		categoryThumbnail =	category.xpath("./a/img/@src")[0]
		
		# Add a Directory Object for the category
		oc.add(DirectoryObject(
			key =	Callback(SortVideos, title=categoryTitle, url=categoryURL),
			title =	categoryTitle,
			thumb =	categoryThumbnail
		))
	
	return oc