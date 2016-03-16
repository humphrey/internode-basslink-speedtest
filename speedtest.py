"""
Simple (and terribly coded) internet speed test.
"""
# SET THESE
github_auth = ('your-github-username', 'your-github-auth-token-thing')
file_size = 3062059
file_url = 'http://d13pl105ykjs4s.cloudfront.net/images/storm_3mb.jpg'
# file_url = 'http://d13pl105ykjs4s.cloudfront.net/images/pinball_9mb.jpg'
# file_url = 'http://speedcheck.cdn.on.net/10meg.test'

import csv
import requests
import json
import base64
from datetime import datetime


# Open the existing results, and read into memory, so that we can add to it
f = open('speedtest-results.csv', 'r')
rd = csv.reader(f)
rows = [r for r in rd]
f.close()

# Download the file
file_size_mb = file_size / 1024.0 / 1024.0
print 'Downloading %.3fMb file from from AWS Cloudfront Sydney...' % file_size_mb
a = datetime.now()
r = requests.get(file_url + '?t=' + unicode(datetime.now()))
b = datetime.now()

# Calculate Speed
c = b - a
data = [unicode(a), c.total_seconds(), '%s' % round(file_size / c.total_seconds() / 1024 * 8), file_size]
print 'Successfully downloaded %.3fMb file from AWS Cloudfront Sydney at %s kbps' % (file_size_mb, data[2])

# Add to our list of tests
rows.append(data)

# Write to CSV File
f = open('speedtest-results.csv', 'w')
wr = csv.writer(f, lineterminator='\n')
wr.writerows(rows)
f.close()
f = open('speedtest-results.csv', 'r')
data_as_csv = f.read()
f.close()

# Read JSON File
f = open('speedtest-results.json', 'r')
items = json.loads(f.read() or '[]')
items.append({
	'timestamp': data[0],
	'seconds': data[1],
	'mbps': data[2],
	'filesize': data[3],
})
f.close()
f = open('speedtest-results.json', 'w')
data_as_json = json.dumps(items)
f.write(data_as_json)
f.close()

print 'Uploading JSON file to Github...'
github_path = 'https://api.github.com/repos/humphrey/internode-basslink-speedtest/contents/home-data.json'
r = requests.put(github_path, auth=github_auth, data=json.dumps({
	'message': 'New Data: {} (JSON)'.format(unicode(data)),
	'content': base64.b64encode(data_as_json),
	'sha': requests.get(github_path, auth=github_auth).json()['sha'],
	'path': 'data.json',
	'branch': 'gh-gages',
}))

print 'Uploading CSV file to Github...'
github_path = 'https://api.github.com/repos/humphrey/internode-basslink-speedtest/contents/home-data.csv'
r = requests.put(github_path, auth=github_auth, data=json.dumps({
	'message': 'New Data: {} (CSV)'.format(unicode(data)),
	'content': base64.b64encode(data_as_csv),
	'sha': requests.get(github_path, auth=github_auth).json()['sha'],
	'path': 'data.csv',
	'branch': 'gh-pages',
}))

grouped = {}
for item in items:
	# 2016-03-16 11:06:00.181000
	ts = item['timestamp']
	key = ts[:14] + ('15' if int(ts[14]) in [0,1,2] else '45')
	grouped.setdefault(key, []).append(float(item['mbps']))

averaged = []
for key in sorted(grouped.keys()):
	averaged.append([key, int(sum(grouped[key]) / len(grouped[key]))])

print 'Uploading Graph JSON file to Github...'
github_path = 'https://api.github.com/repos/humphrey/internode-basslink-speedtest/contents/home-data-smoothed.json'
r = requests.put(github_path, auth=github_auth, data=json.dumps({
	'message': 'New Data: {} (JSON)'.format(unicode(data)),
	'content': base64.b64encode(json.dumps(averaged, indent=2)),
	'sha': requests.get(github_path, auth=github_auth).json()['sha'],
	'path': 'data.json',
	'branch': 'gh-pages',
}))

print 'All Done!'
