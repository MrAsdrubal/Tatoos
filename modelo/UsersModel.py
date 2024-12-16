import json
import os

class UsersModel:
    def __init__(self, file_path='users.json'):
        self.file_path = file_path
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}

    def save_users(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.users, file)

    def validate_user(self, username, password):
        return username in self.users and self.users[username] == password

    def register_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = password
        self.save_users()
        return True