from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .credentials import MpesaAccessToken, LipanaMpesaPpassword
from .models import Profile, Project, Question, Reply, Note, Message, User, VideoTutorial, Like, Category, Payment, Goal
from django.contrib.auth.models import User
import os
from django.db.models import Q
import time
import subprocess
from django.conf import settings
import json
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
import requests
from .forms import VideoUploadForm, EditUserForm, EditProjectForm
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.core.paginator import Paginator
import uuid
import random

# Create your views here.

def generate_call_link(request):
    call_id = str(uuid.uuid4())
    link = request.build_absolute_uri(f"/call/{call_id}/")
    return JsonResponse({"link": link})

@staff_member_required
def administrator_dashboard(request):
    users = User.objects.all()
    projects = Project.objects.all()
    pending_videos = VideoTutorial.objects.filter(status='PENDING').order_by('-uploaded_at')
    return render(request, 'administrator.html', {
        'users': users,
        'projects': projects,
        'pending_videos': pending_videos,
    })

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('administrator_dashboard')


@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('administrator_dashboard')  # Redirect to admin dashboard after saving
    else:
        form = EditUserForm(instance=user)

    return render(request, 'edit_user.html', {'form': form, 'user': user})

@staff_member_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return redirect('administrator_dashboard')

@staff_member_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = EditProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('administrator_dashboard')  # Redirect to admin dashboard after saving
    else:
        form = EditProjectForm(instance=project)

    return render(request, 'edit_project.html', {'form': form, 'project': project})

@staff_member_required
def approve_video(request, video_id):
    video = get_object_or_404(VideoTutorial, id=video_id, status='PENDING')
    video.status = 'APPROVED'
    video.save()
    return redirect('administrator_dashboard')

@staff_member_required
def delete_video(request, video_id):
    video = get_object_or_404(VideoTutorial, id=video_id)
    video.delete()
    return redirect('administrator_dashboard')

def forum(request):
    questions = Question.objects.prefetch_related('replies', 'replies__likes').order_by("-created_at")
    trending_questions = Question.objects.all().order_by("-created_at")[:5]
    notes = Note.objects.all().order_by("-uploaded_at")
    categories = Category.objects.all()

    leaderboard = Profile.objects.annotate(
        total_activity=F('total_questions') + F('total_answers')
    ).order_by('-total_activity')

    return render(request, "forum.html",  {"questions": questions, "notes": notes, 'leaderboard': leaderboard, "trending_questions": trending_questions, 'categories': categories})

@login_required
def post_question(request):
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        Question.objects.create(user=request.user, title=title, body=body)
        # Update user profile
        user_profile = Profile.objects.get(user=request.user)
        user_profile.total_questions += 1
        user_profile.save()
        return redirect('forum')

@login_required
def reply_question(request, question_id):
    # Get the question
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        body = request.POST.get("reply")  # Get the reply content
        if body:
            # Save the reply
            Reply.objects.create(body=body, user=request.user, question=question)
            messages.success(request, "Your reply has been posted!")
        else:
            # Show error message if the reply body is empty
            messages.error(request, "Reply cannot be empty.")
            return render(request, "forum.html", {"question": question})  # Redisplay form with question context

    # Redirect to the question detail or forum
    return redirect("forum")  # Redirect to the forum page or appropriate URL

def view_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    replies = question.replies.all().order_by("-created_at")

    # Paginate replies
    paginator = Paginator(replies, 5)  # 5 replies per page
    page_number = request.GET.get("page")
    replies_page = paginator.get_page(page_number)

    context = {
        "question": question,
        "replies": replies_page,
    }
    return render(request, "forum.html", context)

@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user = request.user

    # Check if the user has already liked the question
    existing_like = Like.objects.filter(user=user, question=question).first()

    if existing_like:
        existing_like.delete()  # Remove the like if it already exists
    else:
        Like.objects.create(user=user, question=question)  # Add a like

    return JsonResponse({'likes_count': question.likes.count()})

@login_required
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    user = request.user

    # Check if the user has already liked the reply
    existing_like = Like.objects.filter(user=user, reply=reply).first()

    if existing_like:
        existing_like.delete()  # Remove the like if it already exists
    else:
        Like.objects.create(user=user, reply=reply)  # Add a like

    return JsonResponse({'likes_count': reply.likes.count()})

def leaderboard(request):
    # Sort users by total questions and answers (combined score if needed)
    users = Profile.objects.annotate(total_activity=F('total_questions') + F('total_answers')).order_by(
        '-total_activity')

    # Pass the users to the template
    return render(request, 'forum.html', {'users': users})


@login_required
def upload_notes(request):
    if request.method == "POST":
        title = request.POST["title"]
        file = request.FILES["file"]
        Note.objects.create(user=request.user, title=title, file=file)
        return redirect("forum")


