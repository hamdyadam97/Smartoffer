from django.urls import path

from .views import (
    PersonListView, PersonDetailView, PersonCreateView, PersonUpdateView, PersonDeleteView,
    TeamListView, TeamDetailView, TeamCreateView, TeamUpdateView, TeamDeleteView,
    team_create_ajax, team_update_ajax,
    BranchAccessListView, BranchAccessCreateView, BranchAccessUpdateView, BranchAccessDeleteView,
    RoleListView, RoleDetailView, RoleCreateView, RoleUpdateView, RoleDeleteView,
    EmployeeRoleListView, EmployeeRoleCreateView, EmployeeRoleUpdateView, EmployeeRoleDeleteView,
    EmployeePerformanceListView, EmployeePerformanceCreateView, EmployeePerformanceUpdateView, EmployeePerformanceDeleteView,
)

urlpatterns = [
    # Person URLs
    path('persons/', PersonListView.as_view(), name='person-list'),
    path('persons/<int:pk>/', PersonDetailView.as_view(), name='person-detail'),
    path('persons/create/', PersonCreateView.as_view(), name='person-create'),
    path('persons/<int:pk>/update/', PersonUpdateView.as_view(), name='person-update'),
    path('persons/<int:pk>/delete/', PersonDeleteView.as_view(), name='person-delete'),

    # Team URLs
    path('teams/', TeamListView.as_view(), name='team-list'),
    path('teams/<str:slug>/', TeamDetailView.as_view(), name='team-detail'),
    path('teams/create/', TeamCreateView.as_view(), name='team-create'),
    path('teams/<str:slug>/update/', TeamUpdateView.as_view(), name='team-update'),
    path('teams/<str:slug>/delete/', TeamDeleteView.as_view(), name='team-delete'),
    path('teams/ajax/create/', team_create_ajax, name='team-create-ajax'),
    path('teams/ajax/<int:pk>/update/', team_update_ajax, name='team-update-ajax'),

    # BranchAccess URLs
    path('branch-accesses/', BranchAccessListView.as_view(), name='branchaccess-list'),
    path('branch-accesses/create/', BranchAccessCreateView.as_view(), name='branchaccess-create'),
    path('branch-accesses/<int:pk>/update/', BranchAccessUpdateView.as_view(), name='branchaccess-update'),
    path('branch-accesses/<int:pk>/delete/', BranchAccessDeleteView.as_view(), name='branchaccess-delete'),

    # Role URLs
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('roles/create/', RoleCreateView.as_view(), name='role-create'),
    path('roles/<int:pk>/update/', RoleUpdateView.as_view(), name='role-update'),
    path('roles/<int:pk>/delete/', RoleDeleteView.as_view(), name='role-delete'),

    # EmployeeRole URLs
    path('employee-roles/', EmployeeRoleListView.as_view(), name='employeerole-list'),
    path('employee-roles/create/', EmployeeRoleCreateView.as_view(), name='employeerole-create'),
    path('employee-roles/<int:pk>/update/', EmployeeRoleUpdateView.as_view(), name='employeerole-update'),
    path('employee-roles/<int:pk>/delete/', EmployeeRoleDeleteView.as_view(), name='employeerole-delete'),

    # EmployeePerformance URLs
    path('employee-performances/', EmployeePerformanceListView.as_view(), name='employeeperformance-list'),
    path('employee-performances/create/', EmployeePerformanceCreateView.as_view(), name='employeeperformance-create'),
    path('employee-performances/<int:pk>/update/', EmployeePerformanceUpdateView.as_view(), name='employeeperformance-update'),
    path('employee-performances/<int:pk>/delete/', EmployeePerformanceDeleteView.as_view(), name='employeeperformance-delete'),
]
