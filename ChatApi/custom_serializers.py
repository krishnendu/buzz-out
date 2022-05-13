from rest_framework import serializers
from django.core.exceptions import ValidationError
import json

class JsonListField(serializers.Field):
    
    def to_representation(self, value):
        return json.loads(value)

    def to_internal_value(self, data):
        try:
            if(type(data)==str):
                data = json.loads(data)
            return json.dumps(data)
        except:
            raise ValidationError('Not correct json format')