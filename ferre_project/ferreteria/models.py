from django.utils import timezone
from django.db import models, transaction
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import F

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default='Sin descripción')

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El campo de nombre de usuario debe estar establecido')

        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)  
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='ferreteria_users',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='ferreteria_user_permissions', 
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # Puedes agregar otros campos si son necesarios

    def __str__(self):
        return self.username


class Category(models.Model):
    id_categorie = models.AutoField(primary_key=True, db_column='id_categorie')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Supplier(models.Model):
    id_supplier = models.AutoField(primary_key=True, db_column='id_supplier')
    name = models.CharField(max_length=100)
    name_contact  =models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=255)
    country  = models.CharField(max_length=100)
    cp  = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

#Checador Asistencia
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  


    def __str__(self):
        return self.name
    
class Card(models.Model):
    card_id = models.AutoField(primary_key=True)
    serial_number = models.CharField(max_length=50, unique=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.serial_number    


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    entry_type = models.CharField(max_length=10)  
    serial_tag = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.serial_tag} - {self.timestamp} ({self.entry_type})"

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Product(models.Model):
    id_product = models.AutoField(primary_key=True, db_column='id_product')
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost =models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.name
    

class Sale(models.Model):
    sale_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sales')

    def __str__(self):
        return f"Sale {self.sale_id} - {self.customer} - {self.date}"
    
class SaleDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Sale {self.sale.sale_id})"    
    

class Purchase(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Purchase {self.purchase_id} - {self.supplier.name} - {self.date}"

class PurchaseDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Purchase {self.purchase.purchase_id})"
