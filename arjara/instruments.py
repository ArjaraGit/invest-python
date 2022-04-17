import copy

from tinkoff.invest import Client, Instrument
from tinkoff.invest.token import TOKEN

from arjara.settings import AccountStatus
from arjara.config import acc_name_list, figi_list, ticker_list, isin_list, currency_list

def get_instruments_list(**kwargs):
    share_list = []
    with Client(TOKEN) as client:
        shares = client.instruments.shares(instrument_status=1)

        for share in shares.instruments:
            share_list.append({"figi": share.figi, "ticker": share.ticker, "isin": share.isin, "currency": share.currency, "lot": share.lot})

        # Фильтры по переданным параметрам
        if ("figi" in kwargs and len(kwargs["figi"]) > 0):
            share_list = list(filter(lambda item: item['figi'] in kwargs["figi"], share_list))

        if ("ticker" in kwargs and len(kwargs["ticker"]) > 0):
            share_list = list(filter(lambda item: item['ticker'] in kwargs["ticker"], share_list))

        if ("isin" in kwargs and len(kwargs["isin"]) > 0):
            share_list = list(filter(lambda item: item['isin'] in kwargs["isin"], share_list))

        if ("currency" in kwargs and len(kwargs["currency"]) > 0):
            share_list = list(filter(lambda item: item['currency'] in kwargs["currency"], share_list))

        return share_list

def get_account_list(**kwargs):
    acc_list = []
    with Client(TOKEN) as client:
        accounts = client.users.get_accounts().accounts

        for acc in accounts:
            if (acc.status == AccountStatus.ACCOUNT_STATUS_OPEN.value):
                acc_list.append({"id": acc.id, "name": acc.name, "type": acc.type, "status": acc.status})

        # Фильтр по списку счетов
        if ("name" in kwargs and len(kwargs["name"]) > 0):
            acc_list = list(filter(lambda item: item["name"] in kwargs["name"], acc_list))

        return acc_list

def get_current_position(**kwargs):
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
                if ticker != None:
                    security_list[ticker["ticker"]] = item.balance

            for item in positions.money:
                money_list[item.currency] = item.units

            position_list[acc["name"]] = copy.deepcopy(security_list)
            money_list.clear()
            security_list.clear()

    return position_list


if __name__ == "__main__":
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

    position_list = get_current_position()

    print(position_list)
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


