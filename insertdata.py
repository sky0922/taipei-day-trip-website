from flask import Flask
from flask import json
import pymysql, os
from dotenv import load_dotenv
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
newDatabaseName = "tpetravel"

#開始創資料庫 tpetravel
create_db_connect = pymysql.connect(host = MYSQL_HOST, user = MYSQL_USER, password = MYSQL_PASS, charset = 'utf8', use_unicode = True )

try:
    cursorInsatnce = create_db_connect.cursor()                                    
    sqlStatement = "CREATE DATABASE "+newDatabaseName
    cursorInsatnce.execute(sqlStatement)

except Exception as e:
    print("Exeception occured:{}".format(e))

else:
    print("Create Database tpetravel success!")

finally:
    create_db_connect.close()


def connect_mysql():  
    global connect, cursor 
    connect = pymysql.connect(host = MYSQL_HOST, db = newDatabaseName, user = MYSQL_USER, password = MYSQL_PASS,
            charset = 'utf8', use_unicode = True, cursorclass = pymysql.cursors.DictCursor)
    cursor = connect.cursor()


#開始創資料表 tpelocation
connect_mysql()
create_table_sql = """CREATE TABLE tpelocation(
                    uid INT AUTO_INCREMENT PRIMARY KEY COMMENT '獨立編號',
                    id INT NOT NULL COMMENT '資料來源景點 ID',
                    name varchar(255) NOT NULL COMMENT 'stitle',
                    category varchar(255) NOT NULL COMMENT 'CAT2',
                    description text NOT NULL COMMENT 'xbody',
                    address varchar(255) NOT NULL COMMENT 'address',
                    transport text COMMENT 'info',
                    mrt text COMMENT 'MRT',
                    latitude float NOT NULL COMMENT 'latitude',
                    longitude float NOT NULL COMMENT 'longitude'
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

try:
    cursor.execute(create_table_sql) 

except Exception as e:
    print("Exeception occured:{}".format(e))

else:
    print("Create Table tpelocation success!")


#開始創資料表 image
create_table_sql2 = """CREATE TABLE image(
                    uid INT AUTO_INCREMENT PRIMARY KEY COMMENT '獨立編號',
                    id INT NOT NULL COMMENT '資料來源景點 ID',
                    name varchar(255) NOT NULL COMMENT 'stitle',
                    src varchar(255) NOT NULL COMMENT 'img url'
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

try:
    cursor.execute(create_table_sql2) 

except Exception as e:
    print("Exeception occured:{}".format(e))

else:
    print("Create Table image success!")

finally:
    cursor.close()



with open("data/taipei-attractions.json", encoding="utf-8") as data:
    data = json.load(data)
    data_dict = data["result"]["results"]

    # print (type(data_dict[0]))
    # print(data_dict[0]['info'])
    # print(data_dict[1]['info'])

    connect_mysql()
    imgid = 0
    for i in data_dict:
        #抓文字資料
        id = i["_id"]
        name = i["stitle"]
        category = i["CAT2"]
        description = i["xbody"]
        description = description.replace("'", "\\'") #處理單引號
        address = i["address"]
        transport = i["info"]
        mrt = i["MRT"]
        latitude = i["latitude"]
        longitude = i["longitude"]

        imgsrc = i["file"].split("http://")

        insertsql = "INSERT INTO tpelocation(id, name, category, description, address, transport, mrt, latitude, longitude) \
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, name, category, description, address, transport, mrt, latitude, longitude)
        cursor.execute(insertsql)

        for j in imgsrc[1:]:
            #抓副檔名是 jpg & png 的圖片網址
            if ".jpg" in j.lower() or ".png" in j.lower():
                insertsql2 = "INSERT INTO image(id, name, src) VALUES ('%d', '%s', '%s')" % (id, name, j)
                cursor.execute(insertsql2)


    connect.commit()
cursor.close()