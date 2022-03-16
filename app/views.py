from django.shortcuts import render, redirect
from django.db import connection

def new_request(request):
    context = {}
    status = ''
    import datetime
    
    def validate_date(d):
        try:
            d_obj = datetime.strptime(d, "%Y-%m-%d")
            d_s = datetime.strftime(d_obj, "%Y-%m-%d")
        except:
            status = 'Please input date as YYYY-MM-DD'
    
    def validate_time(t):
        try:
            t_obj = datetime.strptime(t, "%H-%M")
            t_s = datetime.strftime(t_obj, "%H:%M:%S")
        except:
            status = 'Please input date as HH:MM'
                
    #if request.POST:
        #How to store email of current login user
        
        #Checking date format
        #if not validaterequest.POST['borrow_date']
        #elif:
        
        #elif:
        
        #else:
            
        
    return render(request, 'app/new_request.html', {})



def home(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT item, loaner, date_needed, time_needed, return FROM request ORDER BY date_needed ASC")
        requests = cursor.fetchall()

    result_dict = {'requests': requests}

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
            
        if account == None:
            status = 'Wrong Login Details'
        else:
            return render(request, "app/home.html", {'email' : email})
        
        context['status'] = status
        return render(request, "app/index.html", context)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY name")
        users = cursor.fetchall()

    result_dict = {'records': users}

    return render(request,'app/index.html',result_dict)

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