def category_view(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    questions = Question.objects.filter(category=category)

    return render(request, 'category.html', {'category': category, 'questions': questions})


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Compose the email content
        subject = f"New Contact Inquiry from {name}"
        body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n\n"
            f"Message:\n{message}"
        )
        from_email = 'wanjaladevis81@gmail.com'
        recipient_list = ['wanjaladevis81@gmail.com']

        try:
            send_mail(subject, body, from_email, recipient_list)
            messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
        except Exception as e:
            messages.error(request, f"Failed to send your message. Please try again later. Error: {str(e)}")

        return redirect('contact')

    return render(request, 'contact.html')

def base(request):
    return render(request, 'base.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('home')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('home')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('home')

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Registration successful. You can now log in.")
        return redirect('home')  # Redirect to show the login modal

    return redirect('home')


@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            return redirect('community_forum')  # Redirect to the forum page
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})

@login_required
def community_forum(request):
    questions = []
    notes = []
    # pending_videos = VideoTutorial.objects.filter(status='appoved')
    approved_videos = VideoTutorial.objects.filter(status='APPROVED').order_by('-uploaded_at')
    return render(request, 'forum.html', {
        'questions': questions,
        'notes': notes,
        # 'pending_videos': pending_videos,
        'approved_videos': approved_videos,
    })

@staff_member_required
def approve_video(request, video_id):
    video = VideoTutorial.objects.get(id=video_id)
    video.status = 'APPROVED'
    video.save()
    return redirect('community_forum')



# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('profile')  # Redirect to dashboard after successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('home')  # Redirect to show the login modal

    return redirect('home')


@login_required
def upload_profile_photo(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            profile = request.user.profile
            profile.photo = photo
            profile.save()
            return redirect('profile')  # Redirect to profile page after upload
    return redirect('profile')

@login_required
def add_goal(request):
    if request.method == "POST":
        Goal.objects.create(user=request.user, text=request.POST["goal"])
    return redirect("profile")


@login_required
def profile_view(request):
    # Fetch the user's profile, or create one if it doesn't exist
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    quotes = [
        "The best way to predict the future is to invent it. – Alan Kay",
        "Any fool can write code that a computer can understand. Good programmers write code that humans can understand. – Martin Fowler",
        "First, solve the problem. Then, write the code. – John Johnson",
    ]
    random_quote = random.choice(quotes)
    # Fetch the user's projects
    projects = Project.objects.filter(user=request.user)
    goals = request.user.goals.all()
    activities = request.user.activities.order_by("-timestamp")[:10]
    skills = request.user.skills.all()
    achievements = {
        "projects_count": projects.count(),
        "collaborations": 5,  # Static example
        "skill_level": "Advanced"}
    # Pass both the profile and projects to the template
    return render(request, 'profile.html', {'profile': profile, 'projects': projects, 'achievements': achievements, "recent_activities": activities, "skills": skills, "goals": goals, "random_quote": random_quote})


@login_required
def create_project(request):
    if request.method == 'POST':
        # Get the project name and file type from the form data
        project_name = request.POST.get('project_name')
        file_type = request.POST.get('file_type')

        # Create the project object
        project = Project(user=request.user, name=project_name, file_type=file_type)

        # Save the project to the database
        project.save()

        # Define the file path where the project file will be created
        project_directory = f'projects/{request.user.username}/{project.name}'
        os.makedirs(project_directory, exist_ok=True)  # Create directory if it doesn't exist

        # Generate the file based on the file_type
        if project.file_type == 'html':
            file_content = f'<!DOCTYPE html><html><head><title>{project.name}</title></head><body><h1>{project.name}</h1></body></html>'
            file_extension = '.html'
        elif project.file_type == 'python':
            file_content = f'# {project.name} Python file\nprint("Hello, {project.name}")'
            file_extension = '.py'
        elif project.file_type == 'java':
            file_content = f'// {project.name} Java file\npublic class {project.name} {{\n    public static void main(String[] args) {{\n        System.out.println("{project.name}");\n    }}\n}}'
            file_extension = '.java'
        else:
            file_content = ''
            file_extension = ''

        # Write the file content to a file with the appropriate extension
        file_path = os.path.join(project_directory, f'{project.name}{file_extension}')
        with open(file_path, 'w') as project_file:
            project_file.write(file_content)

        # Success message
        messages.success(request, f"Project '{project.name}' has been created successfully!")

        # Redirect to profile page or project page
        return redirect('profile')  # or redirect to a specific page, like a project detail page

    return render(request, 'profile.html')

@login_required
def start_coding(request, project_id):
    """
    Allow users to view and edit the code of their project.
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)

    # Read the current file content if it exists
    project_directory = f'projects/{request.user.username}/{project.name}'
    file_extension = {
        'html': '.html',
        'python': '.py',
        'java': '.java',
    }.get(project.file_type, '')

    file_path = os.path.join(project_directory, f'{project.name}{file_extension}')
    file_content = ""

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            file_content = file.read()

    return render(request, 'code_editor.html', {'project': project, 'file_content': file_content})


@login_required
def save_project_code(request, project_id):
    """
    Save updated project code to the file.
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        code = request.POST.get('code')  # Get the updated code from the form

        # Save the code to the file
        project_directory = f'projects/{request.user.username}/{project.name}'
        file_extension = {
            'html': '.html',
            'python': '.py',
            'java': '.java',
        }.get(project.file_type, '')

        file_path = os.path.join(project_directory, f'{project.name}{file_extension}')
        os.makedirs(project_directory, exist_ok=True)  # Ensure the directory exists

        with open(file_path, 'w') as file:
            file.write(code)

        messages.success(request, f"Code for project '{project.name}' has been saved successfully!")
        return redirect('profile')  # Redirect back to the profile page

    messages.error(request, "Failed to save the project code. Please try again.")
    return redirect('start_coding', project_id=project_id)

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        project.name = request.POST['project_name']
        project.file_type = request.POST['file_type']
        project.save()
        return redirect('profile')

    return redirect('profile')  # In case it's a GET request, just redirect back to profile page

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        project.delete()
        return redirect('profile')

    return redirect('profile')  # If it's not a POST request, just redirect back

def code_editor(request, project_id):
    project = Project.objects.get(id=project_id)
    users = User.objects.all()  # Fetch all registered users
    return render(request, 'code_editor.html', {'project': project, 'users': users})


@login_required
def search_users(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    results = User.objects.filter(username__icontains=query) if query else None

    if query:
        # Search for users whose username or email contains the query
        results = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))

    if not results:
        messages.warning(request, f"No developer with the username '{query}' is registered.")

    return render(request, 'code_editor.html', {'users': results, 'search_query': query})


