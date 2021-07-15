# TextClassification using GraphConvNeuralNetwork-and-Other-ML-Algorithms
Text classification using Graph Convolutional Neural Network and other Machine Learning Algorithms (Graph Theory Term Project)

# INTRODUCTION

There are many problems that natural language processing deals with today. The problem we want to deal with is text classification, which is one of its subcategories. We aim to solve this problem, which is seen as one of the difficult problems, using graph structures and various machine learning algorithms, especially neural networks.  

Text classification is the process of categorizing the text into a group of words. Text classification can automatically analyze text and then assign a set of predefined tags or categories based on its context. Therefore, the goal of this project is to graph the article and then classify it using GCN (Graph Convolutional Neural Networks) and understand what the article is.

When the articles are considered as a text type, can the words used here, and the meaning obtained by associating be analyzed by the computer? Can a computer understand what type of article is written by doing text analysis? Words are key to understanding what genre the article is about. These keys and relationships can be categorized by introducing them to the computer. 

In this study, we compared 6 different machine learning algorithms using 2 different datasets. Of course, the main topic of our study is the performance of GCN.

# Graph Convolutional Neural Network

![resim](https://user-images.githubusercontent.com/50989796/125816456-21fda870-826d-4a13-a54c-eed9693ee95e.png)

GCNs are a very powerful neural network architecture for machine learning on graphs. In fact, they are so powerful that even a randomly initiated 2-layer GCN can produce useful feature representations of nodes in networks. If you are familiar with convolution layers in Convolutional Neural Networks, ‘convolution’ in GCNs is basically the same operation. It refers to multiplying the input neurons with a set of weights that are commonly known as filters or kernels. The filters act as a sliding window across the whole image and enable CNNs to learn features from neighboring cells. 

There are 2 main types of GCN's that are used for prediction.

1)	Node Level Prediction
2)	Graph Level Prediction

# Models
1) Graph Convolutional Neural Network
2) Fully Connected Neural Network
3) Gaussian Naïve Bayes
4) Categorical Naïve Bayes
5) K-Nearest Neighbor
6) Support Vector Machine

# Data Sets
1) Cora
2) Citeseer

# Final Results

![resim](https://user-images.githubusercontent.com/50989796/125816898-64363f49-abdb-4fe8-8908-0677fb2b972d.png)

# Example Screenshots

GCN Visualization using t-SNE

![resim](https://user-images.githubusercontent.com/50989796/125817184-59cb9fc1-349c-4fce-ab41-9372a92441d6.png)

FCN Visualization using t-SNE

![resim](https://user-images.githubusercontent.com/50989796/125817198-af786ab1-c71d-4787-89ad-3cc0f2f0c9de.png)

# Graph Screenshots

Cora

![resim](https://user-images.githubusercontent.com/50989796/125817248-fd866157-3768-48f4-beed-3d550af788f9.png)

Citeseer

![resim](https://user-images.githubusercontent.com/50989796/125817279-bd45c827-c5e9-4599-ae6b-880b314e59b2.png)


