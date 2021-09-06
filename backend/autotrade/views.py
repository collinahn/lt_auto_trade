# import sys, os
# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))

from lib.RunThread import RunThread
from django.shortcuts import render 
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView 
from .serializers import PostSerializer, UserInfoSerializer
from .models import AutoTrade # Create your views here. 
from lib.SharedMem import SharedMem


class BoardListCreateView(ListCreateAPIView): 
    name = "board-list-create" 
    serializer_class = PostSerializer 
    queryset = AutoTrade.objects.all() 
    
class BoardRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    name = "board-retrieve-update-destroy" 
    serializer_class = PostSerializer 
    queryset = AutoTrade.objects.all()

class ShowCurrentUserInfo(ListCreateAPIView):
    serializers_class = UserInfoSerializer
    sm = SharedMem()
    queryset = sm.get_usr_info()
