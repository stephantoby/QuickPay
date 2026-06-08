from app import create_app 
from flask import render_template 

app = create_app()  #builds the app and creates an instance we could use

@app.route('/')
def root():
    return render_template('homepage.html')



if __name__ == "__main__":  
    app.run(debug=True, port=5000) 

