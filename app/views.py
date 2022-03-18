from django.shortcuts import render, redirect
from django.db import connection 
from django.http import HttpResponse  

def new_request(request):
    context = {}
    status = ''
               
    if request.POST:
        with connection.cursor() as cursor:
            
        #How to store email of current login user
        
        #Checking return later than borrow
            if request.POST['return_date'] < request.POST['borrow_date']:
                status = 'Please ensure return date is later than borrow date'
            else:
                cursor.execute("INSERT INTO request (item, category, date_needed, time_needed, return_date, return_time, meetup_location) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        , [ request.POST['item'], request.POST['category'], request.POST['borrow_date'], request.POST['borrow_time'], request.POST['return_date'], request.POST['return_time'], request.POST['location'] ])
                return redirect('home')  
            
    context['status'] = status
    return render(request, 'app/new_request.html', {})



def home(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT item, loaner, date_needed, time_needed, (return_date - date_needed) as duration FROM request ORDER BY date_needed ASC")
        requests = cursor.fetchall()

    result_dict = {'requests': requests}
    request.session['email'] = email 
    return render(request,'app/home.html',result_dict)

def index(request):
    """Shows the main page"""
    
    #Login
    if request.POST:    
        with connection.cursor() as cursor:
            cursor.execute("SELECT school_email, password FROM users WHERE school_email = %s AND password = %s", [request.POST['school_email'],request.POST['password']])
            account = cursor.fetchone()
            email = request.POST['school_email']
           
        context = {}
        status = ''
        request.session['email'] = email     
        if account == None:
            status = 'Wrong Login Details'
        elif request.POST['school_email'] == 'admin' and request.POST['password'] == '123456':
            return redirect('home_admin')
        else:
            return render(request, "app/home.html", {"email" : email})
        
        context['status'] = status
        return render(request, "app/index.html", context)
    
    #with connection.cursor() as cursor:
        #cursor.execute("SELECT * FROM users ORDER BY name")
        #users = cursor.fetchall()

    #result_dict = {'records': users}

    return render(request,'app/index.html',{})

def logout(request):
   try:
      del request.session['email']
   except:
      pass
   return HttpResponse("<strong>You are logged out.</strong>")

# Create your views here.
def index_ori(request):
    """Shows the main page"""

    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE customerid = %s", [request.POST['school_email']])

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY name")
        users = cursor.fetchall()

    result_dict = {'records': users}

    return render(request,'app/index.html',result_dict)

# Create your views here.
def view(request, id):
    """Shows the main page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [request.POST['customerid']])
            customer = cursor.fetchone()
            ## No customer with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO customers VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['dob'] , request.POST['since'], request.POST['customerid'], request.POST['country'] ])
                return redirect('index')    
            else:
                status = 'Customer with ID %s already exists' % (request.POST['customerid'])


    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, id):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE customers SET first_name = %s, last_name = %s, email = %s, dob = %s, since = %s, country = %s WHERE customerid = %s"
                    , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                        request.POST['dob'] , request.POST['since'], request.POST['country'], id ])
            status = 'Customer edited successfully!'
            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/edit.html", context)

def create_account(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE school_email = %s", [request.POST['school_email']])
            user = cursor.fetchone()
            ## No customer with same id
            if user == None:
                ##TODO: date validation
                if len(request.POST['password']) <6:
                    status = 'Password need to be at least 6 characters'
                
                elif not (request.POST['school_email']).endswith('@u.nus.edu'):
                    status = 'Please use your NUS email address'
                
                else:
                    cursor.execute("INSERT INTO users (name, school_email, password) VALUES (%s, %s, %s)"
                        , [ request.POST['name'], request.POST['school_email'], request.POST['password'] ])
                
                                   
                    return redirect('index')    
            else:
                status = 'User with ID %s already exists' % (request.POST['school_email'])


    context['status'] = status
 
    return render(request, "app/register.html", context)

def profile(request):
    with connection.cursor() as cursor: 
        cursor.execute("SELECT * FROM users WHERE school_email=%s", [request.session['email']]) 
        full_profile= cursor.fetchall()
        cursor.execute("SELECT * FROM request WHERE loaner=%s", [request.session['email']])
        requests= cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE owner= %s", [request.session['email']])
        loans=cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE borrower=%s", [request.session['email']])
        borrowed=cursor.fetchall()
        cursor.execute("SELECT * FROM vouchers WHERE owner_of_voucher=%s", [request.session['email']])
        vouchers=cursor.fetchall() 
    profile_dict = {'full_profile': full_profile, 'requests':requests, 'loans': loans, 'borrowed':borrowed, 'vouchers':vouchers}
    return render(request,'app/profile.html',profile_dict)
    
def voucher(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vouchers")
        vouchers=cursor.fetchall()
    vouchers_dict={'vouchers':vouchers}
    return render(request,'app/voucher.html',vouchers_dict)


