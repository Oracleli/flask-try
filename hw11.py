import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

 
 

# configuration
DATABASE = 'flaskdemo.db'  #Specifying the location od the database
DEBUG = True               #debug mode turned on
SECRET_KEY = 'kerker123^^' #the secret key for sessions
USERNAME = 'user'
PASSWORD = 'pass'

#create application
app=Flask(__name__)
app.config.from_object(__name__)


 
 
 
@app.before_request
def befure_request():
    g.db = connect_db()
    
@app.teardown_request
def teardawn_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()




@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        namelist = g.db.execute('select username from userlist')
        namelist=[row[0] for row in namelist.fetchall()]
        if request.form['username'] in namelist:
            error = 'Existed username, please choose another username'
            return render_template('register.html', error=error)
        elif request.form['password']=='':
            error = 'please enter password'
            return render_template('register.html', error=error)
        else:
            g.db.execute('insert into userlist (username, password) values (?, ?)',
               [request.form['username'], request.form['password']])            
            g.db.commit()
            flash('sucessfully register')
            return redirect(url_for('show_entries'))
    return render_template('register.html', error=error)
    



@app.route('/')
def show_entries():
    if session.get('logged_in'):
        cur = g.db.execute('select title, text, id from entries where username=(?) order by id desc',
                      [session['logged_user']])
        entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]
        return render_template('show_entries.html', entries=entries)
    return render_template('login.html')


@app.route('/del', methods=['POST'])
def del_favorite():
    if not session.get('logged_in'):
        abort(401)
 #   selected=request.form.getlist('deletelist')
 #   any_selected = bool(selected)
 #   return(any_selected)
    for i in request.form.getlist('deletelist'):
        g.db.execute('delete from entries where username=(?) and id=(?)',[session['logged_user'],str(i)])
        g.db.commit() 
    flash('Your website was successfully deleted')
    return redirect(url_for('show_entries'))
    #return(request.form['deletelist'])

       
    



   


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    #g.db.execute('delete from entries where username=(?)',[session['logged_user']])
    #g.db.commit()    
    g.db.execute('insert into entries (username,title, text) values (?, ?, ?)',
               [session['logged_user'], request.form['title'], request.form['text']])
    g.db.commit()
    flash('Your text was successfully updated')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select username, password from userlist where username=(?) ',
                       [request.form['username']])
        check = cur.fetchall()
        if request.form['username'] != check[0][0]:
            error = 'Invalid username'
        if request.form['password'] != check[0][1]:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['logged_user'] = request.form['username'] 
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)





 
@app.route('/logout')
def logout():
    #session.pop('logged_user', None)
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

#    app.run(threaded=True)


if __name__ == '__main__':
    app.run()

