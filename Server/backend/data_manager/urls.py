from django.urls import path
from .views import SubmitDataView
from .views import RequestDataView

urlpatterns = [
    path('submitdata/', SubmitDataView.as_view(), name='submitdata'),
    path('requestdata/', RequestDataView.as_view(), name='requestdata'),
]