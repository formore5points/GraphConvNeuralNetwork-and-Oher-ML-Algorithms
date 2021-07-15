# -*- coding: utf-8 -*-
"""GraphProject

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JfWgyVoxP3fMoz99Wv-4NMAhnZoGG4Nq
"""

!pip install spektral
import numpy as np
import os
import networkx as nx
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import shuffle
from sklearn.metrics import classification_report

from tensorflow.keras.utils import to_categorical

from spektral.layers import GCNConv

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dropout, Dense
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping
import tensorflow as tf
from tensorflow.keras.regularizers import l2

from collections import Counter
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

from sklearn.naive_bayes import GaussianNB, CategoricalNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn import metrics


def limit_data(labels,limit=20,val_num=500,test_num=1000):

    label_counter = dict((l, 0) for l in labels)
    train_idx = []

    for i in range(len(labels)):
        label = labels[i]
        if label_counter[label]<limit:
            train_idx.append(i)
            label_counter[label]+=1
        
        if all(count == limit for count in label_counter.values()):
            break
    
    rest_idx = [x for x in range(len(labels)) if x not in train_idx]
    val_idx = rest_idx[:val_num]
    test_idx = rest_idx[val_num:(val_num+test_num)]
    return train_idx, val_idx,test_idx


def encode_label(labels):
    label_encoder = LabelEncoder()
    labels = label_encoder.fit_transform(labels)
    labels = to_categorical(labels)
    return labels, label_encoder.classes_


def plot_tSNE(labels_encoded,x_tsne):
    color_map = np.argmax(labels_encoded, axis=1)
    plt.figure(figsize=(10,10))
    for cl in range(num_classes):
        indices = np.where(color_map==cl)
        indices = indices[0]
        plt.scatter(x_tsne[indices,0], x_tsne[indices, 1], label=cl)
    plt.legend()
    plt.show()


all_data = []
all_edges = []

for root,dirs,files in os.walk('/content/drive/MyDrive/cora'):
    for file in files:
        if '.content' in file:
            with open(os.path.join(root,file),'r') as f:
                all_data.extend(f.read().splitlines())
        elif 'cites' in file:
            with open(os.path.join(root,file),'r') as f:
                all_edges.extend(f.read().splitlines())   
                
random_state = 77
all_data = shuffle(all_data,random_state=random_state)

labels = []
nodes = []
X = []

for i,data in enumerate(all_data):
    elements = data.split('\t')
    labels.append(elements[-1])
    X.append(elements[1:-1])
    nodes.append(elements[0])

X = np.array(X,dtype=int)
N = X.shape[0]
F = X.shape[1]

edge_list=[]
for edge in all_edges:
    e = edge.split('\t')
    edge_list.append((e[0],e[1]))

print('\nNumber of nodes (N): ', N)
print('\nNumber of features (F) of each node: ', F)
print('\nCategories: ', set(labels))

num_classes = len(set(labels))
print('\nNumber of classes: ', num_classes)

train_idx,val_idx,test_idx = limit_data(labels)

train_mask = np.zeros((N,),dtype=bool)
train_mask[train_idx] = True

val_mask = np.zeros((N,),dtype=bool)
val_mask[val_idx] = True

test_mask = np.zeros((N,),dtype=bool)
test_mask[test_idx] = True

labels_encoded, classes = encode_label(labels)

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edge_list)

A = nx.adjacency_matrix(G)
print('Graph info: ', nx.info(G))

plt.figure(figsize=(12,6))
nx.draw(G, node_size=5, node_color='lightgreen')

channels = 16
dropout = 0.5
l2_reg = 5e-4
learning_rate = 1e-2
epochs = 200
es_patience = 10

A = GCNConv.preprocess(A).astype('f4')

X_in = Input(shape=(F, ))
fltr_in = Input((None, ), sparse=True)

dropout_1 = Dropout(dropout)(X_in)
graph_conv_1 = GCNConv(channels,
                         activation='relu',
                         kernel_regularizer=l2(l2_reg),
                         use_bias=False)([dropout_1, fltr_in])

dropout_2 = Dropout(dropout)(graph_conv_1)
graph_conv_2 = GCNConv(num_classes,
                         activation='softmax',
                         use_bias=False)([dropout_2, fltr_in])

model = Model(inputs=[X_in, fltr_in], outputs=graph_conv_2)
optimizer = Adam(learning_rate=learning_rate)
model.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              weighted_metrics=['acc'])
model.summary()

