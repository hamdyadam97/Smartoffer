import { useEffect, useState } from 'react';
import { usePaymentStore } from '../stores/paymentStore';
import { useRegistrationStore } from '../stores/registrationStore';
import { Plus, Search, Edit2, Trash2, CreditCard, Receipt } from 'lucide-react';

export default function Payments() {
  const { payments, fetchPayments, deletePayment, isLoading } = usePaymentStore();
  const { registrations, fetchRegistrations } = useRegistrationStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPayment, setEditingPayment] = useState(null);
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
      if (editingPayment) {
        await usePaymentStore.getState().updatePayment(editingPayment.id, formData);
      } else {
        await usePaymentStore.getState().createPayment(formData);
      }
      setShowModal(false);
      setEditingPayment(null);
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

  const handleEdit = (payment) => {
    setEditingPayment(payment);
    setFormData({
      account: payment.account,
      code: payment.code,
      amount_number: payment.amount_number,
      type: payment.type,
      payment_method: payment.payment_method,
      note: payment.note || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('هل أنت متأكد من حذف هذا السند؟')) {
      await deletePayment(id);
    }
  };

  const paymentMethods = {
    'CASH': 'نقدي',
    'BANK': 'تحويل بنكي',
    'CHEQUE': 'شيك',
    'CARD': 'بطاقة ائتمان',
    'ONLINE': 'دفع إلكتروني'
  };

  const totalAmount = filteredPayments.reduce((sum, p) => sum + parseFloat(p.amount_number || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">سندات القبض</h1>
          <p className="text-gray-500 mt-1">إدارة المدفوعات والإيصالات</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          سند جديد
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-blue-50 border-blue-200">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Receipt className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">إجمالي السندات</p>
              <p className="text-2xl font-bold text-gray-900">{payments.length}</p>
            </div>
          </div>
        </div>
        <div className="card bg-green-50 border-green-200">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <CreditCard className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">إجمالي المبالغ</p>
              <p className="text-2xl font-bold text-gray-900">{totalAmount.toLocaleString()} ريال</p>
            </div>
          </div>
        </div>
        <div className="card bg-purple-50 border-purple-200">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Receipt className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">متوسط القيمة</p>
              <p className="text-2xl font-bold text-gray-900">
                {payments.length ? Math.round(totalAmount / payments.length).toLocaleString() : 0} ريال
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="البحث بالكود، رقم التسجيل، أو اسم الطالب..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pr-10"
          />
        </div>
      </div>

      {/* Payments Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        ) : filteredPayments.length === 0 ? (
          <div className="text-center py-12">
            <CreditCard className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">لا توجد سندات قبض</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الكود</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">رقم التسجيل</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الطالب</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">المبلغ</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">طريقة الدفع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">النوع</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">التاريخ</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">الإجراءات</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredPayments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{payment.code}</td>
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{payment.account_key}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{payment.student_name}</td>
                    <td className="px-4 py-3 text-sm font-bold text-green-600">
                      {parseFloat(payment.amount_number).toLocaleString()} ريال
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                        {paymentMethods[payment.payment_method] || payment.payment_method}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        payment.type === 'ايرادات اساسية' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'
                      }`}>
                        {payment.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(payment.date).toLocaleDateString('ar-SA')}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => handleEdit(payment)}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
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
              <h2 className="text-xl font-bold">
                {editingPayment ? 'تعديل سند' : 'سند قبض جديد'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="label">التسجيل</label>
                <select
                  value={formData.account}
                  onChange={(e) => setFormData({...formData, account: e.target.value})}
                  className="input"
                  required
                >
                  <option value="">اختر التسجيل</option>
                  {registrations.map((reg) => (
                    <option key={reg.id} value={reg.id}>
                      {reg.key} - {reg.student_name} ({reg.remain_price?.toLocaleString()} ريال متبقي)
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
                <label className="label">المبلغ</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount_number}
                  onChange={(e) => setFormData({...formData, amount_number: e.target.value})}
                  className="input"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">طريقة الدفع</label>
                  <select
                    value={formData.payment_method}
                    onChange={(e) => setFormData({...formData, payment_method: e.target.value})}
                    className="input"
                  >
                    <option value="CASH">نقدي</option>
                    <option value="BANK">تحويل بنكي</option>
                    <option value="CHEQUE">شيك</option>
                    <option value="CARD">بطاقة ائتمان</option>
                    <option value="ONLINE">دفع إلكتروني</option>
                  </select>
                </div>
                <div>
                  <label className="label">النوع</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    className="input"
                  >
                    <option value="ايرادات اساسية">إيرادات أساسية</option>
                    <option value="ايرادات اخرى">إيرادات أخرى</option>
                  </select>
                </div>
              </div>
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
                  {editingPayment ? 'حفظ التChanges' : 'حفظ'}
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
