from django.db import models
from django.contrib.auth.models import User # 导入Django内置的用户模型

class Poem(models.Model):
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    # CASCADE 表示删除用户时，该用户的所有诗歌也一并删除
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创作时间")

    def __str__(self):
        return f'《{self.title}》 by {self.author.username}'


class ForumPost(models.Model):
    """论坛上的帖子"""
    poem = models.OneToOneField(Poem, on_delete=models.CASCADE, related_name='forum_post') # 一首诗只能发一次帖
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    published_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Post by {self.author.username}: {self.poem.title}"

    def number_of_likes(self):
        return self.likes.count()

class Comment(models.Model):
    """帖子的评论"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.poem.title}"