from rest_framework.views import APIView
from django.db.models import Case, When, F, Sum, Max, FloatField
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum, Max, F
from datetime import timedelta
from .models import Data
from user_manager.models import User
from .serializers import DataSerializer

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

class RequestDataView(APIView):
    def post(self, request):
        serializer = DataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        period = serializer.validated_data['period']
        sort_by = serializer.validated_data['sort_by']

        now = timezone.now().date()
        date_filter = {}
        if period == 'day':
            date_filter['date'] = now
        elif period == 'week':
            start_date = now - timedelta(days=6)  # 7 Tage inkl. heute
            date_filter['date__range'] = [start_date, now]
        elif period == 'month':
            start_date = now - timedelta(days=29)  # 30 Tage inkl. heute
            date_filter['date__range'] = [start_date, now]
        # alltime => kein date_filter

        # Aggregation
        leaderboard_data = (
            Data.objects.filter(**date_filter)
            .values('user')  # Gruppierung per FK-Spalte
            .annotate(
                username=Max('user__name'),
                total_reviews=Sum('reviews'),
                total_time=Sum('time'),
                max_streak=Max('streak'),
                total_successful=Sum(F('reviews') * F('retention') / 100.0)
            )
            .annotate(
                retention=Case(
                    When(total_reviews=0, then=0.0),
                    default=100.0 * F('total_successful') / F('total_reviews'),
                    output_field=FloatField()
                )
            )
        )

        # Mapping für Sortierung
        SORT_MAPPING = {
            'reviews': 'total_reviews',
            'streak': 'max_streak',
            'retention': 'retention',
            # 'time': 'total_time' etc., falls benötigt
        }
        sort_field = SORT_MAPPING.get(sort_by, 'total_reviews')
        leaderboard_data = leaderboard_data.order_by(f'-{sort_field}')

        # Formatierung
        result = []
        for entry in leaderboard_data:
            result.append({
                'name': entry['username'],
                'reviews': entry['total_reviews'],
                'time': entry['total_time'],
                'streak': entry['max_streak'],
                'retention': round(entry['retention'], 1),
            })

        return Response(result, status=status.HTTP_200_OK)