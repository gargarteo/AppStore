from django.shortcuts import render, redirect
from django.db import connection 
from django.http import HttpResponse  

def new_request(request):
    context = {}
    status = ''
               
    if request.POST:
        with connection.cursor() as cursor:
        
        #Checking return later than borrow
            if request.POST['return_date'] < request.POST['date_needed']:
                status = 'Please ensure return date is later than borrow date'
            else:
                cursor.execute("INSERT INTO requests(item, loaner, category, date_needed, time_needed,return_date, return_time, meetup_location) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        , [ request.POST['item'], request.session['email'], request.POST['category'], request.POST['date_needed'], request.POST['time_needed'], request.POST['return_date'], request.POST['return_time'], request.POST['meetup_location'] ])
                return redirect('home')  
            
    context['status'] = status
    return render(request, 'app/new_request.html', {})

def admin_home(request):
    ## Suspend customer
    if request.POST:
        if request.POST['action'] == 'suspend_user':
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET suspend = NOT suspend WHERE school_email = %s", [request.POST['school_email']])
                cursor.execute("SELECT * FROM users ORDER BY name ASC")
                users = cursor.fetchall()
                result_dict = {'users': users}
                
                return render(request,'app/admin_home.html',result_dict)
    
    with connection.cursor() as cursor:            
        cursor.execute("SELECT * FROM users ORDER BY name ASC")
        users = cursor.fetchall()

    result_dict = {'users': users}
    return render(request,'app/admin_home.html',result_dict)

def admin_useredit(request, email):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed email
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE school_email = %s", [email])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form
    try:
        if request.POST:
        ##TODO: date validation
            with connection.cursor() as cursor:
                cursor.execute("UPDATE users SET name = %s, demerit_points = %s, vouchers_points = %s, max_request = %s, password = %s WHERE school_email = %s"
                    , [request.POST['name'], request.POST['demerit_points'],
                        request.POST['vouchers_points'] , request.POST['max_request'], request.POST['password'], email ])
                status = 'User edited successfully!'
                cursor.execute("SELECT * FROM users WHERE school_email = %s", [email])
                obj = cursor.fetchone()
    except:
        status = 'Error with updating details, Please ensure points & max request are numerical, length of password is >= 6'


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/admin_useredit.html", context)

def admin_userview(request, email):
    """Shows the main page"""
    #Delete requests
    if request.POST:
        if request.POST['action'] == 'delete_request':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM requests WHERE request_id = %s", [request.POST['request_id']])
    
    with connection.cursor() as cursor: 
        cursor.execute("SELECT * FROM users WHERE school_email=%s", [email]) 
        full_profile= cursor.fetchall()
        cursor.execute("SELECT * FROM requests WHERE loaner=%s", [email])
        requests= cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE owner= %s", [email])
        loan=cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE borrower=%s", [email])
        borrowed=cursor.fetchall()
        cursor.execute("SELECT * FROM vouchers WHERE owner_of_voucher=%s", [email])
        vouchers=cursor.fetchall() 
    profile_dict = {'full_profile': full_profile, 'requests':requests, 'loan': loan, 'borrowed':borrowed, 'voucher':voucher}
    return render(request,'app/admin_userview.html',profile_dict)


def home(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM requests ORDER BY date_needed ASC")
        requests = cursor.fetchall()
    with connection.cursor() as cursor:
        if request.POST:
            if request.POST['action']=="accept_request":
               cursor.execute("SELECT loaner FROM requests WHERE request_id=%s",[request.POST['id']])
               borrower= (cursor.fetchone())[0]
               cursor.execute("SELECT item FROM requests WHERE request_id=%s",[request.POST['id']])
               item= (cursor.fetchone())[0]
               cursor.execute("SELECT date_needed FROM requests WHERE request_id=%s",[request.POST['id']])
               date_borrowed= (cursor.fetchone())[0]
               cursor.execute("SELECT return_date FROM requests WHERE request_id=%s",[request.POST['id']])
               return_deadline= (cursor.fetchone())[0]
               returned_date= return_deadline
               cursor.execute("INSERT INTO loan VALUES (%s, %s, %s, %s, %s, %s, %s)"
                            , [request.POST['id'], borrower, request.session['email'],
                               item , date_borrowed, return_deadline, returned_date])
    result_dict = {'requests': requests}
    return render(request,'app/home.html',result_dict)


def index(request):
    """Shows the main page"""
    
    #Login
    if request.POST:    
        with connection.cursor() as cursor:
            cursor.execute("SELECT school_email, password FROM users WHERE school_email = %s AND password = %s AND suspend = FALSE", [request.POST['school_email'],request.POST['password']])
            account = cursor.fetchone()
            email = request.POST['school_email']
           
        context = {}
        status = ''
        request.session['email'] = email     
        if account == None:
            status = 'Wrong Login Details or your account has been suspended'
        elif request.POST['school_email'] == 'admin@u.nus.edu' and request.POST['password'] == '123456':
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                users = cursor.fetchall()
            result_dict = {'users': users}
            
            return redirect('admin_home')
        #render(request, "app/admin_home.html", {'users': users})
        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM requests")
                requests = cursor.fetchall()
            result_dict = {'requests': requests}
           
            return render(request, "app/home.html", {"requests" : requests})
        
        context['status'] = status
        return render(request, "app/index.html", context)

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
def view_Original(request, id):
    """Shows the main page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add_Original(request):
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
def edit_original(request, id):
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
        cursor.execute("SELECT * FROM requests WHERE loaner=%s", [request.session['email']])
        requests= cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE owner= %s", [request.session['email']])
        loan=cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE borrower=%s", [request.session['email']])
        borrowed=cursor.fetchall()
        cursor.execute("SELECT * FROM vouchers WHERE owner_of_voucher=%s", [request.session['email']])
        vouchers=cursor.fetchall() 
    profile_dict = {'full_profile': full_profile, 'requests':requests, 'loan': loan, 'borrowed':borrowed, 'voucher':voucher}
    return render(request,'app/profile.html',profile_dict)
    
def voucher(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vouchers")
        voucher=cursor.fetchall()
    vouchers_dict={'voucher':voucher}
    
    #Need add the buy functionality
    context = {}
    status = ''
    if request.POST:
        if request.POST['action'] == 'claim':
            with connection.cursor() as cursor:
                cursor.execute("SELECT voucher_points FROM users WHERE school_email=%s", [request.session['email']])
                profilepoints=cursor.fetchall()
                cursor.execute("SELECT points_required FROM vouchers WHERE voucher_id=%s", [request.POST['use']])
                pts= cursor.fetchone()
                if (pts<=profilepoints):
                    cursor.execute("UPDATE voucher SET owner_of_voucher=%s WHERE voucher_id=%s", [request.session['email'],request.POST['use']])
                    cursor.execute("UPDATE users SET vouchers_points=%s-%s WHERE school_email=%s", [profilepoints,pts,request.session['email']])
                else:
                    status = 'Not enough points to purchase voucher!'
    context['status'] = status
    return render(request,'app/voucher.html',vouchers_dict)

#buy voucher function
#def use(request, voucherid):
#    context = {}
#    status = ''
#    if request.POST:
#        if request.POST['action'] == 'claim':
##            with connection.cursor() as cursor:
#                cursor.execute("SELECT voucher_points FROM users WHERE school_email=%s", [request.session['email']])
#                profilepoints=cursor.fetchall()
#                cursor.execute("SELECT points_required FROM vouchers WHERE voucher_id=voucherid")
#                pts= cursor.fetchone()
#                if (voucherid<=(profilepoints)):
#                    cursor.execute("UPDATE voucher SET owner_of_voucher=%s WHERE voucher_id=%s", [request.session['email'],voucherid])
#                    cursor.execute("UPDATE users SET vouchers_points=(profilepoints)-(%s) WHERE school_email=%s", [pts,request.session['email']])
#                else:
#                    status = 'Not enough points to purchase voucher!'
#    context['status'] = status
#    return render(request, "app/voucher.html", context)
    


