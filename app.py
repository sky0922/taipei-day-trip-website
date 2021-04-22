from flask import *
import pymysql, os
from dotenv import load_dotenv
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
newDatabaseName = "tpetravel"

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

def connect_mysql():  
    global connect, cursor 
    connect = pymysql.connect(host = MYSQL_HOST, db = newDatabaseName, user = MYSQL_USER, password = MYSQL_PASS,
            charset = 'utf8', use_unicode = True, cursorclass = pymysql.cursors.DictCursor)
    cursor = connect.cursor()



# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")



# API 用 ID 抓景點資料
@app.route("/api/attraction/<attractionId>")
def api_attraction(attractionId):

	#先確認資料是否為 0 以上的整數
	if attractionId.isdigit():
		connect_mysql()
		selectsql = "select id, name, category, description, address, transport, mrt, latitude, longitude from tpelocation where id = '%s'"  %(attractionId)
		cursor.execute(selectsql)
		selectDB = cursor.fetchone()

		if selectDB != None:
			#抓資料庫內圖片網址資料
			selectURL = "select src from image where id = '%s'" %(attractionId)
			cursor.execute(selectURL)
			imageURL = cursor.fetchall()

			# print ("看圖片 URL", type(imageURL), imageURL[0]["src"])
			# for i in imageURL:
			# 	print (i["src"])
			# 這個 for 迴圈 用一行來寫就是 [i["src"] for i in imageURL]

			data = {
					"data": {
					"id": selectDB["id"],
					"name": selectDB["name"],
					"category": selectDB["category"],
					"description": selectDB["description"],
					"address": selectDB["address"],
					"transport": selectDB["transport"],
					"mrt": selectDB["mrt"],
					"latitude": selectDB["latitude"],
					"longitude": selectDB["longitude"],
					"images": ["http://"+i["src"] for i in imageURL]
            		}
        		}
			return jsonify(data)
		else:
			return jsonify({"error": True, "message": "錯誤：該景點編號沒有資料"})
	else:
		return jsonify({"error": True, "message": "錯誤：資料型態不正確"})

# API 關鍵字 抓景點資料 及 分頁效果




@app.route("/api/attractions")
def attractions():

	page = request.args.get("page")
	keyword = request.args.get("keyword", None)
	data = []

	if page.isdigit():
	
		#無關鍵字，第 0 頁，直接篩出前面 12 筆
		if keyword == None and page == "0":
			connect_mysql()
			selectsql = "select id, name, category, description, address, transport, mrt, latitude, longitude from tpelocation limit %d, %d" %(int(page), int(page)+11) 
			cursor.execute(selectsql)
			selectDB = cursor.fetchall()

			for iiiii in selectDB:				
				selectURL = "select src from image where id = '%s'" %(iiiii["id"])
				cursor.execute(selectURL)
				imageURL = cursor.fetchall()
				
				data.append(
					{
						"id": iiiii["id"],
						"name": iiiii["name"],
						"category": iiiii["category"],
						"description": iiiii["description"],
						"address": iiiii["address"],
						"transport": iiiii["transport"],
						"mrt": iiiii["mrt"],
						"latitude": iiiii["latitude"],
						"longitude": iiiii["longitude"],
						"images": ["http://"+i["src"] for i in imageURL]
						}
				)

			return jsonify({"nextPage": int(page)+1, "data": data})

		if keyword == None and page != "0":

			connect_mysql()
			selectsql = "select id, name, category, description, address, transport, mrt, latitude, longitude from tpelocation limit %d, %d" %(int(page)*12, int(page)*12+11) 
			cursor.execute(selectsql)
			selectDB = cursor.fetchall()

			for iiiii in selectDB:				
				selectURL = "select src from image where id = '%s'" %(iiiii["id"])
				cursor.execute(selectURL)
				imageURL = cursor.fetchall()
				
				data.append(
					{
						"id": iiiii["id"],
						"name": iiiii["name"],
						"category": iiiii["category"],
						"description": iiiii["description"],
						"address": iiiii["address"],
						"transport": iiiii["transport"],
						"mrt": iiiii["mrt"],
						"latitude": iiiii["latitude"],
						"longitude": iiiii["longitude"],
						"images": ["http://"+i["src"] for i in imageURL]
						}
				)

			return jsonify({"nextPage": int(page)+1, "data": data})

		# 	return "無關鍵字，有頁數，篩出 12 筆資料"
			
		# if keyword != None and page == 0:
		# 	return "keyword != None and page == 0"

		# if keyword != None and page != 0:
		# 	return "keyword != None and page != 0"

		# lastitem = page * 12
		# firstitem = lastitem - 11 
	else:
		return jsonify({"error": True, "message": "錯誤：頁數資料型態不正確"})





@app.errorhandler(404)
def error404(error):
    return jsonify({"error": True, "message": "找不到網頁..."})

@app.errorhandler(500)
def error404(error):
    return jsonify({"error": True, "message": "網站異常中..."})


app.run(host="127.0.0.1", port=3000, debug=True)