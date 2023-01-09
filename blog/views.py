from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.db import connection

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def SQLi(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = None
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM auth_user WHERE username = '" + username + "'"
            )
            row = cursor.fetchone()
            if row:
                # Check the password
                print(row)
                hashed_password = row[1]
                # if check_password(password, hashed_password):
                # Return the user object
                user = User(row[0], row[1], row[2])

        # user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog-home')
        else:
            return render(request, 'blog/SQLi.html', {'error': 'Invalid login credentials'})
    else:
        return render(request, 'blog/SQLi.html')

def search(request):
    model = Post
    query = request.GET.get('q')
    results = 'aa'
    if query:
        results = Post.objects.filter(Q(title_icontains=query) | Q(content_icontains=query))

    return render(request, 'blog/post_list.html', {'results': results, 'query': query})

def posts(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/posts.html', context)
