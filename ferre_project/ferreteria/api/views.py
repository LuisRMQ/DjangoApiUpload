from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from ferreteria.models import User, Role,Product,Card, Attendance,Category,Supplier,Sale,Employee,Purchase,Customer, SaleDetail, PurchaseDetail
from ferreteria.api.serializer import UserSerializer ,CardSerializer,AttendanceSerializer,CustomerSerializer,PurchaseSerializer, RegisterSerializer , RoleSerializer,ProductSerializer, CategorySerializer, SupplierSerializer,SaleSerializer,EmployeeSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count,OuterRef, Subquery, Q, Case, When, Value, CharField
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os
from django.utils.timezone import localtime

from django.http import HttpResponseNotFound
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta,time
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RoleView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        
        if user is not None:
            
            if user.role_id_id == 1:  
                response = super().post(request, *args, **kwargs)
                token = response.data['access']
                refresh = response.data['refresh']
                return Response({
                    'refresh': refresh,
                    'access': token,
                    'user': UserSerializer(user).data
                })
            else:
                return Response({'detail': 'Access denied: insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

class CustomTokenObtainPairViewMovil(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        
        if user is not None:
            
            if user.role_id_id == 2:  
                response = super().post(request, *args, **kwargs)
                token = response.data['access']
                refresh = response.data['refresh']
                return Response({
                    'refresh': refresh,
                    'access': token,
                    'user': UserSerializer(user).data
                })
            else:
                return Response({'detail': 'Access denied: insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProductList(APIView):
    def get(self, request, pk=None, *args, **kwargs):
     if pk is None:
        productos = Product.objects.all()
        serializer = ProductSerializer(productos, many=True)
        return Response(serializer.data)
     else:
         try:
             product = Product.objects.get(pk=pk)
         except Product.DoesNotExist:
             return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

         serializer = ProductSerializer(product)
         return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
    
        if product.image:
            image_path = product.image.path
            if os.path.isfile(image_path):
              os.remove(image_path)
    
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)      
    
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TotalSalesAndSalesCountPerDayAPIView(APIView):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        
        sales_per_day = Sale.objects.annotate(date_only=TruncDate('date')) \
            .values('date_only') \
            .annotate(
                total_sales=Sum('total'),
                sales_count=Count('sale_id')  
            ) \
            .order_by('date_only')
        
        return Response(sales_per_day, status=status.HTTP_200_OK)



class CategorieList(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        if pk is None:
            category = Category.objects.all()
            serializer = CategorySerializer(category, many=True)
            return Response(serializer.data)
        else:
         try:
             category = Category.objects.get(pk=pk)
         except Category.DoesNotExist:
             return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

         serializer = CategorySerializer(category)
         return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)       
    
    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
class TotalSalesTodayAPIView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.localdate()  
        
        total_sales = Sale.objects.filter(date__date=today).aggregate(total=Sum('total'))
        total_sales_today = total_sales['total'] or 0

        sales_count = Sale.objects.filter(date__date=today).count()

        return Response({
            'total_sales_today': total_sales_today,
            'sales_count_today': sales_count
        }, status=status.HTTP_200_OK)


class BestAndWorstSellingProductAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            best_selling_product = SaleDetail.objects.values('product__name') \
                .annotate(total_quantity=Sum('quantity')) \
                .order_by('-total_quantity') \
                .first()
            
            best_selling_product_data = {}
            if best_selling_product:
                product_name = best_selling_product['product__name']
                total_quantity = best_selling_product['total_quantity']
                
                best_selling_product_data = {
                    'product_name': product_name,
                    'total_quantity_sold': total_quantity
                }
            else:
                best_selling_product_data = {
                    'product_name': 'No sales found',
                    'total_quantity_sold': 0
                }
            
            all_products_with_sales = Product.objects.annotate(
                total_sales=Sum('saledetail__quantity')
            ).order_by('total_sales')
            
            if best_selling_product:
                all_products_with_sales = all_products_with_sales.exclude(name=best_selling_product['product__name'])
            
            worst_selling_product = all_products_with_sales.first()
            
            zero_sales_product = Product.objects.filter(
                saledetail__isnull=True
            ).first()
            
            worst_selling_product_data = {}
            if zero_sales_product:
                worst_selling_product_data = {
                    'product_name': zero_sales_product.name,
                    'total_quantity_sold': 0
                }
            elif worst_selling_product:
                product_name = worst_selling_product.name
                total_quantity = worst_selling_product.total_sales
                
                worst_selling_product_data = {
                    'product_name': product_name,
                    'total_quantity_sold': total_quantity
                }
            else:
                worst_selling_product_data = {
                    'product_name': 'No products available',
                    'total_quantity_sold': 0
                }
            
            response_data = {
                'best_selling_product': best_selling_product_data,
                'worst_selling_product': worst_selling_product_data
            }
            
            return JsonResponse(response_data, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SalesByDateRangeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            
            if not start_date_str or not end_date_str:
                return JsonResponse({'error': 'Both start_date and end_date are required.'}, status=400)
            
            try:
                start_date = parse_date(start_date_str)
                end_date = parse_date(end_date_str)
                if not start_date or not end_date:
                    raise ValueError
                
                end_date = datetime.combine(end_date, datetime.max.time()).replace(microsecond=0)
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD format.'}, status=400)
            
            sales = SaleDetail.objects.filter(
                sale__date__range=(start_date, end_date)
            ).values('product__name') \
            .annotate(total_quantity=Sum('quantity')) \
            .order_by('product__name')
            
            sales_data_list = list(sales)
            
            response_data = {
                'sales_data': sales_data_list
            }
            
            return JsonResponse(response_data, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

class BestSellingProductAndLowStockAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            best_selling_product = SaleDetail.objects.values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity').first()
            
            best_selling_product_data = {}
            if best_selling_product:
                product_name = best_selling_product['product__name']
                total_quantity = best_selling_product['total_quantity']
                
                best_selling_product_data = {
                    'product_name': product_name,
                    'total_quantity_sold': total_quantity
                }
            else:
                best_selling_product_data = {
                    'error': 'No sales found.'
                }
            
            low_stock_products = Product.objects.filter(available_quantity__lte=3).values('name', 'available_quantity')
            low_stock_products_data = list(low_stock_products)
            
            response_data = {
                'best_selling_product': best_selling_product_data,
                'low_stock_products': low_stock_products_data
            }
            
            return JsonResponse(response_data, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class SupplierTransactionsAPIView(APIView):
     def get(self, request, supplier_id):
        try:
            supplier = get_object_or_404(Supplier, id_supplier=supplier_id)
            products = Product.objects.filter(supplier=supplier).select_related('category')
            product_data = [
                {
                    'id': product.id_product,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'available_quantity': product.available_quantity,
                    'category': product.category.name if product.category else 'Sin categoría'
                }
                for product in products
            ]

            return Response({
                'products': product_data
            })

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=500)


class EmployeeAttendanceAllAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            employees = Employee.objects.all()
            employee_data_list = []

            for employee in employees:
                try:
                    card = Card.objects.get(assigned_to=employee)

                    last_entry = Attendance.objects.filter(
                        serial_tag=card.serial_number, 
                        entry_type='Entrada'
                    ).order_by('-timestamp').first()
                    
                    last_exit = Attendance.objects.filter(
                        serial_tag=card.serial_number, 
                        entry_type='Salida'
                    ).order_by('-timestamp').first()

                    employee_data = {
                        'employee_id': employee.employee_id,
                        'name': employee.name,
                        'serial_number': card.serial_number,
                        'last_entry': localtime(last_entry.timestamp) if last_entry else 'pendiente',
                        'last_exit': localtime(last_exit.timestamp) if last_exit else 'pendiente',
                    }

                except Card.DoesNotExist:
                    employee_data = {
                        'employee_id': employee.employee_id,
                        'name': employee.name,
                        'serial_number': 'Sin Asignar',
                        'last_entry': 'pendiente',
                        'last_exit': 'pendiente'
                    }
                
                employee_data_list.append(employee_data)

            return Response(employee_data_list, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployesAttendanceAPIView(APIView):
     def get(self, request, employee_id):
        try:
            employee = get_object_or_404(Employee, employee_id=employee_id)

            card = get_object_or_404(Card, assigned_to=employee)

            attendances = Attendance.objects.filter(serial_tag=card.serial_number)

            attendance_data = [
                {
                    'timestamp': attendance.timestamp,
                    'entry_type': attendance.entry_type,
                }
                for attendance in attendances
            ]

            employee_data = {
                'name': employee.name,
                'serial_number': card.serial_number,
                'attendances': attendance_data
            }

            return Response(employee_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EmployeeWithUserInfoView(APIView):
    def get(self, request):
        try:
            # Suponiendo que cada Employee tiene un campo 'user' que es una ForeignKey a User
            employees = Employee.objects.annotate(
                username=Subquery(
                    User.objects.filter(id=OuterRef('user_id')).values('username')[:1]
                ),
                user_email=Subquery(
                    User.objects.filter(id=OuterRef('user_id')).values('email')[:1]
                ),
                user_first_name=Subquery(
                    User.objects.filter(id=OuterRef('user_id')).values('first_name')[:1]
                ),
                user_last_name=Subquery(
                    User.objects.filter(id=OuterRef('user_id')).values('last_name')[:1]
                )
            ).values('employee_id', 'name', 'email', 'phone', 'department', 'username', 'user_email', 'user_first_name', 'user_last_name')

            employee_data = [
                {
                    'employee_id': employee['employee_id'],
                    'name': employee['name'],
                    'email': employee['email'],
                    'phone': employee['phone'],
                    'department': employee['department'],
                    'username': employee['username'],
                    'user_email': employee['user_email'],
                    'user_first_name': employee['user_first_name'],
                    'user_last_name': employee['user_last_name']
                }
                for employee in employees
            ]

            return Response({
                'employees': employee_data
            }, status=200)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=500)



class EmployeeAttendanceAPISmartView(APIView):
    def get(self, request):
        try:
            late_time = time(9, 15)
            
            today = timezone.now().date()

            attendance_today_subquery = Attendance.objects.filter(
                serial_tag=OuterRef('card__serial_number'),
                timestamp__date=today
            ).order_by('timestamp')

            employees = Employee.objects.annotate(
                latest_attendance_time=Subquery(attendance_today_subquery.values('timestamp')[:1]),
                marked_today=Case(
                    When(latest_attendance_time__isnull=False, then=Value('Yes')),
                    default=Value('No'),
                    output_field=CharField(),
                ),
                is_late=Case(
                    When(latest_attendance_time__time__gt=late_time, then=Value('Yes')),
                    default=Value('No'),
                    output_field=CharField(),
                )
            ).filter(
                Q(latest_attendance_time__isnull=True) | Q(latest_attendance_time__time__gt=late_time)
            ).values('name', 'marked_today', 'is_late')

            employee_data = [
                {
                    'name': employee['name'],
                    'marked_today': employee['marked_today'],
                    'is_late': employee['is_late']
                }
                for employee in employees
            ]

            return Response({
                'employees': employee_data
            }, status=200)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=500)




def generic_404_view(request):
    return HttpResponseNotFound('<h1>Página no encontrada</h1>')

class SupplierList(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        if pk is None:
            supplier = Supplier.objects.all()
            serializer = SupplierSerializer(supplier, many=True)
            return Response(serializer.data)
        else:
         try:
             supplier = Supplier.objects.get(pk=pk)
         except Supplier.DoesNotExist:
             return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

         serializer = SupplierSerializer(supplier)
         return Response(serializer.data)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)       
    
    def put(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SaleListCreate(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class SaleRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer    


class EmployeeListCreate(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer




class CustomerListCreate(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer    

class PurchaseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class PurchaseDetailAPIView(generics.RetrieveAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer    

class AttendanceListCreate(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer   

class CardListCreate(generics.ListCreateAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer

class CardRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer   