"""Deglitch utility"""

import numpy as np
import pandas as pd

def remove_spikes(x_data, y_spiky_data, threshold=3):
    # convert data to pandas DataFrame
    df = pd.DataFrame(y_spiky_data);
    df['filtered'] = pd.rolling_median(df, window=3, center=True).fillna(method='bfill').fillna(method='ffill')
    diff = df['filtered'].as_matrix()-y_spiky_data
    mean = diff.mean()
    sigma = (y_spiky_data-mean)**2
    sigma = np.sqrt(sigma.sum()/float(len(sigma)))
    ynew = np.where(abs(diff) > threshold * sigma, df['filtered'].as_matrix(), y_spiky_data)	
    return ynew
