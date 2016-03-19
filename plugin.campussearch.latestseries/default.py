import xbmc, xbmcgui, xbmcplugin
import urllib, os
from xml.dom.minidom import parse




#listings

def listLatestSeries():
	url = "http://search.student.utwente.nl/api/feeds?feed=recent-tv-shows"
	try:
		feed = urllib.urlopen(url)
		dom = parse(feed)	
	except Exception:
		message("Could not reach CampusSearch!")
	#for loop
	for node in dom.getElementsByTagName('tv-show'):
		serie 		= node.getElementsByTagName('title')[0].firstChild.nodeValue.encode('ascii', 'replace')
		title	 	= node.getElementsByTagName('episode_name')[0].firstChild.nodeValue.encode('ascii', 'replace')
		season	 	= node.getElementsByTagName('season')[0].firstChild.nodeValue.encode('ascii', 'replace')
		episode 	= node.getElementsByTagName('episode')[0].firstChild.nodeValue.encode('ascii', 'replace')
		aired	 	= node.getElementsByTagName('aired_on')[0].firstChild.nodeValue.encode('ascii', 'replace')

		#still make us able to search, huray!		
		prefix		= ""

		try:		
			imdb		= node.getElementsByTagName('imdb_id')[0].firstChild.nodeValue
			identifier	= imdb+"+s"+season+"x"+episode
		except:
			identifier	= serie+"+s"+season+"x"+episode
#			prefix		= "!"
		
		print identifier
		name		= prefix+"["+aired+"] "+serie+" - "+title+" S"+season+"E"+episode+""
		mode		= "searcheps"
		icon		= ""
	        addDir(name,mode,identifier)

def listAllSeries():
	url = "http://search.student.utwente.nl/api/feeds?feed=all-tv-shows"
	try:
		feed = urllib.urlopen(url)
		dom = parse(feed)	
	except Exception:
		message("Could not reach CampusSearch!")
	#for loop
	for node in dom.getElementsByTagName('tv-show'):
		try:		
			serie 		= node.getElementsByTagName('title')[0].firstChild.nodeValue.encode('ascii', 'replace')
			imdb		= node.getElementsByTagName('imdb_id')[0].firstChild.nodeValue.encode('ascii', 'replace')

			name		= serie
			mode		= "serieeps"
			identifier	= imdb
			addDir(name,mode,identifier)
		except:
			print "campussearch: NO_IMDB serie: "+serie

def listSerie(identifier):
	url = "http://search.student.utwente.nl/api/feeds?feed=tv-show-eps&imdb_id="+identifier #"tt0904208"
	try:
		feed = urllib.urlopen(url)
		dom = parse(feed)	
	except Exception:
		message("Could not reach CampusSearch!")
	#for loop
	for node in dom.getElementsByTagName('tv-show'):
		try:
			title	 = node.getElementsByTagName('episode_name')[0].firstChild.nodeValue.encode('ascii', 'replace')
		except:
			title	= "Geen titel"

		serie 		= node.getElementsByTagName('title')[0].firstChild.nodeValue.encode('ascii', 'replace')
		season	 	= node.getElementsByTagName('season')[0].firstChild.nodeValue.encode('ascii', 'replace')
		episode 	= node.getElementsByTagName('episode')[0].firstChild.nodeValue.encode('ascii', 'replace')
		aired	 	= node.getElementsByTagName('aired_on')[0].firstChild.nodeValue.encode('ascii', 'replace')
		imdb		= node.getElementsByTagName('imdb_id')[0].firstChild.nodeValue.encode('ascii', 'replace')

		prefix	= "";

		if season == "0" or episode == "0":
			identifier	= imdb
			prefix		= "!"
		else:		
			identifier	= imdb+"+s"+season+"x"+episode

		name		= prefix+"["+aired+"] "+serie+" - "+title+" S"+season+"E"+episode+""
		mode		= "searcheps"
		addDir(name,mode,identifier)


def searchEps(identifier):
	url = "http://search.student.utwente.nl/api/search?q=" + identifier.replace(" ", "+") 
	try:
		feed = urllib.urlopen(url)
		dom = parse(feed)	
	except Exception:
		message("Could not reach CampusSearch!")
	#for loop
	for node in dom.getElementsByTagName('result'):
		#online nodes
		if node.getElementsByTagName('online')[0].firstChild.nodeValue == 'yes':
			name	= node.getElementsByTagName('name')[0].firstChild.nodeValue.encode('ascii', 'replace')	
			path	= node.getElementsByTagName('full_path')[0].firstChild.nodeValue	
			size	= node.getElementsByTagName('size')[0].firstChild.nodeValue	
			server	= node.getElementsByTagName('netbios_name')[0].firstChild.nodeValue	
			name	= name
			url	= path

			if node.getElementsByTagName('type')[0].firstChild.nodeValue == 'file':
				addLink(name,url)
			else:
				traversedir(url)

def HOME():
        addDir("Laatste Eps","recenteps","")
        addDir("Alle Series","alleps","")

#helpers

def message(text):
	dialog = xbmcgui.Dialog()
	dialog.ok("Error", text)

def addDir(name,mode,identifier):
        u=sys.argv[0]+"?mode="+urllib.quote_plus(mode)+"&identifier="+urllib.quote_plus(identifier)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="")
        liz.setInfo( type="Video", infoLabels={"title":name} )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage="")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=False)
        return ok

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def traversedir(path):
	print path	
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
			url = sys.argv[0] + "?mode=traverse&identifier=" + url + "/"
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,liz,isFolder=True)
		else:
			xbmcplugin.addDirectoryItem(int(sys.argv[1]),url,liz,isFolder=False)

# main

params=get_params()
name=None
mode=None
identifier=None

try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=urllib.unquote_plus(params["mode"])
except:
        pass
try:
        identifier=urllib.unquote_plus(params["identifier"])
except:
        pass

print "Mode: "+str(mode)
print "Identifier: "+str(identifier)
print "Name: "+str(name)

if mode==None:
        print "Action: HOME"
        HOME()
       
elif mode=="searcheps":
        print "Action: searcheps - "+identifier
        searchEps(identifier)
        
elif mode=="recenteps":
        print "Action: recenteps"
        listLatestSeries()
        
elif mode=="alleps":
        print "Action: alleps"
        listAllSeries()
        
elif mode=="serieeps":
        print "Action: serieeps - "+identifier
        listSerie(identifier)

elif mode=="traversedir":
        print "Action: traversedir - "+identifier
        traversedir(identifier)

else:
	print "No Action..."

xbmcplugin.endOfDirectory(int(sys.argv[1]))

#END

