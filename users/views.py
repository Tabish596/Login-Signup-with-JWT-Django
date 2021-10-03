from django.shortcuts import redirect, render
from .serializers import UserSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
import jwt
import datetime
from django.views import View
# Create your views here.


class RegisterView(View):

    def get(self, request):
        return render(request, 'basic_app/register.html')

    def post(self, request):
        serializer = UserSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return render(request, 'basic_app/index.html')


class LoginView(View):

    def get(self, request):
        return render(request, 'basic_app/login.html')

    def post(self, request):

        if (request.method == 'POST'):

            email = request.POST['email']
            password = request.POST['password']

            user = User.objects.filter(email=email).first()
            if user is None:
                raise AuthenticationFailed('User not found')
            if not user.check_password(password):
                raise AuthenticationFailed('Wrong password inserted')
            payload = {
                'id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
                'iat': datetime.datetime.utcnow()
            }

            token = jwt.encode(payload, 'mykey', algorithm='HS256')

            response = HttpResponseRedirect("/userdetails/")
            response.set_cookie(key='jwt', value=token, httponly=True)
            response.data = {
                'jwt': token
            }
            return response


class Userview(View):

    def get_payload(self, request):
        token = request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'mykey', algorithms=['HS256'])
        return payload

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
        return render(request, 'basic_app/userdetails.html', {'user': serializer.data})

    def post(self, request):
        payload = self.get_payload(request)
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user, data=request.POST, partial=True)
        if serializer.is_valid():
            serializer.save()
        return HttpResponseRedirect(reverse('basic_app:details'))

    def delete(self, request):
        response = HttpResponseRedirect("/login/")
        payload = self.get_payload(request)
        user = User.objects.get(id=payload['id'])
        user.delete()
        response.delete_cookie('jwt')
        return response


class Logout(View):
    def get(self, request):
        if request.method == 'GET':
            response = HttpResponseRedirect("/login/")
            response.delete_cookie('jwt')
            return response
        return redirect("/login/")
