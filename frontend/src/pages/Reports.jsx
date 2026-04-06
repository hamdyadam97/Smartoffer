import { useState, useEffect } from 'react';
import api from '../services/api';

const ReportCard = ({ title, description, icon, onExportExcel, onExportPDF }) => (
  <div className="card">
    <div className="flex items-start justify-between">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-2xl">
          {icon}
        </div>
        <div>
          <h3 className="font-bold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-500 mt-1">{description}</p>
        </div>
      </div>
    </div>
    <div className="flex gap-3 mt-6">
      <button
        onClick={onExportExcel}
        className="flex-1 btn-secondary text-sm flex items-center justify-center gap-2"
      >
        <span>📊</span>
        Excel
      </button>
      <button
        onClick={onExportPDF}
        className="flex-1 btn-danger text-sm flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700"
      >
        <span>📄</span>
        PDF
      </button>
    </div>
  </div>
);

const StatBox = ({ title, value, subtext, color }) => (
  <div className="card text-center">
    <p className="text-gray-500 text-sm mb-2">{title}</p>
    <p className={`text-3xl font-bold ${color}`}>{value}</p>
    {subtext && <p className="text-sm text-gray-400 mt-1">{subtext}</p>}
  </div>
);

export default function Reports() {
  const [stats, setStats] = useState(null);
  const [financial, setFinancial] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    fetchStats();
    fetchFinancial();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/reports/dashboard-stats/');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchFinancial = async () => {
    try {
      const params = {};
      if (dateRange.start_date) params.start_date = dateRange.start_date;
      if (dateRange.end_date) params.end_date = dateRange.end_date;
      
      const response = await api.get('/reports/financial/', { params });
      setFinancial(response.data);
    } catch (error) {
      console.error('Error fetching financial:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportExcel = (type) => {
    window.open(`${import.meta.env.VITE_API_URL}/reports/export/excel/${type}/`, '_blank');
  };

  const exportPDF = (type) => {
    window.open(`${import.meta.env.VITE_API_URL}/reports/export/pdf/${type}/`, '_blank');
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">التقارير</h1>
        <p className="text-gray-600 mt-1">تقارير وإحصائيات النظام</p>
      </div>

      {/* الإحصائيات */}
      {stats && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">إحصائيات سريعة</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatBox
              title="إجمالي الطلاب"
              value={stats.students.total}
              subtext={`+${stats.students.new_this_month} هذا الشهر`}
              color="text-blue-600"
            />
            <StatBox
              title="إجمالي المدفوعات"
              value={`${stats.payments.total.toLocaleString()} ريال`}
              subtext={`${stats.payments.this_month.toLocaleString()} هذا الشهر`}
              color="text-green-600"
            />
            <StatBox
              title="عروض الأسعار"
              value={stats.offers.total}
              subtext={`${stats.offers.converted} مسجل (${stats.offers.conversion_rate}%)`}
              color="text-purple-600"
            />
            <StatBox
              title="التسجيلات"
              value={stats.registrations.total}
              subtext={`+${stats.registrations.this_month} هذا الشهر`}
              color="text-orange-600"
            />
          </div>
        </div>
      )}

      {/* التقرير المالي */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">التقرير المالي</h2>
        
        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <label className="label">من تاريخ</label>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
              className="input"
            />
          </div>
          <div className="flex-1">
            <label className="label">إلى تاريخ</label>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
              className="input"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchFinancial}
              className="btn-primary h-[42px]"
            >
              تحديث
            </button>
          </div>
        </div>

        {financial && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-green-600 text-sm mb-1">إجمالي الإيرادات</p>
              <p className="text-2xl font-bold text-green-700">
                {financial.income.toLocaleString()} ريال
              </p>
              <p className="text-sm text-green-600 mt-1">{financial.payments_count} سند</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-red-600 text-sm mb-1">إجمالي المصروفات</p>
              <p className="text-2xl font-bold text-red-700">
                {financial.expense.toLocaleString()} ريال
              </p>
              <p className="text-sm text-red-600 mt-1">{financial.payments_out_count} سند</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <p className="text-blue-600 text-sm mb-1">الصافي</p>
              <p className={`text-2xl font-bold ${financial.net >= 0 ? 'text-blue-700' : 'text-red-700'}`}>
                {financial.net.toLocaleString()} ريال
              </p>
            </div>
          </div>
        )}
      </div>

      {/* تصدير التقارير */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">تصدير التقارير</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ReportCard
            title="تقرير الطلاب"
            description="قائمة بجميع الطلاب في النظام"
            icon="👨‍🎓"
            onExportExcel={() => exportExcel('students')}
            onExportPDF={() => exportPDF('students')}
          />
          <ReportCard
            title="تقرير المدفوعات"
            description="سندات القبض والمدفوعات"
            icon="💰"
            onExportExcel={() => exportExcel('payments')}
            onExportPDF={() => exportPDF('payments')}
          />
          <ReportCard
            title="تقرير العروض"
            description="عروض الأسعار والتحويلات"
            icon="🏷️"
            onExportExcel={() => exportExcel('offers')}
            onExportPDF={() => exportPDF('offers')}
          />
        </div>
      </div>
    </div>
  );
}
