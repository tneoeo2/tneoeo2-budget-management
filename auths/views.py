from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegistrationSerializer,JWTLoginSerializer

class RegistrationAPIView(generics.CreateAPIView):
    '''
    api/auth/signup/ : 회원가입 api
    '''
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)   #사용자 리프레시 토큰 생성
            access_token = str(refresh.access_token)  
        else:
            raise ParseError(detail="아이디, 비밀번호를 모두 입력해야합니다.")


        return Response({'access_token': access_token}, status=status.HTTP_201_CREATED)


class JWTLoginView(APIView):
    '''
    api/auth/jwt-login/ : 회원가입 api
    '''
    serializer_class = JWTLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValueError as e:
            return Response({'error': e}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = serializer.validated_data
        return Response(tokens, status=status.HTTP_200_OK)