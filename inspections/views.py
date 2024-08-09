from django.shortcuts import render, redirect
from .forms import ImageForm, SignatureForm, TextForm
from .models import Inspection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .forms import ImageForm
import requests

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

def get_api_key():
    with open('api.txt', 'r') as file:
        return file.read().strip()

# Replace 'your_api_key_here' with your actual OCRSpace API key
OCR_API_URL = 'https://api.ocr.space/parse/imageurl'

# View to process the image
@csrf_exempt
def process_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        if image_file:
            # Prepare the files and data for the API request
            files = {'file': image_file}
            payload = {
                'apikey': get_api_key(),
                'language': 'eng',  # Change this if you need another language
            }

            # Send POST request to the OCRSpace API
            response = requests.post(OCR_API_URL, files=files, data=payload)
            result = response.json()

            # Extract the OCR text from the response
            parsed_text = result['ParsedResults'][0]['ParsedText'] if 'ParsedResults' in result else ''
            return JsonResponse({'text': parsed_text})
        else:
            return JsonResponse({'error': 'No image provided'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

