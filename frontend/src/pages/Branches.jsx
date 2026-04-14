import { useEffect, useState } from 'react';
import { branchesApi } from '../services/cbvApi';
import { Plus, Search, Edit2, Trash2, Building2 } from 'lucide-react';

export default function Branches() {
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingBranch, setEditingBranch] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    sub_name: '',
    address: '',
    phone1: '',
    phone2: '',
    mobile: '',
    email: ''
  });

  // جلب الفروع من API
  useEffect(() => {
    fetchBranches();
  }, []);

  const fetchBranches = async () => {
    try {
      setLoading(true);
      const response = await branchesApi.getAll();
      setBranches(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching branches:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingBranch) {
        await branchesApi.update(editingBranch.id, formData);
      } else {
        await branchesApi.create(formData);
      }
      setShowModal(false);
      setEditingBranch(null);
      setFormData({
        code: '', name: '', sub_name: '', address: '',
        phone1: '', phone2: '', mobile: '', email: ''
      });
      fetchBranches();
    } catch (error) {
      console.error('Error saving branch:', error);
      alert('حدث خطأ أثناء الحفظ');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا الفرع؟')) {
      try {
        await api.delete(`/branches/${id}/`);
        fetchBranches();
      } catch (error) {
        console.error('Error deleting branch:', error);
        alert('حدث خطأ أثناء الحذف');
      }
    }
  };

  const handleEdit = (branch) => {
    setEditingBranch(branch);
    setFormData({
      code: branch.code,
      name: branch.name,
      sub_name: branch.sub_name || '',
      address: branch.address || '',
      phone1: branch.phone1 || '',
      phone2: branch.phone2 || '',
      mobile: branch.mobile || '',
      email: branch.email || ''
    });
    setShowModal(true);
  };

  const filteredBranches = branches.filter(branch =>
    branch.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    branch.code?.toString().includes(searchTerm)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">الفروع</h1>
          <p className="text-gray-500 mt-1">إدارة فروع الشركة</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          إضافة فرع
        </button>
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث في الفروع..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Branches Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredBranches.length === 0 ? (
          <div className="text-center py-12">
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا توجد فروع</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الكود</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الاسم</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">العنوان</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الجوال</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">البريد</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredBranches.map((branch) => (
                  <tr key={branch.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{branch.code}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      <div>{branch.name}</div>
                      {branch.sub_name && (
                        <div className="text-xs text-gray-500">{branch.sub_name}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{branch.address || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{branch.mobile || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{branch.email || '-'}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleEdit(branch)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(branch.id)}
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
                {editingBranch ? 'تعديل فرع' : 'إضافة فرع جديد'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الكود</label>
                  <input
                    type="number"
                    value={formData.code}
                    onChange={(e) => setFormData({...formData, code: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الاسم</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الاسم الفرعي</label>
                <input
                  type="text"
                  value={formData.sub_name}
                  onChange={(e) => setFormData({...formData, sub_name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">العنوان</label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="2"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">التليفون 1</label>
                  <input
                    type="text"
                    value={formData.phone1}
                    onChange={(e) => setFormData({...formData, phone1: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">التليفون 2</label>
                  <input
                    type="text"
                    value={formData.phone2}
                    onChange={(e) => setFormData({...formData, phone2: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">المحمول</label>
                  <input
                    type="text"
                    value={formData.mobile}
                    onChange={(e) => setFormData({...formData, mobile: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
                >
                  {editingBranch ? 'حفظ التغييرات' : 'إضافة'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingBranch(null);
                  }}
                  className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg transition-colors"
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
