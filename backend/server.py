from backend import app
from mangum import Mangum

handler = Mangum(app)
