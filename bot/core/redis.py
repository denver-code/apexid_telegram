import redis
import json

r = redis.Redis(
    host="localhost",
    port=6379,
)


def ping():
    return r.ping()


def get_user(id: str):
    dict_bytes = r.get(id)

    if not dict_bytes:
        return {}

    dict_str = dict_bytes.decode("utf-8")

    my_dict = json.loads(dict_str)

    return my_dict


# def get_subscribed_users():
#     return [get_user(id) for id in r.keys() if get_user(id).get("is_subscribed")]


def set_user(id: str, data: dict):
    r.set(id, bytes(json.dumps(data), "utf-8"))


def logout(id: str):
    r.delete(id)


# def is_subscribed(id: str) -> bool:
#     return bool(get_user(id).get("is_subscribed"))


# def toggle_subscription(id: str) -> bool:
#     _user = get_user(id)
#     _user["is_subscribed"] = not bool(_user["is_subscribed"])
#     set_user(id, _user)

#     return _user["is_subscribed"]


def is_user_exist(id: int) -> bool:
    return bool(get_user(id))
