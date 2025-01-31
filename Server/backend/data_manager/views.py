from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Data
from user_manager.models import User

class SubmitDataView(APIView):
    def post(self, request):
        user_data = {
            'anki_uid': request.data.get('anki_uid'),
            'name': request.data.get('name')
        }
        data = request.data.get('data', [])

        user, created = User.objects.update_or_create(
            anki_uid=user_data['anki_uid'],
            defaults={'name': user_data['name']}
        )

        for data_entry in data:
            Data.objects.update_or_create(
                user=user,
                date=data_entry['date'],
                defaults={
                    'reviews': data_entry['reviews'],
                    'time': data_entry['time'],
                    'streak': data_entry['streak'],
                    'retention': data_entry['retention']
                }
            )

        return Response({'status': 'success'}, status=status.HTTP_200_OK)