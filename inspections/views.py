from django.shortcuts import render, redirect
from .forms import ImageForm, SignatureForm, TextForm
from .models import Inspection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .forms import ImageForm
from PIL import Image
from pyzbar.pyzbar import decode
import json
import google.generativeai as genai

from django.shortcuts import render

def step1(request):
    form = ImageForm()
    return render(request, 'inspections/step1.html', {'form': form})

def signup(request):
    return render(request, 'inspections/signup.html')

def step2(request):
    return render(request, 'inspections/step2.html')

def step3(request):
    return render(request, 'inspections/step3.html')

def step4(request):
    return render(request, 'inspections/step4.html')

def step5(request):
    return render(request, 'inspections/step5.html')

def step6(request):
    return render(request, 'inspections/step6.html')

def menu(request):
    return render(request, 'inspections/menu.html')

def service(request):
    return render(request, 'inspections/service.html')

def rate(request):
    return render(request, 'inspections/rate.html')

def contact(request):
    return render(request, 'inspections/contact.html')

def menu_cust(request):
    return render(request, 'inspections/menu_cust.html')

def step1_cust(request):
    form = ImageForm()
    return render(request, 'inspections/step1_cust.html', {'form': form})

def step2_cust(request):
    return render(request, 'inspections/step2_cust.html')

# Settings view
from django.contrib import messages
from django.conf import settings
import os

def settings_view(request):
    return render(request, 'inspections/settings.html')


@csrf_exempt
def process_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if image_file:
            # Open the image using PIL
            image = Image.open(image_file)

            # Decode barcodes from the image using pyzbar
            decoded_objects = decode(image)
            barcode_values = [obj.data.decode('utf-8') for obj in decoded_objects]

            if barcode_values:
                # Save the first detected barcode in the session
                request.session['barcode_string'] = barcode_values[0]
                return JsonResponse({'text': ', '.join(barcode_values)})
            else:
                return JsonResponse({'text': 'No barcodes detected.'})
        else:
            return JsonResponse({'error': 'No image provided'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt  # This will exempt this view from CSRF validation, which might be necessary for API endpoints
def gemini_summarize_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key = data.get('api_key')  # Retrieve the API key sent from the front-end
            text = data.get('text')

            # Validate the presence of the API key and text
            if not api_key:
                return JsonResponse({'error': 'API key is missing'}, status=400)
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)

            # Set the API key for Google Gemini
            genai.configure(api_key = api_key)

            # Use the Google Gemini API to generate a summary
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"""
                The given text is what a user is telling about his CAT vehicle tires.: {text}.
                Summarize the text to fit the following format:
                ▪ Tire Pressure for Left Front: (numeric value)
                ▪ Tire Pressure for Right Front: (numeric value)
                ▪ Tire Condition for Left Front: (Good, Ok, Needs Replacement)
                ▪ Tire Condition for Right Front: (Good, Ok, Needs Replacement)
                ▪ Tire Pressure for Left Rear: (numeric value)
                ▪ Tire Pressure for Right Rear: (numeric value)
                ▪ Tire Condition for Left Rear: (Good, Ok, Needs Replacement)
                ▪ Tire Condition for Right Rear: (Good, Ok, Needs Replacement)
                ▪ Overall Tire Summary: (<1000 characters)

                If the text is not relevant to any tire inspection, respond with "NOT RELEVANT TEXT".
            """)

            # Handle the response from the API
            if response and "NOT RELEVANT TEXT" in response.text:
                return JsonResponse({'error': 'NOT RELEVANT TEXT'}, status=400)
            elif response:
                summary = response.text
                return JsonResponse({'summary': summary})
            else:
                return JsonResponse({'error': 'Failed to generate summary'}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON provided'}, status=400)
        except Exception as e:
            # Catch any other exceptions that may occur
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)



# Login and Siugnup views
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if verify_login(username, password):
            return redirect('step1')
        else:
            return render(request, 'inspections/login.html', {'error': 'Invalid credentials'})

    return render(request, 'inspections/login.html')

def verify_login(username, password):
    return True

from django.shortcuts import render, redirect

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'inspections/signup.html', {'error': 'Passwords do not match'})

        if verify_signup(username, email, password):
            return redirect('step1')
        else:
            return render(request, 'inspections/signup.html', {'error': 'Invalid credentials'})

    return render(request, 'inspections/signup.html')

def verify_signup(username, email, password):
    return True  # For now, this just returns True for demonstration



