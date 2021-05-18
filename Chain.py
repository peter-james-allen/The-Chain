import requests, base64, os, io
from flask import Flask, request, render_template

import matplotlib.pyplot as plt
import networkx as nx

from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

app = Flask(__name__)
app.config["DEBUG"] = True

class SpotifyAPI:
	def __init__(self):
		#Credentials
		self.clientId = CLIENT_ID
		self.clientSecret = CLIENT_SECRET
		self.token = self.get_token()
	
	def get_token(self):
		# Step 1 - Authorization 
		url = "https://accounts.spotify.com/api/token"
		headers = {}
		data = {}
		
		# Encode as Base64
		message = f"{self.clientId}:{self.clientSecret}"
		messageBytes = message.encode('ascii')
		base64Bytes = base64.b64encode(messageBytes)
		base64Message = base64Bytes.decode('ascii')
		
		# Make Request
		headers['Authorization'] = f"Basic {base64Message}"
		data['grant_type'] = "client_credentials"
		r = requests.post(url, headers=headers, data=data)
		
		token = r.json()['access_token']
		
		return token
	
	def search(self,artist):
		headers = {"Authorization": "Bearer " + self.token}
		params={ 'q': artist, 'type': 'artist' }
		searchUrl = 'https://api.spotify.com/v1/search'

		res = requests.get(url=searchUrl, headers=headers, params=params).json()
		
		s_res ={}
		
		for r in res['artists']['items']:
			s_res[r['name']] = r['id']
		
		return s_res
	
	def find_related(self,artistId):
		artistUrl = f"https://api.spotify.com/v1/artists/{artistId}/related-artists"
		headers = {"Authorization": "Bearer " + self.token}
		
		res = requests.get(url=artistUrl, headers=headers).json()

		related_dic = {}
		
		for r in res['artists']:
			related_dic[r['id']] = r['name']
		
		return related_dic
		
class Artist:
	def __init__(self, string):
		
		self.name = string.split("_")[1]
		self.id = string.split("_")[0]
		self.related = SpotifyAPI().find_related(self.id)
		self.related_keys = list(self.related.values())
# 		self.related_keys.sort()
		self.series = [self.id,self.name] + self.related_keys
		self.edges = [[self.name,x] for x in self.related.values()]
		
class Graph:
	def __init__(self,edges):
		return
	
	def savePlot(edges):
		G = nx.Graph()
		for edge in edges:
			G.add_edge(edge[0], edge[1])
		
		pos = nx.spring_layout(G)
		nx.draw(G, pos, font_size=8, with_labels=False)
		
		for p in pos:  # raise text positions
			pos[p][1] += 0.07
		nx.draw_networkx_labels(G, pos)
		
		plt.savefig("./images/{}.png".format(edges[0][1]), format="PNG")
		
		with open("./images/{}.png".format(edges[0][0]), "rb") as img_file:
			my_string = base64.b64encode(img_file.read()).decode('utf8')
		
		return my_string
		
#Home Page
@app.route('/', methods=['GET'])
def homePage():
	return render_template('Home.html')

#Search Page
@app.route('/artists', methods=['GET'])
def searchPage():
	s = request.args.get('artist')
	print(s)
	related = SpotifyAPI().search(s)
	return render_template('Artists.html', search = s, artists = related)

#Related Page
@app.route('/related', methods=['GET'])
def relatedPage():
	artist = request.args.get('chosen')
	counter = request.args.get('loops')
	
	a = Artist(artist)
	edges = a.edges
	print(a.related)
	for key, value in a.related.items():
		print("{}_{}".format(key,value))
		edges += Artist("{}_{}".format(key,value)).edges
		 
		
	rel = Artist(artist)
#	rel_artists = rel.related
	
#	edges = 
	
# 	while counter > 0:
# 		edges = edges + Artist(artist)
# 		counter -= 1
		
	a = artist.split("_")[1]
	pngImageB64String = "data:image/png;base64,{}".format( Graph.savePlot(edges))
		
	return render_template('Related.html', chosen = a, related = rel.related_keys, image = pngImageB64String)

app.run()
