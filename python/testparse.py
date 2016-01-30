#! C:/Python34/python
# -*- coding: UTF-8 -*-

import urllib.request
import http.client
import shutil

# www.admoblkaluga.ru/upload/minsds/pdn/13.doc
http_proxy = '172.16.125.102:3128'

def get_file(url, out_file):
	proxy_handler = urllib.request.ProxyHandler({'http': http_proxy})
	opener = urllib.request.build_opener(proxy_handler)
	with opener.open(url) as response, open(file_name, 'wb') as out_file:
		html = response.read(10)
		if html != b'\xef\xbb\xbf<!DOCTY' :
			print('file!')
			shutil.copyfileobj(response, out_file)
			
	# # Download the file from `url` and save it locally under `file_name`:
	# with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		# shutil.copyfileobj(response, out_file)
	

	
if __name__ == '__main__':
	for i in range(100):
		url = "http://www.admoblkaluga.ru/upload/minsds/pdn/%s.doc" % i
		file_name = "file_%s.doc" % i 
		print(url)
		get_file(url,file_name)

			
	
	# print(response.read())
	
	# with urllib.request.urlopen('http://python.org/') as response:
		# html = response.read()
		# html
		# try: urllib.request.urlopen(req).decode('utf-8')
# ... except urllib.error.URLError as e:
# ...    print(e.reason).decode('utf-8')
