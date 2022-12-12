import html
import json
import logging
import traceback

from loguru import logger
from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler, PollAnswerHandler, MessageHandler, Filters, \
    PicklePersistence

from config import TELEGRAM_BOT_TOKEN, DEV_CHAT_ID, CACHE_FILE_PATH
from data_providers.poll_config_loader import JsonPollConfigLoader
from google_sheet import GoogleSheetExporter
from models.telegram import PollModel, UserModel
from tg_bot.handlers import TelegramUpdateHandler
from tg_bot.parse_utils import parse_max_param, parse_create_poll_args
from tg_bot.poll_generator import PollGenerator
from tg_bot.validation import check_permissions

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update: Update, context: CallbackContext):
    msg = 'Send me poll with "max X" in question to create new limited poll'
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def receive_poll(update: Update, context: CallbackContext) -> None:
    actual_poll = update.effective_message.poll
    try:
        check_permissions(update.effective_user.username)
        options = [o.text for o in actual_poll.options]

        poll_model = PollModel(
            question=actual_poll.question,
            options=options,
            chat_id=update.effective_chat.id,
            option_1_limit=parse_max_param(actual_poll.question),
        )
        handler.create_tg_poll(poll_model, context)

    except Exception as ex:
        logger.error(actual_poll.question, str(ex))
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(ex))


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    answer = update.poll_answer
    poll_id = answer.poll_id
    logger.debug(f'Received answer from poll {poll_id}')

    try:
        poll_model: PollModel = context.bot_data[poll_id]
    except KeyError:
        logger.error(f'Unknown poll update [poll_id={poll_id}]')
        return

    if poll_model.closed:
        return

    poll_model.update_answers(
        selected_options=answer.option_ids,
        user=UserModel(answer.user.first_name, answer.user.last_name, answer.user.username, answer.user.id),
    )

    if len(poll_model.answers[0]) < poll_model.option_1_limit:
        return

    context.bot.stop_poll(poll_model.chat_id, poll_model.message_id)
    poll_model.closed = True
    logger.info(f'Finished poll {poll_id}')

    if not (parent_id := poll_model.combined_poll_message_id):
        handler.on_single_poll_closed(poll_model, context)
        return

    # in case poll is part of combined id, but there are unfinished polls - waiting until all closed
    if not (combined_poll := context.bot_data['combined_polls'][parent_id]).closed:
        return

    handler.on_combined_poll_closed(combined_poll, context)


def create_poll(update: Update, context: CallbackContext):
    location_nm, dttm = parse_create_poll_args(update.message.text)
    combined_poll = poll_generator.create_combined_poll(update.effective_chat.id, location_nm, dttm)

    message = context.bot.send_message(update.message.chat_id, combined_poll.common_message,
        parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    combined_poll.message_id = message.message_id
    for league in combined_poll.leagues:
        handler.create_tg_poll(league.poll, context, combined_poll.message_id)

    context.bot_data['combined_polls'][combined_poll.message_id] = combined_poll


def handle_unknown_command(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def handle_error(update: object, context) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    context.bot.send_message(chat_id=DEV_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def main():
    pickle_cache = PicklePersistence(CACHE_FILE_PATH, store_user_data=False, store_chat_data=False)
    updater = Updater(token=TELEGRAM_BOT_TOKEN, persistence=pickle_cache, workers=1)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', start))
    dispatcher.add_handler(CommandHandler('create_poll', create_poll))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(MessageHandler(Filters.command, handle_unknown_command))
    dispatcher.add_error_handler(handle_error)

    for init_key in ('combined_polls', 'tournaments'):
        if init_key not in dispatcher.bot_data:
            dispatcher.bot_data[init_key] = {}

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    google_sheet_exporter = GoogleSheetExporter('data/client_secret.json', 'data')
    handler = TelegramUpdateHandler(google_sheet_exporter)
    poll_config_loader = JsonPollConfigLoader('data/poll_template.json')
    poll_generator = PollGenerator(poll_config_loader)
    main()
