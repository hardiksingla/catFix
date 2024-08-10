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

def inspection_view(request):
    if request.method == 'POST':
        image_form = ImageForm(request.POST, request.FILES)
        signature_form = SignatureForm(request.POST, request.FILES)
        text_form = TextForm(request.POST)

        if all([image_form.is_valid(), signature_form.is_valid(), text_form.is_valid()]):
            # Save the forms
            inspection = text_form.save(commit=False)
            inspection.image = image_form.cleaned_data['image']
            inspection.signature = signature_form.cleaned_data['signature']

            # Capture user's location (latitude and longitude)
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            inspection.latitude = latitude
            inspection.longitude = longitude

            inspection.save()
            return redirect('success_url')  # Redirect to a success page
    else:
        image_form = ImageForm()
        signature_form = SignatureForm()
        text_form = TextForm()

    return render(request, 'inspection_form.html', {
        'image_form': image_form,
        'signature_form': signature_form,
        'text_form': text_form,
    })


from django.shortcuts import render

def step1(request):
    form = ImageForm()
    return render(request, 'inspections/step1.html', {'form': form})

def login(request):
    return render(request, 'inspections/login.html')

def signup(request):
    return render(request, 'inspections/signup.html')

def step2(request):
    return render(request, 'inspections/step2.html')

def menu(request):
    return render(request, 'inspections/menu.html')

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

genai.configure(api_key="AIzaSyByoWksAxsGmVPJb2vNBUIcAvTuMUvu_G0")  # Replace with your actual API key

@csrf_exempt
def gemini_summarize_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')

            # Check if text is provided
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)

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
            if "NOT RELEVANT TEXT" in response:
                print(response)
                return JsonResponse({'error': 'NOT RELEVANT TEXT'}, status=400)
            elif response:
                summary = response.text
                return JsonResponse({'summary': summary})
            else:
                return JsonResponse({'error': 'Failed to generate summary'}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
