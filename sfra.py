from flask import Flask,render_template,request,redirect,url_for,session
import ibm_db
import re
 
app = Flask(__name__)

app.secret_key='a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLServerCertificate=Cert.crt;UID=pcj17018;PWD=MPcY3wjqbL7MbLBm",'','')


@app.route('/')
def home():
    session['loggedin']=False
    session['cart']=0
    dsql="TRUNCATE TABLE CART IMMEDIATE"
    dstmt=ibm_db.prepare(conn,dsql)
    ibm_db.execute(dstmt)
    return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    global userid
    msg=''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username=? AND password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if(account):
            session['loggedin']=True
            session['id']=account['USERNAME']
            userid = account['USERNAME']
            session['USERNAME']=account['USERNAME']
            msg='Welcome %s!'%userid
            return render_template('home.html',msg=msg)
        else:
            msg="Incorrect username/password"
    return render_template('login.html',msg=msg)



@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM users WHERE username=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg='Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='Name must contain only characters and numbers!'
        else:
            insert_sql ="INSERT INTO users VALUES(?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,password)
            ibm_db.execute(prep_stmt)
            msg='you have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form'
    return render_template('register.html',msg=msg)

@app.route('/alogin',methods=['GET','POST'])
def alogin():
    global adminid
    msg=''

    if request.method == 'POST':
        aname = request.form['aname']
        apassword = request.form['apassword']
        sql = "SELECT * FROM ADMIN WHERE NAME=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,aname)
        ibm_db.bind_param(stmt,2,apassword)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if(account):
            session['aloggedin']=True
            session['aid']=account['NAME']
            adminid = account['NAME']
            session['NAME']=account['NAME']
            msg='Welcome %s!'%adminid
            return render_template('admin.html',msg=msg)
        else:
            msg="Incorrect username/password"
    return render_template('adminlogin.html',msg=msg)



@app.route('/areg',methods=['GET','POST'])
def aregister():
    msg=''
    if request.method == 'POST':
        username = request.form['aname']
        email = request.form['aemail']
        password = request.form['apassword']
        sql = "SELECT * FROM ADMIN WHERE NAME=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg='Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='Name must contain only characters and numbers!'
        else:
            insert_sql ="INSERT INTO admin VALUES(?,?,?)"
            prep_stmt=ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,password)
            ibm_db.execute(prep_stmt)
            msg='you have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form'
    return render_template('adminreg.html',msg=msg)

@app.route('/home')
def homepage():
    if session['loggedin']==True:
        msg='Welcome %s!'%userid
        return render_template('home.html',msg=msg)
    else:
        msg='Please Login!'
        return render_template('login.html',msg=msg)

@app.route('/shop')
def shop():
    if session['loggedin']==True:
        return render_template('shop.html')
    else:
        msg="Please Login!"
        return render_template('login.html',msg=msg)

@app.route('/product/<p1>')
def product(p1):
    img = 'https://sajee.s3.ap.cloud-object-storage.appdomain.cloud/products/%s.jpg' %p1
    print(img)
    product=p1
    sql="SELECT * FROM PRODUCT WHERE NAME =?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,product)
    ibm_db.execute(stmt)
    pro_sql="SELECT PRICE,PRONAME FROM PRODUCT WHERE NAME =?"
    pro_stmt=ibm_db.prepare(conn,pro_sql)
    ibm_db.bind_param(pro_stmt,1,product)
    ibm_db.execute(pro_stmt)
    tuple=ibm_db.fetch_tuple(pro_stmt)
    print(tuple)
    price=tuple[0]
    name=tuple[1]
    return render_template('product.html',img=img,price=price,name=name,product=product)

@app.route('/admin')
def admin():
    if session['aloggedin']==True:
        msg='Welcome %s!'%adminid
        return render_template('admin.html',msg=msg)
    else:
        msg='Please Login!'
        return render_template('adminlogin.html',msg=msg)

@app.route('/logout')
def logout():
    session['loggedin']=False
    session.pop('id',None)
    session.pop('USERNAME',None)
    return render_template('login.html')

@app.route('/alogout')
def alogout():
    session['aloggedin']=None
    session.pop('aid',None)
    session.pop('NAME',None)
    return render_template('adminlogin.html')

@app.route('/cart')
def cart():
    if session['loggedin']==True:
        sql_c="SELECT COUNT(NAME) FROM CART"
        stmt_c=ibm_db.prepare(conn,sql_c)
        ibm_db.execute(stmt_c)
        count1=ibm_db.fetch_tuple(stmt_c)
        print(count1[0])
        count=count1[0]
        name=[]
        price=[]
        link=[]
        proname=[]
        for i in range(count):
            cart_sql="SELECT NAME, PRICE, IMG, ID FROM CART WHERE NO=?"
            cart_stmt=ibm_db.prepare(conn,cart_sql)
            ibm_db.bind_param(cart_stmt,1,i)
            ibm_db.execute(cart_stmt)
            cart=ibm_db.fetch_tuple(cart_stmt)
            name[i]=cart[0]
            price[i]=cart[1]
            link[i]=cart[2]
            proname[i]=cart[3]
        print(link)
        return render_template('cart.html',count=count,name=name,link=link,price=price,proname=proname)
    else:
        msg='Please Login!'
        return render_template('login.html',msg=msg)


@app.route('/addcart/<product>')
def add_cart(product):
    p=product
    sql="SELECT NAME,PRICE,LINK,PRONAME FROM PRODUCT WHERE NAME=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,p)
    ibm_db.execute(stmt)
    cart=ibm_db.fetch_tuple(stmt)
    id=cart[0]
    price=cart[1]
    img=cart[2]
    name=cart[3]
    session['cart']=session['cart']+1
    count=session['cart']
    isql="INSERT INTO CART VALUES(?,?,?,?,?)"
    istmt=ibm_db.prepare(conn,isql)
    ibm_db.bind_param(istmt,1,count)
    ibm_db.bind_param(istmt,2,id)
    ibm_db.bind_param(istmt,3,img)
    ibm_db.bind_param(istmt,4,name)
    ibm_db.bind_param(istmt,5,price)
    ibm_db.execute(istmt)
    msg='successfully added to cart!'
    return render_template('home.html',msg=msg)

@app.route('/buy/<product>')
def buy(product):
    p=product
    sql="SELECT NAME,PRICE FROM PRODUCT WHERE NAME=?"
    stmt=ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,p)
    ibm_db.execute(stmt)
    cart=ibm_db.fetch_tuple(stmt)
    name=cart[0]
    price=cart[1]
    id=session['id']
    sql_c="SELECT COUNT(NAME) FROM BUY"
    stmt_c=ibm_db.prepare(conn,sql_c)
    ibm_db.execute(stmt_c)
    count1=ibm_db.fetch_tuple(stmt_c)
    print(count1[0])
    count=count1[0]+1
    buy_sql="INSERT INTO BUY values(?,?,?,?)"
    buy_stmt=ibm_db.prepare(conn,buy_sql)
    ibm_db.bind_param(buy_stmt,1,count)
    ibm_db.bind_param(buy_stmt,2,id)
    ibm_db.bind_param(buy_stmt,3,name)
    ibm_db.bind_param(buy_stmt,4,price)
    ibm_db.execute(buy_stmt)
    msg='Successfully Purchased!'
    return render_template('home.html',msg=msg)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')