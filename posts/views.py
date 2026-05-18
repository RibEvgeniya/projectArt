from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Post, Category, ContentType, Like, Comment, Grade
from .forms import PostForm, CommentForm
from users.models import User


def home_view(request):
    feed_type = request.GET.get('feed', 'recommendations')
    if feed_type == 'following' and request.user.is_authenticated:
        following_users = request.user.following.all()
        posts = Post.objects.filter(is_published=True, author__in=following_users).order_by('-published_at')
    else:
        posts = Post.objects.filter(is_published=True).order_by('-published_at')
        if request.user.is_authenticated:
            followed_authors = request.user.following.all()
            following_posts = posts.filter(author__in=followed_authors)
            other_posts = posts.exclude(author__in=followed_authors)
            posts = following_posts.union(other_posts).order_by('-published_at')

    query = request.GET.get('q', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(content__icontains=query) | Q(
                tags__name__icontains=query) | Q(author__username__icontains=query))

    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    user_liked_posts = request.user.likes.values_list('post_id', flat=True) if request.user.is_authenticated else []

    context = {
        'posts': posts, 'categories': Category.objects.all(), 'content_types': ContentType.objects.all(),
        'query': query, 'feed_type': feed_type, 'user_liked_posts': user_liked_posts,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'posts/home.html', context)


def post_detail_view(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    post.increment_views()
    user_liked = Like.objects.filter(user=request.user, post=post).exists() if request.user.is_authenticated else False
    comments = post.comments.filter(parent=None, is_approved=True)
    for comment in comments:
        comment.grade = Grade.objects.filter(comment=comment).first()

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            if all([form.cleaned_data.get('composition'), form.cleaned_data.get('technique'),
                    form.cleaned_data.get('color'), form.cleaned_data.get('overall')]):
                Grade.objects.create(comment=comment, composition=form.cleaned_data['composition'],
                                     technique=form.cleaned_data['technique'], color=form.cleaned_data['color'],
                                     overall=form.cleaned_data['overall'])
            messages.success(request, 'Комментарий добавлен')
            return redirect('posts:post_detail', slug=post.slug)
    else:
        form = CommentForm()

    context = {'post': post, 'user_liked': user_liked, 'comments': comments, 'form': form}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Пост создан')
            return redirect('posts:post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})


@login_required
def post_edit_view(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлён')
            return redirect('posts:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form, 'post': post})


@login_required
@require_POST
def post_delete_view(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    post.delete()
    messages.success(request, 'Пост удалён')
    return redirect('users:profile', username=request.user.username)


@login_required
@require_POST
def post_like_view(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    post.likes = post.post_likes.count()
    post.save(update_fields=['likes'])
    return JsonResponse({'success': True, 'liked': liked, 'likes_count': post.likes})


from django.shortcuts import render

# Create your views here.
