from django.urls import path, include
from app.views import RegisterView, user_images, upload_image, query_images, admin_dashboard, update_image, delete_image, upload_detection_results
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from .models import ImagePost

from app import views

from rest_framework import routers


@login_required
def admin_dashboard_page(request):
    if not request.user.is_staff:
        return render(request, 'login.html', {"error": "Not authorized"})
    images = ImagePost.objects.all()
    return render(request, 'admin_dashboard.html', {'images': images})


@login_required
def upload_page(request):
    return render(request, 'upload.html')


@login_required
def edit_image_page(request, image_id):
    img = ImagePost.objects.get(id=image_id)
    return render(request, 'edit_image.html', {'image': img})

router = routers.DefaultRouter()
router.register('ImagePost', views.BlogImage)

urlpatterns = [

    path('api_root/', include(router.urls)),

    # API
    path('api/upload_detections/', views.upload_detection_results, name='upload_detection'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/images/', user_images, name='user_images'),
    path('images/upload/', upload_image, name='upload_image'),
    path('images/query/', query_images, name='query_images'),
    path('admin/images/', admin_dashboard, name='admin_api_dashboard'),
    path('images/<int:image_id>/update/', update_image, name='update_image'),
    path('images/<int:image_id>/delete/', delete_image, name='delete_image'),

    # Pages
    path('login/', views.login_page, name='login_page'),
    path('register-page/', views.register_page, name='register_page'),
    path('user/dashboard/', views.user_dashboard_page, name='user_dashboard_page'),
    path('admin/dashboard/', admin_dashboard_page, name='admin_dashboard_page'),
    path('upload/', upload_page, name='upload_page'),
    path('edit/<int:image_id>/', edit_image_page, name='edit_image_page'),

]
