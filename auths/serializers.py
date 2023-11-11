from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        
        
    def create(self, validated_data):
        username = User(username=validated_data['username'])
        user = User(
            username=username,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user    
    

class JWTLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)   #직렬화시에만 정보노출

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')     

        user = authenticate(username=username, password=password)

        if user and user.is_active:    #로그인 성공시
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return tokens
        else:
            raise serializers.ValidationError("아이디 또는 비밀번호가 잘못되었습니다.")