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
import tempfile
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


@csrf_exempt  # Exempt this view from CSRF validation
def gemini_summarize_battery(request):
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
            genai.configure(api_key=api_key)

            # Use the Google Gemini API to generate a summary for battery information
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"""
                The given text is what a user is telling about the battery of their CAT vehicle: {text}.
                Summarize the text to fit the following format:
                ▪ Battery Make: (Example CAT, ABC, XYZ, etc.)
                ▪ Battery Replacement Date: (in yyyy-MM-dd format)
                ▪ Battery Voltage: (numeric value, e.g., 12V / 13V)
                ▪ Battery Water Level: (Good, Ok or Low)
                ▪ Condition of Battery (Damage): (Put Y if there is any damage, else N)
                ▪ Any Leak/Rust in Battery: (Put Y if there is no leak or rust, else N)
                ▪ Battery Overall Summary: (<1000 characters)

                If the text is not relevant to battery inspection, respond with "NOT RELEVANT TEXT".
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

import base64
import io


# Exterior Inspection

@csrf_exempt
def gemini_summarize_exterior(request):
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
            genai.configure(api_key=api_key)

            # Use the Google Gemini API to generate a summary
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"""
                The given text is what a user is telling about the exterior of their CAT vehicle: {text}.
                Summarize the text to fit the following format:
                ▪ Rust, Dent or Damage to Exterior: (say Y if any rust, dust or damage is present else N, EXPLAIN ONLY IF Y)
                ▪ Oil leak in Suspension: (just put Y if there is any leak else N. DO NOT EXPLAIN)
                ▪ Overall Summary: (<1000 characters)

                If the text is not relevant to any exterior inspection, respond with "NOT RELEVANT TEXT".
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



@csrf_exempt  # Exempt this view from CSRF validation
def gemini_process_issue(request):
    if request.method == 'POST':
        try:
            text = request.POST.get('text')
            api_key = request.POST.get('api_key')  # Retrieve the API key sent from the front-end
            images = request.FILES.getlist('images')

            if not api_key:
                return JsonResponse({'error': 'API key is missing'}, status=400)
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)

            # Set the API key for Google Gemini (or your specific API)
            genai.configure(api_key=api_key)

            image_uris = []
            for image in images:
                # Open the image using PIL and save it to a temporary file
                img = Image.open(image)
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{img.format.lower()}") as temp_img_file:
                    img.save(temp_img_file.name)
                    temp_img_file.close()  # Ensure the file is written and closed

                    # Upload the image to Gemini using the temporary file path
                    uploaded_file = genai.upload_file(
                        path=temp_img_file.name,  # Use the temporary file path
                        display_name=image.name
                    )
                    image_uris.append(uploaded_file.uri)

                # Clean up the temporary file
                os.remove(temp_img_file.name)

            # Use the API to generate a summary based on text and images
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Create the prompt including the text and image URIs
            prompt = f"""
                The user has reported an issue with their CAT vehicle. Below is the provided information:

                - Description of the issue: {text}
                - Number of attached images: {len(image_uris)}

                Please summarize the problem described in the text and provide a brief overview of the content of the images.
            """

            # Add each image URI to the prompt
            for uri in image_uris:
                prompt += f"\n[Image URI: {uri}]"

            # Generate content using the prompt
            response = model.generate_content(prompt)

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
    try:
        user = User.objects.get(username=username)
        if password == user.password:
            return True
    except User.DoesNotExist:
        return False

    return False

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
            save_signup_data(username,password,email)
            return redirect('step1')
        else:
            return render(request, 'inspections/signup.html', {'error': 'Invalid credentials'})

    return render(request, 'inspections/signup.html')

def verify_signup(username, email, password):
    return True  # For now, this just returns True for demonstration



from .models import User

def save_signup_data(username,password,email):
        # Save data to MongoDB
        inspection = User(username=username, password=password, email=email)
        inspection.save()

        

# Data from Tires
@csrf_exempt
def submit_tire_data(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            pressure_left_front = request.POST.get('pressure-left-front')
            pressure_right_front = request.POST.get('pressure-right-front')
            condition_left_front = request.POST.get('condition-left-front')
            condition_right_front = request.POST.get('condition-right-front')
            pressure_left_rear = request.POST.get('pressure-left-rear')
            pressure_right_rear = request.POST.get('pressure-right-rear')
            condition_left_rear = request.POST.get('condition-left-rear')
            condition_right_rear = request.POST.get('condition-right-rear')
            tire_summary = request.POST.get('tire-summary')
            api_key = request.POST.get('api_key')

            images = {
                'left_front': request.POST.get('image-left-front'),
                'right_front': request.POST.get('image-right-front'),
                'left_rear': request.POST.get('image-left-rear'),
                'right_rear': request.POST.get('image-right-rear')
            }

            # Process the data (e.g., send to Gemini, store in DB, etc.)

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt  # Exempt this view from CSRF validation
def submit_battery_data(request):
    if request.method == 'POST':
        try:
            api_key = request.POST.get('api_key')
            battery_make = request.POST.get('battery-make')
            replacement_date = request.POST.get('replacement-date')
            voltage = request.POST.get('battery-voltage')
            water_level = request.POST.get('battery-water-level')
            damage = request.POST.get('battery-damage')
            leak_rust = request.POST.get('leak-rust')
            overall_summary = request.POST.get('battery-summary')

            # Process images
            images = {
                'damage_image': request.FILES.get('image-damage'),
                'leak_rust_image': request.FILES.get('image-leak-rust')
            }

            # Process the data (e.g., send to Gemini, store in DB, etc.)

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def submit_exterior_data(request):
    if request.method == 'POST':
        try:
            # Extract data from request
            rust_damage = request.POST.get('rust-damage')
            oil_leak = request.POST.get('oil-leak')
            exterior_summary = request.POST.get('exterior-summary')
            api_key = request.POST.get('api_key')

            images = {
                'rust_damage': request.POST.get('image-rust-damage'),
                'oil_leak': request.POST.get('image-oil-leak')
            }

            # Process the data (e.g., send to Gemini, store in DB, etc.)

            # Return success response
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

