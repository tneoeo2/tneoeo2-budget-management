from django.urls import path
from .views import RegistrationAPIView,JWTLoginView

app_name = "auths"

urlpatterns =[
    path('signup/',  RegistrationAPIView.as_view(), name='signup'),
    path("jwt-login/", JWTLoginView.as_view(), name='jwt-login'),
    # path("logout", views.Logout.as_view()),
]