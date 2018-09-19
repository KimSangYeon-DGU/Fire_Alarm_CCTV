from firebase import firebase

firebase = firebase.FirebaseApplication("DB address...", None)

user_name = "user1"
cam_name = "CAM01"
title = "log"

Log = {
    "num_of_logs": 2,
    "date": ["2018-01-01", "2018-03-03"],
    "encoded":["null", "null"]
}

Info ={
    "install_date":"2018-09-15",
    "location":"Kitchen",
    "call": "+82 10-xxxx-xxxx"
}

#result = firebase.put("/users/user1/CAM01", "info", Info)
result = firebase.put("/users/"+user_name+"/"+cam_name, title, Log)

#result = firebase.get("/users/user1/CAM01/log", None)

#result["date"].append("2018-04-05")
#result["encoded"].append("null")

#result = firebase.put("/users/user1/CAM01", "log", result)