@login_required
def message_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    success = False

    if request.method == "POST":
        content = request.POST.get("message")
        if content:
            Message.objects.create(sender=request.user, recipient=user, content=content)
            success = True

    # Fetch received messages for the logged-in user
    received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')

    return render(request, "message.html", {
        "user": user,
        "success": success,
        "received_messages": received_messages,
    })


def call_page(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'call.html', {'user': user})


def ide_page(request, project_id):
    projects = Project.objects.filter(id=project_id, user=request.user, file_type__in=['python', 'java'])

    return render(request, 'ide.html', {
        'projects': projects
    })
    # return render(request, 'ide.html', {'project': project})


# Render payment page
def payment_page(request, project_id):
    if request.method == "POST":
        # Handle Admin Access
        admin_passkey = request.POST.get('admin_passkey')

        if admin_passkey:
            if admin_passkey == settings.ADMIN_PASSKEY:

                return redirect('start_coding', project_id=project_id)
            else:
                # Invalid passkey message
                messages.error(request, "Invalid passkey. Access denied.")
                return redirect('profile')

    return render(request, 'payment.html', {'project_id': project_id})


# Generate access token
def get_mpesa_access_token(request):
    consumer_key = "LqDqPg8zz7OnHZ14kgCbmEH3ggc5kORvF2uAGEMkgN5tzEyS"
    consumer_secret = "EvhiHWo89EqM5SioaIGVylZA4G4tl9F1kPc3GK6UyzNJunurjfC4QcoXMAFZGCHm"
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'send_request.html', {"token": validated_mpesa_access_token})

# Process payment request
def process_payment(request, project_id):
    if request.method == "POST":
        package = request.POST.get("package")
        phone_number = request.POST.get("phone")

        # Validate phone number format
        if phone_number.startswith("0"):
            phone_number = "254" + phone_number[1:]

        # Determine package amount
        package_amounts = {"weekly": 1, "2weeks": 180, "3weeks": 250, "monthly": 300, "6months": 150, "yearly": 2500}
        amount = package_amounts.get(package, 0)
        if amount == 0:
            messages.error(request, "Invalid package selected.")
            return redirect("payment_page", project_id=project_id)

        # Initiate MPESA STK Push
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}

        # Prepare request data
        stk_push_request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://37cf-102-0-11-252.ngrok-free.app/mpesa/callback/",
            "AccountReference": "WanjalaTech LTD",
            "TransactionDesc": "CodeSpaceFee"
        }

        try:
            # Send request
            response = requests.post(api_url, json=stk_push_request, headers=headers)
            if response.status_code == 200:
                request.session["payment_status"] = "pending"
                request.session["project_id"] = project_id
                return redirect("check_payment", project_id=project_id)
            else:
                print("Error:", response.status_code, response.text)  # Debug output
                messages.error(request, f"Failed to initiate payment. Error: {response.text}")
                return redirect("payment_page", project_id=project_id)
        except requests.exceptions.RequestException as e:
            # Handle request errors
            print("Request error:", e)
            messages.error(request, "An error occurred while connecting to the MPESA API.")
            return redirect("payment_page", project_id=project_id)
    else:
        messages.error(request, "Invalid request method.")
        return redirect("payment_page", project_id=project_id)


