import requests
from bot.core import config


def login(email: str, password: str) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/public/authorization/signin"

    data = {"email": email, "password": password}

    return requests.post(endpoint, json=data)


def register(data: dict) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/public/authorization/signup"

    _payload = {
        "email": data.get("email"),
        "password": data.get("password"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "phone_number": str(data.get("phone")),
        "gender": data.get("sex"),
        "nationality": data.get("nationality"),
        "born": {
            "place": data.get("born_place"),
            "date": data.get("born_date"),
        },
    }

    return requests.post(endpoint, json=_payload)


def get_profile(token: str) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/private/profile/my"

    headers = {"Authorization": f"{token}"}

    return requests.get(endpoint, headers=headers)


def get_notifications(token: str) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/private/profile/my/notifications"

    headers = {"Authorization": f"{token}"}

    return requests.get(endpoint, headers=headers)


def cabinet(token: str) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/private/application/cabinet"

    headers = {"Authorization": f"{token}"}

    return requests.get(endpoint, headers=headers)


def get_documets(token: str) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/private/profile/my/documents"

    headers = {"Authorization": f"{token}"}

    return requests.get(endpoint, headers=headers)


def get_document(token: str, id: int) -> requests.Response:
    endpoint = f"{config.settings.API_URL}/api/v1/private/profile/my/documents/{id}"

    headers = {"Authorization": f"{token}"}

    return requests.get(endpoint, headers=headers)


def request_verification_code(token: str, id: str) -> requests.Response:
    endpoint = (
        f"{config.settings.API_URL}/api/v1/private/profile/my/documents/{id}/confirm"
    )

    headers = {"Authorization": f"{token}"}

    return requests.get(endpoint, headers=headers)


def verify_code(code: str):
    endpoint = f"{config.settings.API_URL}/api/v1/public/document/verify/{code}"

    return requests.get(endpoint)
