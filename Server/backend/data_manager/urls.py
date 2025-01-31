from django.urls import path
from .views import SubmitDataView

urlpatterns = [
    path('submitdata/', SubmitDataView.as_view(), name='submitdata')
]