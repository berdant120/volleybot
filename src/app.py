import html
import json
import logging
import traceback

from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler, PollAnswerHandler, MessageHandler, Filters, \
    PicklePersistence

from config import TELEGRAM_BOT_TOKEN, DEV_CHAT_ID, CACHE_FILE_PATH
from models import PollModel, UserModel
from utils import check_permissions

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update: Update, context: CallbackContext):
    msg = 'Send me poll with "max X" in question to create new limited poll'
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def receive_poll(update: Update, context: CallbackContext) -> None:
    actual_poll = update.effective_message.poll
    try:
        check_permissions(update.effective_user.username)
        options = [o.text for o in actual_poll.options]

        message = context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=actual_poll.question,
            options=options,
            allows_multiple_answers=actual_poll.allows_multiple_answers,
            is_anonymous=False,
            is_closed=False,
        )

        poll_model = PollModel(
            question=actual_poll.question,
            options=options,
            message_id=message.message_id,
            chat_id=update.effective_chat.id,
        )
        context.bot_data[message.poll.id] = poll_model
        logging.info(f'Created poll {message.poll.id}:{poll_model}')

    except Exception as ex:
        logging.error(actual_poll.question, str(ex))
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(ex))


def receive_poll_answer(update: Update, context: CallbackContext) -> None:
    answer = update.poll_answer
    poll_id = answer.poll_id
    logging.debug(f'Received answer from poll {poll_id}')

    try:
        poll_model = context.bot_data[poll_id]
    except KeyError:
        logging.error(f'Unknown poll update [poll_id={poll_id}]')
        return

    if poll_model.closed:
        return

    poll_model.update_answers(
        selected_options=answer.option_ids,
        user=UserModel(answer.user.first_name, answer.user.username, answer.user.id),
    )

    if len(poll_model.answers[0]) < poll_model.option_1_limit:
        return

    context.bot.stop_poll(poll_model.chat_id, poll_model.message_id)
    poll_model.closed = True

    context.bot.send_message(
        poll_model.chat_id,
        f'Poll is finished. {poll_model.formatted_answer_voters(0, True)}',
        reply_to_message_id=poll_model.message_id,
        parse_mode=ParseMode.HTML,
    )

    logging.info(f'Finished poll {poll_id}')
    del context.bot_data[poll_id]


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
    updater = Updater(token=TELEGRAM_BOT_TOKEN, persistence=pickle_cache)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', start))
    dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
    dispatcher.add_handler(MessageHandler(Filters.poll, receive_poll))
    dispatcher.add_handler(MessageHandler(Filters.command, handle_unknown_command))
    dispatcher.add_error_handler(handle_error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
