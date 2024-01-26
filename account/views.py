from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer, ActivationSerializer, UserSerializer, RegistrationPhoneSerializer, ResetPasswordSerializer, ConfirmPasswordSerializer
from .send_email import send_confirmation_email, send_activation_sms, send_confirmation_password
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, get_object_or_404, ListAPIView
from django.contrib.auth import get_user_model, authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from django.views import View
from rest_framework import status
from django.http import HttpResponseRedirect
from django.urls import reverse
from shopbooks.tasks import send_confirmation_email_task, send_confirmation_password_task

User = get_user_model()

# My views here.
# class RegistrationView(APIView):
#     def post(self, request):
#         serializer = RegistrationSerializer(data = request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         if user:
#             try:
#                 send_confirmation_email(user.email, user.activation_code)
#             except:
#                 return Response({'message': "Зарегистрировался, но на почту код не отправился"})
#         return Response(serializer.data, status=201)
    
class ActivationView(GenericAPIView):
    serializer_class = ActivationSerializer

    def get(self, request):
        code = request.GET.get('u')
        user = get_object_or_404(User, activation_code = code)
        user.is_active = True
        user.save()
        return Response('Успешно активирован', status=200)
    
    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response('Успешно активирован!', status=200)

class   LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message':'Logout successful'}, status=200)
        except Exception as e:
            return Response({'error':'Invalid Token'}, status=400)

# class LoginView(View):
#     template_name = 'login.html'

#     def get(self, request):
#         return render(request, self.template_name)
    
#     def post(self, request):
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         if not email or not password:
#             return render(request, self.template_name, {'error': 'Email and password required!'})
#         user = authenticate(request, email = email, password=password)
#         if user:
#             login(request, user)

#             token_view = TokenObtainPairView.as_view()
#             token_response = token_view(request)

#             if token_response.status_code == status.HTTP_200_OK:
#                 return HttpResponseRedirect(reverse('dashboard') + f'?token={token_response.data["access"]}')
#         else:
#             return render(request, self.template_name, {'error': 'Invalid data'})
        
#         return render(request, self.template_name)
    
class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        action = request.POST.get('action', None)

        if action == 'login':
            return redirect('login')
        elif action == 'register':
            return redirect('registration')
        else:
            return render(request, self.template_name, {'error': 'Invalid action'})
        

class RegistrationView(APIView):
    template_name = 'registration.html'

    def get(self,request):
        return render(request, self.template_name)
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                try:
                    # send_confirmation_email(user.email, user.activation_code)
                    send_confirmation_email_task.delay(user.email, user.activation_code)
                    return redirect('activation')
                except:
                    return Response({"message": "Зарегистрировался, но на почту код не отправился.",
                                     'data': serializer.data}, status=200)
            return Response({'message': 'User registered successfully'})
        else:
            return render(request, self.template_name, {'errors': serializer.errors})
                
def activation_view(request):
    return render(request, 'activation.html')

class RegistrationPhoneView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegistrationPhoneSerializer(data = data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Registered success', status=201)
    
class ResetPasswordView(APIView):
    def get(self, request):
        return Response({'message': 'Please provide an email to reset the password'})
    
    def post(self, request):
        serializer = ConfirmPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email = email)
                user.create_phone_number_code()
                user.save()
                # send_confirmation_password(user.email, user.activation_code)
                send_confirmation_password_task.delay(user.email, user.activation_code)
                return Response({'activation_code': user.activation_code}, status=200)
            except:
                return Response({'message': 'User with this email does not exist!'}, status=404)
        return Response(serializer.errors, status=400)
        
class ResetPasswordConfirmView(APIView):
    def post(self, request):
        code = request.GET.get('u')
        user = get_object_or_404(User, activation_code = code)
        serializer = ResetPasswordSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.activation_code = ''
        user.save()
        return Response('Your password has been successfully updated', status=200)