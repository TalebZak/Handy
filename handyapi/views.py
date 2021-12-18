from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
from .models import *
from .forms import *
from django.core.mail import send_mail, EmailMessage
import mimetypes


class IndexView(TemplateView):
    template_name = 'index.html'


class CustomRegister(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'register.html'

    def get_success_url(self):
        # once done, redirect to index
        return reverse('handy:login')


class Login(LoginView):
    template_name = 'login.html'
    form_class = AuthenticationForm

    def get_success_url(self):
        return reverse('handy:index')


class ServiceCreate(View):
    def get(self, request):
        form = ServiceCreateForm()
        return render(
            request,
            'service_create.html',
            {'form': form}
        )

    def post(self, request):
        form = ServiceCreateForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            # print all attributes of the service
            print(service.__dict__)
            try:
                print(request.user)
                customer = Customer.objects.get(user=request.user)
                service.author = customer
                service.save()
            except:
                messages.error(request, 'You must be logged in to create a service')
                return HttpResponseRedirect(reverse('handy:login'))
            return HttpResponseRedirect(reverse('handy:index'))
        else:
            # render the form with the errors
            return render(
                request,
                'service_create.html',
                {'form': form}
            )


class ServiceListView(ListView):
    # queryset with only services that are not taken
    model = Service
    queryset = Service.objects.filter(taken=False).order_by('day')
    context_object_name = 'service_list'
    template_name = 'services.html'
    paginate_by = 2


class ServiceDetail(View):
    def get(self, request, pk):
        service = Service.objects.get(pk=pk)
        comments = Comment.objects.filter(service=service)
        return render(
            request,
            'service_detail.html',
            {'service': service,
             'comments': comments,
             'form': CommentCreateForm()}
        )


class CommentCreate(View):
    def post(self, request, pk):
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = Provider.objects.get(user=request.user)
            comment.service = Service.objects.get(pk=pk)
            comment.save()
            return HttpResponseRedirect(reverse('handy:service-detail', args=[pk]))
        else:
            return render(
                request,
                'service_detail.html',
                {'form': form,
                 'service': Service.objects.get(pk=pk),
                 'comments': Comment.objects.filter(service=Service.objects.get(pk=pk))}
            )

    def get(self, request, pk):
        form = CommentCreateForm()
        return render(
            request,
            'service_detail.html',
            {'form': form,
             'service': Service.objects.get(pk=pk),
             'comments': Comment.objects.filter(service=Service.objects.get(pk=pk))
             }
        )


class CommentAccept(View):
    def get(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        comment.status = CommentStatus.ACCEPTED
        comment.save()
        return HttpResponseRedirect(reverse(
            'handy:service-detail', args=[comment.service.pk]
        )
        )


class CommentReject(View):
    def get(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        comment.status = CommentStatus.REJECTED
        comment.save()
        return HttpResponseRedirect(reverse(
            'handy:service-detail', args=[comment.service.pk]
        )
        )


class CommentDelete(View):
    def get(self, request, pk):
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return HttpResponseRedirect(reverse(
            'handy:service-detail', args=[comment.service.pk]
        )
        )


def complete_service(request, service_pk, comment_pk):
    service = Service.objects.get(pk=service_pk)
    comment = Comment.objects.get(pk=comment_pk)
    if service.completed:
        return HttpResponseRedirect(reverse('handy:index'))
    form = CompleteForm()
    if request.method == "POST":
        service.completed = True
        service.save()
        form = CompleteForm(request.POST, request.FILES)
        print(request.FILES)
        subject = 'Service completed'
        form.full_clean()
        message = str(form['message'].value()) + '\n' + 'Please find the proof of work in the attachments'
        from_email = settings.EMAIL_HOST_USER
        to_list = [service.author.user.email]
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_list,
        )
        if request.FILES:
            uploaded_file = request.FILES['image']
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
        email.send()
        return HttpResponseRedirect(reverse('handy:index'))
    return render(
        request,
        'complete.html',
        {'form': form,
         'service': service,
         'comment': comment}
    )


class ProviderProfile(View):
    def get(self, request, pk):
        provider = Provider.objects.get(pk=pk)
        return render(
            request,
            'provider_profile.html',
            {'provider': provider,
             'feedbacks': Feedback.objects.filter(recipient=provider),
             'form': FeedbackForm(),
             'exists': Feedback.objects.filter(recipient=provider,
                                               author=Customer.objects.get(user=request.user)).exists()
             }
        )

    def post(self, request, pk):
        provider = Provider.objects.get(pk=pk)
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.recipient = provider
            user = Customer.objects.get(user=request.user)
            feedback.author = user
            feedback.save()
            return HttpResponseRedirect(reverse('handy:provider-profile', args=[pk]))
        return render(
            request,
            'provider_profile.html',
            {'provider': provider,
             'feedbacks': Feedback.objects.filter(provider=provider),
             'form': form,
             'exists': Feedback.objects.filter(recipient=provider,
                                               author=Customer.objects.get(user=request.user)).exists()}
        )