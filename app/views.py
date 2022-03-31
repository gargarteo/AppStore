from django.shortcuts import render, redirect
from django.db import connection 
from django.http import HttpResponse  
import datetime

def new_request(request):
    context = {}
    status = ''             
    if request.POST:
        with connection.cursor() as cursor:
            #Checking if exceed max request
            cursor.execute("SELECT COUNT(*) from requests where loaner =%s and accepted=false", [request.session['email']])
            current_request = cursor.fetchone()
            cursor.execute("SELECT max_request from users where school_email = %s", [request.session['email']])
            max_requests = cursor.fetchone()
            if  current_request < max_requests :
            #Checking return later than borrow
                try:
                    cursor.execute("INSERT INTO requests(item, loaner, category, date_needed, time_needed,return_date, return_time, meetup_location) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        , [ request.POST['item'], request.session['email'], request.POST['category'], request.POST['date_needed'], request.POST['time_needed'], request.POST['return_date'], request.POST['return_time'], request.POST['meetup_location'] ])
                    return redirect('home') 
                
                except:
                    status = 'Please ensure return date is later than borrow date'
                     
            else:
                status = 'Exceeded Max request limit'
    context['status'] = status
    return render(request, 'app/new_request.html', context)


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
    context = {}
    status = ''
    with connection.cursor() as cursor:
        if request.POST:
            if request.POST['action']=="accept_request":
               cursor.execute("SELECT loaner FROM requests WHERE request_id=%s" ,[request.POST['id']])
               borrower= (cursor.fetchone())
               cursor.execute("SELECT item FROM requests WHERE request_id=%s",[request.POST['id']])
               item= (cursor.fetchone())
               cursor.execute("SELECT date_needed FROM requests WHERE request_id=%s",[request.POST['id']])
               date_borrowed= (cursor.fetchone())
               cursor.execute("SELECT return_date FROM requests WHERE request_id=%s",[request.POST['id']])
               return_deadline= (cursor.fetchone())
               returned_date= return_deadline
               cursor.execute("INSERT INTO loan VALUES (%s, %s, %s, %s, %s, %s, %s)", [request.POST['id'], borrower, request.session['email'], item , date_borrowed, return_deadline, returned_date])
               cursor.execute("UPDATE requests SET accepted=true WHERE request_id=%s",[request.POST['id']])
               cursor.execute("UPDATE users SET vouchers_points=vouchers_points+100 WHERE school_email=%s",[request.session['email']])
               return redirect('profile')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM requests WHERE accepted=false and loaner<>%s  ORDER BY date_needed ASC",[request.session['email']])
        #cursor.execute("SELECT * FROM requests r, user u WHERE r.accepted=false and r.loaner<>%s and u.school_email=r.loaner ORDER BY date_needed ASC",[request.session['email']])
        requests = cursor.fetchall()
        cursor.execute("SELECT * FROM requests WHERE accepted=false and loaner=%s and return_date>=CURRENT_DATE ORDER BY date_needed ASC",[request.session['email']])
        my_requests=cursor.fetchall()
        return render(request, "app/home.html",  {'requests': requests, 'my_requests':my_requests})

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
                cursor.execute("SELECT * FROM requests WHERE accepted=false and loaner<>%s",[request.session['email']])
                requests = cursor.fetchall()
                cursor.execute("SELECT * FROM requests WHERE accepted=false and loaner=%s",[request.session['email']])
                my_requests=cursor.fetchall()
            result_dict = {'requests': requests, 'my_requests':my_requests}
            return render(request, "app/home.html",  {'requests': requests, 'my_requests':my_requests})
        
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
                try:
                    cursor.execute("INSERT INTO users (name, school_email, password) VALUES (%s, %s, %s)"
                        , [ request.POST['name'], request.POST['school_email'], request.POST['password'] ])
                    return redirect('index')    
                    
                except:
                    status = 'Please ensure (1) you use your NUS email address (2) password is between 6-12 characters' 
                    
            else:
                status = 'User with ID %s already exists' % (request.POST['school_email'])


    context['status'] = status
 
    return render(request, "app/register.html", context)

def profile(request):
    with connection.cursor() as cursor: 
        cursor.execute("SELECT * FROM users WHERE school_email=%s", [request.session['email']]) 
        full_profile= cursor.fetchall()
        cursor.execute("SELECT * FROM requests WHERE loaner=%s AND accepted=false", [request.session['email']])
        requests= cursor.fetchall()
        cursor.execute("UPDATE loan SET days_overdue= (CURRENT_DATE- return_deadline) WHERE return_deadline<CURRENT_DATE")
        cursor.execute("SELECT COALESCE(SUM(days_overdue),0) FROM loan WHERE borrower=%s", [request.session['email']])
        demerits= cursor.fetchone()
        cursor.execute("UPDATE users SET demerit_points= %s WHERE school_email=%s", [demerits, request.session['email']])
        cursor.execute("SELECT * FROM loan WHERE owner= %s", [request.session['email']])
        loan=cursor.fetchall()
        cursor.execute("SELECT * FROM loan WHERE borrower=%s", [request.session['email']])
        borrowed=cursor.fetchall()
        cursor.execute("SELECT * FROM vouchers WHERE owner_of_voucher=%s", [request.session['email']])
        vouchers=cursor.fetchall() 
        
        #gives an error
        #cursor.execute("SELECT * FROM loan WHERE borrower=%s AND CURRENT_DATE> return_deadline",[request.session['email']])
        #late= cursor.fetchall()
        #if late!= None:
            #cursor.execute("SELECT DATEDIFF(day, return_deadline, CURRENT_DATE) AS DateDiff FROM %s", [late])
            #days_late= cursor.fetchall()
           # cursor.execute("SELECT SUM(DateDiff) AS demerit_pts FROM %s", [days_late])
            #demerits=cursor.fetchone()
           # cursor.execute("UPDATE users SET demerit_points= %s WHERE school_email=%s", [demerits, request.session['email']])
           # cursor.execute("SELECT * FROM users WHERE school_email=%s", [request.session['email']]) 
           # full_profile= cursor.fetchall()        
        if request.POST:
            if request.POST['action'] == 'removereq':
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM requests WHERE request_id=%s", [request.POST['use']])
                    return redirect('profile')
            if request.POST['action']=='returned':
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM loan WHERE request_id=%s", [request.POST['returned']])
                    return redirect('profile')
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
                    return render(request,'app/voucher.html',context)
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
    


