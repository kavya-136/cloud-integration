from functools import lru_cache
from pathlib import Path

from django.conf import settings

import joblib


def get_model_path(kind):
    if kind == 'prediction':
        return Path(settings.ML_MODEL_PATH)
    if kind == 'anomaly':
        return Path(settings.ANOMALY_MODEL_PATH)
    raise ValueError('Unsupported model kind.')


@lru_cache(maxsize=2)
def load_model(kind):
    model_path = get_model_path(kind)
    trusted_dir = (Path(settings.BASE_DIR) / 'ml' / 'models').resolve()
    resolved_path = model_path.resolve()
    if not resolved_path.is_relative_to(trusted_dir):
        raise ValueError('Model path must be inside ml/models.')
    if not model_path.exists():
        raise FileNotFoundError(f'Model file not found: {model_path}')
    if model_path.suffix != '.pkl':
        raise ValueError('Unsupported model file format. Expected .pkl files.')

    return joblib.load(resolved_path)
