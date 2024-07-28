import asyncio
import datetime
import io
import qrcode
import logging
from PIL.Image import Image
from PIL import Image as PImage
from pyzbar.pyzbar import decode
import re
from bot.core.decorators.user import authorization_required
from bot.core import api
from bot.core.config import settings
from bot.core.redis import is_user_exist, set_user, get_user, logout
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F, Bot, Dispatcher, Router, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup

TOKEN = settings.BOT_TOKEN

form_router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class LoginState(StatesGroup):
    email = State()
    password = State()


class RegisterState(StatesGroup):
    email = State()
    password = State()
    first_name = State()
    last_name = State()
    sex = State()
    phone_number = State()
    nationality = State()
    born_date = State()
    born_place = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    parts = [
        f"Hello, {hbold(message.from_user.full_name)}!",
        "Here you can manage your ApexID account and some documents!\n",
        hbold(
            "This bot and API is Work In Progress (WIP) so keep an eye on updates.\n"
        ),
        (
            "I see that you already authorized, you can use /help to get more information"
            if is_user_exist(message.from_user.id)
            else "You are not authorized yet. Please, /login or /register."
        ),
    ]
    await message.answer("\n".join(parts))


@dp.message(Command("logout"))
async def logout_handler(message: Message) -> None:
    logout(message.from_user.id)
    await message.answer("You have been successfully logged out!")


@dp.message(Command("login"))
async def login_handler(message: Message, state: FSMContext) -> None:
    if is_user_exist(message.from_user.id):
        await message.answer("You are already authorized!")
        return

    await message.answer("Please enter your email:")

    await state.set_state(LoginState.email)


@dp.message(LoginState.email)
async def login_email_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(email=message.text)

    await message.answer("Please enter your password:")

    await state.set_state(LoginState.password)


@dp.message(LoginState.password)
async def login_password_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()

    # TODO: add more details about the client as metadata
    _response = api.login(data.get("email"), message.text)

    if _response.status_code != 200:
        await message.answer(
            "Invalid email or password. Please, try again.",
        )
        return

    auth_data = _response.json()

    if not auth_data.get("token"):
        await message.answer(
            "Something went wrong. Please, try again.",
        )
        return

    profile_response = api.get_profile(auth_data.get("token"))

    if profile_response.status_code != 200:
        await message.answer(
            "Something went wrong while fetching your profile. Please, try again.",
        )
        return

    profile_data = profile_response.json()

    set_user(
        message.from_user.id,
        {
            "id": profile_data.get("id"),
            "email": data.get("email"),
            "first_name": profile_data.get("first_name"),
            "token": auth_data.get("token"),
        },
    )

    await message.answer(
        f"Welcome to the system, {hbold(profile_data.get('first_name'))}!"
    )


@dp.message(Command("register"))
async def register_handler(message: Message, state: FSMContext) -> None:
    if is_user_exist(message.from_user.id):
        await message.answer("You are already authorized!")
        return

    await message.answer("Please enter your email:")

    await state.set_state(RegisterState.email)


@dp.message(RegisterState.email)
async def register_email_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(email=message.text)

    await message.answer("Please enter your password:")

    await state.set_state(RegisterState.password)


@dp.message(RegisterState.password)
async def register_password_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(password=message.text)

    await message.answer("Please enter your first name:")

    await state.set_state(RegisterState.first_name)


@dp.message(RegisterState.first_name)
async def register_first_name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)

    await message.answer("Please enter your last name:")

    await state.set_state(RegisterState.last_name)


@dp.message(RegisterState.last_name)
async def register_last_name_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text)

    await message.answer("Please enter your nationality:")
    await state.set_state(RegisterState.nationality)


@dp.message(RegisterState.nationality)
async def register_natinality_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(nationality=message.text)

    await message.answer("Please enter your sex:")
    await state.set_state(RegisterState.sex)


@dp.message(RegisterState.sex)
async def register_sex_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(sex=message.text)

    await message.answer("Please enter your phone number:")
    await state.set_state(RegisterState.phone_number)


@dp.message(RegisterState.phone_number)
async def register_phone_number_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(phone_number=message.text)

    await message.answer("Please enter your born place:")
    await state.set_state(RegisterState.born_place)


@dp.message(RegisterState.born_place)
async def register_born_place_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(born_place=message.text)

    await message.answer("Please enter your born date:")
    await state.set_state(RegisterState.born_date)


