__author__ = 'yedtoss'

# Importing important libraries
import pandas as pd
import numpy as np
import settings



def read_product(filename=None):
    """
    This function reads the product database
    :param filename:
    :return:
    """
    if not filename:
        filename = settings.PRODUCT_FILENAME
    return pd.read_csv(filename, sep='|', header=1)


def read_transactions(filename=None):
    """
    This function reads the transaction data
    :param filename
    :return
    """
    if not filename:
        filename = settings.TRANSACTION_FILENAME
    return pd.read_csv(filename, sep='|', header=1, parse_dates=[4])


def read_meteo_day(filename=None):
    """
    This function reads the meteo for a given day
    :param filename
    :return
    """
    if not filename:
        filename = settings.METEO_DAY_FILENAME
    return pd.read_csv(filename, sep=';', header=1, parse_dates=[0])


def read_meteo_week(filename=None):
    """
    This function reads the meteo for a given week
    :param filename
    :return
    """
    if not filename:
        filename = settings.METEO_WEEK_FILENAME

    # This function is the date parser for the week
    parser = lambda x: pd.datetime.strptime(x, '%Y%W')

    return pd.read_csv(filename, sep=';', header=1, parse_dates=[4], date_parser=parser)


def read_temp(filename=None):
    """
    This function reads the temperature data
    """
    if not filename:
        filename = settings.TEMP_FILENAME

    return pd.read_csv(filename, sep=';', header=1, parse_dates=[3],
                       dtype={0:object, 2:object, 3:object})




if __name__ == "__main__":
    """
    Main module
    """

    products = read_product()

    # trans.loc[1][1]
    trans = read_transactions()

    md = read_meteo_day()

    mw = read_meteo_week()

    temp = read_temp()



