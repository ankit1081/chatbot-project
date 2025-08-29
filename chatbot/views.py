import os
import json
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from google.generativeai import GenerativeModel, configure
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
configure(api_key=GEMINI_API_KEY)

# Create the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=(
        '''You are Conversational and image recognition chatbot, an AI assistant. Your role is to assist users by providing clear, accurate, 
        and engaging responses. You can handle complex queries, generate creative ideas, and analyze multimodal data 
        like text and images. Always respond professionally and adapt your style based on the user's needs.'''
    ),
)

# Chat session
chat_session = model.start_chat(history=[])

# Function to interact with Gemini API for chat
def get_gemini_chat_response(user_message):
    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        logger.error(f"Error getting chat response: {str(e)}")
        return "Sorry, I encountered an issue processing your request."

# Chat view
@login_required
@csrf_exempt
def chat_view(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_message = body.get('message', '')

            if not user_message:
                return JsonResponse({'error': 'No message provided.'}, status=400)

            response_message = get_gemini_chat_response(user_message)

            return JsonResponse({'response': response_message})

        except Exception as e:
            logger.error(f"Error in chat_view: {str(e)}")
            return JsonResponse({'error': f"Internal Server Error: {str(e)}"}, status=500)
    else:
        return render(request, 'chat.html')






# User signup view
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


# User login view
def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            error = "Invalid username or password."
    return render(request, 'login.html', {'error': error})


# User logout view
def logout_view(request):
    logout(request)
    return redirect('login')