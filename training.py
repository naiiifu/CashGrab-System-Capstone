from sklearn.neural_network  import MLPClassifier

from joblib import dump
import json
import numpy as np

decTreeFile = 'decisionTree.joblib'

trainingSet = "./trainingSet.json"
validationSet = "./trainingSet.json"

def Validate(validationSet):
    global clf

    jsonObj = loadJson(validationSet)
    (data, labels) = formatData(jsonObj)

    correct = 0
    incorrect = 0

    assert(len(data) == len(labels))

    for i in range(0, len(data)):
        result = clf.predict([data[i]])

        if(result == [labels[i]]):
            correct = correct + 1
        else:
            incorrect = incorrect + 1
    
    print("correct: {correct}".format(correct=correct))
    print("incorrect: {incorrect}".format(incorrect=incorrect))

def loadJson(path):
    with open(path, 'r') as f:
        data = json.load(f)
        return data

def formatData(jsonObj):
    data = []
    labels = []

    for entry in jsonObj:
        #dataArray = np.column_stack((entry["dim4"], entry["dim8"]))
        dataArray = np.float32(entry["dim8"])
        data.append(dataArray.reshape(-1))
        labels.append(entry["value"])
    
    return (data, labels)

if __name__ == "__main__":
    global data
    global labels
    jsonObj = loadJson(trainingSet)
    (data, labels) = formatData(jsonObj)

    global clf
    clf = MLPClassifier(max_iter = 20000)
    clf.fit(data, labels)

    # does this even do anything?
    # MLPClassifier(...)

    Validate(validationSet)

    # serialize tree
    dump(clf, decTreeFile) 
