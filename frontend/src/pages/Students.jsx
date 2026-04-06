import { useEffect, useState } from 'react';
import { useStudentStore } from '../stores/studentStore';
import { Plus, Search, Edit2, Trash2, User, GraduationCap } from 'lucide-react';

export default function Students() {
  const { students, fetchStudents, deleteStudent, isLoading } = useStudentStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '',
    second_name: '',
    third_name: '',
    forth_name: '',
    mobile: '',
    phone: '',
    email: '',
    address: '',
    identity_number: '',
    nationality: '',
    birth_date: '',
    qualification: '',
    level: 'مبتدئ'
  });

  useEffect(() => {
    fetchStudents();
  }, []);

  const filteredStudents = students.filter(student => 
    student.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.mobile?.includes(searchTerm) ||
    student.identity_number?.includes(searchTerm)
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const studentData = {
        ...formData,
        contact: {
          first_name: formData.first_name,
          second_name: formData.second_name,
          third_name: formData.third_name,
          forth_name: formData.forth_name,
          mobile: formData.mobile,
          phone: formData.phone,
          address: formData.address,
          identity_number: formData.identity_number,
          nationality: formData.nationality,
          birth_date: formData.birth_date,
          qualification: formData.qualification
        }
      };
      
      if (editingStudent) {
        await useStudentStore.getState().updateStudent(editingStudent.id, studentData);
      } else {
        await useStudentStore.getState().createStudent(studentData);
      }
      setShowModal(false);
      setEditingStudent(null);
      resetForm();
    } catch (error) {
      console.error('Error saving student:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      second_name: '',
      third_name: '',
      forth_name: '',
      mobile: '',
      phone: '',
      email: '',
      address: '',
      identity_number: '',
      nationality: '',
      birth_date: '',
      qualification: '',
      level: 'مبتدئ'
    });
  };

  const handleEdit = (student) => {
    setEditingStudent(student);
    setFormData({
      first_name: student.first_name || '',
      second_name: student.second_name || '',
      third_name: student.third_name || '',
      forth_name: student.forth_name || '',
      mobile: student.mobile || '',
      phone: student.phone || '',
      email: student.email || '',
      address: student.address || '',
      identity_number: student.identity_number || '',
      nationality: student.nationality || '',
      birth_date: student.birth_date || '',
      qualification: student.qualification || '',
      level: student.level || 'مبتدئ'
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا الطالب؟')) {
      await deleteStudent(id);
    }
  };

  const levelColors = {
    'مبتدئ': 'bg-green-100 text-green-800',
    'متوسط': 'bg-yellow-100 text-yellow-800',
    'متقدم': 'bg-red-100 text-red-800'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">الطلاب</h1>
          <p className="text-gray-500 mt-1">إدارة بيانات الطلاب والمتدربين</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          طالب جديد
        </button>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث بالاسم، الجوال، أو رقم الهوية..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pr-10"
          />
        </div>
      </div>

      {/* Students Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredStudents.length === 0 ? (
          <div className="text-center py-12">
            <GraduationCap className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا يوجد طلاب</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الطالب</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">رقم الهوية</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الجوال</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المستوى</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredStudents.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                          <User className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-gray-900">{student.full_name}</div>
                          <div className="text-sm text-gray-500">{student.email || '-'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{student.identity_number || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900" dir="ltr">{student.mobile || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${levelColors[student.level] || 'bg-gray-100'}`}>
                        {student.level}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => handleEdit(student)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(student.id)}
                          className="p-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">
                {editingStudent ? 'تعديل طالب' : 'طالب جديد'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">الاسم الأول *</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    className="input"
                    required
                  />
                </div>
                <div>
                  <label className="label">الاسم الثاني</label>
                  <input
                    type="text"
                    value={formData.second_name}
                    onChange={(e) => setFormData({...formData, second_name: e.target.value})}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">الاسم الثالث</label>
                  <input
                    type="text"
                    value={formData.third_name}
                    onChange={(e) => setFormData({...formData, third_name: e.target.value})}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">الاسم الرابع *</label>
                  <input
                    type="text"
                    value={formData.forth_name}
                    onChange={(e) => setFormData({...formData, forth_name: e.target.value})}
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">رقم الجوال</label>
                  <input
                    type="text"
                    value={formData.mobile}
                    onChange={(e) => setFormData({...formData, mobile: e.target.value})}
                    className="input"
                    dir="ltr"
                  />
                </div>
                <div>
                  <label className="label">البريد الإلكتروني</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="input"
                    dir="ltr"
                  />
                </div>
              </div>
              <div>
                <label className="label">العنوان</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="input"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">رقم الهوية</label>
                  <input
                    type="text"
                    value={formData.identity_number}
                    onChange={(e) => setFormData({...formData, identity_number: e.target.value})}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">الجنسية</label>
                  <input
                    type="text"
                    value={formData.nationality}
                    onChange={(e) => setFormData({...formData, nationality: e.target.value})}
                    className="input"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">تاريخ الميلاد</label>
                  <input
                    type="date"
                    value={formData.birth_date}
                    onChange={(e) => setFormData({...formData, birth_date: e.target.value})}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">المؤهل</label>
                  <input
                    type="text"
                    value={formData.qualification}
                    onChange={(e) => setFormData({...formData, qualification: e.target.value})}
                    className="input"
                  />
                </div>
              </div>
              <div>
                <label className="label">المستوى</label>
                <select
                  value={formData.level}
                  onChange={(e) => setFormData({...formData, level: e.target.value})}
                  className="input"
                >
                  <option value="مبتدئ">مبتدئ</option>
                  <option value="متوسط">متوسط</option>
                  <option value="متقدم">متقدم</option>
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="flex-1 btn-primary">
                  {editingStudent ? 'حفظ التChanges' : 'إضافة'}
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="flex-1 btn-secondary"
                >
                  إلغاء
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
