import { useEffect, useState } from 'react';
import { studentsApi, coursesApi, paymentsApi, offersApi } from '../services/cbvApi';

const StatCard = ({ title, value, icon, color }) => (
  <div className="card flex items-center gap-4">
    <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl ${color}`}>
      {icon}
    </div>
    <div>
      <p className="text-gray-500 text-sm">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  </div>
);

export default function Dashboard() {
  const [stats, setStats] = useState({
    students: 0,
    courses: 0,
    payments: 0,
    offers: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [studentsRes, coursesRes, paymentsRes, offersRes] = await Promise.all([
          studentsApi.getAll(),
          coursesApi.getAll(),
          paymentsApi.getAll(),
          offersApi.getAll(),
        ]);

        setStats({
          students: studentsRes.data.count || studentsRes.data.results?.length || 0,
          courses: coursesRes.data.count || coursesRes.data.results?.length || 0,
          payments: paymentsRes.data.count || paymentsRes.data.results?.length || 0,
          offers: offersRes.data.count || offersRes.data.results?.length || 0,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">لوحة التحكم</h1>
        <p className="text-gray-600 mt-1">نظرة عامة على النظام</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card h-24 animate-pulse bg-gray-100" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="إجمالي الطلاب"
            value={stats.students}
            icon="👨‍🎓"
            color="bg-blue-100 text-blue-600"
          />
          <StatCard
            title="الدورات المتاحة"
            value={stats.courses}
            icon="📚"
            color="bg-green-100 text-green-600"
          />
          <StatCard
            title="سندات القبض"
            value={stats.payments}
            icon="💰"
            color="bg-yellow-100 text-yellow-600"
          />
          <StatCard
            title="عروض الأسعار"
            value={stats.offers}
            icon="🏷️"
            color="bg-purple-100 text-purple-600"
          />
        </div>
      )}

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">إجراءات سريعة</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="/students" className="card hover:shadow-md transition-shadow group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
                ➕
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">طالب جديد</h3>
                <p className="text-sm text-gray-500">إضافة طالب جديد للنظام</p>
              </div>
            </div>
          </a>

          <a href="/registrations" className="card hover:shadow-md transition-shadow group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-xl group-hover:bg-green-600 group-hover:text-white transition-colors">
                📝
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">تسجيل جديد</h3>
                <p className="text-sm text-gray-500">تسجيل طالب في دورة</p>
              </div>
            </div>
          </a>

          <a href="/offers" className="card hover:shadow-md transition-shadow group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-xl group-hover:bg-purple-600 group-hover:text-white transition-colors">
                🏷️
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">عرض سعر</h3>
                <p className="text-sm text-gray-500">إنشاء عرض سعر جديد</p>
              </div>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
