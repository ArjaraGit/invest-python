from enum import Enum

""" Пустые списки не менять и не удалять """
""" Счета """
acc_name_list = []

""" Инициализация пустых списков для начитки документов """
figi_list = []
ticker_list = []
isin_list = []
currency_list = []

""" 
    Часть инструментов в base.yaml называется иначе
    Соответствия задам через словарь: ключ - инструмент в тинькофф, значение - инструмент в base.yaml
    Тикеры "*-RM" тут указывать не нужно
"""
replace_items = {"RUB": "RUR",
                 "HHR": "HHRU"
                 }


class AccountStatus(Enum):
    ACCOUNT_STATUS_UNSPECIFIED = 0
    ACCOUNT_STATUS_NEW = 1
    ACCOUNT_STATUS_OPEN = 2
    ACCOUNT_STATUS_CLOSED = 3


class AccountType(Enum):
    ACCOUNT_TYPE_UNSPECIFIED = 0
    ACCOUNT_TYPE_TINKOFF = 1
    ACCOUNT_TYPE_TINKOFF_IIS = 2
    ACCOUNT_TYPE_INVEST_BOX = 3
