# E:\Program\poetry_project\core\urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 核心功能
    path('', views.generate_poem_view, name='generate'),
    path('generate/', views.generate_poem_view, name='generate'),
    path('save_poem/', views.save_poem_view, name='save_poem'),
    path('my-poems/', views.my_poems_view, name='my_poems'),

    # 认证
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset_form.html',
                                                                 email_template_name='core/password_reset_email.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'),
         name='password_reset_complete'),

    # 论坛功能 URLs
    path('forum/', views.forum_list_view, name='forum_list'),
    path('forum/post/<int:post_id>/', views.forum_post_detail_view, name='forum_post_detail'),
    path('poem/<int:poem_id>/publish/', views.publish_to_forum_view, name='publish_to_forum'),
    path('forum/post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),

    # --- 新增：删除诗歌的URL ---
    path('poem/<int:poem_id>/delete/', views.delete_poem_view, name='delete_poem'),

    # AJAX 交互 URLs
    path('forum/post/<int:post_id>/like/', views.like_post_view, name='like_post'),
    path('forum/post/<int:post_id>/critique/', views.request_ai_critique_view, name='request_ai_critique'),
]
