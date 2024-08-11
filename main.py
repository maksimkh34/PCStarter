import logging
import pickle

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from wakeonlan import send_magic_packet

from const_vars import PKL_DB_REG_USERS, PC_MAC, REG_KEY

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
registered_users = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if user.id not in registered_users:
        await update.message.reply_html(
            rf"default user"
        )
    else:
        await update.message.reply_html(
            rf"registered"
        )
    await update.message.reply_html(
        rf"registered users: {len(registered_users)}"
    )


async def start_pc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    send_magic_packet(PC_MAC)
    await update.message.reply_html(
        rf"sending package...",
        reply_markup=ForceReply(selective=True),
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if not update.message.text.__contains__(REG_KEY):
        await update.message.reply_html(
            rf"invalid register code",
            reply_markup=ForceReply(selective=True),
        )
        return

    if user.id in registered_users:
        await update.message.reply_html(
            rf"already registered"
        )
        return

    await update.message.reply_html(
        rf"registering {user.id}"
    )
    registered_users.append(user.id)

def main() -> None:
    global registered_users
    try:
        with open(PKL_DB_REG_USERS, 'rb') as load_file:
            # Deserialize and load the object from the file
            registered_users = pickle.load(load_file)
    except FileNotFoundError:
        open(PKL_DB_REG_USERS, 'w').close()

    application = Application.builder().token("7297128287:AAGC2rWlUJFiKA49gC-2W-wwjsf3AF3aIMM").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("start_pc", start_pc))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
    with open(PKL_DB_REG_USERS, 'wb') as file:
        pickle.dump(registered_users, file)
