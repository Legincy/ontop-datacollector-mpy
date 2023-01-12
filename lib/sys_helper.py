# -*- coding:utf-8 -*-

def file_or_dir_exists(path):
    try:
        with open(path, mode="r") as reader:
            return True
    except OSError:
        return False


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def create_enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


Status = create_enum("INIT", "PENDING", "CONNECTED", "DISCONNECTED", "ERROR")
