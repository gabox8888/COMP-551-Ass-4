import numpy as np
import csv
import random
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)

min_dist = 1000

def cluster_data(X,plot=False,clusters=5,state=1):
    colors = []
    for i in range(clusters):
        colors.append(np.random.rand(3,1))
    coords = list(map(lambda x: x[7:9],X))
    coords = np.asarray(coords)
    x_coords = list(map(lambda x: [x[0]],coords))
    y_coords = list(map(lambda x: [x[1]],coords))
    kmeans = KMeans(n_clusters=clusters, random_state=state).fit(coords)
    labels = kmeans.labels_
    cluster_sizes = list(range(clusters))
    for i in labels:
        cluster_sizes[i] += 1
    # print(cluster_sizes)
    if plot:
        for i,x in enumerate(labels):
            plt.scatter(x_coords[i], y_coords[i], s=80, c=colors[x])
        plt.show()
    [x.append(labels[i]) for i,x in enumerate(X)]
    return X


def load_data(csv_all):
    all_points = csv.DictReader(open(csv_all))
    X = []
    Y = [] 
    abs_num = 0
    pre_num = 0
    for x,row in enumerate(all_points):
        if row['status'] == '0.0' and float(row['distance']) > min_dist:
            temp = [row['May_Mean_Temp1'],row['May_Mean_Precip1'],row['Slope'],row['Elevation'],row['FlowDir'],row['FlowAcc_Flow1'],row['StreamO_over1'],row['decimalLongitude'],row['decimalLatitude'],row['distance'],row['status']]
            temp = list(map(lambda x : float(x) if x != '' else 0, temp))
            X.append(temp)
            Y.append(row['status'])
            abs_num += 1
        elif row['status'] == '1.0':
            temp = [row['May_Mean_Temp1'],row['May_Mean_Precip1'],row['Slope'],row['Elevation'],row['FlowDir'],row['FlowAcc_Flow1'],row['StreamO_over1'],row['decimalLongitude'],row['decimalLatitude'],row['distance'],row['status']]
            temp = list(map(lambda x : float(x) if x != '' else 0, temp))
            X.append(temp)
            Y.append(row['status'])
            pre_num += 1
    print("Absence Size: {}, Presence Size: {}".format(abs_num,pre_num))
    return X,Y

# baseline model
def create_baseline():
	# create model
	model = Sequential()
	model.add(Dense(5, input_dim=6, init='normal', activation='relu'))
	# model.add(Dense(6, input_dim=8, init='normal', activation='sigmoid'))
	# model.add(Dense(6, input_dim=6, init='normal', activation='relu'))
	model.add(Dense(6, input_dim=5, init='normal', activation='relu'))
	model.add(Dense(1, init='normal', activation='sigmoid'))
	# Compile model
	model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
	return model

def validation_train_split(X,Y,clusters=5):
    cluster_list = list(range(clusters))
    random.shuffle(cluster_list)
    split = int(clusters * 0.7)
    train_list = cluster_list[:split]
    val_list = cluster_list[split:]
    x_train = []
    y_train = []
    x_val = []
    y_val =[]
    for i,x in enumerate(X):
        if x[11] in train_list:
            x_train.append(x[:7])
            y_train.append(Y[i])
        else:
            x_val.append(x[:7])
            y_val.append(Y[i])
    x_train = np.asarray(x_train)
    y_train = np.asarray(y_train)
    x_val = np.asarray(x_val)
    y_val = np.asarray(y_val)

    return x_train, y_train, x_val, y_val

def save_data(data,csv_file):
    with open(csv_file, "w",newline='') as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows(data)

def main():
    X,Y = load_data('../data/everything_clean.csv')
    # print(X)
    new_X = cluster_data(X,plot=False,clusters=50,state=20)

    x_train,y_train,x_val,y_val = validation_train_split(new_X,Y,clusters=100)
    x_train = np.delete(x_train,4,1)
    x_val = np.delete(x_val,4,1)
    # save_data(new_X,"../data/completed_final_asian_carp.csv")
    # evaluate model with standardized dataset
    # estimator = KerasClassifier(build_fn=create_baseline, nb_epoch=10, batch_size=500, verbose=1)
    # estimator.fit(x_train,y_val)
    # y_pred = estimator.predict(x_val)
    # kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed)
    # results = cross_val_score(estimator, X, Y, cv=kfold)

    model = create_baseline()
    model.fit(x_train, y_train, nb_epoch=200, batch_size=500)
    loss_and_metrics = model.evaluate(x_val, y_val, batch_size=500)

    print(loss_and_metrics)

if __name__ == '__main__': main() 