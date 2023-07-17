from settings_env import db_user, db_pass, db_host, db_port, db_name

_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
