from django.utils.translation import ugettext_lazy as _

BACKEND_POSTGRESQL_PSYCOPG2 = 1
BACKEND_POSTGRESQL = 2
BACKEND_MYSQL = 3
BACKEND_SQLITE3 = 4
BACKEND_ORACLE = 5

BACKEND_CHOICES = (
    (BACKEND_POSTGRESQL_PSYCOPG2, _('PostgreSQL (psycopg2)')),
    (BACKEND_POSTGRESQL, _('PostgreSQL')),
    (BACKEND_MYSQL, _('MySQL')),
    (BACKEND_SQLITE3, _('SQLite')),
    (BACKEND_ORACLE, _('Oracle')),
)

BACKEND_CLASSES = {
    BACKEND_POSTGRESQL_PSYCOPG2: 'django.db.backends.postgresql_psycopg2',
    BACKEND_POSTGRESQL: 'django.db.backends.postgresql',
    BACKEND_MYSQL: 'django.db.backends.mysql',
    BACKEND_SQLITE3: 'django.db.backends.sqlite3',
    BACKEND_ORACLE: 'django.db.backends.oracle',
}
