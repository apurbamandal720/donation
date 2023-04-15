from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import permissions, authentication, viewsets, views, status, generics
from rest_framework.generics import GenericAPIView
from accounts.serializers import *
from donation import settings
import random
from django.core.mail import send_mail
from rest_framework.views import APIView
# Create your views here.

class RegistrationAPI(GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                if 'message' in user:
                    return Response(user)
                otp = random.randint(1111, 9999)
                subject = 'Verify your account'
                message = f'Hi {user["first_name"]}, Your regition OTP is- \n {otp} \nFrom Dotation team'
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user['email'], ]
                send_mail(subject, message, email_from, recipient_list)
                model_data = request.data.copy()
                model_data['otp'] = otp
                model_data['type'] = 'register'
                model_data['created_by'] = user['user']
                model_data['updated_by'] = user['user']
                serializer = OTPSerializer(data=model_data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'status': True, 'user_otp': serializer.data})
                return Response(serializer.errors)
            return Response(serializer.errors)
        except Exception as e:
            error_data = {
                "status": "failed",
                "message": str(e)
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        

class UserLoginAPI(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email=request.data['email']).last()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_verified = Otp.objects.filter(type='register', created_by=user.id, verify="true").last()
        if is_verified:
            token, created = Token.objects.get_or_create(
                    user=serializer.validated_data['user'])
            request = {
                    'user': serializer.validated_data['user']
                }
            response_serializer = UserLoginReplySerializer(token, context={'request': request})
            return Response({'status': True, 'data': response_serializer.data}, status=status.HTTP_202_ACCEPTED)  
        return Response({'status': False, 'message': 'Please verify your OTP first.', 'email': user.email}, status=status.HTTP_400_BAD_REQUEST)

        

class OTPView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        user = User.objects.filter(email=request.data['email']).last() 
        if user:
            otp = random.randint(1111, 9999)
            try:
                subject = 'Donation Team'
                message = f'Hi {user.username}, Here is OTP from Donation Team.\n{otp}'
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email, ]
                send_mail(subject, message, email_from, recipient_list)
            except Exception as e:
                print('send email.')
            model_data = request.data.copy()
            model_data['otp'] = otp
            model_data['type'] = request.data['otp_type']
            model_data['created_by'] = user.pk
            model_data['updated_by'] = user.pk
            serializer = OTPSerializer(data=model_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        return Response({'message': 'There is no user register with this email.'})

    def put(self, request):
        user = User.objects.filter(email=request.data['email']).last()
        if user:
            query_otp = Otp.objects.filter(created_by=user.id, type=request.data['otp_type']).last()
            if query_otp:
                query_data = {
                    'verify': 'true'
                }
                if int(request.data['otp']) == int(query_otp.otp):
                    query_update = OTPSerializer(query_otp, data=query_data)
                    if query_update.is_valid():
                        query_update.save()
                        return Response({'message': 'you have successfully verify OTP.'}, status=status.HTTP_200_OK)
                    return Response({'message': query_update.errors}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'OTP that you enter is not valid.', 'status': 400},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Please send OTP first.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'There is no user register with this email.'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = (permissions.AllowAny,)

    def put(self, request):
        try:
            user = User.objects.filter(email=request.data['email']).last()
            if user:
                password = str(random.randint(00000000, 99999999))
                user.set_password(password)
                user.save()
                subject = 'Dotation Account Reset Password'
                message = f'Hi {user.first_name}, Your Reset Password is- \n\n {password} \n\nFrom Dotation team'
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email, ]
                send_mail(subject, message, email_from, recipient_list)
                return Response({"status": True, 'message': f'Your reset password send this email {user.email}.'}, status=status.HTTP_201_CREATED)
            return Response({"status": False, 'message': 'There is no user register with this email.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_data = {
                "status": False,
                "message": str(e)
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        

class RequestDonationViewSet(viewsets.ModelViewSet):
    serializer_classes = {
        'create': RequestDonationSerializer,
        'list': RequestDonationListSerializer,
    }
    default_serializer_class = RequestDonationSerializer
    queryset = RequestDonation.objects.all().order_by('-id')
    permission_classes = [permissions.IsAuthenticated,]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(self.get_queryset(), many=True)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        serializer = self.get_serializer_class()(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)







