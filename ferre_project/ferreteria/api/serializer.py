from rest_framework import serializers
from ferreteria.models import User
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.response import Response 
from ferreteria.models import Role, Customer,Attendance,Card,Product, Category, Supplier,Sale, SaleDetail,Employee,PurchaseDetail,Purchase
from django.db.models import F

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'role_id']  

    def create(self, validated_data):
        role_id = validated_data.pop('role_id', None)
        user = User.objects.create_user(
            username=validated_data['username'], 
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        if role_id:
            user.role_id = role_id
            user.save()
        return user

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'        

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'         

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'         

class SaleDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = SaleDetail
        fields = ['detail_id', 'sale', 'product', 'quantity', 'unit_price']
        read_only_fields = ['detail_id', 'sale']  

class SaleSerializer(serializers.ModelSerializer):
    details = SaleDetailSerializer(many=True)

    class Meta:
        model = Sale
        fields = ['sale_id', 'date', 'customer', 'total', 'employee', 'details']
        read_only_fields = ['sale_id', 'date'] 

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        sale = Sale(**validated_data)

        with transaction.atomic():
            try:
                for detail_data in details_data:
                    product = detail_data['product']
                    quantity = detail_data['quantity']

                    if quantity > product.available_quantity:
                        raise ValidationError(f"No hay suficiente stock para el producto {product.name}. La venta no puede completarse.")

                sale.save()

                for detail_data in details_data:
                    SaleDetail.objects.create(sale=sale, **detail_data)

                    product = detail_data['product']
                    quantity = detail_data['quantity']
                    product.available_quantity -= quantity
                    product.save()

            except ValidationError as e:
                raise serializers.ValidationError({'respuesta': str(e)})

        return sale

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        instance.customer = validated_data.get('customer', instance.customer)
        instance.total = validated_data.get('total', instance.total)
        instance.employee = validated_data.get('employee', instance.employee)

        with transaction.atomic():
            instance.save()

            instance.details.all().delete()
            for detail_data in details_data:
                SaleDetail.objects.create(sale=instance, **detail_data)

                product = detail_data['product']
                quantity = detail_data['quantity']
                product.available_quantity -= quantity
                product.save()

        return instance
    
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
#Se crean tabla detalle compra, para almacenar el detalle, se activan signals para manejar el incremento
# de productos al hacer la compra, al momento de que se detecte un evento de creacion de este modelo
#se activa el signal para poder hacer la suma del inventario.
class PurchaseDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = PurchaseDetail
        fields = ['detail_id', 'purchase', 'product', 'quantity', 'unit_price']
        read_only_fields = ['detail_id', 'purchase']  

class PurchaseSerializer(serializers.ModelSerializer):
    details = PurchaseDetailSerializer(many=True)

    class Meta:
        model = Purchase
        fields = ['purchase_id', 'date', 'supplier', 'total', 'details']
        read_only_fields = ['purchase_id', 'date']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        
        with transaction.atomic():
            try:
                purchase = Purchase.objects.create(**validated_data)

                for detail_data in details_data:
                    product = detail_data['product']
                    quantity = detail_data['quantity']

                    if quantity <= 0:
                        raise ValidationError("La cantidad debe ser mayor que cero.")


                    PurchaseDetail.objects.create(purchase=purchase, **detail_data)

                    product.available_quantity = F('available_quantity') + quantity
                    product.save()

            except ValidationError as e:
                raise serializers.ValidationError({'respuesta': str(e)})

        return purchase

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        instance.supplier = validated_data.get('supplier', instance.supplier)
        instance.total = validated_data.get('total', instance.total)

        with transaction.atomic():
            instance.save()

            instance.details.all().delete()
            for detail_data in details_data:
                product = detail_data['product']
                quantity = detail_data['quantity']

                if quantity <= 0:
                    raise ValidationError("La cantidad debe ser mayor que cero.")

                if quantity > product.available_quantity:
                    raise ValidationError(f"No hay suficiente stock para el producto {product.name}. La compra no puede completarse.")

                PurchaseDetail.objects.create(purchase=instance, **detail_data)

                product.available_quantity = F('available_quantity') + quantity
                product.save()

        return instance        