tbCallBack_GCN = tf.keras.callbacks.TensorBoard(
    log_dir='./Tensorboard_GCN_cora',
)
callback_GCN = [tbCallBack_GCN]

validation_data = ([X, A], labels_encoded, val_mask)
model.fit([X, A],
          labels_encoded,
          sample_weight=train_mask,
          epochs=epochs,
          batch_size=N,
          validation_data=validation_data,
          shuffle=False,
          callbacks=[
              EarlyStopping(patience=es_patience,  restore_best_weights=True),
              tbCallBack_GCN
          ])


X_te = X[test_mask]
A_te = A[test_mask,:][:,test_mask]
y_te = labels_encoded[test_mask]

y_pred = model.predict([X_te, A_te], batch_size=N)
report = classification_report(np.argmax(y_te,axis=1), np.argmax(y_pred,axis=1), target_names=classes)
print('GCN Classification Report: \n {}'.format(report))


layer_outputs = [layer.output for layer in model.layers]
activation_model = Model(inputs=model.input, outputs=layer_outputs)
activations = activation_model.predict([X,A],batch_size=N)

x_tsne = TSNE(n_components=2).fit_transform(activations[3])
plot_tSNE(labels_encoded,x_tsne)

es_patience = 10
optimizer = Adam(lr=1e-2)
l2_reg = 5e-4
epochs = 200

model_fnn = Sequential()
model_fnn.add(Dense(
                    128,
                    input_dim=X.shape[1],
                    activation=tf.nn.relu,
                    kernel_regularizer=tf.keras.regularizers.l2(l2_reg))
             )
model_fnn.add(Dropout(0.5))
model_fnn.add(Dense(256, activation=tf.nn.relu))
model_fnn.add(Dropout(0.5))
model_fnn.add(Dense(num_classes, activation=tf.keras.activations.softmax))


model_fnn.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              weighted_metrics=['acc'])


tbCallBack_FNN = TensorBoard(
    log_dir='./Tensorboard_FNN_cora',
)

validation_data_fnn = (X, labels_encoded, val_mask)
model_fnn.fit(
                X,labels_encoded,
                sample_weight=train_mask,
                epochs=epochs,
                batch_size=N,
                validation_data=validation_data_fnn,
                shuffle=False,
                callbacks=[
                  EarlyStopping(patience=es_patience,  restore_best_weights=True),
                  tbCallBack_FNN
          ])



y_pred = model_fnn.predict(X_te)
report = classification_report(np.argmax(y_te,axis=1), np.argmax(y_pred,axis=1), target_names=classes)
print('FCNN Classification Report: \n {}'.format(report))


layer_outputs = [layer.output for layer in model_fnn.layers] 
activation_model = Model(inputs=model_fnn.input, outputs=layer_outputs)
activations = activation_model.predict([X])


x_tsne = TSNE(n_components=2).fit_transform(activations[3])
plot_tSNE(labels_encoded,x_tsne)


labels_2 = []

for i in labels_encoded:
    if i[0] == 1:
        labels_2.append(classes[0])
    elif i[1] == 1:
        labels_2.append(classes[1])
    elif i[2] == 1:
        labels_2.append(classes[2])
    elif i[3] == 1:
        labels_2.append(classes[3])
    elif i[4] == 1:
        labels_2.append(classes[4])
    elif i[5] == 1:
        labels_2.append(classes[5])
    elif i[6] == 1:
        labels_2.append(classes[6])


labels_2_y = []

for i in y_te:
    if i[0] == 1:
        labels_2_y.append(classes[0])
    elif i[1] == 1:
        labels_2_y.append(classes[1])
    elif i[2] == 1:
        labels_2_y.append(classes[2])
    elif i[3] == 1:
        labels_2_y.append(classes[3])
    elif i[4] == 1:
        labels_2_y.append(classes[4])
    elif i[5] == 1:
        labels_2_y.append(classes[5])
    elif i[6] == 1:
        labels_2_y.append(classes[6])


gnb = GaussianNB()
gnb.fit(X, labels_2)
pred_point = gnb.predict(X_te)
print("Gaussian Naive Bayes\nAccuracy: ", metrics.accuracy_score(labels_2_y, pred_point))
report = classification_report(labels_2_y, pred_point, target_names=classes)
print(report)

