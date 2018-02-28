import pymysql.cursors
tablename = "Participants_Data"
database = "Podcast_Study"
connection = pymysql.connect(host='localhost',
                         user='root',
                         password='root',
                         charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS " + database)
connection.select_db(database)

sql_create = "CREATE TABLE IF NOT EXISTS " + tablename + "(\
        `participantsID` BIGINT NOT NULL AUTO_INCREMENT,\
        `workerID` VARCHAR(100) NOT NULL,\
        `assignmentID` VARCHAR(100) NOT NULL,\
        `hitID` VARCHAR(100) NOT NULL,\
        `assignedCode` VARCHAR(45) NOT NULL,\
        PRIMARY KEY (`participantsID`)\
       )"
cursor.execute(sql_create)
connection.commit()


sql_create = "CREATE PROCEDURE `sp_createParticipant`(\
    IN p_workerID VARCHAR(40),\
    IN p_assignmentID VARCHAR(40),\
    IN p_hitID VARCHAR(40),\
    IN p_assignedCode VARCHAR(40)\
)\
    insert into Participants_Data(workerID, assignmentID, hitID, assignedCode)\
    values (p_workerID, p_assignmentID, p_hitID,p_assignedCode)"

cursor.execute(sql_create)
connection.commit()

cursor.close()
connection.close()