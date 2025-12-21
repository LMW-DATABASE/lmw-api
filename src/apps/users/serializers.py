from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="Este nome de usuário já está em uso."
                    )
                ]
            },
            'email': {
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        message="Um usuário com este e-mail já existe."
                    )
                ]
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user