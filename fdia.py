# -*- coding: utf-8 -*-
"""FDIA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Gm-1v2Ni_W6SA2nVlWa-qGThd38gf6CX

# False Data Injection Attack Detection

A false data injection attack is when an external entity will insert false readings into networks collecting data from sensors. Machine Learning can be used to identify the attacks within the data.
Stages:
- Generate large data set of some kind with standard un-compromised readings
- Overwrite some readings with compromised, false readings
- Throw ML at the data
- Produce a large deep learning architecture to identify FDIA

## Data Set

- Data set is a 14 bus smart grid network. 11 consumer lines taking readings (What we are concerned with). 8 lines where energy is being produced (Wind, Solar, Coal and Gas).
- Consumers take readings of 'LoadMinPower' which is the minimum power needed for a power supply to correctly function. Otherwise, the power supply will flicker, and may go off and on rapidly.
- FDIA may inject incorrect data that damages power supplies by falsifying how much power is needed to maintain power supply health. This would cause damage to power supplies, economic damage repairing supplies and from potential network downtime while repairing. 
- Injection of false data into the acquired LoadMinPower data set from https://zenodo.org/record/1220935 to mimic FDI attack
"""

#importing library for data
import pandas as pd
import numpy as np
import time

#read csv into dataframe
df = pd.read_csv(r'LoadMinPower.csv', sep=',', header=0)
df.head(5)

#Mean of each column
col_means = [np.array(df.get([f'{i}'])).mean() for i in range(1, 12)]
print(f" Means for all columns in the data set: \n{col_means}")

#Variance of each column
col_vars = [np.array(df.get([f'{i}'])).var() for i in range(1, 12)]
print(f" Variance for all columns in the data set: \n{col_vars}")

"""## False Data Injection
- Injecting False data into the data set to mimic a FDIA
- Then convert to appropriate format for ML
- Also need to generate labels. (1 for compromised sensor, 0 for uncompromised).
- Choose random sensors to compromise each time (np.random.choice(1,12)*5) and append a 1 for a compromised sensor, 0 for non
- Do not need to append normal noises as the data set is real, not artificially generated
- Experiment with injecting different L2 norm distances of data and seeing classification accuracy differences
- maybe negate small amounts to mimic an attacker trying to get less power than what is needed, to damage the power supplies
- assume attacker doesn't know mean and variance, so injects tiny decrements in between 0 and 1 to each target

## Data Mining
- injecting into all rows of data
- creation of labels
"""

#to avoid tampering of original df
initial_data = df.copy()

np.random.normal(0.6, 0.15, 5)

#data injecting function
def inject(target):
  #Selecting how many sensors to attack
  sensors_to_attack = np.random.randint(2,6)
  #Indices of target readings
  indices = np.random.choice((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), sensors_to_attack, replace = False) + 2 # skipping first data and time values
  #Getting values to inject, Gaussian distribution 0.1 deviation around 0.2
  values_to_inject = np.random.normal(0.6, 0.15, sensors_to_attack)
  #Negating values from target series
  target[indices] -= values_to_inject
  #return of series after injection
  #print(f"injecting values: {values_to_inject}, at indices: {indices}")
  #print(indices)
  return [target, indices - 2]

#Performing the false data injection
t0 = time.perf_counter()   #timing

features = []
labels = []
#looping through each row in df
for index, values in initial_data.iterrows():
  #if statement to inject half of the data
  if np.random.random() < 0.5:
    #get injected row through function call, passing in series of sensor values
    injected_row = inject(values)
    #append 1 to label of row as this network reading has been compromised
    labels.append(1)
    #append new injected values to features as list
    features.append(list(injected_row[0][2:]))
    #setting row equal to new injected row in dataframe
    initial_data.at[index] = injected_row[0]
  else:
    #append normal values and 0 label as no injection takes place
    features.append(list(values[2:]))
    labels.append(0)

t1 = time.perf_counter()   #timing

#Features and Labels into a numpy array for ML
features = np.array(features)
labels = np.array(labels)

print(f"--------DATA-INJECTED-------- (In {t1-t0} Seconds)")

#Storing features and labels as csv
"""
np.savetxt('features.csv', features, delimiter=',')
np.savetxt('labels.csv', labels, delimiter=',')
features = np.array(pd.read_csv('features.csv'))
labels = np.array(pd.read_csv('labels.csv')).astype(int)
"""

