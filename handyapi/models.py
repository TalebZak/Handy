from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
# import all custom user necessary models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from phone_field import PhoneField
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, phone, city
                    , is_active=True, is_admin=False, is_staff=False, is_superuser=False):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a last name')
        if not phone:
            raise ValueError('Users must have a phone number')
        if not city:
            raise ValueError('Users must have a city')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            city=city,
            is_active=is_active,
            is_admin=is_admin,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name, last_name, phone, city):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a last name')
        if not phone:
            raise ValueError('Users must have a phone number')
        if not city:
            raise ValueError('Users must have a city')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            city=city,
            is_active=True,
            is_admin=True,
            is_staff=True,
            is_superuser=True,

        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    ADMIN = 'admin'
    STAFF = 'staff'
    STATUS = (
        (ADMIN, _('Admin User')),
        (STAFF, _('Staff User')),
    )
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    phone = PhoneField(blank=False, null=False, help_text='Contact phone number')
    CITIES = (
        ('Bogor', 'Bogor'),
        ('Depok', 'Depok'),
        ('Jakarta', 'Jakarta'),
        ('Tangerang', 'Tangerang'),
    )
    city = models.CharField(max_length=50, choices=CITIES, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'city']
    USER_TYPES_CHOICES = (
        (1, 'customer'),
        (2, 'provider'),
    )
    user_type = models.IntegerField(choices=USER_TYPES_CHOICES, default=1)
    objects = UserManager()

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
        return True

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    # save method that will be called when saving the user and uses create_user method from UserManager


# create a class customer extending user model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')

    # add a field for customer's address

    # before customer is saved, a user with the base data is created then the customer is saved

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


# create a class Provider extending user model with a rating
class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider')
    # add a field for provider's rating
    rating = models.FloatField(default=0.0)

    # before provider is saved, a user with the base data is created then the provider is saved

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Service(models.Model):
    title = models.CharField(max_length=30, null=False, blank=False)
    price = models.IntegerField(default=0, null=False, blank=False)
    description = models.TextField(max_length=500, null=False, blank=False)
    image = models.ImageField(upload_to='service_images', blank=True)
    taken = models.BooleanField(default=False)
    address = models.TextField(max_length=500, null=False, blank=False)
    # settable day
    day = models.DateField(default=timezone.now)
    author = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='services')
    posted_at = models.DateTimeField(default=timezone.now)
    # categories that we can choose one from like Cleaning, plumbing
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    # method that would add 50 to price if the day is the same as today and the service did not exist before and save the change to database once saved
    def save(self, *args, **kwargs):
        if self.day == timezone.now().date():
            self.price += 50
        super(Service, self).save(*args, **kwargs)


# create a class CommentStatus that would be used to set the status of the comment from accepted, rejected or pending
class CommentStatus(models.TextChoices):
    ACCEPTED = 'ACCEPTED', _('Accepted')
    REJECTED = 'REJECTED', _('Rejected')
    PENDING = 'PENDING', _('Pending')


class Comment(models.Model):
    text = models.TextField(max_length=500)
    author = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='comments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    date = models.DateTimeField(default=timezone.now)
    new_price = models.IntegerField(default=0)
    # comment status
    posted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=CommentStatus.choices, default=CommentStatus.PENDING)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    # if the comment is accepted,
    # the price of the service will be changed to the new price and other comments will be rejected
    def save(self, *args, **kwargs):
        if self.status == CommentStatus.ACCEPTED:
            self.service.price = self.new_price-50
            self.service.taken = True
            self.service.save()
            Comment.objects.filter(
                service=self.service).exclude(id=self.id).update(status=CommentStatus.REJECTED
            )
            # set taken to true

        super(Comment, self).save(*args, **kwargs)


class Feedback(models.Model):
    text = models.TextField(max_length=500)
    author = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='feedbacks')
    recipient = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(default=0, null=False, blank=False,
                                 validators=[MaxValueValidator(10), MinValueValidator(1)])
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

    # when saved the rating of the provider will be updated
    def save(self, *args, **kwargs):

        self.recipient.rating = (self.recipient.rating * self.recipient.feedback.count() + self.rating) / (
                self.recipient.feedback.count() + 1)
        self.recipient.save()
        super(Feedback, self).save(*args, **kwargs)


