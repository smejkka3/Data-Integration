
import requests


url = "http://gorilla.bigdama.tu-berlin.de:8001/DataCleaningEvaluator/"
dataset = open("inputDB.csv", "r").read()
r = requests.post(url, data={"value": dataset})
if r.status_code != 200:
	print("There is an error! The error code:", r.status_code)
print(r.text)
