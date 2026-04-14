import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useCBVAuthStore } from '../stores/cbvAuthStore';

const menuItems = [
  { path: '/', label: 'الرئيسية', icon: '📊' },
  { path: '/students', label: 'الطلاب', icon: '👨‍🎓' },
  { path: '/courses', label: 'الدورات', icon: '📚' },
  { path: '/branches', label: 'الفروع', icon: '🏢' },
  { path: '/registrations', label: 'التسجيلات', icon: '📝' },
  { path: '/payments', label: 'المدفوعات', icon: '💰' },
  { path: '/offers', label: 'عروض الأسعار', icon: '🏷️' },
  { path: '/reports', label: 'التقارير', icon: '📈' },
];

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useCBVAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-blue-600">Smart Offer</h1>
          <p className="text-sm text-gray-500 mt-1">نظام إدارة المعاهد</p>
        </div>

        <nav className="p-4 space-y-1">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname === item.path
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200 bg-white">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-bold">
              {user?.first_name?.[0] || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 truncate">
                {user?.get_full_name || user?.email}
              </p>
              <p className="text-sm text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full btn-secondary text-sm flex items-center justify-center gap-2"
          >
            <span>🚪</span>
            تسجيل الخروج
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