cnb = CategoricalNB()
cnb.fit(X, labels_2)
pred_point = cnb.predict(X_te)
print("Categorical Naive Bayes\nAccuracy: ", metrics.accuracy_score(labels_2_y, pred_point))
report = classification_report(labels_2_y, pred_point, target_names=classes)
print(report)


classifier = KNeighborsClassifier(n_neighbors=1)
classifier.fit(X, labels_2)
y_pred = classifier.predict(X_te)
print("Knn with K = 3\nAccuracy: ", metrics.accuracy_score(labels_2_y, y_pred))
report = classification_report(labels_2_y, y_pred, target_names=classes)
print(report)


classifier = svm.SVC(kernel="linear", C=1)
model = classifier.fit(X, labels_2)
predicted = classifier.predict(X=X_te)
print("Support Vector Machine\nAccuracy: ", metrics.accuracy_score(labels_2_y, predicted))
report = classification_report(labels_2_y, predicted, target_names=classes)
print(report)

"""DİĞER VERİ SETİ"""

all_data = []
all_edges = []

for root,dirs,files in os.walk('/content/drive/MyDrive/citeseer'):
    for file in files:
        if '.content' in file:
            with open(os.path.join(root,file),'r') as f:
                all_data.extend(f.read().splitlines())
        elif 'cites' in file:
            with open(os.path.join(root,file),'r') as f:
                all_edges.extend(f.read().splitlines())   
                
random_state = 77
all_data = shuffle(all_data,random_state=random_state)      

labels = []
nodes = []
X = []

for i,data in enumerate(all_data):
    elements = data.split('\t')
    labels.append(elements[-1])
    X.append(elements[1:-1])
    nodes.append(elements[0])

X = np.array(X,dtype=int)
N = X.shape[0]
F = X.shape[1]

edge_list=[]
for edge in all_edges:
    e = edge.split('\t')
    edge_list.append((e[0],e[1]))

print('\nNumber of nodes (N): ', N)
print('\nNumber of features (F) of each node: ', F)
print('\nCategories: ', set(labels))

num_classes = len(set(labels))
print('\nNumber of classes: ', num_classes)

train_idx,val_idx,test_idx = limit_data(labels)

train_mask = np.zeros((N,),dtype=bool)
train_mask[train_idx] = True

val_mask = np.zeros((N,),dtype=bool)
val_mask[val_idx] = True

test_mask = np.zeros((N,),dtype=bool)
test_mask[test_idx] = True

labels_encoded, classes = encode_label(labels)

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edge_list)


A = nx.adjacency_matrix(G)
A = A[0:3312,0:3312]
print('Graph info: ', nx.info(G))

plt.figure(figsize=(12,6))
nx.draw(G, node_size=5, node_color='lightgreen')

channels = 16
dropout = 0.5
l2_reg = 5e-4
learning_rate = 1e-2
epochs = 200
es_patience = 10

A = GCNConv.preprocess(A).astype('f4')

X_in = Input(shape=(F, ))
fltr_in = Input((None, ), sparse=True)

dropout_1 = Dropout(dropout)(X_in)
graph_conv_1 = GCNConv(channels,
                         activation='relu',
                         kernel_regularizer=l2(l2_reg),
                         use_bias=False)([dropout_1, fltr_in])

dropout_2 = Dropout(dropout)(graph_conv_1)
graph_conv_2 = GCNConv(num_classes,
                         activation='softmax',
                         use_bias=False)([dropout_2, fltr_in])


model = Model(inputs=[X_in, fltr_in], outputs=graph_conv_2)
optimizer = Adam(learning_rate=learning_rate)
model.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              weighted_metrics=['acc'])
model.summary()

tbCallBack_GCN = tf.keras.callbacks.TensorBoard(
    log_dir='./Tensorboard_GCN_cora',
)
callback_GCN = [tbCallBack_GCN]


validation_data = ([X, A], labels_encoded, val_mask)
model.fit([X, A],
          labels_encoded,
          sample_weight=train_mask,
          epochs=epochs,
          batch_size=N,
          validation_data=validation_data,
          shuffle=False,
          callbacks=[
              EarlyStopping(patience=es_patience,  restore_best_weights=True),
              tbCallBack_GCN
          ])


X_te = X[test_mask]
A_te = A[test_mask,:][:,test_mask]
y_te = labels_encoded[test_mask]

y_pred = model.predict([X_te, A_te], batch_size=N)
report = classification_report(np.argmax(y_te,axis=1), np.argmax(y_pred,axis=1), target_names=classes)
print('GCN Classification Report: \n {}'.format(report))

