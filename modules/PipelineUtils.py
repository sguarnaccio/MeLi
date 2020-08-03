import tensorflow as tf
from tensorflow import keras

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)
tf.config.experimental.set_memory_growth(physical_devices[1], True)

from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Reshape
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model

from tensorflow.keras.optimizers import Adam


from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np


class Autoencoder:
    @staticmethod
    def build(feature_dim, hidden_layers=(128, 64), latentDim=32):
        # inicializo el input shape con las dimensiones de los onehot encoding 
        # de mis variables categoricas

        inputShape = (feature_dim, )
        chanDim = -1
        
        # define el input del encoder
        inputs = Input(shape=inputShape)
        x = inputs
        # loop over the number of filters
        for hl in hidden_layers:
            # apply a DENSE => RELU => BN operation
            x = Dense(hl, activation='tanh')(x)
            x = LeakyReLU(alpha=0.2)(x)
            x = BatchNormalization(axis=chanDim)(x)
        # construimos el vector latente o encoding de mis features
        latent = Dense(latentDim)(x)
        # build the encoder model
        encoder = Model(inputs, latent, name="encoder")
        
        
        # start building the decoder model which will accept the
        # output of the encoder as its inputs
        latentInputs = Input(shape=(latentDim,))
        x = Dense(hidden_layers[-1], activation='tanh')(latentInputs)
        x = LeakyReLU(alpha=0.2)(x)
        x = BatchNormalization(axis=chanDim)(x)
        # loop over our number of filters again, but this time in
        # reverse order
        for hl in hidden_layers[-2::-1]:
            # apply a DENSE => RELU => BN operation
            x = Dense(hl, activation='tanh')(x)
            x = LeakyReLU(alpha=0.2)(x)
            x = BatchNormalization(axis=chanDim)(x)
            
        x = Dense(feature_dim)(x)
        outputs = Activation("sigmoid")(x)
        
        # build the decoder model
        decoder = Model(latentInputs, outputs, name="decoder")
        # our autoencoder is the encoder + decoder
        autoencoder = Model(inputs, decoder(encoder(inputs)),
            name="autoencoder")
        # return a 3-tuple of the encoder, decoder, and autoencoder
        return (encoder, decoder, autoencoder)
    
    
class NumericalCategoricalSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names, feature_dimension):
        self.attribute_names = attribute_names
        self.feature_dimension = feature_dimension
        
    def fit(self, X, y=None):
        if 'latitude' in self.attribute_names:
            self.lat_median = X['latitude'].median()
            self.lon_median = X['longitude'].median()
            
        return self
    
    def transform(self, X):
        if 'latitude' in self.attribute_names:
            
            X['latitude'].fillna(self.lat_median, inplace=True)
            X['longitude'].fillna(self.lon_median, inplace=True)
                
            return X[self.attribute_names].values
        
        else:
            return X.iloc[:,-self.feature_dimension:].values
        
        
class DimensionReducer(BaseEstimator, TransformerMixin):
    def __init__(self, feature_dimension, opt = Adam(lr=1e-3), 
                 epoch = 25, batch_size = 32, h_layers = (32, 24), 
                 latent_dim = 16):
        
        self.h_layers = h_layers
        self.latent_dim = latent_dim
        self.feature_dimension = feature_dimension
        self.opt = opt
        
        self.EPOCHS = epoch
        self.BATCH_SIZE = batch_size
        
    def fit(self, X, y=None):
        (self.encoder, self.decoder, self.autoencoder) = Autoencoder.build(self.feature_dimension, 
                                                                           hidden_layers=self.h_layers, 
                                                                           latentDim = self.latent_dim)
        
        self.autoencoder.compile(loss="mse", optimizer=self.opt)
        H = self.autoencoder.fit(
            X, X,
            epochs=self.EPOCHS,
            batch_size=self.BATCH_SIZE)
            
        return self
    
    def transform(self, X):
        return self.encoder.predict(X)