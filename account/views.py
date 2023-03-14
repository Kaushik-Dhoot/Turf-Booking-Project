import random
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render
from twilio.rest import Client
from datetime import date,datetime
from account.models import Slot_booking,Ratings

User=get_user_model()

phone = ''
otp = ''

def home_page(request):
    return render(request,'index.html')


def about_us(request):
    return render(request,'about_us.html')


def Login(request):

    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(phone=phone ,password=password)

        if user is not None:
            login(request,user)
            fname = user.first_name
            context = {'fname':fname}
            messages.success(request,'Logged in successfully !')
            return render(request,'dashbord.html',context)
        
        else:
            messages.error(request,'Login failed, Invalid Credentials!')
            return redirect('Login')


    return render(request,'Login.html')


def SignUp(request):

    if request.method =='POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        global phone
        phone = request.POST.get('number')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if User.objects.filter(phone=phone).exists():
            messages.error(request,'Phone number already exists ! PLease Login to Continue')
            return redirect('Login')
        if len(password)<8 :
            messages.error(request,'Password too short! Password must have 8 characters.')
            return redirect('SignUp')
        if password != cpassword:
            messages.error(request,'Passwords does not Match')
            return redirect('SignUp')

        global otp
        otp = str(random.randint(100000,999999))
        print(f' Generated OTP : {otp}')
        
        my_user = User.objects.create_user(phone=phone,password=password)
        my_user.first_name = fname
        my_user.last_name = lname
        sendotp(phone)
        my_user.save()
        messages.success(request,f"Enter OTP sent to your Mobile Number {phone}")

        return render(request, 'verifyotp.html')

    return render(request,'SignUp.html')


def Logout(request):
    logout(request)
    messages.success(request,'Logged out successfully !')
    return redirect('Login')


def dashbord(request):

    if request.user.is_anonymous:
        messages.error(request,'Please Login first')
        return redirect('/Login')
    usr = request.user
    fname = usr.get_full_name()
    context = {'fname':fname}
    return render(request,'dashbord.html',context)


def pricing(request):
    return render(request,'pricing.html')

def ratings(request):

    if request.method == 'POST':
        comment = request.POST.get('comment')
        fname = request.user.first_name
        lname = request.user.last_name
        full_name = fname+' '+lname
        date_today = date.today()


        review = Ratings(name=full_name,comment=comment,created_at=date_today)
        review.save()
    
    all_reviews = Ratings.objects.all().order_by('-created_at')
    context = {}

    context['reviews'] = all_reviews

    return render(request,'ratings.html',context)