layer_outputs = [layer.output for layer in model.layers]
activation_model = Model(inputs=model.input, outputs=layer_outputs)
activations = activation_model.predict([X,A],batch_size=N)


x_tsne = TSNE(n_components=2).fit_transform(activations[3])
plot_tSNE(labels_encoded,x_tsne)

es_patience = 10
optimizer = Adam(lr=1e-2)
l2_reg = 5e-4
epochs = 200


model_fnn = Sequential()
model_fnn.add(Dense(
                    128,
                    input_dim=X.shape[1],
                    activation=tf.nn.relu,
                    kernel_regularizer=tf.keras.regularizers.l2(l2_reg))
             )
model_fnn.add(Dropout(0.5))
model_fnn.add(Dense(256, activation=tf.nn.relu))
model_fnn.add(Dropout(0.5))
model_fnn.add(Dense(num_classes, activation=tf.keras.activations.softmax))


model_fnn.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              weighted_metrics=['acc'])


tbCallBack_FNN = TensorBoard(
    log_dir='./Tensorboard_FNN_cora',
)


validation_data_fnn = (X, labels_encoded, val_mask)
model_fnn.fit(
                X,labels_encoded,
                sample_weight=train_mask,
                epochs=epochs,
                batch_size=N,
                validation_data=validation_data_fnn,
                shuffle=False,
                callbacks=[
                  EarlyStopping(patience=es_patience,  restore_best_weights=True),
                  tbCallBack_FNN
          ])



y_pred = model_fnn.predict(X_te)
report = classification_report(np.argmax(y_te,axis=1), np.argmax(y_pred,axis=1), target_names=classes)
print('FCNN Classification Report: \n {}'.format(report))


layer_outputs = [layer.output for layer in model_fnn.layers] 
activation_model = Model(inputs=model_fnn.input, outputs=layer_outputs)
activations = activation_model.predict([X])


x_tsne = TSNE(n_components=2).fit_transform(activations[3])
plot_tSNE(labels_encoded,x_tsne)


labels_2 = []

for i in labels_encoded:
    if i[0] == 1:
        labels_2.append(classes[0])
    elif i[1] == 1:
        labels_2.append(classes[1])
    elif i[2] == 1:
        labels_2.append(classes[2])
    elif i[3] == 1:
        labels_2.append(classes[3])
    elif i[4] == 1:
        labels_2.append(classes[4])
    elif i[5] == 1:
        labels_2.append(classes[5])
    elif i[6] == 1:
        labels_2.append(classes[6])


labels_2_y = []

for i in y_te:
    if i[0] == 1:
        labels_2_y.append(classes[0])
    elif i[1] == 1:
        labels_2_y.append(classes[1])
    elif i[2] == 1:
        labels_2_y.append(classes[2])
    elif i[3] == 1:
        labels_2_y.append(classes[3])
    elif i[4] == 1:
        labels_2_y.append(classes[4])
    elif i[5] == 1:
        labels_2_y.append(classes[5])
    elif i[6] == 1:
        labels_2_y.append(classes[6])


gnb = GaussianNB()
gnb.fit(X, labels_2)
pred_point = gnb.predict(X_te)
print("Gaussian Naive Bayes\nAccuracy: ", metrics.accuracy_score(labels_2_y, pred_point))
report = classification_report(labels_2_y, pred_point, target_names=classes)
print(report)

cnb = CategoricalNB()
cnb.fit(X, labels_2)
pred_point = cnb.predict(X_te)
print("Categorical Naive Bayes\nAccuracy: ", metrics.accuracy_score(labels_2_y, pred_point))
report = classification_report(labels_2_y, pred_point, target_names=classes)
print(report)

classifier = KNeighborsClassifier(n_neighbors=3)
classifier.fit(X, labels_2)
y_pred = classifier.predict(X_te)
print("Knn with K = 3\nAccuracy: ", metrics.accuracy_score(labels_2_y, y_pred))
report = classification_report(labels_2_y, y_pred, target_names=classes)
print(report)

classifier = svm.SVC(kernel="linear", C=1)
model = classifier.fit(X, labels_2)
predicted = classifier.predict(X=X_te)
print("Support Vector Machine\nAccuracy: ", metrics.accuracy_score(labels_2_y, predicted))
report = classification_report(labels_2_y, predicted, target_names=classes)
print(report)

