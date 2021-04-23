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
	#這邊是用 uid 來找景點，uid 是資料存入系統後自動產生的序號，id 則是原始 json 資料 _id 值
	#兩個資料表的 id 欄位存的都是 _id 的值，所以用 id 欄位來對照就可以抓到對應圖片
	if attractionId.isdigit():
		connect_mysql()
		selectsql = "select * from tpelocation where uid = '%s'"  %(attractionId)
		cursor.execute(selectsql)
		selectDB = cursor.fetchone()

		if selectDB != None:
			#抓資料庫內圖片網址資料
			selectURL = "select src from image where id = '%s'" %(selectDB["id"])
			cursor.execute(selectURL)
			imageURL = cursor.fetchall()

			# print ("看圖片 URL", type(imageURL), imageURL[0]["src"])
			# for i in imageURL:
			# 	print (i["src"])
			# 這個 for 迴圈 用一行來寫就是 [i["src"] for i in imageURL]

			data = {
					"data": {
					"id": selectDB["uid"],
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
	
		#無關鍵字，有頁數，抓出資料庫對應資料
		#若沒有下一頁，nextPage 會變成空值
		if keyword == None:
			connect_mysql()
			selectsql = "select * from tpelocation limit %d, %d" %(int(page)*12, 12) 
			cursor.execute(selectsql)
			selectDB = cursor.fetchall()

			if selectDB == ():
				return jsonify({"error": True, "message": "錯誤：該分頁已無資料"})

			# count 這個變數主要是要計算 fetchall 出來數量是多少，如果少於 12 代表沒有下一頁
			count = 0
			for eachdata in selectDB:				
				selectURL = "select src from image where id = '%s'" %(eachdata["id"])
				cursor.execute(selectURL)
				imageURL = cursor.fetchall()
				
				data.append(
					{
						"id": eachdata["uid"],
						"name": eachdata["name"],
						"category": eachdata["category"],
						"description": eachdata["description"],
						"address": eachdata["address"],
						"transport": eachdata["transport"],
						"mrt": eachdata["mrt"],
						"latitude": eachdata["latitude"],
						"longitude": eachdata["longitude"],
						"images": ["http://"+i["src"] for i in imageURL]
						}
				)
				count += 1

			if count > 11:
				nextpage = int(page)+1
			else:
				nextpage = None

			return jsonify({"nextPage": nextpage, "data": data})

		else:
			connect_mysql()

			#因為有 % 符號的關係，改用 format 方式寫 SQL 語法，搜尋景點名稱中只要有出線關鍵字就抓資料出來
			selectsql = f"select * from tpelocation where name LIKE '%"+keyword+f"%' limit {int(page)*12}, 12"
			
			cursor.execute(selectsql)
			selectDB = cursor.fetchall()

			if selectDB == ():
				return jsonify({"error": True, "message": "錯誤：該頁已無結果或關鍵字沒有搜尋到結果"})

			count = 0
			for eachdata in selectDB:				
				selectURL = "select src from image where id = '%s'" %(eachdata["id"])
				cursor.execute(selectURL)
				imageURL = cursor.fetchall()
				
				data.append(
					{
						"id": eachdata["uid"],
						"name": eachdata["name"],
						"category": eachdata["category"],
						"description": eachdata["description"],
						"address": eachdata["address"],
						"transport": eachdata["transport"],
						"mrt": eachdata["mrt"],
						"latitude": eachdata["latitude"],
						"longitude": eachdata["longitude"],
						"images": ["http://"+i["src"] for i in imageURL]
						}
				)
				count += 1

			if count > 11:
				nextpage = int(page)+1
			else:
				nextpage = None
				
			return jsonify({"nextPage": nextpage, "data": data})

	else:
		return jsonify({"error": True, "message": "錯誤：頁數資料型態不正確"})


@app.errorhandler(404)
def error404(error):
    return jsonify({"error": True, "message": "找不到網頁..."})

@app.errorhandler(500)
def error404(error):
    return jsonify({"error": True, "message": "網站異常中..."})


app.run(host="0.0.0.0", port=3000, debug=True)