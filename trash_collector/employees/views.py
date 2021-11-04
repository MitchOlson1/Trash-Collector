from django.contrib.auth import login
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.apps import apps
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Employee
from django.core.exceptions import ObjectDoesNotExist



# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers.Customer')
    all_customers= Customer.objects.all()

    logged_in_user = request.user
    try: 
        logged_in_employee = Employee.objects.get(user=logged_in_user)

        today= date.today()

        customers = Customer.objects.filter(zip_code=logged_in_employee.zip_code)
        today_customers= customers.filter(weekly_pickup=today)
        active_pickups = today_customers.exclude(suspend_start__lt=today,)

        context = {
            'logged_in_employee':logged_in_employee,
            'today': today,
            'all_customers': all_customers,
        }

        return render(request, 'employees/index.html',context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))


def create(request):
    logged_in_user=request.user
    if request.method == "Post":
        name_from_signup = request.POST.get('name'), 
        zip_from_signup = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_signup, user= logged_in_user, zip_code = zip_from_signup)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee =Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_signup=request.POST.get('name')
        zip_from_signup=request.POST.get('zip_code')
        logged_in_employee.name = name_from_signup
        logged_in_employee.zip_code = zip_from_signup
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context={
            'logged_in_employee': logged_in_employee
        }
        return render(request,'employees/create.html') 

@login_required
def confirm_pickup(request, customer_id):
    Customers = apps.get_model('customers.Customer')
    customer = Customers.objects.get(id=customer_id)
    today = date.today()
    customer.date_of_last_pickup = today
    customer.balance -=20
    customer.save()
    return HttpResponseRedirect(reverse('employees:index'))

def view_pickups(request):
    Customers = apps.get_model('customers.Customer')
    all_customers = Customers.objects.all()
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    today = date.today()
    day_name = today.strftime("%A")
    day_name = day_name.upper()
    customers_that_share_pickup_day = []
    employee_selection = request.POST['pickup_day_drop_down']
    context = {
        'logged_in_employee': logged_in_employee,
        'all_customers': all_customers,
        'customers_that_share_pickup_day': customers_that_share_pickup_day,
        'today': today,
        'day_name': day_name
    }
    try:
        for customer in all_customers:
            if customer.weekly_pickup == employee_selection:
                customers_that_share_pickup_day.append(customer)
        if customers_that_share_pickup_day != None:
            return render(request, 'employees/index.html', context)
        else:
            return HttpResponseRedirect(reverse('employees:index'))
    except(ValueError):
        return HttpResponseRedirect(reverse('employees:index'))
       