@dp.message(RegisterState.born_date)
async def register_born_date_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(born_date=message.text)

    data = await state.get_data()
    await state.clear()

    _response = api.register(data)

    if _response.status_code != 200:
        await message.answer(
            "Something went wrong. Please, try again.",
        )
        print(_response.json())
        return

    await message.answer(
        "You have been successfully registered!\nPlease, /login and then use /apply as at the moment your account is not active."
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """

    Allow user to cancel any action

    """

    current_state = await state.get_state()

    if current_state is None:

        return

    logging.info("Cancelling state %r", current_state)

    await state.clear()

    await message.answer(
        "Cancelled.",
    )


@dp.message(Command("profile"))
@authorization_required
async def profile_handler(message: Message) -> None:
    token = get_user(message.from_user.id).get("token")
    profile_response = api.get_profile(token)

    if profile_response.status_code != 200:
        await message.answer(
            "Something went wrong while fetching your profile. Please, try again.",
        )
        return

    profile_data = profile_response.json()

    parts = [
        f"Your profile information:\n",
        f"ID: {hbold(profile_data.get('id'))}",
        f"First Name: {hbold(profile_data.get('first_name'))}\n",
        "At the moment, this is the only information we able to provide you through profile.",
        "If you want to get your documents, please use /documents command.",
        "Or you can use /cabinet to manage your applications.",
    ]

    await message.answer("\n".join(parts))


@dp.message(Command("notifications"))
async def notifications_handler(message: Message) -> None:
    token = get_user(message.from_user.id).get("token")
    notifications_response = api.get_notifications(token)

    if notifications_response.status_code != 200:
        await message.answer(
            "Something went wrong while fetching your notifications. Please, try again.",
        )
        return

    notifications_data = notifications_response.json()

    if not notifications_data:
        await message.answer("You don't have any notifications.")
        return

    parts = [
        f"Your notifications:\n",
    ]

    """
    {
		"_id": "65ce9227ac91b58fd40c91bd",
		"user_id": "65ce28267e6a49005d3f5c5d",
		"message": "New device signed in to your account, DeviceID: 65ce9227ac91b58fd40c91bc",
		"created_at": "2024-02-15T22:37:27.535000",
		"created_by": "system",
		"metadata": {}
	},
    """

    total_notifications = len(notifications_data)

    limit = 5
    if len(message.text.split()) > 1:
        if message.text.split()[1] == "all":
            limit = total_notifications

    notifications_data = sorted(
        notifications_data, key=lambda x: x.get("created_at"), reverse=True
    )[:limit]

    for notification in notifications_data:
        datetime_object = datetime.datetime.fromisoformat(
            notification.get("created_at")[:-1]
        )

        formated_time = datetime_object.strftime("%Y-%m-%d %H:%M:%S")

        parts.append(
            f"{notification.get('message')}\n{hbold(formated_time)} from {hbold(notification.get('created_by'))}\n"
        )

    if total_notifications > limit:
        parts.append(
            f"Only {hbold(limit)} latest notifications are shown.\nUse '/notifications all' to see all of them."
        )
    else:
        parts.append(f"Total {hbold(total_notifications)} notifications are shown.")

    await message.answer("\n".join(parts))


@dp.message(Command("cabinet"))
async def cabinet_handler(message: Message) -> None:
    token = get_user(message.from_user.id).get("token")
    cabinet_response = api.cabinet(token)

    if cabinet_response.status_code != 200:
        await message.answer(
            "Something went wrong while fetching your cabinet. Please, try again.",
        )
        return

    cabinet_data = cabinet_response.json()

    if not cabinet_data:
        await message.answer("You don't have any applications.")
        return

    parts = [
        f"Your applications:\n",
    ]

    """
    {
		"reference": "REF_65ce667912550a490394e2f1",
		"status": "approved"
	}
    """

    for application in cabinet_data:
        parts.append(
            f"{hbold(application.get('reference'))} is {hbold(application.get('status'))}\n"
        )

    await message.answer("\n".join(parts))


@dp.message(Command("documents"))
async def documents_handler(message: Message) -> None:
    token = get_user(message.from_user.id).get("token")
    documents_response = api.get_documets(token)

    if documents_response.status_code != 200:
        await message.answer(
            "Something went wrong while fetching your documents. Please, try again.",
        )
        return

    documents_data = documents_response.json()

    if not documents_data:
        await message.answer("You don't have any documents.")
        return

    builder = InlineKeyboardBuilder()

    for document in documents_data:
        builder.add(
            types.InlineKeyboardButton(
                text=document.get("metadata").get("document_name"),
                callback_data=f"document_{document.get('_id')}",
            )
        )

    await message.answer(
        "Please select the document you want to get:", reply_markup=builder.as_markup()
    )


def image_to_byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


@dp.message(F.photo)
async def photo_handler(message: types.Message) -> None:
    image_file = io.BytesIO()
    await message.bot.download(message.photo[-1].file_id, image_file)
    img = PImage.open(image_file)

    decoded_data = decode(img)

    if not decoded_data:
        await message.answer("No QR code detected.")
        return

    qr_code_data = decoded_data[0].data.decode("utf-8")

    if not re.match(r"^[a-f\d]{24}$", qr_code_data):
        await message.answer("Invalid QR code.")
        return

    verification_response = api.verify_code(qr_code_data)

    if verification_response.status_code != 200:
        _response_data = verification_response.json()
        if _response_data.get("detail"):
            return await message.answer(
                f"Verification failed: {_response_data.get('detail')}"
            )
        return await message.answer("Verification failed.")

    document_data = verification_response.json()

    parts = [
        # f"{hbold(document_data.get('document_name'))}",
    ]

    for key, value in document_data.items():
        parts.append(f"\n{key.replace('_', ' ').capitalize()}\n{hbold(value)}\n")

    parts.append(
        "Document is valid and verified.\nThis message will be deleted in 3 minutes."
    )

    _m = await message.answer("\n".join(parts))

    await asyncio.sleep(180)

    await _m.delete()


@dp.callback_query(F.data.startswith("verification_"))
async def verification_code_handler(query: types.CallbackQuery) -> None:
    document_id = query.data.split("_")[1]
    token = get_user(query.from_user.id).get("token")
    verification_response = api.request_verification_code(token, document_id)

    if verification_response.status_code != 200:
        await query.message.edit_text(
            "Something went wrong while requesting the verification code.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    verification_data = verification_response.json()

    qr = qrcode.make(verification_data.get("token"))

    # remove mackup from the message
    await query.message.delete_reply_markup()

    await query.message.answer_photo(
        photo=types.BufferedInputFile(
            image_to_byte_array(qr),
            filename="qr_code.png",
        ),
        caption="Verification QR code.\nPlease, scan it with your device.\n\nThis QR code is valid for 3 minutes.",
    )


@dp.callback_query(F.data.startswith("document_"))
async def callback_query_handler(query: types.CallbackQuery) -> None:
    # functionality basing on the query data
    document_id = query.data.split("_")[1]
    token = get_user(query.from_user.id).get("token")
    selected_document = api.get_document(token, document_id)

    if selected_document.status_code != 200:
        await query.message.edit_text(
            "Something went wrong while fetching the document.",
            # remove keyboard
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    selected_document = selected_document.json()
    await query.answer("Document is sent to you.")

    document_data = selected_document.get("data")

    parts = [
        f"{hbold(selected_document.get('metadata').get('document_name'))}\n",
    ]

    for key, value in document_data.items():
        if isinstance(value, dict):
            # parts.append(f"{key.replace('_', ' ').capitalize()} Information")
            for k, v in value.items():
                parts.append(
                    f"{key.replace('_', ' ').capitalize()} {k.replace('_', ' ').capitalize()}\n{hbold(v)}\n"
                )
            # parts.append("")
        else:
            parts.append(f"{key.replace('_', ' ').capitalize()}\n{hbold(value)}\n")

    # Provide verification code button
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Request verification code",
            callback_data=f"verification_{selected_document.get('_id')}",
        )
    )

    await query.message.edit_text("\n".join(parts), reply_markup=builder.as_markup())


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # set commands

    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Start the bot"),
            types.BotCommand(command="help", description="Get help"),
            types.BotCommand(command="login", description="Login to the system"),
            types.BotCommand(command="register", description="Register to the system"),
            types.BotCommand(command="logout", description="Logout from the system"),
            types.BotCommand(command="profile", description="Get your profile"),
            types.BotCommand(
                command="notifications", description="Get your notifications"
            ),
            types.BotCommand(command="cabinet", description="Get your applications"),
            types.BotCommand(command="documents", description="Get your documents"),
        ]
    )

    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/log_{current_date}.txt"

    logging.basicConfig(
        # filename=log_file,
        # filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    asyncio.run(main())
