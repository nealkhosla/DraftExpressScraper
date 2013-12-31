from bs4 import BeautifulSoup
import urllib2
import csv
import time
import sys

year_urls = ['http://www.draftexpress.com/nba-draft-history/?syear=' + str(i) for i in range(2006,2014)]
player_urls = []

trial_player = 'http://www.draftexpress.com/profile/Andre-Drummond-5772/stats/'
trial_year = 'http://www.draftexpress.com/nba-draft-history/?syear=2012'

def identifySeniorSeason(table):
	rows = table.find_all('tr')
	for i, row in enumerate(rows):
		elements = row.find_all('td')
		if len(elements) > 1:
			if 'NBA' in elements[1].contents[0] or 'DLEAGUE' in elements[1].contents[0]:
				return i-1

def convertHeightToInches(next):
	height = int(next[0]) * 12
	pos = next.index('\'')
	height += float(next[pos+1:-1]) 
	return height

def getMeasurements(table, measurements):
	rows = table.find_all('tr')
	keys = []
	for row in rows:
		for r in row.find_all('td'):
			try:
				next = r.contents[0].encode('ascii', 'ignore')
				if '\'' in next:
					next = convertHeightToInches(next)
				else:
					next = float(next)
			except:
				next = -1
			measurements.append(next)
	return measurements

def writeBasicStats(table, index, data):
	rows = table.find_all('tr')
	college_stats = []
	for i, r in enumerate(rows[index].find_all('td')):
		if i > 2:
			try:
				college_stats.append(float(r.contents[0]))
			except:
				college_stats.append(0.0)
	data += college_stats
	rookie_stats = []
	for i, r in enumerate(rows[index + 1].find_all('td')):
		if i > 2:
			try:
				rookie_stats.append(float(r.contents[0]))
			except:
				rookie_stats.append(0.0)
	data += rookie_stats
	aggregate_stats = [0] * len(rookie_stats)
	for i, row in enumerate(rows):
		if i > index:
			try:
				games_played = int(row.find_all('td')[3].contents[0])
				aggregate_stats[0] += games_played

				for j, r in enumerate(row.find_all('td')):
					if j > 3:
						# print r.contents[0]
						try:
							aggregate_stats[j-3] += games_played * float(r.contents[0])
						except:
							aggregate_stats[j-3] += 0.0
			except:
				continue
	average_stats = [0] * len(aggregate_stats)
	for i, stat in enumerate(aggregate_stats):
		average_stats[i] = stat / aggregate_stats[0]
	data += average_stats
	
	return data

def createRowTitle(soup):
	title = soup.title.contents[0]
	pos1 = title.index(':') + 1
	pos2 = title.index(',')
	title = title[pos1:pos2].strip().encode('ascii', 'ignore')
	return [title]

def getSoup(url):
	c = urllib2.urlopen(url)
	contents = c.read()
	soup = BeautifulSoup(contents, 'lxml')
	return soup

def isTable(span_title):
	if span_title == 'Basic Statistics' or span_title == 'Basic Statistics Per 40 Pace Adjusted' or span_title == 'Efficiency Statistics' or span_title == 'Usage Statistics':
		return True
	return False

def getStats2(url):
	print url
	soup = getSoup(url)
	row = createRowTitle(soup)
	spans = soup.find_all('span', {'class': 'red_heading_large'})
	measurementTitle = soup.find('span', {'class': 'red_heading_bold'})
	with open('data3.csv', 'a') as f:
		try:
			row = getMeasurements(measurementTitle.parent.next_sibling, row)
		except:
			row  = row + ([-1] * 12)
		try:
			writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONE)
			for span in spans:
				if isTable(span.contents[0]):
					table = span.next_sibling.next_sibling.next_sibling
					index = identifySeniorSeason(table)
					if index:
						row = writeBasicStats(table, index, row)
					else:
						row = row + ([-1] * (241 - len(row)))
			writer.writerow(row)
		except Exception as e:
			print e
			print sys.exc_traceback.tb_lineno 
			writer.writerow(row)

	return row

def getLinks(url):
	c = urllib2.urlopen(url)
	contents = c.read()
	soup = BeautifulSoup(contents, 'lxml')
	links = soup.find_all('a')
	profiles = []
	for link in links:
		if 'profile' in link['href']:
			profiles.append('http://www.draftexpress.com/' + str(link['href']) + 'stats')
	return profiles

# getStats(trial_player)
for year in year_urls:
	for player_profile in getLinks(year):
		getStats2(player_profile)
		time.sleep(2)


