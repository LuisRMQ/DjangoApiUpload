from django.http import JsonResponse

class RestrictAPIRoutesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_paths = [
            '/api/asistenciasmart/',
            '/api/categorias',
            '/api/asistencia/',
            '/api/salesacumuladas/', 
            '/api/asistenciasmart/' 
            '/api/productsestadisticas/', 
            '/api/totalsalesandclients/'
   '/api/employeeattendance/', 
   '/api/best-selling-and-low-stock-products/', 
   '/api/total_sales_today/', 
    '/api/asistencia/<int:pk>/',
    '/api/tarjetas/', 
    '/api/tarjetas/<int:pk>/', 
   '/api/productos/', 
   '/api/productos/<int:pk>/',
   '/api/register/', 
    '/api/token/refresh/', 
    '/api/roles/', 
   '/api/users/', 
    '/api/users/<int:pk>/', 
    '/api/categorias',
    '/api/categorias/<int:pk>/',
    '/api/proveedores/', 
    '/api/proveedores/<int:pk>/', 
    '/api/ventas/', 
    '/api/ventas/<int:pk>/', 
    '/api/employees/', 
    '/api/purchases/', 
    '/api/purchases/<int:pk>/', 
    '/api/employees/<int:pk>/', 
    '/api/customers/', 
    '/api/customers/<int:pk>/', 
    '/api/attendance/<int:employee_id>/transactions/', 
    '/api/suppliers/<int:supplier_id>/transactions/', 
        ]

        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if request.path in restricted_paths and ('mozilla' in user_agent or 'chrome' in user_agent or 'safari' in user_agent):
            return JsonResponse({"message": "Esta ruta no está disponible"})

        response = self.get_response(request)
        return response