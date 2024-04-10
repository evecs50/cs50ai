import csv
import sys
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    # print(f'Loaded {len(evidence)} number of data points')
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )
    # print('Train-test split')
    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    # print('Done predictions')
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

    sensitivity, specificity = evaluate(y_test, my_knn(1, X_train, y_train, X_test))
    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - 0 Administrative, an integer
        - 1 Administrative_Duration, a floating point number
        - 2 Informational, an integer
        - 3 Informational_Duration, a floating point number
        - 4 ProductRelated, an integer
        - 5 ProductRelated_Duration, a floating point number
        - 6 BounceRates, a floating point number
        - 7 ExitRates, a floating point number
        - 8 PageValues, a floating point number
        - 9 SpecialDay, a floating point number
        - 10 Month, an index from 0 (January) to 11 (December)
        - 11 OperatingSystems, an integer
        - 12 Browser, an integer
        - 13 Region, an integer
        - 14 TrafficType, an integer
        - 15 VisitorType, an integer 0 (not returning) or 1 (returning)
        - 16 Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    month_mapping = {
        "Jan": 0,
        "Feb": 1,
        "Mar": 2,
        "Apr": 3,
        "May": 4,
        "June": 5,
        "Jul": 6,
        "Aug": 7,
        "Sep": 8,
        "Oct": 9,
        "Nov": 10,
        "Dec": 11
    }

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        evidence = []
        label = []
        for row in reader:
            data = {h:d for h,d in zip(header, row)}
            data['Administrative'] = int(data['Administrative'])
            data['Administrative_Duration'] = float(data['Administrative_Duration'])
            data['Informational'] = int(data['Informational'])
            data['Informational_Duration'] = float(data['Informational_Duration'])
            data['ProductRelated'] = int(data['ProductRelated'])
            data['ProductRelated_Duration'] = float(data['ProductRelated_Duration'])
            data['BounceRates'] = float(data['BounceRates'])
            data['ExitRates'] = float(data['ExitRates'])
            data['PageValues'] = float(data['PageValues'])
            data['SpecialDay'] = float(data['SpecialDay'])
            data['Month'] = month_mapping[data['Month']]
            data['OperatingSystems'] = int(data['OperatingSystems'])
            data['Browser'] = int(data['Browser'])
            data['Region'] = int(data['Region'])
            data['TrafficType'] = int(data['TrafficType'])
            data['VisitorType'] = 1 if data['VisitorType'] == 'Returning_Visitor' else 0
            data['Weekend'] = 1 if data['Weekend'] == 'TRUE' else 0
            data['Revenue'] = 1 if data['Revenue'] == 'TRUE' else 0
            data = list(data.values())
            evidence.append(data[:-1])
            label.append(data[-1])

    return evidence, label


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_positives = sum((l == 1 and p == 1) for l, p in zip(labels, predictions))
    positives = sum(labels)
    true_negatives = sum((l == 0 and p == 0) for l, p in zip(labels, predictions))
    negatives = len(labels) - sum(labels)
    sensitivity = true_positives / positives
    specificity = true_negatives / negatives
    return sensitivity, specificity

def my_knn(k, x_train, y_train, x_test):
    t1 = time.time()
    # distance = np.linalg.norm(np.array(x_train)[:,np.newaxis] - np.array(x_test), axis=2)
    y_test = [0 for i in range(len(x_test))]
    for i in range(len(x_test)):
        distance = [np.linalg.norm(np.array(x_test[i])-y) for y in np.array(x_train)]
        argmin_dist = np.argmin(distance)
        y_test[i] = y_train[argmin_dist]
    t2 = time.time()
    print(f'time used: {t2-t1}')
    ##return y_test
    t3 = time.time()
    y_test = [0 for i in range(len(x_test))]
    distance = [0 for j in range(len(x_train))]
    for i in range(len(x_test)):
        for j in range(len(x_train)):
            distance[j] = sum((a-b)*(a-b) for a, b in zip(x_test[i], x_train[j]))
        argmin_dist = np.argmin(distance)
        y_test[i] = y_train[argmin_dist]
    print(f'y_test length{len(y_test)}:')
    print(y_test[0:3])
    t4 = time.time()
    print(f'time used {t4-t3}')
    return y_test

if __name__ == "__main__":
    main()
