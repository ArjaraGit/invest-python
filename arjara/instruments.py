import copy
import math
from pathlib import Path
import yaml
from functools import wraps
from time import time

from tinkoff.invest import Client
from tinkoff.invest.token import TOKEN

from arjara.settings import AccountStatus, figi_list, ticker_list, isin_list, currency_list, replace_items
from arjara.config import acc_name_list, yaml_path, base_yaml_file


def timing(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        if __name__ == "__main__":
            print('{}: {} sec'.format(f.__name__, te - ts))
        return result

    return wrap


@timing
def yaml_directory_clear(path, file_exception=base_yaml_file):
    for child in Path(path).iterdir():
        if child != Path(path, file_exception):
            child.unlink()


@timing
def read_from_base_yaml(path):
    with open(path) as file:
        base_yaml_dict = yaml.full_load(file)
    return base_yaml_dict


def write_to_yaml(file_path, file_name, list_to_write):
    with open(Path(file_path, (str(file_name) + ".yaml")), "w") as file:
        yaml.dump(list_to_write, file)


@timing
def prepare_and_write_to_yaml(position_list):
    base_yaml_path = Path(yaml_path, base_yaml_file)
    yaml_directory_clear(path=Path(yaml_path))

    temp_not_exist_in_base = {}
    acc_not_exist_in_base = {}

    final_dict_to_file = {}

    base_yaml_dict = read_from_base_yaml(path=base_yaml_path)

    base_yaml_money_dict = \
        {key: value for (key, value) in base_yaml_dict.items() if ("positions" not in key)}
    base_yaml_position_dict_non_rm = \
        {key: value for (key, value) in base_yaml_dict["positions"].items() if ("-RM" not in key)}
    base_yaml_position_dict_RM = \
        {key: value for (key, value) in base_yaml_dict["positions"].items() if ("-RM" in key)}

    for acc in position_list:
        temp_base_yaml_money_dict = {**base_yaml_money_dict}
        temp_base_yaml_position_dict_NON_RM = {**base_yaml_position_dict_non_rm}
        temp_base_yaml_position_dict_RM = {**base_yaml_position_dict_RM}

        for keyA, valueA in position_list[acc].items():
            if keyA == "positions":
                for keyP, valueP in position_list[acc]["positions"].items():
                    if keyP in temp_base_yaml_position_dict_NON_RM.keys():
                        temp_base_yaml_position_dict_NON_RM[keyP] = valueP
                    elif (keyP + "-RM") in base_yaml_position_dict_RM.keys():
                        temp_base_yaml_position_dict_RM[keyP + "-RM"] = valueP
                    else:
                        temp_not_exist_in_base[keyP] = valueP
            else:
                if keyA in temp_base_yaml_money_dict.keys():
                    temp_base_yaml_money_dict[keyA] = valueA
                else:
                    temp_not_exist_in_base[keyA] = valueA

        temp_base_yaml_position_dict_NON_RM.update(temp_base_yaml_position_dict_RM)
        final_dict_to_file.update(temp_base_yaml_money_dict)
        final_dict_to_file.update({"positions": temp_base_yaml_position_dict_NON_RM})

        acc_not_exist_in_base[acc] = copy.deepcopy(temp_not_exist_in_base)

        write_to_yaml(file_path=yaml_path, file_name=acc, list_to_write=final_dict_to_file)

        temp_base_yaml_money_dict.clear()
        temp_base_yaml_position_dict_NON_RM.clear()
        temp_base_yaml_position_dict_RM.clear()
        temp_not_exist_in_base.clear()

    ret_message = "\nТикеры не из списка:\n"
    for acc in acc_not_exist_in_base.keys():
        ret_message = ret_message + str(acc) + ":\n"
        for tiker, value in acc_not_exist_in_base[acc].items():
            ret_message = ret_message + "\t" + str(tiker) + ": " + str(value) + "\n"
    ret_message += "\n"

    return ret_message


@timing
def filter_by(original_list, exception_list, key):
    if key in exception_list and len(exception_list[key]) > 0:
        original_list = list(filter(lambda item: item[key] in exception_list[key], original_list))
    return original_list


@timing
def get_instruments_list(**kwargs):
    share_list = []
    with Client(TOKEN) as client:
        shares = client.instruments.shares(instrument_status=1)

        for share in shares.instruments:
            share_list.append(
                {"figi": share.figi, "ticker": share.ticker, "isin": share.isin, "currency": share.currency,
                 "lot": share.lot})

        share_list = filter_by(original_list=share_list, exception_list=kwargs, key="figi")
        share_list = filter_by(original_list=share_list, exception_list=kwargs, key="ticker")
        share_list = filter_by(original_list=share_list, exception_list=kwargs, key="isin")
        share_list = filter_by(original_list=share_list, exception_list=kwargs, key="currency")

        return share_list


@timing
def get_account_list(**kwargs):
    acc_list = []
    with Client(TOKEN) as client:
        accounts = client.users.get_accounts().accounts

        for acc in accounts:
            if acc.status == AccountStatus.ACCOUNT_STATUS_OPEN.value:
                acc_list.append({"id": acc.id, "name": acc.name, "type": acc.type, "status": acc.status})

        acc_list = filter_by(original_list=acc_list, exception_list=kwargs, key="name")

        return acc_list


@timing
def get_current_position():
    position_list = {}
    money_list = {}
    security_list = {}

    acc_list = get_account_list(name=acc_name_list)
    share_list = get_instruments_list(figi=figi_list, ticker=ticker_list, isin=isin_list, currency=currency_list)

    with Client(TOKEN) as client:
        for acc in acc_list:
            positions = client.operations.get_positions(account_id=acc["id"])

            for item in positions.securities:
                ticker = next((x for x in share_list if x["figi"] == item.figi), None)
                if ticker is not None:
                    # TODO: сделать отдельную функцию для замены ключей
                    if ticker["ticker"] in replace_items.keys():
                        security_list[replace_items[ticker["ticker"]]] = item.balance
                    else:
                        security_list[ticker["ticker"]] = item.balance

            for item in positions.money:
                if item.currency in ["usd", "rub", "eur"]:
                    # TODO: сделать отдельную функцию для замены ключей
                    if item.currency.upper() in replace_items.keys():
                        money_list[replace_items[item.currency.upper()]] = math.trunc(item.units)
                    else:
                        money_list[item.currency.upper()] = math.trunc(item.units)

            money_list.update({"positions": security_list})
            position_list[acc["name"]] = copy.deepcopy(money_list)

            money_list.clear()
            security_list.clear()

    return position_list


if __name__ == "__main__":
    position_list = get_current_position()
    acc_not_exist_in_base = prepare_and_write_to_yaml(position_list)

    print(acc_not_exist_in_base)

    """
    acc_list = get_account_list(name=acc_name_list)
    
    print(acc_list)
    print()

    for item in acc_list:
        print(item)

    print()
    """
    """ ************************************************* """

    """
    share_list = get_instruments_list(figi=figi_list, ticker=ticker_list, isin=isin_list, currency=currency_list)
    
    for share in share_list:
        print(share)
    
    print()
    """
    """ ************************************************* """
    """
    position_list = get_current_position()

    print(position_list)
    """
    """
    for item in position_list:
        print("Счет: {}".format(item))
        for key in item:
            print(key, str(item[key]))
    """

    """
    print(position_list)
    print()
    """

    """
    print("Список бумаг:")
    for key in security_list:
        print("figi: {}, count: {}".format(key, security_list[key]))
    print()

    print("Список валют:")
    for key in money_list:
        print("currency: {}, count: {}".format(key, money_list[key]))
    print()
    """
