from app import app, db

@app.routes('/')
def home():
    return render_template('index.html')