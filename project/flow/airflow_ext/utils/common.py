def find_key_in_dicts(main_d: dict, keys_to_find: list) -> str:
    result = None
    if isinstance(main_d, dict):
        for ktf in keys_to_find:
            if ktf in main_d:
                if isinstance(main_d[ktf], str):
                    result = str(main_d[ktf])
                    break

        if not result:
            for kid in main_d:
                if isinstance(main_d[kid], dict):
                    result = find_key_in_dicts(main_d[kid], keys_to_find)
                    if result:
                        break
    return result
