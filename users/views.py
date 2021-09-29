from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
import jwt
import datetime
# Create your views here.


class RegisterView(APIView):

    def get(self, request):
        return render(request, 'basic_app/register.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):

    def get(self, request):
        return render(request, 'basic_app/login.html')

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        if not user.check_password(password):
            raise AuthenticationFailed('Wrong password inserted')
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'mykey', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response
        """ return HttpResponseRedirect(reverse('basic_app:details')) """


class Userview(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'mykey', algorithms=['HS256'])
        except:
            raise AuthenticationFailed('jwt expired signature error')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        """ return Response(serializer.data) """
        return render(request, 'basic_app/userdetails.html', {'user': serializer.data})

    def post(self, request):
        token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'mykey', algorithms=['HS256'])
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return HttpResponseRedirect(reverse('basic_app:details'))

    def delete(self, request):
        token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'mykey', algorithms=['HS256'])
        user = User.objects.get(id=payload['id'])
        user.delete()
        return HttpResponseRedirect(reverse('basic_app:index'))


class Logout(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout Success'
        }
        return response


class Index(APIView):
    def get(self, request):
        response = Response()
        response.delete_cookie('jwt')
        return render()
