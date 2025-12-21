from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status, serializers
from django.contrib.auth import authenticate, login
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from apps.users.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser

authentication_classes = [TokenAuthentication]

@api_view(['POST'])
@permission_classes([])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([])
def login_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            print(token)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser]) # Apenas admins autenticados podem acessar
def set_admin_role(request, user_id):
    """
    View para um admin promover outro usuário a admin.
    """
    try:
        user_to_promote = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Torna o usuário um admin
    user_to_promote.is_staff = True
    user_to_promote.save()

    return Response(
        {'message': f'User {user_to_promote.username} is now an admin.'}, 
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser]) # Apenas admins autenticados podem acessar
def list_users(request):
    """
    View para listar todos os usuários.
    Para testes usar:
    user: admin
    password: admin123
    email: admin@email.com
    """
    users = User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name')
    return Response(users, status=status.HTTP_200_OK)