from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save


class MyUserManager(BaseUserManager):
    def create_user(self, email, user_choices, password=None):
        if not email:
            raise ValueError('Votre adresse email est obligatoire !')

        user = self.model(email=self.normalize_email(email), user_choices=user_choices)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_choices, password=None):
        user = self.create_user(email, user_choices=user_choices, password=password)
        user.is_admin = True
        user.is_staff = True

        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):

    USER_CHOICES = (
        ('ETUDIANT', 'ETUDIANT'),
        ('PROFESSEUR', 'PROFESSEUR')
    )
    email = models.EmailField(max_length=255, unique=True)
    user_choices = models.CharField(max_length=50, choices=USER_CHOICES, default='ETUDIANT')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_choices']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(default="user.png", upload_to="photos", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)


def post_save_receiver(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


post_save.connect(post_save_receiver, sender=CustomUser)