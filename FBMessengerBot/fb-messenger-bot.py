#!/usr/bin/python3
from fbchat import Client
from fbchat.models import Message


username = "username.or.email"
password = "password"


client = Client(username, password)

users = client.fetchThreadList()
print(users)

detailed_users = [list(client.fetchThreadInfo(user.uid).values())[0] for user in users]


# short by number of message
sorted_detailed_users = sorted(detailed_users, key=lambda u: u.message_count, reverse=True)

top_friend = sorted_detailed_users[0]
print("Top Friend: ", top_friend.name, "with a message count of", top_friend.message_count)


client.send(Message(text=f"Congratulations {top_friend.name}, You are now top rated {top_friend.message_count} message!"
                    ), thread_id=top_friend.uid)


"""
# get all users you talked to in messenger in your account
all_users = client.fetchAllUsers()
print("You talked with a total of", len(all_users), "users!")
"""

client.logout()
