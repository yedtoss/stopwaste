__author__ = 'yedtoss'

import xgboost as xgb
import preprocess
from sklearn.metrics import mean_absolute_error
from sklearn.cross_validation import train_test_split
import numpy as np
from sklearn.svm import SVR


def compute_relative_absolute_error(y_true, y_pred):
    """
    This function compute the relative absolute error in percentage
    :param y_true: the true demand
    :param y_pred:  the forecasted prediction
    :return: the relative absolute error
    """

    return 100.*np.sum(abs(y_true-y_pred)/y_true)/len(y_true)


def train():

    # Getting the data
    datas = preprocess.get_preprocess_data()

    # Separating the features from the label
    X = datas[:, :-1]
    y = datas[:, datas.shape[1]-1]

    #X = X.astype(np.float)
    #y = y.astype(np.float)



    # Splitting the training set into test and validation set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Training using the Gradient Boosting Tree algorithm
    gbm = xgb.XGBRegressor(max_depth=30, n_estimators=100, learning_rate=0.05).fit(X_train, y_train)
    # Testing
    predictions = gbm.predict(X_test)

    # Error for the Gradient Boosting Tree Algorithm
    print('Mean Absolute Error of Gradient Boosting', mean_absolute_error(y_test, predictions))
    print('Mean Relative Error of Gradient Boosting', compute_relative_absolute_error(y_test, predictions))

    # Plotting utility to see relations and importance of each features
    #xgb.to_graphviz(gbm, num_trees=2)


    # Training a deeper Gradient Boosting
    gbm_deep = xgb.XGBRegressor(max_depth=50, n_estimators=200, learning_rate=0.05).fit(X_train, y_train)
    # Testing
    predictions_deep = gbm_deep.predict(X_test)
    # Error for SVM Algorithm
    print('Mean Absolute Error of Deeper Gradient Boosting', mean_absolute_error(y_test, predictions_deep))
    print('Mean Relative Error of Deeper Gradient Boosting', compute_relative_absolute_error(y_test, predictions_deep))

    print('The error of EXP4 is ', run_exp4([gbm, gbm_deep], X_test, y_test))


def run_exp4(algorithms, X_test, y_test):
    """
    This function runs the multi-armed bandit EXP4 algorithm on some algorithms
    and return the overall performance
    :param algorithms: algorithms to learning in online
    :param X_test: the test set
    :param y_test: the true answer
    :return: the mean relative absolute error
    """

    #Get the number of rounds
    T = len(y_test)

    # Get the number of arms
    K = len(algorithms)

    # Set the weights of each arms
    W = np.ones(K)

    # Set the error
    error = 0.



    p = (1./K)*np.ones(K)

    # Set the exploration parameter gamma
    gamma = min(1, np.sqrt(K*np.log(K)/((np.exp(1)-1)*T)))

    for round in range(T):

        # Get advice vectors
        predictions = np.zeros(K)
        for k in range(K):
            predictions[k] = algorithms[k].predict(np.atleast_2d(X_test[round, :]))


        # Set the probabilities of taking each arm
        p = (1-gamma)*W*predictions/np.sum(W) + gamma/K

        # Pick one arm and receives rewards
        action = np.random.choice(range(K), p=p/np.sum(p))
        reward = 1-compute_relative_absolute_error([y_test[round]], predictions[action])
        error += 1-reward

        # Update the weights
        W[action] = W[action]*np.exp(reward*(gamma/K)/p[action])

    return error/T





if __name__ == "__main__":
    train()





