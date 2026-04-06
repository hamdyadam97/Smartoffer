import { useEffect, useState } from 'react';
import { useRegistrationStore } from '../stores/registrationStore';
import { useCourseStore } from '../stores/courseStore';
import { useStudentStore } from '../stores/studentStore';
import { Plus, Search, Edit2, Trash2, UserPlus } from 'lucide-react';

export default function Registrations() {
  const { registrations, fetchRegistrations, deleteRegistration, isLoading } = useRegistrationStore();
  const { courses, fetchCourses } = useCourseStore();
  const { students, fetchStudents } = useStudentStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingRegistration, setEditingRegistration] = useState(null);
  const [formData, setFormData] = useState({
    course: '',
    student: '',
    code: '',
    course_price: '',
    course_discount_amount: '',
    course_payment_type: 'نقدي',
    note: ''
  });

  useEffect(() => {
    fetchRegistrations();
    fetchCourses();
    fetchStudents();
  }, []);

  const filteredRegistrations = registrations.filter(reg => 
    reg.student_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    reg.key?.includes(searchTerm) ||
    reg.course_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingRegistration) {
        await useRegistrationStore.getState().updateRegistration(editingRegistration.id, formData);
      } else {
        await useRegistrationStore.getState().createRegistration(formData);
      }
      setShowModal(false);
      setEditingRegistration(null);
      resetForm();
    } catch (error) {
      console.error('Error saving registration:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      course: '',
      student: '',
      code: '',
      course_price: '',
      course_discount_amount: '',
      course_payment_type: 'نقدي',
      note: ''
    });
  };

  const handleEdit = (reg) => {
    setEditingRegistration(reg);
    setFormData({
      course: reg.course,
      student: reg.student,
      code: reg.code,
      course_price: reg.course_price,
      course_discount_amount: reg.course_discount_amount || '',
      course_payment_type: reg.course_payment_type,
      note: reg.note || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا التسجيل؟')) {
      await deleteRegistration(id);
    }
  };

  const calculateRequired = () => {
    const price = parseFloat(formData.course_price) || 0;
    const discount = parseFloat(formData.course_discount_amount) || 0;
    if (formData.course_payment_type === 'نقدي') {
      return price - (price * discount / 100);
    }
    return price;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">التسجيلات</h1>
          <p className="text-gray-500 mt-1">إدارة تسجيلات الطلاب في الدورات</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          تسجيل جديد
        </button>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث بالاسم، الكود، أو الدورة..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pr-10"
          />
        </div>
      </div>

      {/* Registrations Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredRegistrations.length === 0 ? (
          <div className="text-center py-12">
            <UserPlus className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا توجد تسجيلات</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الكود</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الطالب</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الدورة</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">السعر المطلوب</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المدفوع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المتبقي</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredRegistrations.map((reg) => (
                  <tr key={reg.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{reg.key}</td>
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900">{reg.student_name}</div>
                      <div className="text-sm text-gray-500">{reg.student_mobile}</div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{reg.course_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {reg.required_price?.toLocaleString()} ريال
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-sm ${reg.paid_price > 0 ? 'text-green-600' : 'text-gray-500'}`}>
                        {reg.paid_price?.toLocaleString()} ريال
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-sm ${reg.remain_price > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {reg.remain_price?.toLocaleString()} ريال
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => handleEdit(reg)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(reg.id)}
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
          <div className="bg-white rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">
                {editingRegistration ? 'تعديل تسجيل' : 'تسجيل جديد'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="label">الطالب</label>
                <select
                  value={formData.student}
                  onChange={(e) => setFormData({...formData, student: e.target.value})}
                  className="input"
                  required
                >
                  <option value="">اختر الطالب</option>
                  {students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.full_name} - {student.mobile}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">الدورة</label>
                <select
                  value={formData.course}
                  onChange={(e) => setFormData({...formData, course: e.target.value})}
                  className="input"
                  required
                >
                  <option value="">اختر الدورة</option>
                  {courses.map((course) => (
                    <option key={course.id} value={course.id}>
                      {course.master_name} - {course.instructor || 'بدون محاضر'}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">الكود</label>
                <input
                  type="number"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value})}
                  className="input"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">سعر الدورة</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.course_price}
                    onChange={(e) => setFormData({...formData, course_price: e.target.value})}
                    className="input"
                    required
                  />
                </div>
                <div>
                  <label className="label">نسبة الخصم/الربح (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.course_discount_amount}
                    onChange={(e) => setFormData({...formData, course_discount_amount: e.target.value})}
                    className="input"
                  />
                </div>
              </div>
              <div>
                <label className="label">نوع الدفع</label>
                <select
                  value={formData.course_payment_type}
                  onChange={(e) => setFormData({...formData, course_payment_type: e.target.value})}
                  className="input"
                >
                  <option value="نقدي">نقدي</option>
                  <option value="تقسيط">تقسيط</option>
                  <option value="آجل">آجل</option>
                </select>
              </div>
              {formData.course_price && (
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <span className="font-medium">السعر المطلوب:</span> {calculateRequired().toLocaleString()} ريال
                  </p>
                </div>
              )}
              <div>
                <label className="label">ملاحظات</label>
                <textarea
                  value={formData.note}
                  onChange={(e) => setFormData({...formData, note: e.target.value})}
                  className="input"
                  rows="3"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="flex-1 btn-primary">
                  {editingRegistration ? 'حفظ التChanges' : 'تسجيل'}
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
