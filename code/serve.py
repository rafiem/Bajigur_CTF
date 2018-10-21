from bajigur import run_app
import os

app = run_app()
app.run(threaded=True,host="0.0.0.0")
