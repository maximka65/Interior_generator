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
        # midjourney_api_url = "https://api.thenextleg.io/v2/imagine"
        midjourney_api_url = "https://cl.imagineapi.dev/items/images/"
        
        # payload = json.dumps({
        #     "msg": midjourney_prompt,
        #     "ref": "",
        #     "webhookOverride": "",
        #     "ignorePrefilter": "false"
        # })
        payload = json.dumps({
            "prompt": midjourney_prompt  # ваш сформированный запрос
        })

        # headers = {
        #     'Authorization': 'Bearer f71703ff-7e0f-4fd3-9a99-ede8c1d62910',
        #     'Content-Type': 'application/json'
        # }

        headers = {
            'Authorization': 'Bearer u667iLDO2Xfu0-qpv_nu82EeeDtYGlsf',  # TODO: Замените на ваш токен
            'Content-Type': 'application/json'
        }

        print("SENDING REQUEST", midjourney_prompt)
        # response = requests.request("POST", midjourney_api_url, headers=headers, data=payload)
        response = requests.post(midjourney_api_url, headers=headers, data=payload)
        

        print(response, response.text)
        if response.status_code == 200:
            time_to_sleep = 6
            time_check = 0
            midjourney_result = response.json()
            print(midjourney_result)
            # trying to get picture
            # message_id = midjourney_result.get('messageId')
            image_id = midjourney_result['data']['id']
            
            # Цикл ожидания готовности изображения
            for _ in range(10):  # Предположим, что мы проверяем статус каждые 6 секунд, до 1 минуты
                time.sleep(6)
                status_response = requests.get(f"{midjourney_api_url}{image_id}", headers=headers)
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result['data']['status'] == 'completed':
                        # Изображение готово
                        image_url = status_result['data']['url']
                        upscaled_urls = status_result['data'].get('upscaled_urls', [])
                        # Возвращаем основной URL изображения и массив увеличенных изображений
                        return JsonResponse({
                            'imageUrl': image_url,
                            'upscaledUrls': upscaled_urls
                        }, safe=False)
                    elif status_result['data']['status'] == 'failed':
                        # Произошла ошибка при создании изображения
                        return JsonResponse({'error': 'Image creation failed.'}, status=500)
                else:
                    # Произошла ошибка соединения
                    return JsonResponse({'error': 'Failed to check image status.'}, status=status_response.status_code)

            # Изображение не было готово в течение установленного времени
            return JsonResponse({'error': 'Image creation timed out.'}, status=408)
        else:
            # Произошла ошибка при запросе на создание изображения
            return JsonResponse({'error': 'Failed to initiate image creation.'}, status=creation_response.status_code)

    # Если метод не POST, отображаем форму загрузки
    return render(request, 'photo_app/upload.html')









    #         expire_mins = 2
    #         # picture_url = f'https://api.thenextleg.io/v2/message/{message_id}?expireMins={expire_mins}'
    #         picture_response = None
    #         while time_check < 300:
    #             picture_response = requests.get(picture_url, headers=headers)
    #             print(picture_response.json())
    #             if picture_response.json().get('progress') >= 100:
    #                 break
    #             if picture_response.json().get('progress') == "incomplete":
    #                 try:
    #                     fs.delete(name=uploaded_image.name)
    #                 except:
    #                     pass
    #                 return JsonResponse({"error": "Something going wrong with response"})
    #             time_check += 6
    #             time.sleep(time_to_sleep)
    #         try:
    #             fs.delete(name=uploaded_image.name)
    #         except:
    #             pass
    #         return JsonResponse({'imageUrl':  picture_response.json().get('response').get('imageUrl')}, safe=False)
    #     else:
    #         try:
    #             fs.delete(name=uploaded_image.name)
    #         except:
    #             pass
    #         return JsonResponse({'error': 'Failed to process integration with MidJourney.'}, status=500)
    # return render(request, 'photo_app/upload.html')
