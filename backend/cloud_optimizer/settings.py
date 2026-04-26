from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-development-key-change-in-production',
)
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'ml',
    'optimizer',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloud_optimizer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloud_optimizer.wsgi.application'
ASGI_APPLICATION = 'cloud_optimizer.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_SECURE = False

ML_MODEL_PATH = config('ML_MODEL_PATH', default=str(BASE_DIR / 'ml' / 'models' / 'model.pkl'))
ANOMALY_MODEL_PATH = config('ANOMALY_MODEL_PATH', default=str(BASE_DIR / 'ml' / 'models' / 'anomaly.pkl'))

CARBON_GRAMS_PER_CPU_HOUR = config('CARBON_GRAMS_PER_CPU_HOUR', default=55.0, cast=float)
CARBON_GRAMS_PER_MEMORY_GB_HOUR = config('CARBON_GRAMS_PER_MEMORY_GB_HOUR', default=8.0, cast=float)

REGION_CARBON_FACTORS = {
    'us-east-1': 1.0,
    'us-west-2': 0.9,
    'eu-central-1': 0.75,
    'ap-south-1': 1.15,
}

REGION_COST_MAPPING = {
    'us-east-1': 1.0,
    'us-west-2': 1.08,
    'eu-central-1': 1.12,
    'ap-south-1': 0.95,
}

CHATBOT_KNOWLEDGE_BASE = {
    'default': 'Ask about budget alerts, sustainability, region optimization, and recommendations.',
    'sustainability': 'Use /optimizer/carbon/ to log emissions and /optimizer/sustainability/ for score.',
    'region': 'Use /optimizer/region-advisor/ to compare costs across regions.',
}
