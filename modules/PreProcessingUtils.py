from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np


class GetDummies(BaseEstimator, TransformerMixin):
       
    def __init__(self):
        self.enc = None
        
    def fit(self, X, y=None):
        self.enc = OneHotEncoder(handle_unknown='ignore', sparse=False)

        self.enc.fit(X)
        
            
        return self
    
    def transform(self, X):
        out = self.enc.transform(X)
        self.categorical_dimension = out.shape[1]
        
        return pd.DataFrame(out)
    
    def get_categorical_dimension(self):
        return self.categorical_dimension
    
    
    
#spliteo estratificadamente en base al sold quantity
def split_train_test(dataset, split_ratio, seed, efective_sample = 30):
    
    
    train_set = pd.DataFrame()
    test_set = pd.DataFrame()
    
    #sampleo estratificado por sold quantity para garantizar la existencia dee muestras de todos  los grupos
    for cat in dataset.sold_quantity.unique():
        stratum = dataset[dataset['sold_quantity'] == cat].copy()
        
        #sampleo una cantidad determinada para que quede balanceeado, ya  que existe un desbalance importantre entre grupos
        #efective_sample = frac * total => frac = efective_sample / total
        if stratum.shape[0] > efective_sample:
            frac = efective_sample / stratum.shape[0]
        else:
            #si hay meenos muestras que efective_sample, entonces considero todo
            frac = 1 
            
        stratum = stratum.sample(frac=frac, random_state=1) 
        stratum = stratum.reset_index(drop=True)
        
        #mezclo los  indices y separo en train y test
        shuffled_indices = np.random.RandomState(seed=seed).permutation(len(stratum))
        train_set_size = int(len(stratum) * split_ratio)
        train_indices = shuffled_indices[:train_set_size]
        test_indices = shuffled_indices[train_set_size:]
        
        train_stratum = stratum.iloc[train_indices]
        test_stratum = stratum.iloc[test_indices]
        
        train_set = pd.concat([train_set, train_stratum], ignore_index=True)
        test_set = pd.concat([test_set, test_stratum], ignore_index=True)
        
    return train_set, test_set


#spliteo estratificadamente en base al sold quantity
def sample_cat(dataset, seed, efective_sample = 30):
    
    
    data_df = pd.DataFrame()
    
    
    #sampleo estratificado por sold quantity para garantizar la existencia dee muestras de todos  los grupos
    for cat in dataset.sold_quantity.unique():
        stratum = dataset[dataset['sold_quantity'] == cat].copy()
        
        #sampleo una cantidad determinada para que quede balanceeado, ya  que existe un desbalance importantre entre grupos
        #efective_sample = frac * total => frac = efective_sample / total
        if stratum.shape[0] > efective_sample:
            frac = efective_sample / stratum.shape[0]
        else:
            #si hay meenos muestras que efective_sample, entonces considero todo
            frac = 1 
            
        stratum = stratum.sample(frac=frac, random_state=1) 
        stratum = stratum.reset_index(drop=True)
        
        #mezclo los  indices 
        shuffled_indices = np.random.RandomState(seed=seed).permutation(len(stratum))
        stratum = stratum.iloc[shuffled_indices]

        data_df = pd.concat([data_df, stratum], ignore_index=True)
        
        
    return data_df