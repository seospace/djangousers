import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_REGISTRATION_ACTIVATOR_SETTINGS = {
    'REGISTRATION_FROM_EMAIL': 'from@test.email',
    'REGISTRATION_MAX_AGE': 50000,
    'REGISTRATION_SECRET_KEY': 'secret_tes234324',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates',),
            os.path.join(BASE_DIR, 'tests/templates', ),
        ]
        ,
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