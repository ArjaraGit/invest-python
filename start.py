from arjara.instruments import get_current_position, prepare_and_write_to_yaml

if __name__ == "__main__":
    acc_not_exist_in_base = prepare_and_write_to_yaml(get_current_position())

    print(acc_not_exist_in_base)
