import numpy as np
import librosa

def normalizar(v):
    return v / (np.linalg.norm(v) + 1e-9)

def espectro_fft(y):
    """Magnitud FFT normalizada."""
    Y = np.fft.rfft(y)
    mag = np.abs(Y)
    return normalizar(mag)

def mfcc_features(y, sr, n_mfcc=20):
    """MFCC normalizados."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    return normalizar(mfcc_mean)

def similitud(v1, v2):
    """Correlación entre dos vectores."""
    return float(np.corrcoef(v1, v2)[0, 1])
