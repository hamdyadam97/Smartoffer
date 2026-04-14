import { useEffect, useState } from 'react';
import { useCBVPaymentStore } from '../stores/cbvPaymentStore';
import { useCBVRegistrationStore } from '../stores/cbvRegistrationStore';
import { Plus, Search, Edit2, Trash2, CreditCard, Receipt } from 'lucide-react';

export default function Payments() {
  const { payments, fetchPayments, deletePayment, isLoading } = useCBVPaymentStore();
  const { registrations, fetchRegistrations } = useCBVRegistrationStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    account: '',
    code: '',
    amount_number: '',
    type: 'ايرادات اساسية',
    payment_method: 'CASH',
    note: ''
  });

  useEffect(() => {
    fetchPayments();
    fetchRegistrations();
  }, []);

  const filteredPayments = payments.filter(payment => 
    payment.code?.toString().includes(searchTerm) ||
    payment.account_key?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    payment.student_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await useCBVPaymentStore.getState().createPayment(formData);
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Error saving payment:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      account: '',
      code: '',
      amount_number: '',
      type: 'ايرادات اساسية',
      payment_method: 'CASH',
      note: ''
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا السند؟')) {
      await deletePayment(id);
    }
  };

  const paymentMethodLabels = {
    'CASH': 'نقدي',
    'BANK': 'تحويل بنكي',
    'CHEQUE': 'شيك',
    'CARD': 'بطاقة ائتمان',
    'ONLINE': 'دفع إلكتروني'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">سندات القبض</h1>
          <p className="text-gray-500 mt-1">إدارة المدفوعات وسندات القبض</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          سند قبض جديد
        </button>
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث برقم السند، الطالب..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Payments Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredPayments.length === 0 ? (
          <div className="text-center py-12">
            <Receipt className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا توجد سندات قبض</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الكود</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">التاريخ</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الطالب</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المبلغ</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">النوع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">طريقة الدفع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredPayments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{payment.code}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {new Date(payment.date).toLocaleDateString('ar-EG')}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {payment.student_name || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-green-600">
                      {payment.amount_number?.toLocaleString()} ج.م
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">{payment.type}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {paymentMethodLabels[payment.payment_method] || payment.payment_method}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => handleDelete(payment.id)}
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
              <h2 className="text-xl font-bold">سند قبض جديد</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">التسجيل</label>
                <select
                  value={formData.account}
                  onChange={(e) => setFormData({...formData, account: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">اختر التسجيل</option>
                  {registrations.map(reg => (
                    <option key={reg.id} value={reg.id}>
                      {reg.get_key} - {reg.student_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الكود</label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({...formData, code: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">المبلغ</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount_number}
                  onChange={(e) => setFormData({...formData, amount_number: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">النوع</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({...formData, type: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ايرادات اساسية">إيرادات أساسية</option>
                  <option value="ايرادات اخرى">إيرادات أخرى</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">طريقة الدفع</label>
                <select
                  value={formData.payment_method}
                  onChange={(e) => setFormData({...formData, payment_method: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="CASH">نقدي</option>
                  <option value="BANK">تحويل بنكي</option>
                  <option value="CHEQUE">شيك</option>
                  <option value="CARD">بطاقة ائتمان</option>
                  <option value="ONLINE">دفع إلكتروني</option>
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
                  حفظ
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
