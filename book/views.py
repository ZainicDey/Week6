from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Book, BorrowRecord, UserProfile,Category,Review
from django.core.mail import send_mail
from .forms import UserRegistrationForm, UserProfileForm, ReviewForm
from django.shortcuts import render, get_object_or_404
from decimal import Decimal
def book_list(request):
    category_id = request.GET.get('category_id')
    if category_id:
        books = Book.objects.filter(categories__id=category_id)
    else:
        books = Book.objects.all()
    categories = Category.objects.all()
    return render(request, 'book_list.html', {'books': books, 'categories': categories})
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = Review.objects.filter(book=book)
    return render(request, 'book_detail.html', {'book': book,'reviews':reviews})
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('book_list')
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('book_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('book_list')

@login_required
def deposit_money(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(amount)
            request.user.userprofile.deposit(amount)
            return redirect('profile') 
        except ValueError:
            error = 'Invalid amount. Please enter a valid number.'
            return render(request, 'deposit_money.html', {'error': error})
    
    return render(request, 'deposit_money.html')
@login_required
def borrow_book(request, book_id):
    book = Book.objects.get(id=book_id)
    borrow_record = BorrowRecord(user=request.user, book=book)
    try:
        borrow_record.borrow()
        return redirect('profile')
    except ValueError as e:
        return render(request, 'book_detail.html', {'book': book, 'error': str(e)})

@login_required
def create_or_update_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user = request.user

    try:
        review = Review.objects.get(book=book, user=user)
        created = False
    except Review.DoesNotExist:
        review = None
        created = True

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = user
            review.save()
            return redirect('book_detail', pk=book_id)
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'book': book,
        'created': created,
    }
    return render(request, 'review.html', context)
@login_required
def return_book(request, borrow_id):
    borrow_record = BorrowRecord.objects.get(id=borrow_id)
    borrow_record.return_book()
    return redirect('profile')

@login_required
def profile(request):
    borrow_records = request.user.borrow_records.all()
    return render(request, 'profile.html', {'borrow_records': borrow_records})