"""## Train and Test Data"""

#sklearn library for machine learning and data selection
from sklearn.model_selection import train_test_split

#train test split to split data into training and test data
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=1, shuffle=True)

"""### Linear Regression Classifier"""

#import needed model
from sklearn.linear_model import LogisticRegression
#metric for accuracy score of classifications
from sklearn.metrics import accuracy_score

#lin reg initialized
lin = LogisticRegression()
#fitting training data
lin.fit(X_train, y_train.ravel())
#getting predictions
lin_preds = lin.predict(X_test)
#accuracy score of Linear Regression Classifier
print(f"Accuracy of Linear Regression: {round(accuracy_score(y_test, lin_preds)*100)}")

"""## Decision Tree Classifier"""

#import decision tree classifier
from sklearn.tree import DecisionTreeClassifier

#decision tree initialized
tree = DecisionTreeClassifier()
#fitting training data
tree.fit(X_train, y_train.ravel())
#getting predictions
tree_preds = tree.predict(X_test)
#accuracy score of Decision Tree Classifier
print(f"Accuracy of Decision Tree: {round(accuracy_score(y_test, tree_preds)*100)}")

"""## KNN Nearest Neighbour Classifier"""

#Import KNN from sklearn
from sklearn.neighbors import KNeighborsClassifier

#KNN classifier
knn_model = KNeighborsClassifier()
#fitting training data
knn_model.fit(X_train, y_train.ravel())
#getting predictions of KNN
knn_predictions = knn_model.predict(X_test)
#Accuracy of KNN
print(f"Accuracy of KNN: {round(accuracy_score(y_test, knn_predictions)*100)}%")

"""## SVM Classifier """

#SVM import
from sklearn.svm import SVC

#Support Vector Machine Implementation
svm = SVC()
#fitting training data
svm.fit(X_train, y_train.ravel())
#predictions of SVM
svm_predictions = svm.predict(X_test)
#accuracy score of SVM
print(f"Accuracy of SVM: {round(accuracy_score(y_test, svm_predictions)*100)}%")

"""## Random Forest Classifier using SKLearn"""

#libraries
from sklearn.ensemble import RandomForestClassifier

#Model initialized
rf_model = RandomForestClassifier(n_estimators=300, max_depth=30)
#fitting training data, 'ravel()' to get in flat matrix form
rf_model.fit(X_train, y_train.ravel())
#getting rf predictions of test data
rf_predictions = rf_model.predict(X_test)
#getting accuracy score of predictions
print(f"Accuracy of Random Forest: {round(accuracy_score(y_test, rf_predictions)*100)}%")

"""## XGBoost Classifier"""

#xgboost library
from xgboost import XGBClassifier

#XGBoost classifier
x_model = XGBClassifier()
#fitting training data
x_model.fit(X_train, y_train.ravel())
#getting predictions of XGBoost
x_predictions = x_model.predict(X_test)
#Accuracy of XGBoost
print(f"Accuracy of XGBoost: {round(accuracy_score(y_test, x_predictions)*100)}%")

"""## Convolutional Neural Network Model Creation using Keras"""

#keras for network implementation
from tensorflow.keras.models import Sequential, save_model, load_model
from tensorflow.keras.layers import Conv1D, Dropout, MaxPool1D, Flatten, Dense, BatchNormalization, LeakyReLU
from tensorflow.keras.callbacks import EarlyStopping

#reshape train data to fit into CNN
X_train_cnn = X_train.copy().reshape(len(X_train), 11, 1)

#callbacks to avoid overfitting
callback = EarlyStopping(monitor='accuracy', patience=4)

"""### CNN1"""

#Building the model
cnn1 = Sequential()
cnn1.add(Conv1D(filters=100, kernel_size=3, strides=1, activation='relu', input_shape=(11,1)))
cnn1.add(Conv1D(filters=200, kernel_size=3, strides=1, padding = 'same', activation='relu'))
cnn1.add(BatchNormalization())
cnn1.add(LeakyReLU())
cnn1.add(Dropout(0.5))
cnn1.add(Conv1D(filters=100, kernel_size=3, strides=1, activation='relu'))
cnn1.add(Dropout(0.5))
cnn1.add(Conv1D(filters=50, kernel_size=3, strides=1, padding = 'same', activation='relu'))
cnn1.add(Dropout(0.5))
cnn1.add(Conv1D(filters=100, kernel_size=3, strides=1, activation='relu'))
#cnn1.add(BatchNormalization())
#cnn1.add(LeakyReLU())
cnn1.add(Flatten())
cnn1.add(Dense(100, activation='relu'))
cnn1.add(Dense(1, activation='sigmoid'))
print(cnn1.summary())
cnn1.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

