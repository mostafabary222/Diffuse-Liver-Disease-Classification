from rest_framework import serializers 
from .models import Model 

class ModelSerializers(serializers.ModelSerializer): 
    class meta: 
        model=Model 
        fields='__all__'