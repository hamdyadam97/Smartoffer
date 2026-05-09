from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Contact, Student
from .forms import StudentForm


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.select_related('contact').all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(contact__first_name__icontains=search) |
                Q(contact__forth_name__icontains=search) |
                Q(contact__mobile__icontains=search)
            )
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        preferred = self.request.GET.get('preferred_contact')
        if preferred:
            queryset = queryset.filter(preferred_contact=preferred)
        return queryset


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'


class StudentCreateView(LoginRequiredMixin, CreateView):
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


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
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


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')
