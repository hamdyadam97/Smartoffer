from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from accounts.mixins import BranchPermissionMixin, filter_by_branch

from .models import Contact, Student
from .forms import StudentForm


class StudentListView(BranchPermissionMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    required_perm = 'view_student'
    branch_field = 'accounts__course__master__branch'

    def get_queryset(self):
        queryset = Student.objects.select_related('contact').all()
        queryset = filter_by_branch(queryset, self.request.user, 'accounts__course__master__branch')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(contact__first_name__icontains=search) |
                Q(contact__forth_name__icontains=search) |
                Q(contact__mobile__icontains=search) |
                Q(slug__icontains=search)
            )
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        preferred = self.request.GET.get('preferred_contact')
        if preferred:
            queryset = queryset.filter(preferred_contact=preferred)
        return queryset.distinct()


class StudentDetailView(BranchPermissionMixin, DetailView):
    required_perm = 'view_student'
    model = Student
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'students/student_detail.html'
    context_object_name = 'student'


class StudentCreateView(BranchPermissionMixin, CreateView):
    required_perm = 'add_student'
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')

    def form_valid(self, form):
        contact_data = {
            'first_name': form.cleaned_data['first_name'],
            'second_name': form.cleaned_data['second_name'],
            'third_name': form.cleaned_data['third_name'],
            'forth_name': form.cleaned_data['forth_name'],
            'address': form.cleaned_data['address'],
            'mobile': form.cleaned_data['mobile'],
            'phone': form.cleaned_data['phone'],
            'nationality': form.cleaned_data['nationality'],
            'identity_number': form.cleaned_data['identity_number'],
            'identity_location': form.cleaned_data['identity_location'],
            'identity_start_date': form.cleaned_data['identity_start_date'],
            'birth_date': form.cleaned_data['birth_date'],
            'birth_location': form.cleaned_data['birth_location'],
            'qualification': form.cleaned_data['qualification'],
            'photo': form.cleaned_data['photo'],
        }
        contact = Contact.objects.create(**contact_data)
        form.instance.contact = contact
        return super().form_valid(form)


class StudentUpdateView(BranchPermissionMixin, UpdateView):
    required_perm = 'change_student'
    model = Student
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')

    def form_valid(self, form):
        contact = self.object.contact
        contact.first_name = form.cleaned_data['first_name']
        contact.second_name = form.cleaned_data['second_name']
        contact.third_name = form.cleaned_data['third_name']
        contact.forth_name = form.cleaned_data['forth_name']
        contact.address = form.cleaned_data['address']
        contact.mobile = form.cleaned_data['mobile']
        contact.phone = form.cleaned_data['phone']
        contact.nationality = form.cleaned_data['nationality']
        contact.identity_number = form.cleaned_data['identity_number']
        contact.identity_location = form.cleaned_data['identity_location']
        contact.identity_start_date = form.cleaned_data['identity_start_date']
        contact.birth_date = form.cleaned_data['birth_date']
        contact.birth_location = form.cleaned_data['birth_location']
        contact.qualification = form.cleaned_data['qualification']
        contact.photo = form.cleaned_data['photo']
        contact.save()
        return super().form_valid(form)


class StudentDeleteView(BranchPermissionMixin, DeleteView):
    required_perm = 'delete_student'
    model = Student
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')


@require_POST
def student_create_ajax(request):
    form = StudentForm(request.POST, request.FILES)
    if form.is_valid():
        contact_data = {
            'first_name': form.cleaned_data['first_name'],
            'second_name': form.cleaned_data['second_name'],
            'third_name': form.cleaned_data['third_name'],
            'forth_name': form.cleaned_data['forth_name'],
            'address': form.cleaned_data['address'],
            'mobile': form.cleaned_data['mobile'],
            'phone': form.cleaned_data['phone'],
            'nationality': form.cleaned_data['nationality'],
            'identity_number': form.cleaned_data['identity_number'],
            'identity_location': form.cleaned_data['identity_location'],
            'identity_start_date': form.cleaned_data['identity_start_date'],
            'birth_date': form.cleaned_data['birth_date'],
            'birth_location': form.cleaned_data['birth_location'],
            'qualification': form.cleaned_data['qualification'],
            'photo': form.cleaned_data['photo'],
        }
        contact = Contact.objects.create(**contact_data)
        student = Student.objects.create(
            contact=contact,
            level=form.cleaned_data['level'],
            preferred_contact=form.cleaned_data['preferred_contact']
        )
        return JsonResponse({'success': True, 'message': 'تم إنشاء الطالب بنجاح', 'id': student.id, 'slug': student.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def student_update_ajax(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST, request.FILES, instance=student)
    if form.is_valid():
        contact = student.contact
        contact.first_name = form.cleaned_data['first_name']
        contact.second_name = form.cleaned_data['second_name']
        contact.third_name = form.cleaned_data['third_name']
        contact.forth_name = form.cleaned_data['forth_name']
        contact.address = form.cleaned_data['address']
        contact.mobile = form.cleaned_data['mobile']
        contact.phone = form.cleaned_data['phone']
        contact.nationality = form.cleaned_data['nationality']
        contact.identity_number = form.cleaned_data['identity_number']
        contact.identity_location = form.cleaned_data['identity_location']
        contact.identity_start_date = form.cleaned_data['identity_start_date']
        contact.birth_date = form.cleaned_data['birth_date']
        contact.birth_location = form.cleaned_data['birth_location']
        contact.qualification = form.cleaned_data['qualification']
        contact.photo = form.cleaned_data['photo']
        contact.save()
        student.level = form.cleaned_data['level']
        student.preferred_contact = form.cleaned_data['preferred_contact']
        student.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث الطالب بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
