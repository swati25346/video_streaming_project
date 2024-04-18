import cv2
import threading
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse,StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.shortcuts import render,get_object_or_404
from .models import Video
from .api import UserSerializer,VideoSerializer

# User Registration 
@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required!'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists!'}, status=400)
        else:
            user = User.objects.create_user(username=username, password=password)
            return JsonResponse({'message': 'User created successfully!', 'user_id': user.id})
    else:
        return JsonResponse({'error': 'Method not allowed!'}, status=405)
    
# User Login
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful!', 'user_id': user.id})
        else:
            return JsonResponse({'error': 'Invalid credentials!'}, status=401)
    else:
        return JsonResponse({'error': 'Method not allowed!'}, status=405)

# User Logout 
@csrf_exempt
@login_required
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout!'})

# Upload Video 
@csrf_exempt
@login_required
def upload_video(request):
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        url = data.get('url')
        user = request.user
        video = Video.objects.create(name=name, url=url, user=user)
        return JsonResponse({'message': 'Video uploaded successfully!', 'video_id': video.id})
    else:
        return JsonResponse({'error': 'Method not allowed!'}, status=405)

# Edit Video API
@csrf_exempt
@login_required
def edit_video(request, video_id):
    video = Video.objects.get(id=video_id)
    if request.method == 'POST':
        data = request.POST
        video.name = data.get('name')
        video.url = data.get('url')
        video.save()
        return JsonResponse({'message': 'Video updated successfully!'})
    else:
        return JsonResponse({'error': 'Method not allowed!'}, status=405)

# Delete Video
@csrf_exempt
@login_required
def delete_video(request, video_id):
    video = Video.objects.get(id=video_id)
    video.delete()
    return JsonResponse({'message': 'Video deleted successfully!'})

# Search Videos 
@csrf_exempt
@login_required
def search_videos(request):
    query = request.GET.get('q')
    videos = Video.objects.filter(name__icontains=query)
    video_data = [{'id': video.id, 'name': video.name, 'url': video.url} for video in videos]
    return JsonResponse({'videos': video_data})

class VideoStreamThread(threading.Thread):
    def __init__(self, video_url):
        super().__init__()
        self.video_url = video_url
        self.cap = cv2.VideoCapture(self.video_url)
        self.frame = None
        self.running = True

    def run(self):
        while self.running:
            ret, self.frame = self.cap.read()
            if not ret:
                break
        self.cap.release()

    def stop(self):
        self.running = False

#all-list
@csrf_exempt
@login_required
def video_list(request):
    videos = Video.objects.all()
    context = {'videos': videos}
    return render(request, 'video/video_list.html', context)

# Watch Video 
@csrf_exempt
@login_required
def watch_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    # Initialize and start the video stream thread
    video_thread = VideoStreamThread(video.url)
    video_thread.start()

    # Function to generate video frames
    def video_feed():
        while True:
            frame = video_thread.frame
            if frame is None:
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    response = StreamingHttpResponse(video_feed(), content_type='multipart/x-mixed-replace; boundary=frame')

    # stop the video stream thread when the response is closed
    def on_stream_close():
        video_thread.stop()
        video_thread.join()
    response.streaming_content_on_close = on_stream_close

    return response