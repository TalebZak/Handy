from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    USER_TYPES_CHOICES = (
        (1, 'customer'),
        (2, 'provider'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPES_CHOICES, widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = User
        if User.USERNAME_FIELD == 'email':
            fields = ('email',)
        fields += ('first_name', 'last_name', 'phone', 'city')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        user.user_type = user_type
        user.save()
        if user_type == '1':
            customer = Customer.objects.create(user=user)
            customer.save()
        else:
            provider = Provider.objects.create(user=user)
            provider.save()


class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('title', 'description', 'price', 'image', 'category',
                  'day', 'address')
        widgets = {
            'day': DateInput(),
        }


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'new_price')


class CompleteForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
    image = forms.ImageField(required=False)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ('author', 'recipient', 'date')

