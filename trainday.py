import json


def save_rating(data, rating_file):
    data = json.dumps(data)
    data = json.loads(str(data))

    with open(rating_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


data = {
    "users": []
}

data["users"].append({
    "name": "{message.from_user.first_name}",
    "chat_id": "message.from_user.id",
    "rating": 2
})

save_rating(data, "rating_file.json")


def read_rating(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


users = read_rating("rating_file.json")
for user in users["users"]:
    print(user)
