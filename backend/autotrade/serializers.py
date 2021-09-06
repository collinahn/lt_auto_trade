from rest_framework import serializers
from .models import AutoTrade

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTrade
        fields = [
            'mstr_stockid',
            'mstr_stockname',
            'mn_price',
            'mn_quantity',
            'mstr_sale_strategy'
        ]

# class UserInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = [
#             'Log_in_state',
#             'Name',
#             'ID',
#             'n_account',
#             'account_ID',
#         ]
