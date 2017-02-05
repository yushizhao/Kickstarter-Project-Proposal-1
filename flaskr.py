import os
import pandas as pd
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
from bokeh.charts import Bar, output_file, show
from bokeh.embed import components

# configuration
DATABASE = 'flaskr.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'Yushi'
PASSWORD = 'Yushi'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()
		
@app.route('/', methods=['GET', 'POST'])
def show_category_state():
    db = get_db()
    category_state = pd.read_sql_query(
"""SELECT * FROM CategoryState;""",
    db)
    p = Bar(category_state, 
            label='category', values='COUNT(*)', agg='sum', group='state',
            title="How many projects reached their minimum funding goal?", 
            legend='top_right')
    if request.method == 'POST':
        if request.form['viz'] == 'Plot':
            subcategory_state = category_state[category_state.category == request.form['category']]
            p_sub = Bar(subcategory_state, 
                    label='subcategory', values='COUNT(*)', agg='sum', group='state',
                    title="under category %s"%request.form['category'], 
                    legend='top_right')		
            return render_template('layout.html', bokeh_plot = components(p), plot_sub = components(p_sub))
    return render_template('layout.html', bokeh_plot = components(p), plot_sub = None)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 33507))
    # app.run(host='0.0.0.0', port=port)
    app.run()
