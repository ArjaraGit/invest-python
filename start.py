from arjara.instruments import get_current_position

if __name__ == "__main__":
    position_list = get_current_position()

    for item in position_list:
        print(item + ":")
        for ticker in position_list[item]:
            print("\t{}: {}".format(ticker, position_list[item][ticker]))