#Training the model
cnn1.fit(X_train_cnn, y_train, epochs=25, batch_size=500, validation_split=0.2, verbose=2)

"""### CNN2"""

#Building the model
cnn2 = Sequential()
cnn2.add(Conv1D(filters=100, kernel_size=3, strides=1, activation='relu', input_shape=(11,1)))
cnn2.add(Dropout(0.5))
cnn2.add(BatchNormalization())
cnn2.add(LeakyReLU())
cnn2.add(Conv1D(filters=50, kernel_size=3, strides=1, padding = 'same', activation='relu'))
cnn2.add(Dropout(0.5))
cnn2.add(Flatten())
cnn2.add(Dense(100, activation='relu'))
cnn2.add(Dense(1, activation='sigmoid'))
print(cnn2.summary())
cnn2.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

#Training the model
cnn2.fit(X_train_cnn, y_train, epochs=25, batch_size=500, validation_split=0.2, verbose=0)

"""### CNN3"""

#Building the model
cnn3 = Sequential()
cnn3.add(Conv1D(filters=16, kernel_size=2, strides=1, activation='relu', input_shape=(11,1)))
cnn3.add(Dropout(0.5))
cnn3.add(Conv1D(filters=32, kernel_size=2, strides=1, activation='relu', input_shape=(11,1)))
cnn3.add(Flatten())
cnn3.add(Dense(20, activation='relu'))
cnn3.add(Dense(1, activation='sigmoid'))
print(cnn3.summary())
cnn3.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

#Training the model
cnn3.fit(X_train_cnn, y_train, epochs=25, batch_size=500, validation_split=0.2, verbose=0)

"""## CNN Model Accuracy Scores"""

#Reshape test data for scores
X1_test = X_test.copy().reshape(len(X_test), 11, 1)

"""###### CNN1"""

#Predictions with CNN
cnn1_preds = cnn1.evaluate(X1_test, y_test, verbose=0)
#accuracy of CNN1
print(f"Accuracy of CNN1: {round(cnn1_preds[1]*100)}%")

"""###### CNN2"""

#Predictions with CNN
cnn2_preds = cnn2.evaluate(X1_test, y_test, verbose=0)
#accuracy of CNN2
print(f"Accuracy of CNN2: {round(cnn2_preds[1]*100)}%")

"""###### CNN3"""

#Predictions with CNN
cnn3_preds = cnn3.evaluate(X1_test, y_test, verbose=0)
#accuracy of CNN2
print(f"Accuracy of CNN3: {round(cnn3_preds[1]*100)}%")



"""###Testing on new data
- Get LoadMaxPower and create a test data set 
- check accuracy of trained models on new test data set
"""

#Trying random forest (Accuracy 94% on Min Power Data Set)
type(rf_model)

#test data set
testing = pd.read_csv(r'LoadMaxPower.csv', header=0)
testing.head(5)

"""#####Injecting false data into the test data"""

#Performing the false data injection
t0 = time.perf_counter()   #timing

max_features = []
max_labels = []
#looping through each row in df
for index, values in testing.iterrows():
  #if statement to inject half of the data
  if np.random.random() < 0.5:
    #get injected row through function call, passing in series of sensor values
    injected_row = inject(values)
    #append 1 to label of row as this network reading has been compromised
    max_labels.append(1)
    #append new injected values to features as list
    max_features.append(list(injected_row[0][2:]))
    #setting row equal to new injected row in dataframe
    #initial_data.at[index] = injected_row[0]
  else:
    #append normal values and 0 label as no injection takes place
    max_features.append(list(values[2:]))
    max_labels.append(0)

t1 = time.perf_counter()   #timing

#Features and Labels into a numpy array for ML
max_features = np.array(max_features)
max_labels = np.array(max_labels)

print(f"--------DATA-INJECTED-------- (In {t1-t0} Seconds)")

#predicting from data
rf_max_predictions = rf_model.predict(max_features)
#getting accuracy score of predictions
print(f"Accuracy of Random Forest on Max Power Data: {round(accuracy_score(max_labels, rf_max_predictions)*100)}%")

