import pymongo
from tornado import template

class MongoStruct:
	conn = None
	mydb = None
	mytable = None
	def init(self):
		self.conn = pymongo.Connection('192.168.2.5',27017)
		self.mydb = self.conn.neihanba
		self.mytable = self.mydb.text
	def select(self, data):
		cursor = self.mytable.find().sort("time",pymongo.DESCENDING)
		index = 0
		while index < cursor.count() :
			data.append(cursor.next())
			index += 1


def work():
	mongo = MongoStruct()
	mongo.init()
	mongodata = []
	text_data = []
	mongo.select(mongodata)
	index = 0
	pagenum = 0
	fnow = None
	tplfile = open("./template/template.html")
	tpl = template.Template(tplfile.read())
	while index < len(mongodata):
		if index % 20 == 0:
			fnow = open("./data/text_"+str(pagenum)+".html", "w")
			data = {}
			data["pre"] = "/text_"+str(pagenum-1)+".html"
			data["next"] = "/text_"+str(pagenum+1)+".html"
			data["items"] = text_data
			fnow.write(tpl.generate(data=data))
			fnow.close()
			text_data = []
			pagenum += 1
			print "write %d"%(pagenum)

		text_data.append(mongodata[index])
		index += 1
			
def main():
	work()


if __name__ == "__main__":
	main()
