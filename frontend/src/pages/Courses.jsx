import { useEffect, useState } from 'react';
import { useCourseStore } from '../stores/courseStore';
import { Plus, Search, Edit2, Trash2, BookOpen } from 'lucide-react';

export default function Courses() {
  const { courses, masters, fetchCourses, fetchMasters, deleteCourse, isLoading } = useCourseStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [formData, setFormData] = useState({
    master: '',
    code: '',
    instructor: '',
    company_name: '',
    max_student_count: 1,
    target_level: 'الكل',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    fetchCourses();
    fetchMasters();
  }, []);

  const filteredCourses = courses.filter(course => 
    course.instructor?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.master_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCourse) {
        await useCourseStore.getState().updateCourse(editingCourse.id, formData);
      } else {
        await useCourseStore.getState().createCourse(formData);
      }
      setShowModal(false);
      setEditingCourse(null);
      setFormData({
        master: '',
        code: '',
        instructor: '',
        company_name: '',
        max_student_count: 1,
        target_level: 'الكل',
        start_date: '',
        end_date: ''
      });
    } catch (error) {
      console.error('Error saving course:', error);
    }
  };

  const handleEdit = (course) => {
    setEditingCourse(course);
    setFormData({
      master: course.master,
      code: course.code,
      instructor: course.instructor || '',
      company_name: course.company_name || '',
      max_student_count: course.max_student_count || 1,
      target_level: course.target_level || 'الكل',
      start_date: course.start_date || '',
      end_date: course.end_date || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذه الدورة؟')) {
      await deleteCourse(id);
    }
  };

  const levelColors = {
    'مبتدئ': 'bg-green-100 text-green-800',
    'متوسط': 'bg-yellow-100 text-yellow-800',
    'متقدم': 'bg-red-100 text-red-800',
    'الكل': 'bg-blue-100 text-blue-800'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">الدورات</h1>
          <p className="text-gray-500 mt-1">إدارة الدورات والفصول التدريبية</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          إضافة دورة
        </button>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث في الدورات..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pr-10"
          />
        </div>
      </div>

      {/* Courses Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredCourses.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا توجد دورات</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الكود</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">التخصص</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المحاضر</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الشركة</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المستوى</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الحد الأقصى</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredCourses.map((course) => (
                  <tr key={course.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{course.code}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{course.master_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{course.instructor || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{course.company_name || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${levelColors[course.target_level] || 'bg-gray-100'}`}>
                        {course.target_level}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{course.max_student_count}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => handleEdit(course)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(course.id)}
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
                {editingCourse ? 'تعديل دورة' : 'إضافة دورة جديدة'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="label">التخصص</label>
                <select
                  value={formData.master}
                  onChange={(e) => setFormData({...formData, master: e.target.value})}
                  className="input"
                  required
                >
                  <option value="">اختر التخصص</option>
                  {masters.map((master) => (
                    <option key={master.id} value={master.id}>
                      {master.code} - {master.name}
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
              <div>
                <label className="label">المحاضر</label>
                <input
                  type="text"
                  value={formData.instructor}
                  onChange={(e) => setFormData({...formData, instructor: e.target.value})}
                  className="input"
                />
              </div>
              <div>
                <label className="label">الشركة</label>
                <input
                  type="text"
                  value={formData.company_name}
                  onChange={(e) => setFormData({...formData, company_name: e.target.value})}
                  className="input"
                />
              </div>
              <div>
                <label className="label">المستوى المستهدف</label>
                <select
                  value={formData.target_level}
                  onChange={(e) => setFormData({...formData, target_level: e.target.value})}
                  className="input"
                >
                  <option value="مبتدئ">مبتدئ</option>
                  <option value="متوسط">متوسط</option>
                  <option value="متقدم">متقدم</option>
                  <option value="الكل">جميع المستويات</option>
                </select>
              </div>
              <div>
                <label className="label">الحد الأقصى للطلاب</label>
                <input
                  type="number"
                  value={formData.max_student_count}
                  onChange={(e) => setFormData({...formData, max_student_count: e.target.value})}
                  className="input"
                  min="1"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">تاريخ البداية</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">تاريخ النهاية</label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                    className="input"
                  />
                </div>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="flex-1 btn-primary">
                  {editingCourse ? 'حفظ التChanges' : 'إضافة'}
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
