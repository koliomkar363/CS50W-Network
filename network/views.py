import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post


@csrf_exempt
def index(request):
    user = request.user
    msg = ""

    if request.method == "POST":
        post = request.POST["post"]

        if post == "":
            msg = "empty"
        elif len(post) > 200:
            msg = "error"
        else:
            Post.objects.create(
                uploader=user,
                body=post
            )
            msg = "success"

    posts = Post.objects.all()

    # Pagination
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts = page_obj.object_list

    # Hide the create post box if page number is not 1
    new_post = False
    if page_number is None or page_number == '1':
        new_post = True

    return render(request, "network/index.html", {
        "new_post": new_post,
        "posts": posts,
        "page_obj": page_obj,
        "msg": msg
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def profile(request, user_id):
    user = request.user
    uploader = User.objects.get(pk=user_id)
    posts = Post.objects.filter(uploader=user_id)
    count = posts.count()

    # Pagination
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts = page_obj.object_list

    # Toggle user's following
    if request.method == "POST":
        if user.following.filter(id=uploader.id).exists():
            user.following.remove(uploader)
        else:
            user.following.add(uploader)

    follows = uploader.following.all().count()
    followers = uploader.followers.all().count()
    following = False

    if follows == "":
        follows = 0

    if followers == "":
        followers = 0

    # Check if the user2 is followed by the user
    if user.following.filter(id=uploader.id).exists():
        following = True

    return render(request, "network/profile.html", {
        "user": user,
        "uploader": uploader,
        "posts": posts,
        "page_obj": page_obj,
        "count": count,
        "follows": follows,
        "followers": followers,
        "following": following
    })


@login_required
def following(request):
    username = request.user
    posts = Post.objects.filter(uploader__in=username.following.all())

    # Pagination
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts = page_obj.object_list

    return render(request, "network/following.html", {
        "posts": posts,
        "page_obj": page_obj
    })


@csrf_exempt
@login_required
def update(request, post_id):
    post = Post.objects.get(pk=post_id)

    # Saving the edited post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Get contents of post
    data = json.loads(request.body)

    # Update the body of the post
    if data.get("body") is not None:
        post.body = data["body"]
        post.save(update_fields=["body"])

    return JsonResponse({"message": "Changes saved successfully!"}, status=201)


@csrf_exempt
@login_required
def like(request, post_id):
    user = request.user.id

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(post.serialize())

    if request.method == "PUT":
        data = json.loads(request.body)
        if data["likes"]:
            post.likes.add(user)
        else:
            post.likes.remove(user)

        return HttpResponse(status=204)

    # Like must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)
