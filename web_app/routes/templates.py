from fastapi.templating import Jinja2Templates
from os.path import join as join_path


templates = Jinja2Templates(directory=join_path("web_app", "templates"))
