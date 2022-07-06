import datetime
import routeros_api
import config


def create_time_stamp(**kwargs):
    """
    Возвращает дату timestamp
    :param kwargs: days, hours
    :return: int (Unix timestamp)
    """
    next_date = datetime.datetime.today() + datetime.timedelta(**kwargs)
    time_stamp = int(datetime.datetime.timestamp(next_date))
    return time_stamp


def router_role_and_get_response(disable: bool) -> str:
    connection = routeros_api.RouterOsApiPool(
        config.MIKROTIK_HOST,
        username=config.MIKROTIK_LOGIN,
        password=config.MIKROTIK_PASS,
        plaintext_login=True
    )

    api = connection.get_api()
    list_filters = api.get_resource('ip/firewall/filter/')

    role = list_filters.get(comment="switcher")

    if len(role):
        role_id = role[0].get('id')
        if role_id:
            attr = "true" if disable else "false"
            list_filters.set(id=role_id, disabled=attr)
            role = list_filters.get(comment="switcher")

        to_send = '\n'.join([f"{k}: {v}" for k, v in role[0].items()])
    else:
        to_send = 'No response'

    return to_send


if __name__ == "__main__":
    pass
