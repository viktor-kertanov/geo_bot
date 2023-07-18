from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext

def remove_keyboard_on_root_message(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        # Call the original function
        result = func(update, context, *args, **kwargs)

        # Get the root message ID from context.chat_data
        root_message_id = context.chat_data.get('root_message_id')

        # Check if there's a root message ID and the current update is not a callback query
        if root_message_id:
            # Remove the inline keyboard from the root message
            context.bot.edit_message_reply_markup(
                chat_id=update.effective_chat.id,
                message_id=root_message_id,
                reply_markup=None
            )

            # Clear the root message ID from chat_data
            context.chat_data['root_message_id'] = None

        return result

    return wrapper
