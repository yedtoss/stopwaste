__author__ = 'yedtoss'

import os


# Base path of the data
BASE_DATA_PATH = '/Users/yedtoss/Documents/Projects/Back2Hack/carrefour_data'

# Name of the product data
PRODUCT_FILENAME = os.path.join(BASE_DATA_PATH, '01_ConsoTrendTopic/01_Products/F_Products_01_01.csv')

# Name of the transaction data
TRANSACTION_FILENAME = os.path.join(BASE_DATA_PATH,
                                    '01_ConsoTrendTopic/02_SalesTransactions/F_SalesTransactions_01_02.csv')


# Name of the meteo per day data
METEO_DAY_FILENAME = os.path.join(BASE_DATA_PATH,
                                    '00_Common/02_Meteo/meteo_day.csv')


# Name of the meteo per week data
METEO_WEEK_FILENAME = os.path.join(BASE_DATA_PATH,
                                    '00_Common/02_Meteo/meteo_week.csv')


# Name of the temperature
TEMP_FILENAME = os.path.join(BASE_DATA_PATH,
                                    '00_Common/02_Meteo/TEMP_MAG_2016.csv')


# Global identifier of the dijon store
DIJON_ID = 3020470420000

# Global identifier of the caen store
CAEN_ID = 3021080300300


TRANSACTION_IDX = {

    "EAN": 0
}


METEO_DAY_IDX = {

    "EAN": 3,
    "DAY": 0
}