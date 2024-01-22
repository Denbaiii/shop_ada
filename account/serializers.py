from rest_framework import serializers
from django.contrib.auth import get_user_model
from .send_email import send_activation_sms
from shopbooks.tasks import send_activation_sms_task

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length = 6, max_length = 20, required = True, write_only = True)
    password_confirmation = serializers.CharField(min_length = 6, max_length = 20, required = True, write_only = True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirmation', 'first_name', 'last_name', 'username', 'avatar')

    def validate(self, attrs):
            password = attrs['password']
            password_confirmation = attrs.pop('password_confirmation')
            if password != password_confirmation:
                raise serializers.ValidationError(
                    'The password must be the same'
                )
            if password.isdigit() or password.isalpha():
                raise serializers.ValidationError(
                    'The password must contain letters and numbers'
                )
            return attrs
        
    def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user
    

class ActivationSerializer(serializers.Serializer):
    code = serializers.CharField(required = True)

    def validate(self, attrs):
        self.code = attrs['code']
        return attrs
    
    def save(self, **kwargs):
        try:
            user = User.objects.get(activation_code = self.code)
            user.is_active = True
            user.activation_code = ''
            user.save()
        except:
            raise serializers.ValidationError('Неверный код активации!')
        
class UserSerializer(serializers.ModelSerializer):
     class Meta:
          model = User
          exclude = ('password',)

class RegistrationPhoneSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length = 6, max_length = 20, required = True, write_only = True)
    password_confirmation = serializers.CharField(min_length = 6, max_length = 20, required = True, write_only = True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirmation', 'first_name', 'last_name', 'username','phone_number')
    
    def validate(self, attrs):
            password = attrs['password']
            password_confirmation = attrs.pop('password_confirmation')
            if password != password_confirmation:
                raise serializers.ValidationError(
                    'The password must be the same!'
                )
            if password.isdigit() or password.isalpha():
                raise serializers.ValidationError(
                    'The password must contain letters and numbers!'
                )
            return attrs


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # send_activation_sms(user.phone_number, user.activation_code)
        send_activation_sms_task.delay(user.phone_number, user.activation_code)
        return user
    
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length = 6, max_length = 20, required = True, write_only = True)
    password_confirmation = serializers.CharField(min_length = 6, max_length = 20, required = True, write_only = True)
    
    def validate(self, attrs):
        password = attrs['new_password']
        password_confirmation = attrs.pop('password_confirmation')
        
        if password!=password_confirmation:
            raise serializers.ValidationError(
                'Password must be same'
            )
            
        if password.isdigit() or password.isalpha():
            raise serializers.ValidationError(
                'The password must contain letters and numbers'
            )
        return attrs
    
    

class ConfirmPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


     