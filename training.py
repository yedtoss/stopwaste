__author__ = 'yedtoss'

import xgboost as xgb
import preprocess
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score
from sklearn.cross_validation import train_test_split
import numpy as np




def compute_relative_absolute_error(y_true, y_pred):

    return 100.*np.sum(abs(y_true-y_pred)/y_true)/len(y_true)

def compute_relative_mean_error(y_true, y_pred):

    return

def train():

    datas = preprocess.get_preprocess_data()

    X = datas[:, :-1]
    y = datas[:, datas.shape[1]-1]

    print(X.shape, y.shape)

    X = X.astype(np.float)
    y = y.astype(np.float)



    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    gbm = xgb.XGBRegressor(max_depth=30, n_estimators=100, learning_rate=0.05).fit(X_train, y_train)

    predictions = gbm.predict(X_test)

    print(mean_absolute_error(y_test, predictions))

    print(compute_relative_absolute_error(y_test, predictions))

    #xgb.plot_importance(gbm)



if __name__ == "__main__":
    train()





