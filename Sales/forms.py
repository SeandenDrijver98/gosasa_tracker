from django.forms import ModelForm
from .models import DailySale


class DailySaleForm(ModelForm):
    class Meta:
        model = DailySale
        exclude = []