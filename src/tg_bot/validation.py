from config import ACCESS_WHITE_LIST


def check_permissions(user_name):
    if not ACCESS_WHITE_LIST:
        return

    error_msg = 'You don`t have permissions to use this function, please contact @berd_ant for more info'
    if user_name not in ACCESS_WHITE_LIST:
        raise Exception(error_msg)
