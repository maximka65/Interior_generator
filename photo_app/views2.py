import json
import os
import time

import requests
from django.http import QueryDict
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from photo_app.service import MidJourneyIntegration
from photo_service import settings

from django.core.files.storage import FileSystemStorage
from django.conf import settings


@csrf_exempt
def process_integration(request):
    if request.method == 'POST':
        print("POST")
        content_type = request.META.get('CONTENT_TYPE')
        if content_type.startswith("multipart/form-data"):
           form = request.POST
        else:
           raw_data = "{" + request.body.decode('utf-8').replace(" ", "") + "}"
           query_string = '&'.join([f'{key}={value}' for key, value in json.loads(raw_data).items()])
           form = QueryDict(query_string)
        uploaded_image = request.FILES.get('image')
        name_if_uploaded = ""
        fs = None
        if uploaded_image:
            name_if_uploaded = uploaded_image.name
            temp_dir = settings.TEMP_DIR
            file_path = os.path.join(temp_dir, uploaded_image.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_image.chunks():
                    destination.write(chunk)
            fs = FileSystemStorage(location=temp_dir)

        generation_type = form.get('generation_type', 'creative')
        room_type = form.get('room_type', 'kitchen')
        style = form.get('style', '')
        facade_form = form.get('facade_form', '')
        hints = form.get('hints', '')
        print("INTEGRATION")
        midjourney_integration = MidJourneyIntegration(
            uploaded_image_name=name_if_uploaded,
            generation_type=generation_type,
            room_type=room_type,
            style=style,
            facade_form=facade_form,
            hints=hints
        )

        midjourney_prompt = midjourney_integration.get_midjourney_prompt()
        # FIXME
        midjourney_api_url = "https://api.thenextleg.io/v2/imagine"
        # midjourney_api_url = "https://cl.imagineapi.dev/items/images/"
        payload = json.dumps({
            "msg": midjourney_prompt,
            "ref": "",
            "webhookOverride": "",
            "ignorePrefilter": "false"
        })
        headers = {
            'Authorization': 'Bearer f71703ff-7e0f-4fd3-9a99-ede8c1d62910',
            'Content-Type': 'application/json'
        }
        print("SENDING REQUEST", midjourney_prompt)
        response = requests.request("POST", midjourney_api_url, headers=headers, data=payload)
        print(response, response.text)
        if response.status_code == 200:
            time_to_sleep = 6
            time_check = 0
            midjourney_result = response.json()
            print(midjourney_result)
            # trying to get picture
            message_id = midjourney_result.get('messageId')
            expire_mins = 2
            picture_url = f'https://api.thenextleg.io/v2/message/{message_id}?expireMins={expire_mins}'
            picture_response = None
            while time_check < 300:
                picture_response = requests.get(picture_url, headers=headers)
                print(picture_response.json())
                if picture_response.json().get('progress') >= 100:
                    break
                if picture_response.json().get('progress') == "incomplete":
                    try:
                        fs.delete(name=uploaded_image.name)
                    except:
                        pass
                    return JsonResponse({"error": "Something going wrong with response"})
                time_check += 6
                time.sleep(time_to_sleep)
            try:
                fs.delete(name=uploaded_image.name)
            except:
                pass
            return JsonResponse({'imageUrl':  picture_response.json().get('response').get('imageUrl')}, safe=False)
        else:
            try:
                fs.delete(name=uploaded_image.name)
            except:
                pass
            return JsonResponse({'error': 'Failed to process integration with MidJourney.'}, status=500)
    return render(request, 'photo_app/upload.html')
