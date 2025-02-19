from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://6c22589a.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context) 
    
    else: 
        return HttpResponse('<h1>hi</h1>')


def get_dealers_by_state(request, state):
    if request.method == "GET":
        url = "https://6c22589a.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealer_by_state_from_cf(url, state)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    context['dealer_id'] = dealer_id
    if request.method == "GET":
        url = "https://6c22589a.us-south.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        if len(reviews) > 0:
            context['reviews'] = reviews           
            reviewer_names = ' '.join([review.review for review in reviews])
            review_sentiments = ' '.join([review.sentiment for review in reviews])
        # return HttpResponse(reviewer_names + ' ' + review_sentiments)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    user = request.user
    if user.is_authenticated and request.method == 'POST':
        url = "https://6c22589a.us-south.apigw.appdomain.cloud/api/review"
        review = dict()
        review['purchase_date'] = request.POST['purchasedate']
        review['dealership'] = dealer_id
        review['review'] = request.POST['content']
        review['name'] = 'priyaDutta'
        if 'purchasecheck' in request.POST.keys():
            review['purchase'] = True
        else:
            review['purchase'] = False

        if request.POST['car'] == '0':
            review['car_make'] = 'Audi'
            review['car_model'] = 'Audi 1'
            review['car_year'] = '2022'
        elif request.POST['car'] == '1':
            review['car_make'] = 'Audi'
            review['car_model'] = 'Audi 2'
            review['car_year'] = '2022'
        elif request.POST['car'] == '2':
            review['car_make'] = 'Audi'
            review['car_model'] = 'Audi 3'
            review['car_year'] = '2021'
        elif request.POST['car'] == '3':
            review['car_make'] = 'Mercedes'
            review['car_model'] = 'Benz 1'
            review['car_year'] = '2022'
        elif request.POST['car'] == '4':
            review['car_make'] = 'Mercedez'
            review['car_model'] = 'Benz 2'
            review['car_year'] = '2020'
        review['id'] = (random.random() + 1) * 100000000
        print("type of car")
        print(request.POST)
        json_payload = dict()
        json_payload['review'] = review
        postreview = post_request(url, json_payload=json_payload)

        if postreview:
            print(postreview)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return HttpResponse('<h1>failed</h1>')
        
    elif request.method == 'GET':
        print('get request')
        context = {}
        context['dealer_id'] = dealer_id
        carmakes = CarMake.objects.all()
        cars = []
        
        fieldobjcarmake = CarMake._meta.get_field('name')
        namecarmodel = CarModel._meta.get_field('name')
        yearcarmodel = CarModel._meta.get_field('year')
        for car in carmakes:
            print('cars are')
            print(cars)
            carmodels = car.carmodel_set.all()
            
            for model in carmodels: 
                carObj = {}
                carObj['name'] = namecarmodel.value_from_object(model)
                carObj['year'] = yearcarmodel.value_from_object(model).strftime("%Y")
                carObj['make'] = fieldobjcarmake.value_from_object(car)
                cars.append(carObj)
            #name = fieldobj.value_from_object(car)
            #print(name)
            
        
        context['cars'] = cars
        return render(request, 'djangoapp/add_review.html', context)
 
