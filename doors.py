# all the imports
import psycopg2
import psycopg2.extras
import sys
import os
import urlparse
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack

# configuration
PROD = False
DATABASE = 'Door'
DEBUG = True
SECRET_KEY = 'door@manypossiblities-109834'
DB_USERNAME = 'postgres'
DB_PASSWORD = '123456'
HOST = 'localhost' 
USERNAME = 'IAMHERO'
PASSWORD = 'qsc@WDV'

app = Flask(__name__)
app.config.from_object(__name__)

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	top = _app_ctx_stack.top
	if not hasattr(top, 'postgres_db'):
		if os.environ.get('DATABASE_URL') is None:
			postgres_db = psycopg2.connect(database=app.config['DATABASE'], user=app.config['DB_USERNAME'], host=app.config['HOST'],  password=app.config['DB_PASSWORD'])
		else:
			url = urlparse.urlparse(os.environ["DATABASE_URL"])
			postgres_db =psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)

		top.postgres_db = postgres_db

	return top.postgres_db

@app.teardown_appcontext
def close_db_connection(exception):
	"""Closes the database again at the end of the request."""
	top = _app_ctx_stack.top
	if hasattr(top, 'postgres_db'):
		top.postgres_db.close()

#admin pages
@app.route('/super')
def admin_index():
	if not session.get('admin_logged_in'):
		return redirect(url_for('admin_login'))
	db = get_db()
	cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	cur.execute('''SELECT   * FROM   public."BestBooks"''')
	books = cur.fetchall()
	
	return render_template('show_entries.html', books=books)

@app.route('/super/<itemid>', methods=['GET', 'POST'])
def admin_item_detail(itemid):
	if not session.get('admin_logged_in'):
		return redirect(url_for('admin_login'))
	error = None
	if request.method == "POST":
		book_type = request.form['selectType']
		book_name = request.form['txtName']
		book_SubTitle = request.form['txtSubTitle']
		book_affUrl = request.form['txtAffUrl']
		book_page = request.form['txtPages']
		book_desc = request.form['txtDesc']
		book_pub = request.form['txtPub']
		book_lang = request.form['txtLang']
		book_isbn10 = request.form['txtISBN10']
		book_isbn13 = request.form['txtISBN13']
		book_review = request.form['txtReview']
		book_rank = request.form['txtRank']



		db = get_db()
		cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		cur.execute('''UPDATE "BestBooks"
   						SET "Type"=%s, "Name"=%s, "SubTitle"=%s, "AffiliateURL"=%s, "Desc"=%s, "Pages"=%s, 
       					"Publisher"=%s, "Language"=%s, "ISBN10"=%s, "ISBN13"=%s, "AvgCustReview"=%s, 
       					"AmazonRank"=%s
 						WHERE "BestBooks"."ID" = %s''', (book_type, book_name, book_SubTitle, book_affUrl, 
 							book_desc, book_page, book_pub, book_lang, book_isbn10, book_isbn13, book_review, book_rank, itemid))

		db.commit()
		return redirect(url_for('admin_index'))
	elif request.method == "GET":

		db = get_db()
		cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		cur.execute('''SELECT   * FROM   public."BestBooks" where "BestBooks"."ID" = %s''', (itemid))
		book = cur.fetchone()	
		return render_template('show_item.html',book=book)



@app.route('/super/add', methods=['GET', 'POST'])
def admin_item_add():
	if not session.get('admin_logged_in'):
		return redirect(url_for('admin_login'))
	error = None
	if request.method == "POST":
		book_type = request.form['selectType']
		book_name = request.form['txtName']
		book_SubTitle = request.form['SubTitle']
		book_affUrl = request.form['txtAffUrl']
		book_page = request.form['txtPages']
		book_desc = request.form['txtDesc']
		book_pub = request.form['txtPub']
		book_lang = request.form['txtLang']
		book_isbn10 = request.form['txtISBN10']
		book_isbn13 = request.form['txtISBN13']
		book_review = request.form['txtReview']
		book_rank = request.form['txtRank']

		db = get_db()
		cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		cur.execute('''INSERT INTO "BestBooks"(
            "Type", "Name", "SubTitle", "AffiliateURL", "Desc", "Pages", "Publisher", 
            "Language", "ISBN10", "ISBN13", "AvgCustReview", "AmazonRank")
		    VALUES (%s, %s, %s, %s, %s, %s, %s, 
		            %s, %s, %s, %s, %s)''', (book_type, book_name, book_SubTitle, book_affUrl, 
 							book_desc, book_page, book_pub, book_lang, book_isbn10, book_isbn13, book_review, book_rank))
		db.commit()

		return redirect(url_for('admin_index'))

	elif request.method == "GET":
		return render_template('show_item.html')

@app.route('/asksupercode', methods=['GET', 'POST'])
def admin_login():
	error = None
	if request.method == 'POST':
		if request.form['superCode'].lower() != app.config['USERNAME'].lower():
			error = 'You are not SuperMan'
		elif request.form['superPass'] != app.config['PASSWORD']:
			error = 'You are not SuperMan'
		else:
			session['admin_logged_in'] = True
			return redirect(url_for('admin_index'))
	return render_template('admin_login.html', error=error)


#portal pages
@app.route('/')
def portal_index():
	db = get_db()
	cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	cur.execute('''SELECT   * FROM   "BestBooks" where "BestBooks"."Deleted" != True OR "BestBooks"."Deleted" IS NULL Order by "BestBooks"."AvgCustReview", "BestBooks"."AmazonRank"''')
	books = cur.fetchall()
	
	return render_template('public/index.html', books=books)	

if __name__ == '__main__':
	app.run()
