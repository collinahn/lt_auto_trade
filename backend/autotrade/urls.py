#backend/post/urls.py
from django.urls import path
from .views import BoardListCreateView, BoardRetrieveUpdateDestroyAPIView, ShowCurrentUserInfo

urlpatterns = [
    path('', BoardListCreateView.as_view(), name=BoardListCreateView.name),
    path('<int:pk>/', BoardRetrieveUpdateDestroyAPIView.as_view(), name = BoardRetrieveUpdateDestroyAPIView.name),
    path('userinfo', ShowCurrentUserInfo.as_view())
]