# Check payment status
def check_payment(request, project_id):
    start_time = time.time()
    while time.time() - start_time < 30:
        payment_status = request.session.get("payment_status")
        if payment_status == "completed":
            return redirect("ide", project_id=project_id)
        time.sleep(5)  # Check every 5 seconds

    messages.error(request, "No payment detected within 1 minute.")
    return redirect("payment_page", project_id=project_id)


@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        payment_status = data.get("Body", {}).get("stkCallback", {}).get("ResultCode", -1)

        if payment_status == 0:

            request.session["payment_status"] = "completed"
        else:

            request.session["payment_status"] = "failed"

        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "Invalid request method."})

def check_pay(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        mpesa_code = request.POST.get('mpesa_code')

        try:

            payment = Payment.objects.get(phone=phone, mpesa_code=mpesa_code)

            return redirect('ide')

        except Payment.DoesNotExist:
            # Provide user feedback and redirect to the check payment page
            messages.error(request, "No payment detected with the provided details.")
            return redirect('profile')


# Execute Python or Java code
def execute_code(request):
    if request.method == "POST":
        code = request.POST.get('code')
        language = request.POST.get('language')

        if language == 'python':
            result = execute_python_code(code)
        elif language == 'java':
            result = execute_java_code(code)
        else:
            return JsonResponse({'error': 'Unsupported language'}, status=400)

        return JsonResponse({'result': result})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def execute_python_code(code):
    try:
        # Save the code to a temp file and execute
        with open('temp_code.py', 'w') as f:
            f.write(code)

        import subprocess
        result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

def execute_java_code(code):
    try:
        # Save the code to a temp file and compile
        with open('TempCode.java', 'w') as f:
            f.write(code)

        # Compile the Java code
        compile_result = subprocess.run(['javac', 'TempCode.java'], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return compile_result.stderr

        # Run the compiled Java program
        run_result = subprocess.run(['java', 'TempCode'], capture_output=True, text=True)
        os.remove('TempCode.java')  # Clean up temp file
        os.remove('TempCode.class')  # Clean up compiled class
        return run_result.stdout if run_result.returncode == 0 else run_result.stderr
    except Exception as e:
        return str(e)

def run_code(request):
    if request.method == "POST":
        code = request.POST.get("code")
        language = request.POST.get("language")

        # Map languages to command-line commands
        command_map = {
            "python": ["python3", "-c"],
            "javascript": ["node", "-e"],
            "java": ["java"],
            "c": ["gcc", "-x", "c", "-", "-o", "temp.out", "&&", "./temp.out"],
            "cpp": ["g++", "-x", "c++", "-", "-o", "temp.out", "&&", "./temp.out"],
        }

        command = command_map.get(language)
        if not command:
            return JsonResponse({"error": "Unsupported language"}, status=400)

        try:
            process = subprocess.run(
                command, input=code, text=True, capture_output=True, timeout=10
            )
            return JsonResponse({"output": process.stdout})
        except subprocess.TimeoutExpired:
            return JsonResponse({"error": "Execution timed out"}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def save_file(request):
    if request.method == "POST":
        file_name = request.POST.get("file_name")
        content = request.POST.get("content")

        if not file_name or not content:
            return JsonResponse({"error": "Invalid data"}, status=400)

        project_dir = "/path/to/project/directory"
        file_path = os.path.join(project_dir, file_name)

        try:
            with open(file_path, "w") as file:
                file.write(content)
            return JsonResponse({"message": "File saved successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# Load project files
def project_files(request):
    project_dir = os.path.join(settings.MEDIA_ROOT, 'projects', str(request.user.id))
    if os.path.exists(project_dir):
        files = os.listdir(project_dir)
    else:
        files = []

    return JsonResponse({'files': files})

# Load a specific project file
def load_file(request, project_id):
    try:
        project = get_object_or_404(Project, id=project_id)
        # Retrieve project files (assuming the related field is named 'project_files')
        files = project.project_files.all()  # Use 'project_files' instead of 'files'
        file_names = [file.name for file in files]
        return JsonResponse({'files': file_names})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)





