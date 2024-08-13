"""
URL configuration for ferre_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from ferreteria.api.views import EmployeeWithUserInfoView,CustomTokenObtainPairViewMovil,EmployeeAttendanceAPISmartView,RegisterView,SalesByDateRangeAPIView,TotalSalesAndSalesCountPerDayAPIView,BestAndWorstSellingProductAPIView,BestSellingProductAndLowStockAPIView,EmployeeAttendanceAllAPIView,TotalSalesTodayAPIView,EmployesAttendanceAPIView,CardRetrieveUpdateDestroy,CardListCreate,AttendanceRetrieveUpdateDestroy,AttendanceListCreate,SupplierTransactionsAPIView,CustomerListCreate,CustomerRetrieveUpdateDestroy, RoleView,PurchaseDetailAPIView, PurchaseListCreateAPIView,CustomTokenObtainPairView,EmployeeRetrieveUpdateDestroy,ProductList,CategorieList,SupplierList,UserListCreate,EmployeeListCreate, UserRetrieveUpdateDestroy,SaleListCreate,SaleRetrieveUpdateDestroy
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('api/asistencia/', AttendanceListCreate.as_view(), name='attendance-list'),
    path('api/asd/', EmployeeWithUserInfoView.as_view(), name='attendance-list'),
    path('api/salesacumuladas/', SalesByDateRangeAPIView.as_view(), name='sales-acist'), 
    path('api/asistenciasmart/', EmployeeAttendanceAPISmartView.as_view(), name='asasc-acist'),    
    path('api/productsestadisticas/', BestAndWorstSellingProductAPIView.as_view(), name='products-esta'),
    path('api/totalsalesandclients/', TotalSalesAndSalesCountPerDayAPIView.as_view(), name='totaldays-list'),
    path('api/employeeattendance/', EmployeeAttendanceAllAPIView.as_view(), name='attendance-all'),
    path('api/best-selling-and-low-stock-products/', BestSellingProductAndLowStockAPIView.as_view(), name='best-selling-and-low-stock-products'),
    path('api/total_sales_today/', TotalSalesTodayAPIView.as_view(), name='total_sales_today'),
    path('api/asistencia/<int:pk>/', AttendanceRetrieveUpdateDestroy.as_view(), name='attendance-detail'),
    path('api/tarjetas/', CardListCreate.as_view(), name='card-list'),
    path('api/tarjetas/<int:pk>/', CardRetrieveUpdateDestroy.as_view(), name='card-detail'),
    path('api/productos/', ProductList.as_view(), name='product-list'),
    path('api/productos/<int:pk>/',ProductList.as_view(), name="product-detail"),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/loginv1/', CustomTokenObtainPairViewMovil.as_view(), name='token_obtain_pair222'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/roles/', RoleView.as_view(), name='roles'),
    path('api/users/', UserListCreate.as_view(), name='user-list-create'),
    path('api/users/<int:pk>/', UserRetrieveUpdateDestroy.as_view(), name='user-retrieve-update-destroy'),
    path('api/categorias',CategorieList.as_view(), name="categories-list"),
    path('api/categorias/<int:pk>/',CategorieList.as_view(), name="categories-detail"),
    path('api/proveedores/', SupplierList.as_view(), name="proveedores-list"),
    path('api/proveedores/<int:pk>/', SupplierList.as_view(), name='proveedores-detail'),   
    path('api/ventas/', SaleListCreate.as_view(), name='ventas-list-create'),
    path('api/ventas/<int:pk>/', SaleRetrieveUpdateDestroy.as_view(), name='ventas-detail'),
    path('api/employees/', EmployeeListCreate.as_view(), name='employee-list-create'),
    path('api/purchases/', PurchaseListCreateAPIView.as_view(), name='purchase-list-create'),
    path('api/purchases/<int:pk>/', PurchaseDetailAPIView.as_view(), name='purchase-detail'),
    path('api/employees/<int:pk>/', EmployeeRetrieveUpdateDestroy.as_view(), name='employee-retrieve-update-destroy'),
    path('api/customers/', CustomerListCreate.as_view(), name='customer-list-create'),
    path('api/customers/<int:pk>/', CustomerRetrieveUpdateDestroy.as_view(), name='customer-retrieve-update-destroy'),
    path('api/attendance/<int:employee_id>/transactions/', EmployesAttendanceAPIView.as_view(), name='attendance-transactions'),
    path('api/suppliers/<int:supplier_id>/transactions/', SupplierTransactionsAPIView.as_view(), name='supplier-transactions'),
]

