from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from decimal import Decimal
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='book_images/')
    borrowing_price = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category, related_name='books')

    def __str__(self):
        return self.title

class Review(models.Model):
    book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'book')
    def __str__(self):
        return f'Review for {self.book.title} by {self.user.username}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def deposit(self, amount):
        if isinstance(amount, Decimal):
            self.balance += amount
            self.save()
            send_mail(
                'Deposit Successful',
                f'You have successfully deposited {amount} to your account.',
                'ihanik.ad@gmail.com',
                [self.user.email],
                fail_silently=False,
            )
        else:
            raise ValueError('Amount must be a Decimal.')

    def __str__(self):
        return self.user.username

class BorrowRecord(models.Model):
    user = models.ForeignKey(User, related_name='borrow_records', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(blank=True, null=True)

    def borrow(self):
        if self.user.userprofile.balance >= self.book.borrowing_price:
            self.user.userprofile.balance -= self.book.borrowing_price
            self.user.userprofile.save()
            self.save()
            send_mail(
                'Book Borrowed',
                f'You have successfully borrowed {self.book.title}.',
                'from@example.com',
                [self.user.email],
                fail_silently=False,
            )
        else:
            raise ValueError("Insufficient balance to borrow this book")

    def return_book(self):
        if self.return_date is None:
            self.return_date = timezone.now()
            self.user.userprofile.balance += self.book.borrowing_price
            self.user.userprofile.save()
            self.save()
            send_mail(
                'Book Returned',
                f'You have successfully returned {self.book.title}.',
                'from@example.com',
                [self.user.email],
                fail_silently=False,
            )

    def __str__(self):
        return f'{self.book.title} borrowed by {self.user.username}'

