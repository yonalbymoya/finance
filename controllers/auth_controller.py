from models.database import get_user


def validation_login(username, password):
    user = get_user(username)
    print("Esto es password en validation: ", user[2])
    if user:
        if user[2] == password:
            return True
    return False
