import xbmc, xbmcgui, xbmcplugin
import urllib, os
from xml.dom.minidom import parse



def message(text):
	dialog = xbmcgui.Dialog()
	dialog.ok("Error", text)

def getMovieName():
		keyboard = xbmc.Keyboard('','Wat zoek je?')
		keyboard.doModal()	
		if (keyboard.isConfirmed()):
			return keyboard.getText()		

def getResults(film,category,minSize,maxSize):
	wantedKeywords = [[''],['avi','mov','wmv','iso','img','mp4','mkv'],['avi','mkv'],['mkv']]
	notWantedKeywords = ["1080p", "1080i"]
	unwantedKeywordFound = 0
	wantedKeywordFound = 0
	found = 0
	
	film  = film.replace(" ", "+")
	filmUrl = "http://search.student.utwente.nl/api/search?q=" + film + "&page=0&dirsonly=no&n=100&minsize="+minSize+"m&maxsize="+maxSize+"m"
	try:
		feed = urllib.urlopen(filmUrl)
		dom = parse(feed)	
	except Exception:
		message("Could not reach CampusSearch!")
	#check through all the <result>	
	for node in dom.getElementsByTagName('result'):
		#only take those which are online!
		if node.getElementsByTagName('online')[0].firstChild.nodeValue == 'yes':

			# we dont want bluray or any orther HD movie, the xbox cannot play it!
			for keyword in notWantedKeywords:
				if node.getElementsByTagName('full_path')[0].firstChild.nodeValue.find(keyword) != -1 or node.getElementsByTagName('name')[0].firstChild.nodeValue.find(keyword) != -1:
					unwantedKeywordFound = 1		

			#check catagorie
			for keyword in wantedKeywords[category]:
				if node.getElementsByTagName('full_path')[0].firstChild.nodeValue.find(keyword) != -1 or node.getElementsByTagName('name')[0].firstChild.nodeValue.find(keyword) != -1:
					wantedKeywordFound = 1	
	
			if (unwantedKeywordFound == 0) and (wantedKeywordFound == 1):       
				# okay, everything seems clear, now lets get rid of the directories, we only want the files!
				#if node.getElementsByTagName('full_path')[0].firstChild.nodeValue.endswith(".avi") or node.getElementsByTagName('full_path')[0].firstChild.nodeValue.endswith(".mp4"):
				addDir(node.getElementsByTagName('name')[0].firstChild.nodeValue, node.getElementsByTagName('full_path')[0].firstChild.nodeValue, '')
				found = 1
			unwantedKeywordFound = 0
			wantedKeywordFound = 0	
	xbmcplugin.endOfDirectory(int(sys.argv[1]), 1)			
	if found != 1:
		message("nothing found!")		

def addDir(name,path,iconimage):
	#root level, we only want the files or directories from the search results, not what is inside the folders
	if name != '':
		isDir = os.path.isdir(path)
		liz=xbmcgui.ListItem(name,'')
		#os.path.isdir does apparently not work for samba shares, so dirty hack has to be applied :)
		#if isDir:
		if path[len(path) - 4] != ".":
			url = sys.argv[0] + "?path=" + path + "/"
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,liz,isDir)
		else:
#			xbmcplugin.addDirectoryItem(int(sys.argv[1]),path,liz)
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),path,liz,isFolder=False)
	else:
		# os.listdir also does not work with samba shares, using xbmc httpapi as a workaround
		#folderContents = os.listdir(path)
		response = xbmc.executehttpapi("GetDirectory(" + path + ")")
		# remove <li> tags
		response = response.replace("<li>", "")
		# we only want the directories and files, so remove the absolute network path
		response = response.replace(path, "")
		# also "dir/" has to be just "dir"
		response = response.replace("/", "")
		# first token is a newline, we do not want that
		response = response.replace("\n", "", 1)
		# we split at each newline, so that we have a list of dirs & files
		folderContents = response.split('\n')
		for entries in folderContents:
			url = os.path.join(path,entries)
			#url = path + entries
			isDir = os.path.isdir(url)
			liz=xbmcgui.ListItem(entries,'')
			if isDir:
				url = sys.argv[0] + "?path=" + url + "/"
				xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,liz,isDir)
			else:
#				xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,liz)
				xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,liz)
		xbmcplugin.endOfDirectory(int(sys.argv[1]), 1)	
	return (0)

if ((len(sys.argv) == 3) and (cmp (sys.argv[2][0:6],"?path=") == 0)):
	addDir('', sys.argv[2][6:], '')
else:
	movieName 	= ''
	movieName 	= getMovieName()

	if movieName is not None:

		category	= 2
		catTypes	= ['alles','video (avi,mov,wmv,iso,img,mp4,mkv)','beschaafde formaten (avi,mkv)','hardcore HD (mkv)']
#		catTypes	= ['alles','video','audio']

		minSizeTypes	= ['600','600','600','600']
		minSize		= minSizeTypes[category]

		maxSizeTypes	= ['6000','6000','6000','6000']
		maxSize		= maxSizeTypes[category]

		if xbmcgui.Dialog().yesno('Mierenneuken? Specifieker dan dit:','Type: '+catTypes[category], 'Formaat: '+minSize+'M tot '+maxSize+'M','(En ik flikker 1080 er sowieso uit!)'):

			category 	= xbmcgui.Dialog().select('Category',catTypes)
			if category == -1: category = 0	

			minSize	  	= xbmcgui.Dialog().numeric(0,'Minimale grootte (M)',minSizeTypes[category])
			if minSize is None: minSize = '0'

			maxSize	  	= xbmcgui.Dialog().numeric(0,'Maximale grootte (M)',maxSizeTypes[category])
			if maxSize is None: maxSize = '100000'
		
		getResults(movieName,category,minSize,maxSize)

