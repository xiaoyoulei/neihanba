# -*- coding: utf-8 -*-
import urllib2
import hashlib
import pymongo
import time
from bs4 import BeautifulSoup


class MongoStruct:
	conn = None
	mydb = None
	mytable = None
	def init(self):
		self.conn = pymongo.Connection('192.168.2.5',27017)
		self.mydb = self.conn.neihanba
		self.mytable = self.mydb.text
	def insert(self, data, insertnum):
		if self.mytable.find({"id":data["id"]}).count() == 0:
			insertnum += 1
			self.mytable.insert(data)



def work(url, ansarr) :
	res = urllib2.urlopen(url).read().decode('GB18030')
	context = BeautifulSoup(res)
	pp = context.findAll('p')
	titles = context.select('.title')
	datas = context.select('.con')
	if len(titles) != len(datas):
		return
	index = -1 # be careful about -1
	while index < len(titles)-1:
		index += 1
		item = {}
		item["title"] = titles[index].text.strip()
		item["id"] = hashlib.md5(item["title"].encode('utf-8')).hexdigest()
		if datas[index].img != None:
			continue
		datatmp = datas[index].getText(separator="||").split("||")
		if len(datatmp) >= 5 :
			item["data"] = ''.join(datatmp[5:-1])
		else :
			continue
		if len(item["title"]) == 0 or len(item["data"]) == 0:
			continue
		item["time"] = int(time.time())
		ansarr.append(item)

def main():
	mongo = MongoStruct()
	mongo.init()
	insertnum = 0
	allindex = 0
	index = 20
	while index > 1 :
		index -= 1
		ansarr = []
		url = "http://m.neihan8.com/article/list_5_"+str(index)+".html"
		print "start @ [%s] index[%d] insert[%d]"%(url, allindex, insertnum)
		work(url,ansarr)
		for item in ansarr :
			mongo.insert(item, insertnum)
			allindex += 1
		#	print "id[%s] \ntitle [%s] \ndata[%s]"%(item["id"],item["title"].encode('utf-8'), item["data"].encode('utf8'))

if __name__ == "__main__" :
	main()
