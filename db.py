# -*- coding: utf-8 -*-
import logging
import os
import json
from json import JSONDecodeError


def load_db():
    try:
        logging.info("Trying to load groups DB.")
        with open('groups.json', 'r', encoding='utf-8') as json_data_file:
            groups = json.load(json_data_file)

        logging.info("Groups DB successfully loaded!")
        return groups

    except FileNotFoundError:
        logging.info(
            "There is no groups DB file in folder, so I created new.")
        groups = {}
        save_db(groups)
        return groups

    except JSONDecodeError:
        logging.info(
            "Seems like groups DB file is broken, so I backed up old one and created new.")
        os.rename('groups.json', 'groups.json.bak')
        groups = {}
        save_db(groups)
        return groups


def save_db(groups):
    with open('groups.json', 'w', encoding='utf-8') as json_data_file:
        json.dump(groups, json_data_file, indent=4, ensure_ascii=False)
    logging.info("Groups list successfully saved.")
