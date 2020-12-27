from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin, FormView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View, TemplateView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer, DjangoUserSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


from .models import Personne, Doc
from .forms import UserForm


class ConnexionView(generic.ListView):
    template_name = 'login/connexion.html'
    context_object_name = 'all_personne'

    def get_queryset(self):
        return Personne.objects.all()


class ProfileView(generic.DetailView):
    model = Personne
    template_name = 'login/detail.html'


class ModifUsager(CreateView):
    model = Personne
    fields = ['user_infos', 'user_logo']


class CreationFile(CreateView):
    model = Doc
    fields = ['fichier_titre', 'fichier_description', 'fichier_file']

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user.personne_set.get()
        return super(CreationFile, self).form_valid(form)


class SuppressionFile(DeleteView):
    model = Doc

    def get_success_url(self):
        return reverse_lazy('login:detail', kwargs={'slug': self.request.user.personne_set.get().slug})


class ModifUpdate(UpdateView):
    model = Personne
    fields = ['user_infos', 'user_logo']
    # success_url =  reverse_lazy('login:details')


class UserFormView(View):
    form_class = UserForm
    template_name = 'login/registration_form.html'

    # display a blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            user.personne_set.create(user_logo='Anonymous.png', slug=username)

            # returns User objects if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return redirect('login:connexion')

        return render(request, self.template_name, {'form': form})


class LoginView(TemplateView):
    template_name = 'login/login_management.html'

    def post(self, request, **kwargs):
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if (user is not None and user.is_active) or request.session['user_id'] is not None:
            login(request, user)
            return redirect('login:connexion')


class LogoutView(TemplateView):
    template_name = 'login/login_management.html'

    def get(self, request, **kwargs):
        logout(request)
        return render(request, self.template_name)

class LoginApiView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    queryset = None

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = LoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            obj = User.objects.prefetch_related('personne_set').get(email = data['email'])
            user = authenticate(username=obj.username, password=data['password'])
            if user is not None or request.session['user_id'] is not None:
                login(request, user)
                logged_user = DjangoUserSerializer(instance=obj).data
                return Response(logged_user, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

#    if not user:
#                 return Response({'error': 'Invalid Credentials'}, status=404)
#             token = Token.objects.get_or_create(user=user)
#             return Response({'token': token.key}, status=200)

class LogoutApiView(APIView):
    serializer_class = None
    def get(self, request, *args, **kwargs):
        logout(request)
        if not request.user.is_authenticated:
            return Response(status=HTTP_200_OK)
        return Response(status=HTTP_400_BAD_REQUEST)



