from rest_framework import generics, permissions, viewsets
from app.serializers import RegisterSerializer, ImageSerializer
from django.contrib.auth.models import User
from app.models import ImagePost
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import logout
from django.core.files.storage import default_storage

import json


class BlogImage(viewsets.ModelViewSet):
    queryset = ImagePost.objects.all()
    serializer_class = ImageSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


    def get(self, request, *args, **kwargs):
        print("DEBUG: RegisterView GET called")
        try:
            template = get_template('register.html')
            rendered_template = template.render({})
            return HttpResponse(rendered_template)
        except Exception as e:
            print("DEBUG: Template loading error:", e)
            return HttpResponse("Template error: " + str(e))


def login_page(request):
    print("DEBUG: The login_page view is running")
    return render(request, 'login.html')
  

def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')

        # Validate the inputs
        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('register_page')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_page')

        # Create the user
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)  # Hash the password securely
        )

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login_page')  # Redirect to the login page

    # For GET requests, render the registration form
    return render(request, 'register.html')

@login_required
def user_dashboard_page(request):
    print ("DEBUG: Logged-in user:", request.user)
    images = ImagePost.objects.filter(author=request.user).order_by('-timestamp')

    return render(request, 'user_dashboard.html', 
                  {'images': images,
                   'user': request.user})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_images(request):
    # Return images of the logged-in user
    images = ImagePost.objects.filter(author=request.user)
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)

@login_required
def upload_image(request):
    if request.method == "POST" and request.FILES.get('image'):
        image = request.FILES['image']
        title = request.POST.get('title', 'Untitled')
        text = request.POST.get('text', '')
        tags = request.POST.get('tags', '')

        # Save the uploaded image to the database
        ImagePost.objects.create(
            author=request.user,
            title=title,
            text=text,
            tags=tags,
            image=image,
        )

        # Redirect to the user dashboard
        return redirect('user_dashboard_page')
    else:
        return redirect('user_dashboard_page')  # Redirect back if no image is uploaded

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_images(request):
    # Query by tags, timestamp, author
    tags = request.query_params.get('tags')
    author_username = request.query_params.get('author')
    timestamp = request.query_params.get('timestamp') 
    
    qs = ImagePost.objects.all()
    if tags:
        qs = qs.filter(tags__icontains=tags)
    if author_username:
        qs = qs.filter(author__username=author_username)
    if timestamp:
        qs = qs.filter(timestamp__date=timestamp)

    serializer = ImageSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if not request.user.is_staff:
        return Response({"detail": "Not authorized"}, status=403)
    images = ImagePost.objects.all()
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_image(request, image_id):
    # Admin or owner can update
    try:
        img = ImagePost.objects.get(id=image_id)
    except ImagePost.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    if not request.user.is_staff and img.author != request.user:
        return Response({"detail": "Not authorized"}, status=403)

    img.title = request.data.get('title', img.title)
    img.text = request.data.get('text', img.text)
    img.tags = request.data.get('tags', img.tags)
    # If image provided, replace it:
    if 'image' in request.FILES:
        img.image = request.FILES['image']
    img.save()

    serializer = ImageSerializer(img)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_id):
    try:
        img = ImagePost.objects.get(id=image_id)
    except ImagePost.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    if not request.user.is_staff and img.author != request.user:
        return Response({"detail": "Not authorized"}, status=403)

    img.delete()
    return Response({"detail": "Deleted"}, status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_detection_results(request):

    print("Request POST Data:", request.POST)
    print("Request FILES:", request.FILES)

    try:
        # Extract JSON data and image
        data = json.loads(request.POST.get('data', '{}'))
        image = request.FILES.get('image')

        # Validate required fields
        if not image or "image_name" not in data or "detections" not in data:
            return Response({"error": "Missing required fields"}, status=400)
        
        print("Image received:", image)
        print("Data received:", data)

        # Save the uploaded image
        image_path = default_storage.save(f"images/{data['image_name']}", image)

        # Save results to the database
        detections_text = "\n".join(
            [f"Class: {det['class']}, Confidence: {det['confidence']}, BBox: {det['bbox']}" for det in data['detections']]
        )

        ImagePost.objects.create(
            author=request.user,
            title=f"{data['image_name']}",
            text=detections_text,
            tags="YOLOv5 Detection Results",
            image=image_path
        )

        return Response({"message": "Detections uploaded successfully"}, status=201)
    except Exception as e:
        print("Error:", e)
        return Response({"error": str(e)}, status=400)

