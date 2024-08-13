from rest_framework.routers import DefaultRouter
from ferreteria.api.views import UserViewSet
from django.urls import path, include
from ferreteria.api.views import generic_404_view


urlpatterns = [
   # path('api/', include('ferreteria.api.urls'))
   path('', generic_404_view),
]