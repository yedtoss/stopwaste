__author__ = 'yedtoss'

# Importing important libraries
import pandas as pd
import numpy as np
import settings
from workalendar.europe import France


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
    :param date the date we want to query
    :param meteo_day data containing all meteo
    :param store_id the store where the meteo
    :return the weather data on that date at that store
    """
    return meteo_day[(meteo_day['STO_EAN'] == store_id) & (meteo_day['DATE_KEY'] == date)]


def get_volume_product_on_date(product_barcode, date, store_id, transactions):
    """
    This function gives us the sum of all sales value for a given product on a given date.
    It also return the quantity of products sold in weight
    :param product_barcode the barcode of the product
    :param the date of the transaction (Only year, month, day)
    :param store_id the store where the transactions were made
    :param transactions the data containing all transactions made
    :return the total sales and weight of the given product
    """
    transactions_day = transactions[(transactions['STO_EAN'] == store_id) &
                        (transactions['BARCODE'] == product_barcode) &
                        (transactions['TRX_DATETIME'] >= pd.to_datetime(date).date())
                        &(transactions['TRX_DATETIME'] < (pd.to_datetime(date) + pd.DateOffset(1)))]

    # If the transaction does not exist return None
    if transactions_day.empty:
        return None

    return {"price": np.sum(transactions_day['SAL_AMT_WTAX'].values),
            "weight": np.sum(transactions_day['SAL_UNIT_QTY_WEIGHT'].values)}


def generate_day_type(date):
    """
    This function convert a date to the corresponding type of the day
    (working day/holiday/Mon-Sun)
    """
    cal = France()

    if cal.is_holiday(date):
        # If Mon-Friday
        if date.weekday() in range(5):
            return 0.
        else:
            return 1.
    else:
        if date.weekday() in range(5):
            return 1.
        else:
            return 0.



def generate_weather_conditions(temperature, temp_type):
    """
    This function generates the weather conditions using a mini-type trapezium distribution
    the temperature and its type
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


def generate_training_testing_dataset(store_id, transactions, meteo_day, max_days=2500,
                                      single_barcode=0):
    """
    This function generates the training and testing data
    :param store_id the id of the store
    :param transactions the data containing all transactions
    :param meteo_day data containing the meted data
    :param max_days the max number of days to use in the training
    :param single_barcode is not None, indicates to only return training for a single
     product whose position depends on single_barcode. If None all products are included
     :return the data with features extracted
    """

    # Get the minimum and maximum of date in the transactions
    min_date = transactions[(transactions['STO_EAN'] == store_id)].min()['TRX_DATETIME'].date()
    max_date = transactions[(transactions['STO_EAN'] == store_id)].max()['TRX_DATETIME'].date()

    # Get the number of days between the two date
    num_days = (max_date - min_date).days

    # Get the list of unique products barcode in the transactions
    products_barcode = transactions['BARCODE'].unique()

    # Only do one single barcode if activated
    if single_barcode is not None:
        products_barcode = [products_barcode[single_barcode]]


    # Array to contain all training data
    all_data_first_level = []

    # For each day and for each product
    for day in xrange(num_days):

        print(day)

        # If we have already considered more days than allowed, stop
        if day > max_days:
            break


        # Get the date corresponding to this day
        date = min_date + pd.DateOffset(day)
        # Get the weather of the date
        weather = get_weather_on_date(date, meteo_day, store_id).head(n=1)

        # If the weather is empty we skip this day
        if weather.empty:
            continue

        # For each product to include
        for product_barcode in products_barcode:

            # Get the volume and inventory data
            volume = get_volume_product_on_date(product_barcode, date, store_id, transactions)

            # If no volume could be found skip this date,product pair
            if volume is None:
                continue

            # Get the type of the current date
            day_type = generate_day_type(date)


            # Generating complex features based on the simpler one

            # This contains respectively yesterday, the day before yesterday and the same day as current one in
            # previous week
            yesterday = date - pd.DateOffset(1)
            two_days_ago = date - pd.DateOffset(2)
            one_week_ago = date - pd.DateOffset(7)

            # Get the day type of yesterday and 2 days ago
            day_type_yesterday = generate_day_type(yesterday)
            day_type_2days_ago = generate_day_type(two_days_ago)

            # Get the volume of yesterday, 2days ago and 1 week ago
            volume_yesterday = get_volume_product_on_date(product_barcode, yesterday, store_id, transactions)
            volume_2days_ago = get_volume_product_on_date(product_barcode, two_days_ago, store_id, transactions)
            volume_one_week_ago = get_volume_product_on_date(product_barcode, one_week_ago, store_id, transactions)


            # Get the total sales and the total weight of product done yesterday, 2 days ago and 1 week ago
            volume_price_yesterday = 0
            volume_weight_yesterday = 0
            if volume_yesterday is not None:
                volume_price_yesterday = volume_yesterday["price"]
                volume_weight_yesterday = volume_yesterday["weight"]

            volume_price_2days_ago = 0
            volume_weight_2days_ago = 0
            if volume_2days_ago is not None:
                volume_price_2days_ago = volume_2days_ago["price"]
                volume_weight_2days_ago = volume_2days_ago["weight"]

            volume_price_one_week_ago = 0
            volume_weight_one_week_ago = 0
            if volume_one_week_ago is not None:
                volume_price_one_week_ago = volume_one_week_ago["price"]
                volume_weight_one_week_ago = volume_one_week_ago["weight"]



            # Using historical weather data
            weather_yesterday = get_weather_on_date(yesterday, meteo_day, store_id).head(n=1)
            temperature_min_yesterday = 0
            temperature_max_yesterday = 0
            if not weather_yesterday.empty:
                temperature_min_yesterday = weather_yesterday['TEMPERATURE_VALUE_MIN'].values[0]
                temperature_max_yesterday = weather_yesterday['TEMPERATURE_VALUE_MIN'].values[0]


            #tmp = [weather['TEMPERATURE_VALUE_MIN'].values[0], weather['TEMPERATURE_VALUE_MAX'].values[0],
            #       weather['PRECIPITATION_VALUE'].values[0], weather['SUNSHINE_DURATION'].values[0],
            #       weather['SNOW_DEPTH'].values[0], day_type, volume["price"], volume["weight"]]


            # Saving Features
            tmp = [weather['TEMPERATURE_VALUE_MIN'].values[0], weather['TEMPERATURE_VALUE_MAX'].values[0],
                   day_type, volume["price"], volume_price_yesterday,volume_weight_yesterday,
                   volume_price_2days_ago, volume_weight_2days_ago,
                   volume_price_one_week_ago, volume_weight_one_week_ago, temperature_min_yesterday,
                   temperature_max_yesterday,day_type_yesterday, day_type_2days_ago,
                   volume["weight"]]

            all_data_first_level.append(tmp)

    return all_data_first_level


def get_preprocess_data():

    # Reading transaction
    trans = read_transactions()

    # Eliminating row containing missing data
    trans = trans.dropna()

    # Reading meteo data
    md = read_meteo_day()

    return np.asarray(generate_training_testing_dataset(settings.DIJON_ID, trans, md), dtype=np.float)


if __name__ == "__main__":
    """
    Main module
    """

    # These are just for quick testing of this module
    products = read_product()

    # trans.loc[1][1]
    trans = read_transactions()

    md = read_meteo_day()

    mw = read_meteo_week()

    temp = read_temp()

    get_weather_on_date(pd.to_datetime('01/07/2014'), md, settings.DIJON_ID)



