"""
URLs for Class-Based Views (CBV)
"""
from django.urls import path

from .cbv_views import (
    # Company
    CompanyListCreateAPIView,
    CompanyDetailAPIView,
    
    # Branch
    BranchListCreateAPIView,
    BranchDetailAPIView,
    BranchStatisticsAPIView,
    BranchActiveListAPIView,
    
    # Bank
    BankListCreateAPIView,
    BankDetailAPIView,
    
    # MasterCategory
    MasterCategoryListCreateAPIView,
    MasterCategoryDetailAPIView,
)

urlpatterns = [
    # Company URLs
    path('companies/', CompanyListCreateAPIView.as_view(), name='company-list'),
    path('companies/<int:pk>/', CompanyDetailAPIView.as_view(), name='company-detail'),
    
    # Branch URLs
    path('branches/', BranchListCreateAPIView.as_view(), name='branch-list'),
    path('branches/active/', BranchActiveListAPIView.as_view(), name='branch-active'),
    path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),
    path('branches/<int:pk>/statistics/', BranchStatisticsAPIView.as_view(), name='branch-statistics'),
    
    # Bank URLs
    path('banks/', BankListCreateAPIView.as_view(), name='bank-list'),
    path('banks/<int:pk>/', BankDetailAPIView.as_view(), name='bank-detail'),
    
    # MasterCategory URLs
    path('master-categories/', MasterCategoryListCreateAPIView.as_view(), name='mastercategory-list'),
    path('master-categories/<int:pk>/', MasterCategoryDetailAPIView.as_view(), name='mastercategory-detail'),
]
