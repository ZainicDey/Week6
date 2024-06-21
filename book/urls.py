from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('deposit_money/', views.deposit_money, name='deposit_money'),
    path('', views.book_list, name='book_list'),
    path('review/<int:book_id>/', views.create_or_update_review, name='create_or_update_review'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),
    path('profile/', views.profile, name='profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)