def booking(request):

    if request.method == 'POST':
        
        name = request.user.first_name +' '+ request.user.last_name
        phone = request.user.phone
        if request.user.is_superuser :
            name = request.POST.get('name')
            phone = request.POST.get('phone')
        s_date = request.POST.get('sdate')
        stime = request.POST.get('stime')
        etime = request.POST.get('etime')

        if etime == '00:00':
            etime = '23:59'

        booking_start = s_date+' '+stime+':00+00:00'
        booking_end = s_date+' '+etime+':00+00:00'

        now = datetime.now()
        time_now = now.strftime("%H")
        date_today = date.today()
        check_date = datetime.strptime(s_date, '%Y-%m-%d').date()
        check_start_time = (datetime.strptime(stime, "%H:%M"))
        check_end_time = (datetime.strptime(etime, "%H:%M"))

        int_check_start_time = int(datetime.strftime(check_start_time, "%H"))
        int_check_end_time = int(datetime.strftime(check_end_time, "%H"))

        if int_check_start_time > int_check_end_time :
            messages.error(request,'Start Time must be less than End Time of Booking !')
            return render(request,'Booking.html')

        if check_date < date_today :
            messages.error(request,'Past Date is not valid for Booking !')
            return render(request,'Booking.html')
        elif check_date == date_today:
            if int(time_now) > int_check_start_time :
                messages.error(request,'Incorrect Time Please Enter Future Time !')
                return render(request,'Booking.html')

        case_1 = Slot_booking.objects.filter(start_time__lt=booking_end, end_time__gt = booking_end).exists()
        case_2 = Slot_booking.objects.filter(start_time__lt=booking_start, end_time__gt=booking_start).exists()
        case_3 = Slot_booking.objects.filter(start_time__gte=booking_start, end_time__lte=booking_end).exists()

        if case_1 or case_2 or case_3:
            messages.error(request,'The slot is already Booked !')
            return render(request,'Booking.html')
        else:

            u_phone = request.user.phone
            usr = User.objects.get(phone = u_phone)
            cnt,total_hours,user_bookings = count_price(request,s_date,stime,etime)
            msg_1=''
            if int(total_hours) >= 5:
                msg_1 = 'You got 300rs Discount for booking more than 5 hours'
                cnt -= 300
                
            elif user_bookings%5 ==0 :
                msg_1 = 'You got 10' +' % '+ f'discount for {user_bookings}th booking'
                cnt -= (cnt//10)
            
            booking = Slot_booking(name=name,phone=phone,start_time=s_date+' '+stime,end_time=s_date+' '+etime,total=cnt)
            booking.save()
            usr.booking_count += 1
            booking_otp = str(random.randint(100000,999999))
            send_conf(request=request,from_=s_date+' '+stime,to_=s_date+' '+etime,otp=booking_otp)
            usr.save()

            messages.success(request,'Your Booking is successfull !! ' + msg_1)  
            if request.user.is_superuser :
                return redirect('all_bookings')
            return redirect('history')


    return render(request,'booking.html')


def count_price(request,sdate,stime,etime):

    total_price = 0

    t1 = datetime.strptime(stime, "%H:%M")
    t2 = datetime.strptime(etime, "%H:%M")


    t1_int = int(datetime.strftime(t1, "%H"))
    t2_int = int(datetime.strftime(t2, "%H"))
    t2_min = int(datetime.strftime(t2, "%M"))
    print(t2_min)
    

    d1 = datetime.strptime(sdate, '%Y-%m-%d').date()
    day = d1.weekday()

    if t2_int == 23 and t2_min == 59:
        t2_int = 24

    delta = t2-t1

    total_hours = delta.total_seconds()/(60*60)

    user_bookings = request.user.booking_count
    user_bookings += 1

    for i in range(t1_int,t2_int):
        if day <=4 :
            if 6 <= i < 12 :
                total_price += 800
            elif 12 <= i <18 :
                total_price += 700
            elif 18 <= i <=24 or 0 <= i < 6 :
                total_price += 900
        else :
            if 6 <= i < 12 :
                total_price += 900
            elif 12 <= i <18 :
                total_price += 800
            elif 18 <= i <=24 or 0 <= i < 6 :
                total_price += 1000

    return (total_price,total_hours,user_bookings)


def history(request):
    phone = request.user.phone
    all_bookings = Slot_booking.objects.filter(phone=phone).order_by('-start_time')
    # print(all_bookings)
    context={}
    context['booking'] = all_bookings
    return render(request,'history.html',context)

def all_bookings(request):

    all_bookings = Slot_booking.objects.all().order_by('-start_time')
    context = {}

    total_income = 0
    context['all_booking'] = all_bookings

    for i in all_bookings :
        total_income += i.total

    context['income'] = total_income

    return render(request,'all_bookings.html',context)


def equipment (request):
    return render(request,'equipment.html')


def sendotp(phone):)
    sid = 'Twilio_sid'
    auth_id = 'Twilio_auth_key'
    v_sid = 'Twilio_verification_id'
    t_client = Client(sid,auth_id)

    verification = t_client.verify.services(v_sid) \
                                        .verifications \
                                        .create(to=f'+91{phone}',channel='sms')
    


def send_conf(request,from_,to_,otp):
    sid = 'Twilio_sid'
    auth_id = 'Twilio_auth_key'
    t_number = 'Twilio_phone_number'
    phone = request.user.phone
    client = Client(sid,auth_id)
    text = client.messages.create(
        body = f'Booking Confirm from {from_} to {to_}. \n Otp for booking is {otp} \n- Team Greenfield',
        from_ = t_number,
        to = f'+917066352978'
    )


def verifyotp(request):
    global phone
    global otp

    if request.method == 'POST':
        eotp = request.POST.get('otp')
        print(eotp)
        print(type(eotp))
        sid = 'Twilio_sid'
        auth_id = 'Twilio_auth_key'
        v_sid = 'Twilio_verification_id'
        t_client = Client(sid,auth_id)
        check = t_client.verify.services(v_sid) \
                            .verification_checks \
                                .create(to=f'+91{phone}',code=eotp)
        
        if check.status == 'approved':
            usr = User.objects.get(phone = phone )
            usr.phone_verified = True
            usr.save()
            messages.success(request,'Phone Number verified Successfully! Please Log in')
            return redirect('Login')
        
        else :
            messages.error(request,'Incorrect OTP')
            return render(request,'verifyotp.html')
    
    else :
        return redirect('home_page')
