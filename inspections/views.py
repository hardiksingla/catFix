from django.shortcuts import render, redirect
from .forms import ImageForm, SignatureForm, TextForm
from .models import BrakeInspection, ExteriorInspection, Inspection
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
import datetime
import logging
from .models import User , TyreInspection , BatteryInspection

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
def save_inspection(request):
    if request.method == 'POST':
        # Get the data from the form submission
        model_number = request.POST.get('model_number')
        serial_number = request.POST.get('serial_number')
        date_time = request.POST.get('date_time')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        signature = request.POST.get('signature')

        # Retrieve other form data (e.g., customer name, customer ID, image)
        customer_name = "Sample Customer"  # Replace with actual data
        customer_id = "12345"              # Replace with actual data
        image_file = request.FILES.get('image')

        # Save the inspection data to MongoDB
        inspection = Inspection(
            customer_name=customer_name,
            customer_id=customer_id,
            image=image_file,
            signature=signature,  # Store as base64 encoded string
            model_number=model_number,
            serial_number=serial_number,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            created_at=datetime.datetime.fromisoformat(date_time) if date_time else datetime.datetime.now()
        )
        inspection.save()

        # Redirect to the next page or render a success message
        return redirect('success_page')  # Replace 'success_page' with your actual success page

    return render(request, 'form_page.html')

'''

@csrf_exempt 
def process_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if image_file:
            image = Image.open(image_file)
            decoded_objects = decode(image)

            barcode_values = [obj.data.decode('utf-8') for obj in decoded_objects]

            if barcode_values:
                model_number = barcode_values[0][3:10]
                serial_number = barcode_values[0][10:]

                # Save data to session
                request.session['inspection_data'] = {
                    'model_number': model_number,
                    'serial_number': serial_number,
                    'latitude': latitude,
                    'longitude': longitude,
                    'date_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'signature': request.POST.get('signature')  # Assuming signature is being sent as a base64 string
                }
                print("Inspection Data Stored in Session:", request.session['inspection_data'])

                return JsonResponse({'text': ', '.join(barcode_values), 'status': 'success'})
            else:
                return JsonResponse({'text': 'No barcodes detected.'})
        else:
            return JsonResponse({'error': 'No image provided'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
'''

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
@csrf_exempt 
def save_inspection_data(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            inspection_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if inspection_data:
            model_number = inspection_data.get('model_number')
            serial_number = inspection_data.get('serial_number')
            latitude = inspection_data.get('latitude')
            longitude = inspection_data.get('longitude')
            date_time = inspection_data.get('date_time')
            signature = inspection_data.get('signature')

            # Save the data to your database
            inspection = Inspection(
                customer_name="Sample Customer",  # Replace with actual data or retrieve from request
                customer_id="12345",              # Replace with actual data or retrieve from request
                model_number=model_number,
                serial_number=serial_number,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                created_at=date_time,
                signature=signature
            )
            inspection.save()

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'error': 'No inspection data found'}, status=400)

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
                saveTyreData(text, summary)
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


def saveTyreData(text, summary):
    print(summary)
    
    # data = TyreInspection()
    pass

@csrf_exempt  # Exempt this view from CSRF validation
def gemini_summarize_battery(request):
    print("Inside gemini_summarize_battery")
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


