__author__ = 'yedtoss'

# Importing important libraries
import pandas as pd
import numpy as np
import settings
import sortedcontainers as sc



def read_product(filename=None):
    """
    This function reads the product database
    :param filename:
    :return:
    """
    if not filename:
        filename = settings.PRODUCT_FILENAME
    return pd.read_csv(filename, sep='|')


def read_transactions(filename=None):
    """
    This function reads the transaction data
    :param filename
    :return
    """
    if not filename:
        filename = settings.TRANSACTION_FILENAME
    return pd.read_csv(filename, sep='|', parse_dates=[4])


def read_meteo_day(filename=None):
    """
    This function reads the meteo for a given day
    :param filename
    :return
    """
    if not filename:
        filename = settings.METEO_DAY_FILENAME
    return pd.read_csv(filename, sep=';', parse_dates=[0])


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

    return pd.read_csv(filename, sep=';', parse_dates=[4], date_parser=parser)


def read_temp(filename=None):
    """
    This function reads the temperature data
    """
    if not filename:
        filename = settings.TEMP_FILENAME

    return pd.read_csv(filename, sep=';', parse_dates=[3],
                       dtype={0: object, 2: object, 3: object})


def get_weather_on_date(date, meteo_day, store_id):
    """
    This function gives us all the weather information/prediction for a given day in a given store
    """
    return meteo_day[(meteo_day['STO_EAN'] == store_id) & (meteo_day['DATE_KEY'] == date)]


def get_volume_product_on_date(product_barcode, date, store_id, transactions):
    """
    This function gives us the sum of all sales value for a given product on a given date
    """
    transactions_day = transactions[(transactions['STO_EAN'] == store_id) &
                        (transactions['BARCODE'] == product_barcode) &
                        (transactions['TRX_DATETIME'] >= pd.to_datetime(date).date())
                        & (transactions['TRX_DATETIME'] < (pd.to_datetime(date) + pd.DateOffset(1)))]

    return np.sum(transactions_day['SAL_AMT_WTAX'])


def generate_training_testing_dataset(store_id, transactions, meteo_day):
    """
    This function generates the training and testing data
    """

    # Get the minimum and maximum of date in the transactions
    min_date = transactions[(transactions['STO_EAN'] == store_id)].min()['TRX_DATETIME'].date()
    max_date = transactions[(transactions['STO_EAN'] == store_id)].max()['TRX_DATETIME'].date()

    # Get the number of days between the two date
    num_days = (max_date - min_date).days

    # Get the list of unique products barcode in the transactions
    products_barcode = transactions['BARCODE'].unique()


    all_data_first_level = []
    # For each day and for each product

    for date in xrange(num_days):
        for product_barcode in products_barcode:
            tmp = get_weather_on_date(date, meteo_day, store_id)
            get_volume_product_on_date(product_barcode, date, store_id, transactions)













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

    get_weather_on_date(pd.to_datetime('01/07/2014'), md, settings.DIJON_ID)



