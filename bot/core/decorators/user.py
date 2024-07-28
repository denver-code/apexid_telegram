from functools import wraps
from bot.core.redis import is_user_exist


def authorization_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if is_user_exist(args[0].from_user.id):
            return await func(*args, **kwargs)

        await args[0].answer(
            "You are not authorized yet. Please, /login or /register.",
        )

    return wrapper