@csrf_exempt
def gemini_summarize_brake(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key = data.get('api_key')
            text = data.get('text')

            if not api_key:
                return JsonResponse({'error': 'API key is missing'}, status=400)
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"""
                The given text is what a user is telling about the brakes of their CAT vehicle.: {text}.
                Summarize the text to fit the following format:
                ▪ Brake Fluid level: (Good, Ok , Low )
                ▪ Brake Condition for Front: (Good, Ok, Needs Replacement)
                ▪ Brake Condition for Rear: (Good, Ok, Needs Replacement)
                ▪ Emergency Brake: ( Good , Ok , Low )
                ▪ Brake Overall Summary: (<1000 characters)

                If the text is not relevant to any brake inspection, respond with "NOT RELEVANT TEXT".
            """)

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
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def gemini_summarize_engine(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key = data.get('api_key')
            text = data.get('text')

            if not api_key:
                return JsonResponse({'error': 'API key is missing'}, status=400)
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"""
                The given text is what a user is telling about the engine of their CAT vehicle: {text}.
                Summarize the text to fit the following format:
                ▪ Rust, Dents or Damage in Engine: (Y if any rust, dent or damage is present else N. Provide  no explanation)
                ▪ Engine Oil Condition: (Good / Bad)
                ▪ Engine Oil Color: (Clean / Brown / Black)
                ▪ Brake Fluid Condition: (Good / Bad)
                ▪ Brake Fluid Color: (Clean / Brown / Black)
                ▪ Any Oil Leak in Engine: (Y if there is any leak else N. Provide no explanation)
                ▪ Engine Overall Summary: (<1000 characters)

                If the text is not relevant to any engine inspection, respond with "NOT RELEVANT TEXT".
            """)

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
        user = User.objects.get(username=username)
        if password == user.password:
            if user.user_type == 'service_person':
                return redirect('step1')
            else:
                return redirect('step1_cust')
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
        user_type = request.POST.get('user_type')
        print(request.POST)
        if password != confirm_password:
            return render(request, 'inspections/signup.html', {'error': 'Passwords do not match'})

        if verify_signup(username, email, password):
            save_signup_data(username, password, email, user_type)
            return redirect('step1')
        else:
            return render(request, 'inspections/signup.html', {'error': 'Invalid credentials'})

    return render(request, 'inspections/signup.html')

def verify_signup(username, email, password):
    return True  # For now, this just returns True for demonstration





def save_signup_data(username, password, email, user_type):
    # Save data to the database using Django's ORM
    user = User(username=username, password=password, email=email, user_type=user_type)
    user.save()

        

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
            
            tyre_inspection = TyreInspection.objects.create(
            left_front_pressure=pressure_left_front,
            right_front_pressure=pressure_right_front,
            left_front_condition=condition_left_front,
            right_front_condition=condition_right_front,
            left_rear_pressure=pressure_left_rear,
            right_rear_pressure=pressure_right_rear,
            left_rear_condition=condition_left_rear,
            right_rear_condition=condition_right_rear,
            overall_summary=tire_summary
            )

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

            battery_inspection = BatteryInspection.objects.create(
            battery_make=battery_make,
            replacement_date=replacement_date,
            voltage=voltage,
            water_level=water_level,
            condition_damage=damage,
            leak_rust=leak_rust,
            overall_summary=overall_summary
        )
            
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

            exterior_inspection = ExteriorInspection.objects.create(
            rust_damage=rust_damage,
            oil_leak=oil_leak,
            exterior_summary=exterior_summary
        )
            
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


@csrf_exempt
def submit_brake_data(request):
    if request.method == 'POST':
        try:
            brake_fluid_level = request.POST.get('brake-fluid-level')
            brake_condition_front = request.POST.get('brake-condition-front')
            brake_condition_rear = request.POST.get('brake-condition-rear')
            emergency_brake = request.POST.get('emergency-brake')
            brake_summary = request.POST.get('brake-summary')
            api_key = request.POST.get('api_key')

            brake_inspection = BrakeInspection.objects.create(
            brake_fluid_level=brake_fluid_level,
            brake_condition_front=brake_condition_front,
            brake_condition_rear=brake_condition_rear,
            emergency_brake=emergency_brake,
            brake_summary=brake_summary
        )
            
            images = {
                'front_brake': request.POST.get('image-brake-front'),
                'rear_brake': request.POST.get('image-brake-rear')
            }

            # Process the data (e.g., send to Gemini, store in DB, etc.)

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def submit_engine_data(request):
    if request.method == 'POST':
        try:
            engine_damage = request.POST.get('engine-damage')
            engine_oil_condition = request.POST.get('engine-oil-condition')
            engine_oil_color = request.POST.get('engine-oil-color')
            brake_fluid_condition = request.POST.get('brake-fluid-condition')
            brake_fluid_color = request.POST.get('brake-fluid-color')
            engine_oil_leak = request.POST.get('engine-oil-leak')
            engine_summary = request.POST.get('engine-summary')
            api_key = request.POST.get('api_key')

            images = {
                'engine_images': request.POST.get('image-engine')
            }

            # Process the data (e.g., send to Gemini, store in DB, etc.)

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
