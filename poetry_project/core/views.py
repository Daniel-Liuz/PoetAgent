# E:\Program\poetry_project\core\views.py

# Python 标准库 & 第三方库
import json
import requests

# Django 核心库
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# 本地应用 (core) 的导入
from .forms import CustomUserCreationForm
from .models import Poem, ForumPost, Comment


# --- 认证视图 ---

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('generate')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


# --- 核心功能视图 ---

@login_required
def generate_poem_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        input_text = data.get('inputText')

        flask_api_url = 'http://127.0.0.1:5000/process'
        try:
            response = requests.post(flask_api_url, json={'inputText': input_text})
            response.raise_for_status()
            poem_data = response.json()
            generated_poem = poem_data.get('result')
            return JsonResponse({'status': 'success', 'poem': generated_poem})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'error', 'message': f'诗歌生成服务连接失败: {e}'})

    return render(request, 'core/generate.html')

@login_required
def my_poems_view(request):
    poems = Poem.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'core/my_poems.html', {'poems': poems})

@login_required
def save_poem_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            if not title or not content:
                return JsonResponse({'status': 'error', 'message': '标题和内容不能为空。'}, status=400)
            Poem.objects.create(title=title, content=content, author=request.user)
            return JsonResponse({'status': 'success', 'message': '诗歌已成功保存到“我的作品”！'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'保存失败: {e}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

# --- 新增：删除诗歌的视图 ---
@login_required
def delete_poem_view(request, poem_id):
    """处理删除诗歌的请求"""
    if request.method == 'POST':
        poem = get_object_or_404(Poem, pk=poem_id)
        if request.user != poem.author:
            return HttpResponseForbidden("你没有权限删除这首诗。")
        poem.delete()
        return redirect('my_poems')
    return redirect('my_poems')


# --- 论坛相关视图 ---

@login_required
def forum_list_view(request):
    posts = ForumPost.objects.all().order_by('-published_at')
    return render(request, 'core/forum_list.html', {'posts': posts})


@login_required
def forum_post_detail_view(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    all_comments = post.comments.all().order_by('created_at')
    user_has_liked = post.likes.filter(id=request.user.id).exists()
    ai_comment = all_comments.filter(author__username='AI_Poet_Critique').first()
    human_comments = all_comments.exclude(author__username='AI_Poet_Critique')

    return render(request, 'core/forum_post_detail.html', {
        'post': post,
        'human_comments': human_comments,
        'user_has_liked': user_has_liked,
        'ai_comment': ai_comment,
    })


@login_required
def publish_to_forum_view(request, poem_id):
    if request.method == 'POST':
        poem = get_object_or_404(Poem, id=poem_id, author=request.user)
        if not ForumPost.objects.filter(poem=poem).exists():
            post = ForumPost.objects.create(poem=poem, author=request.user)
            return redirect('forum_post_detail', post_id=post.id)
    return redirect('my_poems')


@login_required
def add_comment_view(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
    return redirect('forum_post_detail', post_id=post.id)


# --- AJAX 交互视图 ---

@login_required
def like_post_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(ForumPost, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'likes_count': post.number_of_likes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def request_ai_critique_view(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(ForumPost, id=post_id)
        ai_username = 'AI_Poet_Critique'
        ai_user, _ = User.objects.get_or_create(username=ai_username)
        if post.comments.filter(author=ai_user).exists():
            return JsonResponse({'status': 'already_exists'})
        try:
            ai_server_url = 'http://127.0.0.1:5001/get_ai_critique'
            response = requests.post(ai_server_url, json={'poem': post.poem.content}, timeout=120)
            response.raise_for_status()
            ai_data = response.json()
            critique = ai_data.get('critique')
            if critique:
                Comment.objects.create(post=post, author=ai_user, content=critique)
                return JsonResponse({'status': 'success', 'critique': critique, 'author': ai_username})
            else:
                return JsonResponse({'status': 'error', 'message': 'AI未能生成评论。'}, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'error', 'message': f'无法连接到AI服务: {e}'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'发生内部错误: {e}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
