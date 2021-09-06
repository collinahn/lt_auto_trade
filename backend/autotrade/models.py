from django.db import models

# Create your models here.
class AutoTrade(models.Model):
    mstr_stockid = models.CharField(max_length=10)
    mstr_stockname = models.TextField()
    mn_price = models.IntegerField(default=0)
    mn_quantity = models.IntegerField(default=0)
    mstr_sale_strategy = models.TextField()

    def __str__(self):
        return self.title

