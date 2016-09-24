__author__ = 'yedtoss'

# Importing important libraries
import pandas as pd
import numpy as np
import settings
from workalendar.europe import France
import datetime

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

    return {"price": np.sum(transactions_day['SAL_AMT_WTAX']),
            "weight": np.sum(transactions_day['SAL_UNIT_QTY_WEIGHT'])}



def generate_day_type(date):
    """
    This function convert a date to the corresponding type of the day
    (working day/holiday/Mon-Sun)
    """
    cal = France()

    if cal.is_holiday(date):
        # If Mon-Friday
        if date.weekday() in range(5):
            return 0
        else:
            return 1
    else:
        if date.weekday() in range(5):
            return 1
        else:
            return 0



def generate_weather_conditions(temperature, temp_type):
    """
    """

    if temp_type == "MIN" or temperature < 5:
        if temperature > 10:
            return 0
        elif temperature >= 0:
            return (10.-temperature)/10.
        else:
            return 1

    elif temp_type == "AVG":

        if temperature > 25:
            return 0
        elif temperature >= 15:
            return (25.-temperature)/(25.-15)
        elif temperature >= 5:
            return (temperature-5.)/(15-5.)

    elif temp_type == "MAX":
        if temperature > 40:
            return 1
        elif temperature >= 20:
            return (temperature-20)/(40.-20)
        else:
            return 0


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
    for day in xrange(num_days):

        print(day)

        date = min_date + pd.DateOffset(day)

        # Get the weather of the date
        weather = get_weather_on_date(date, meteo_day, store_id).head(n=1)
        for product_barcode in products_barcode:

            # Get the volume
            volume = get_volume_product_on_date(product_barcode, date, store_id, transactions)
            day_type = generate_day_type(date)



            # Generating complex features based on the simpler one

            # yesterday = date - pd.DateOffset(1)
            # two_days_ago = date - pd.DateOffset(2)
            # day_type_yesterday = generate_day_type(yesterday)
            # day_type_2days_ago = generate_day_type(two_days_ago)
            #
            # volume_yesterday = get_volume_product_on_date(product_barcode, yesterday, store_id, transactions)
            # volume_2days_ago = get_volume_product_on_date(product_barcode, two_days_ago, store_id, transactions)
            # weather_yesterday = get_weather_on_date(yesterday, meteo_day, store_id).head(n=1)


            tmp = [weather['TEMPERATURE_VALUE_MIN'], weather['TEMPERATURE_VALUE_MAX'],
                   weather['PRECIPITATION_VALUE'], weather['SUNSHINE_DURATION'],
                   weather['SNOW_DEPTH'], day_type, volume["price"], volume["weight"]]

            all_data_first_level.append(tmp)


    return all_data_first_level







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



