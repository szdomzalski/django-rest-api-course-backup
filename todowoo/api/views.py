from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser

from .serializers import ToDoSerializer, ToDoCompleteSerializer

from todo.models import Todo


# Create your views here.
class TodoCompletedList(generics.ListAPIView):
    serializer_class = ToDoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        return Todo.objects.filter(user=user, datecompleted__isnull=False).order_by('-datecompleted')


class TodoListCreate(generics.ListCreateAPIView):
    serializer_class = ToDoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        return Todo.objects.filter(user=user, datecompleted__isnull=True).order_by('-created')

    def perform_create(self, serializer: ToDoSerializer) -> None:
        serializer.save(user=self.request.user)


class ToDoDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ToDoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        return Todo.objects.filter(pk=self.kwargs['pk'], user=user)


class ToDoComplete(generics.UpdateAPIView):
    serializer_class = ToDoCompleteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        return Todo.objects.filter(pk=self.kwargs['pk'], user=user)

    def perform_update(self, serializer: ToDoCompleteSerializer) -> None:
        serializer.instance.datecompleted = timezone.now()
        serializer.save()


@csrf_exempt
def signup(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(data['username'], password=data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return JsonResponse(
                {'error': 'That username has already been taken. Please choose a new username.'},
                status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(request, username=data['username'], password=data['password'])
        if user is None:
            return JsonResponse(
                {'error': 'Could not login. Please check username and password'},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                token = Token.objects.get(user=user)
            except Exception:
                token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=status.HTTP_200_OK)
