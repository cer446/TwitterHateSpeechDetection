#!/usr/bin/env python

""" Utilities for transforming text into a numerical representation """

from collections import Counter
import numpy as np
from torch.autograd import Variable
import torch

def build_vocab(vocab_size, text_vector):
    """
    finds vocabulary of most common words
    vocab_size: maximum number of words in vocabulary
    text_vector: vector containing cleaned text
    """
    vocab = Counter()
    for text in text_vector:
        for word in text.split(' '):
            vocab[word.lower()]+=1
    vocab = dict(vocab.most_common(vocab_size))
    return vocab

def build_idx(vocab):
    """
    maps words to indexes and indexes to words
    """
    word2index = {}
    index2word = {}

    word2index['PAD'] = 0
    index2word[0] = 'PAD'

    word2index['UNK'] = 1
    index2word[1] = 'UNK'

    for i,word in enumerate(vocab):
        word2index[word.lower()] = i+2
        index2word[i+2] = word.lower()

    return word2index, index2word

def load_glove(path):
    """
    creates a dictionary mapping words to vectors from a file in glove format.
    """
    with open(path) as f:
        glove = {}
        for line in f.readlines():
            values = line.split()
            word = values[0]
            vector = np.array(values[1:], dtype='float32')
            glove[word] = vector
        return glove

def build_weights_matrix(vectors, custom_vectors, index2word, size = 200):
    """
    creates matrix of weights for initializing model
    """
    weights_matrix = np.zeros((len(index2word), size))
    words_found = 0
    words_found_custom = 0

    for i, word in index2word.items():
        try: 
            weights_matrix[i] = vectors[index2word[i]]
            words_found += 1
        except KeyError:
            try:
                weights_matrix[i] = custom_vectors[index2word[i]]
                words_found_custom +=1
            except KeyError:
                weights_matrix[i] = np.random.rand(size)

    #initialize pad embedding to zero
    weights_matrix[0, ] = np.zeros(size)

    print ('words_found: ' + str(words_found/len(index2word)) + \
        ' additional_words_found: ' + str(words_found_custom/len(index2word)))

    return weights_matrix

def sort_batch(X, y, lengths):
    lengths, indx = lengths.sort(dim=0, descending=True)
    X = X[indx]
    y = y[indx]
    return X, y, lengths

def get_validation_predictions(validation_data_loader, model):
    predictions = []
    pred_labels = []
    #get training predictions
    it = iter(validation_data_loader)
    num_batch = len(validation_data_loader)
    # Loop over all batches
    for i in range(num_batch):
        batch_x,batch_y,batch_len = next(it)
        batch_x,batch_y,batch_len = sort_batch(batch_x,batch_y,batch_len)
        tweets = Variable(batch_x.transpose(0,1))
        batch_labels = Variable(batch_y)
        lengths = batch_len.numpy()
        outputs = model(tweets, lengths)
        _, pred = torch.max(outputs.data, 1)
        predictions.extend(list(pred.numpy()))
        pred_labels.extend(list(batch_labels.data.numpy()))
    return predictions, pred_labels

