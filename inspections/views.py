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
import datetime
import logging
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
logger = logging.getLogger(__name__)
@csrf_exempt 
def save_inspection_data(request):
    if request.method == 'POST':
        try:
            # Log the raw body for debugging
            logger.debug(f"Raw request body: {request.body.decode('utf-8')}")
            
            # Parse JSON data from the request body
            inspection_data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if inspection_data:
            model_number = inspection_data.get('model_number')
            serial_number = inspection_data.get('serial_number')
            latitude = inspection_data.get('latitude')
            longitude = inspection_data.get('longitude')
            date_time = inspection_data.get('date_time')
            signature = inspection_data.get('signature')

            # Log the parsed data for debugging
            logger.debug(f"Parsed inspection data: {inspection_data}")

            # Your database saving logic here...
            
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
            
            # Clear the session data if needed
            # del request.session['inspection_data']

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
from django.shortcuts import render, redirect

def save_signup_data(username,password,email):
        # Save data to MongoDB
        inspection = User(username=username, password=password, email=email)
        inspection.save()

 
'''
@csrf_exempt
def process_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        customer_name = request.POST.get('customer_name')
        customer_id = request.POST.get('customer_id')

        if image_file and customer_name and customer_id:
            # Open the image using PIL
            image = Image.open(image_file)

            # Decode barcodes from the image using pyzbar
            decoded_objects = decode(image)
            barcode_values = [obj.data.decode('utf-8') for obj in decoded_objects]

            if barcode_values:
                barcode_string = barcode_values[0]  # Use the first barcode value

                # Extract model number and serial number from barcode_string
                model_number = barcode_string[:7]  # Extract model number (assumed first 7 characters)
                serial_number = barcode_string[7:]  # Extract serial number (remaining characters)

                # Save the data to the database
                
                inspection = Inspection.objects.create(
                    customer_name=customer_name,
                    customer_id=customer_id,
                    image=image_file,
                    latitude=latitude,
                    longitude=longitude,
                    model_number=model_number,
                    serial_number=serial_number
                )

                
                print("customer_name", customer_name)
                print("customer_id", customer_id)
                print("latitude", latitude)
                print("longitude", longitude)
                print("model_number", model_number)
                print("serial_number", serial_number)

                return JsonResponse({'text': barcode_string})
            else:
                return JsonResponse({'text': 'No barcodes detected.'})
        else:
            return JsonResponse({'error': 'Required data missing'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


'''