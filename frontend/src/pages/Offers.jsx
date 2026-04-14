import { useEffect, useState } from 'react';
import { useCBVOfferStore } from '../stores/cbvOfferStore';
import { Plus, Search, Edit2, Trash2, FileText, CheckCircle } from 'lucide-react';

export default function Offers() {
  const { offers, fetchOffers, deleteOffer, isLoading } = useCBVOfferStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingOffer, setEditingOffer] = useState(null);
  const [formData, setFormData] = useState({
    master: '',
    code: '',
    customer_name: '',
    customer_identity_number: '',
    customer_mobile: '',
    customer_email: '',
    master_price: '',
    master_discount_amount: '',
    master_payment_type: 'نقدي',
    note: ''
  });

  useEffect(() => {
    fetchOffers();
  }, []);

  const filteredOffers = offers.filter(offer => 
    offer.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    offer.customer_mobile?.includes(searchTerm) ||
    offer.code?.toString().includes(searchTerm)
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingOffer) {
        await useCBVOfferStore.getState().updateOffer(editingOffer.id, formData);
      } else {
        await useCBVOfferStore.getState().createOffer(formData);
      }
      setShowModal(false);
      setEditingOffer(null);
      resetForm();
    } catch (error) {
      console.error('Error saving offer:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      master: '',
      code: '',
      customer_name: '',
      customer_identity_number: '',
      customer_mobile: '',
      customer_email: '',
      master_price: '',
      master_discount_amount: '',
      master_payment_type: 'نقدي',
      note: ''
    });
  };

  const handleEdit = (offer) => {
    setEditingOffer(offer);
    setFormData({
      master: offer.master || '',
      code: offer.code || '',
      customer_name: offer.customer_name || '',
      customer_identity_number: offer.customer_identity_number || '',
      customer_mobile: offer.customer_mobile || '',
      customer_email: offer.customer_email || '',
      master_price: offer.master_price || '',
      master_discount_amount: offer.master_discount_amount || '',
      master_payment_type: offer.master_payment_type || 'نقدي',
      note: offer.note || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا العرض؟')) {
      await deleteOffer(id);
    }
  };

  const handleConvert = async (id) => {
    if (window.confirm('هل تريد تحويل هذا العرض إلى تسجيل؟')) {
      try {
        await useCBVOfferStore.getState().convertOffer(id);
        alert('تم تحويل العرض بنجاح');
      } catch (error) {
        console.error('Error converting offer:', error);
      }
    }
  };

  const paymentTypeColors = {
    'نقدي': 'bg-green-100 text-green-800',
    'تقسيط': 'bg-yellow-100 text-yellow-800',
    'آجل': 'bg-red-100 text-red-800'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">عروض الأسعار</h1>
          <p className="text-gray-500 mt-1">إدارة عروض الأسعار للعملاء</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          عرض سعر جديد
        </button>
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث باسم العميل، الجوال..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Offers Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredOffers.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا توجد عروض أسعار</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الكود</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">العميل</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الجوال</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">السعر</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الخصم</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">النوع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الحالة</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredOffers.map((offer) => (
                  <tr key={offer.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{offer.code}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{offer.customer_name}</td>
                    <td className="px-4 py-3 text-sm text-gray-900" dir="ltr">{offer.customer_mobile || '-'}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {offer.master_price?.toLocaleString()} ج.م
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{offer.master_discount_amount}%</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${paymentTypeColors[offer.master_payment_type] || 'bg-gray-100'}`}>
                        {offer.master_payment_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {offer.registered ? (
                        <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 inline mr-1" />
                          مسجل
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                          معلق
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {!offer.registered && (
                          <button 
                            onClick={() => handleConvert(offer.id)}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="تحويل إلى تسجيل"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                        )}
                        <button 
                          onClick={() => handleEdit(offer)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(offer.id)}
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
                {editingOffer ? 'تعديل عرض سعر' : 'عرض سعر جديد'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">التخصص</label>
                <select
                  value={formData.master}
                  onChange={(e) => setFormData({...formData, master: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">اختر التخصص</option>
                  {/* TODO: Add masters list */}
                </select>
              </div>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">اسم العميل *</label>
                <input
                  type="text"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">رقم الهوية</label>
                  <input
                    type="text"
                    value={formData.customer_identity_number}
                    onChange={(e) => setFormData({...formData, customer_identity_number: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الجوال</label>
                  <input
                    type="text"
                    value={formData.customer_mobile}
                    onChange={(e) => setFormData({...formData, customer_mobile: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    dir="ltr"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">البريد الإلكتروني</label>
                <input
                  type="email"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({...formData, customer_email: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  dir="ltr"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">السعر</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.master_price}
                    onChange={(e) => setFormData({...formData, master_price: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">نسبة الخصم</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.master_discount_amount}
                    onChange={(e) => setFormData({...formData, master_discount_amount: e.target.value})}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">نوع الدفع</label>
                <select
                  value={formData.master_payment_type}
                  onChange={(e) => setFormData({...formData, master_payment_type: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="نقدي">نقدي</option>
                  <option value="تقسيط">تقسيط</option>
                  <option value="آجل">آجل</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
                <textarea
                  value={formData.note}
                  onChange={(e) => setFormData({...formData, note: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="3"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors">
                  {editingOffer ? 'حفظ التغييرات' : 'إضافة'}
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
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
