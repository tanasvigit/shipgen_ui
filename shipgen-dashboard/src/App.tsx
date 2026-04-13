
import React, { useState, useEffect } from 'react';
import {
  HashRouter as Router,
  Routes,
  Route,
  Link,
  useLocation,
  Navigate,
  Outlet
} from 'react-router-dom';
import {
  LayoutDashboard,
  Menu,
  X,
  Bell,
  User,
  LogOut,
  Search,
  Box,
  Package,
  Sparkles,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import AIAssistant from './components/AIAssistant';
// Dashboard Sub-pages
import DashboardWrapper from './components/Dashboard/DashboardWrapper';
import DashboardOverview from './components/Dashboard/DashboardOverview';
// Orders Sub-pages
import LogisticsLayout from './components/Logistics/LogisticsLayout';
import CustomersList from './components/Logistics/CustomersList';
import OrdersWrapper from './components/Orders/OrdersWrapper';
import OrdersList from './components/Orders/OrdersList';
import OrderDetail from './components/Orders/OrderDetail';
import DispatchBoard from './components/Orders/DispatchBoard';
// Warehouse Sub-pages
import WarehouseWrapper from './components/Warehouse/WarehouseWrapper';
import ZonesManagement from './components/Warehouse/ZonesManagement';
import InventoryList from './components/Warehouse/InventoryList';
import GRNProcess from './components/Warehouse/GRNProcess';
// Fleet Sub-pages
import FleetWrapper from './components/Fleet/FleetWrapper';
import FleetDashboard from './components/Fleet/FleetDashboard';
import FleetsList from './components/Fleet/FleetsList';
import ServiceAreasList from './components/Fleet/ServiceAreasList';
import ZonesList from './components/Fleet/ZonesList';
import TrackingNumbersList from './components/Fleet/TrackingNumbersList';
import TrackingStatusesList from './components/Fleet/TrackingStatusesList';
import PayloadsList from './components/Fleet/PayloadsList';
import PayloadDetail from './components/Fleet/PayloadDetail';
import VehiclesList from './components/Fleet/VehiclesList';
import VehicleDetail from './components/Fleet/VehicleDetail';
import DriversList from './components/Fleet/DriversList';
import DriverDetail from './components/Fleet/DriverDetail';
import EntitiesList from './components/Fleet/EntitiesList';
import ContactsList from './components/Fleet/ContactsList';
import ContactDetail from './components/Fleet/ContactDetail';
import PlacesList from './components/Fleet/PlacesList';
import PlaceDetail from './components/Fleet/PlaceDetail';
import VendorsList from './components/Vendors/VendorsList';
import VendorDetail from './components/Fleet/VendorDetail';
import IssuesList from './components/Fleet/IssuesList';
import IssueDetail from './components/Fleet/IssueDetail';
import FuelReportsList from './components/Fleet/FuelReportsList';
import FuelReportDetail from './components/Fleet/FuelReportDetail';
// Billing Sub-pages
import BillingWrapper from './components/Billing/BillingWrapper';
import InvoicesList from './components/Billing/InvoicesList';
import InvoiceDetail from './components/Billing/InvoiceDetail';
import PaymentsList from './components/Billing/PaymentsList';
import PaymentRecord from './components/Billing/PaymentRecord';
// Reports Sub-pages
import ReportsWrapper from './components/Reports/ReportsWrapper';
import ReportsList from './components/Reports/ReportsList';
import ReportDetail from './components/Reports/ReportDetail';
import FilesList from './components/Files/FilesList';
import DevicesList from './components/Devices/DevicesList';
import DeviceDetail from './components/Devices/DeviceDetail';
import ActivitiesList from './components/Activities/ActivitiesList';
import ActivityDetail from './components/Activities/ActivityDetail';
import NotificationsList from './components/Notifications/NotificationsList';
import GroupsList from './components/Groups/GroupsList';
import ExtensionsList from './components/Extensions/ExtensionsList';
import ApiCredentialsList from './components/ApiCredentials/ApiCredentialsList';
import ApiEventsList from './components/ApiEvents/ApiEventsList';
import ApiEventDetail from './components/ApiEvents/ApiEventDetail';
import ApiRequestLogsList from './components/ApiRequestLogs/ApiRequestLogsList';
import ApiRequestLogDetail from './components/ApiRequestLogs/ApiRequestLogDetail';
import CustomFieldsList from './components/CustomFields/CustomFieldsList';
import CustomFieldValuesList from './components/CustomFieldValues/CustomFieldValuesList';
import CompaniesList from './components/Companies/CompaniesList';
import UsersList from './components/Users/UsersList';
import CommentsList from './components/Comments/CommentsList';
import Profile from './components/Profile/Profile';
import OutstandingInvoices from './components/Reports/OutstandingInvoices';
import TransactionsList from './components/Transactions/TransactionsList';
import TransactionDetail from './components/Transactions/TransactionDetail';
import SchedulesList from './components/Schedules/SchedulesList';
import ScheduleItemsList from './components/Schedules/ScheduleItemsList';
import ScheduleTemplatesList from './components/Schedules/ScheduleTemplatesList';
import ScheduleAvailabilityList from './components/Schedules/ScheduleAvailabilityList';
import ScheduleConstraintsList from './components/Schedules/ScheduleConstraintsList';
import ScheduleMonitorList from './components/Schedules/ScheduleMonitorList';
import ScheduleMonitorDetail from './components/Schedules/ScheduleMonitorDetail';
import { getFilteredNavigationItems } from './constants';
import { normalizeUserRole, UserRole } from './types';
import { canAccessRoute, hasAccess } from './utils/roleAccess';
import RoleGuard from './components/RoleGuard';
import { PageTransition } from './components/ui/PageTransition';
import Footer from './components/Footer';
import Login from './components/Login';
import { mockAuthUser } from './mocks/data/auth';
import { APP_MODE } from './config/appMode';
import { logout } from './services/auth';
import { ToastProvider } from './components/ui/ToastProvider';
import PremiumSidebar from './components/Sidebar';
import TopNavbar from './components/TopNavbar';

interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  companyId: string;
}

const DEFAULT_MOCK_USER: User = {
  id: mockAuthUser.id,
  email: mockAuthUser.email,
  name: mockAuthUser.name,
  role: normalizeUserRole(mockAuthUser.role),
  companyId: mockAuthUser.company_id,
};

const ScrollToTopOnRouteChange: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    // Keep both window and the scrollable main container at top after navigation.
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    const main = document.querySelector('main');
    if (main) {
      main.scrollTo({ top: 0, left: 0, behavior: 'auto' });
    }
  }, [location.pathname, location.search]);

  return null;
};

const Sidebar: React.FC<{ isOpen: boolean; setIsOpen: (v: boolean) => void; onLogout: () => void; currentUser: User | null }> = ({ isOpen, setIsOpen, onLogout, currentUser }) => {
  const location = useLocation();
  const currentPath = location.pathname.substring(1) || 'dashboard';
  const [isLogisticsOpen, setIsLogisticsOpen] = useState(() => currentPath.startsWith('logistics'));
  const [isFleetOpen, setIsFleetOpen] = useState(() => currentPath.startsWith('fleet'));

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden animate-fade-in"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside className={`fixed lg:static inset-y-0 left-0 w-64 bg-slate-50 border-r border-gray-200 z-50 transform transition-transform duration-300 ease-out flex flex-col ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="h-16 flex items-center px-6 border-b border-gray-100 flex-shrink-0">
          <div className="flex items-center">
            <img src="/logo_logistic.png" alt="ShipGen" className="h-12 w-auto" />
          </div>
        </div>

        <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
          {currentUser && getFilteredNavigationItems(currentUser.role).map((item) => {
            const isActive = currentPath === item.id || currentPath.startsWith(`${item.id}/`);

            if (item.id === 'logistics') {
              return (
                <div key={item.id} className="space-y-1">
                  <button
                    type="button"
                    onClick={() => setIsLogisticsOpen(open => !open)}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                      ? 'bg-primary-100 text-primary-700 shadow-soft'
                      : 'text-gray-600 hover:bg-white hover:text-gray-900'
                      }`}
                  >
                    <span className="flex items-center">
                      <span className="mr-3">{item.icon}</span>
                      <span className="font-medium text-sm">{item.label}</span>
                    </span>
                    {isLogisticsOpen ? (
                      <ChevronUp size={18} />
                    ) : (
                      <ChevronDown size={18} />
                    )}
                  </button>

                  {isLogisticsOpen && (
                    <div className="ml-4 mt-1 space-y-0.5">
                      <Link
                        to="/logistics/orders"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'logistics/orders' || currentPath.startsWith('logistics/orders/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Orders List
                      </Link>
                    </div>
                  )}
                </div>
              );
            }

            if (item.id === 'fleet') {
              return (
                <div key={item.id} className="space-y-1">
                  <button
                    type="button"
                    onClick={() => setIsFleetOpen((open) => !open)}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                      ? 'bg-primary-100 text-primary-700 shadow-soft'
                      : 'text-gray-600 hover:bg-white hover:text-gray-900'
                      }`}
                  >
                    <span className="flex items-center">
                      <span className="mr-3">{item.icon}</span>
                      <span className="font-medium text-sm">{item.label}</span>
                    </span>
                    {isFleetOpen ? (
                      <ChevronUp size={18} />
                    ) : (
                      <ChevronDown size={18} />
                    )}
                  </button>

                  {isFleetOpen && (
                    <div className="ml-4 mt-1 space-y-0.5">
                      <Link
                        to="/fleet/fleets"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/fleets' || currentPath.startsWith('fleet/fleets/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Fleets
                      </Link>
                      <Link
                        to="/fleet/service-areas"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/service-areas' || currentPath.startsWith('fleet/service-areas/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Service Areas
                      </Link>
                      <Link
                        to="/fleet/zones"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/zones' || currentPath.startsWith('fleet/zones/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Zones
                      </Link>
                      <Link
                        to="/fleet/tracking-numbers"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/tracking-numbers' || currentPath.startsWith('fleet/tracking-numbers/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Tracking Numbers
                      </Link>
                      <Link
                        to="/fleet/tracking-statuses"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/tracking-statuses' || currentPath.startsWith('fleet/tracking-statuses/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Tracking Statuses
                      </Link>
                      <Link
                        to="/fleet/payloads"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/payloads' || currentPath.startsWith('fleet/payloads/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Payloads
                      </Link>
                      <Link
                        to="/fleet/dashboard"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/dashboard'
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Fleet dashboard
                      </Link>
                      <Link
                        to="/fleet/vehicles"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/vehicles' || currentPath.startsWith('fleet/vehicles/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Vehicles
                      </Link>
                      <Link
                        to="/fleet/drivers"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/drivers' || currentPath.startsWith('fleet/drivers/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Drivers
                      </Link>
                      <Link
                        to="/fleet/entities"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/entities' || currentPath.startsWith('fleet/entities/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Entities
                      </Link>
                      <Link
                        to="/fleet/contacts"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/contacts' || currentPath.startsWith('fleet/contacts/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Contacts
                      </Link>
                      <Link
                        to="/fleet/places"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/places' || currentPath.startsWith('fleet/places/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Places
                      </Link>
                      <Link
                        to="/fleet/vendors"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/vendors' || currentPath.startsWith('fleet/vendors/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Vendors
                      </Link>
                      <Link
                        to="/fleet/issues"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/issues' || currentPath.startsWith('fleet/issues/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Issues
                      </Link>
                      <Link
                        to="/fleet/fuel-reports"
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center px-4 py-2 rounded-lg text-sm transition ${currentPath === 'fleet/fuel-reports' || currentPath.startsWith('fleet/fuel-reports/')
                          ? 'bg-blue-50 text-blue-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                          }`}
                      >
                        Fuel Reports
                      </Link>
                    </div>
                  )}
                </div>
              );
            }

            return (
              <Link
                key={item.id}
                to={`/${item.id}`}
                onClick={() => setIsOpen(false)}
                className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                  ? 'bg-primary-100 text-primary-700 shadow-soft'
                  : 'text-gray-600 hover:bg-white hover:text-gray-900'
                  }`}
              >
                <span className="mr-3">{item.icon}</span>
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            );
          })}

          {currentUser && hasAccess(currentUser.role, 'ai-assistant') && (
            <div className="pt-4 mt-4 border-t border-gray-50">
              <Link
                to="/ai-assistant"
                onClick={() => setIsOpen(false)}
                className={`flex items-center px-4 py-3 rounded-xl transition-all ${currentPath === 'ai-assistant'
                  ? 'bg-gradient-to-r from-primary-700 to-primary-600 text-white shadow-md'
                  : 'text-indigo-600 hover:bg-indigo-50 font-semibold text-sm'
                  }`}
              >
                <span className="mr-3"><Sparkles size={20} /></span>
                <span>ShipGen AI</span>
              </Link>
            </div>
          )}
        </nav>

        <div className="absolute bottom-0 w-full p-4 border-t border-gray-100 bg-slate-50">
          {currentUser && (
            <div className="flex items-center p-3 rounded-xl bg-gray-50 border border-gray-100 mb-2">
              <div className="w-10 h-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center font-bold">
                {currentUser.name[0]}
              </div>
              <div className="ml-3 overflow-hidden">
                <p className="text-sm font-bold text-gray-900 truncate">{currentUser.name}</p>
                <p className="text-[10px] text-gray-500 uppercase tracking-tight">{currentUser.role.replace(/_/g, ' ')}</p>
              </div>
            </div>
          )}
          <button
            onClick={onLogout}
            className="w-full flex items-center justify-center space-x-2 py-2 text-xs font-bold text-red-500 hover:bg-red-50 rounded-lg transition"
            aria-label="Sign out"
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};

const Header: React.FC<{ setIsOpen: (v: boolean) => void }> = ({ setIsOpen }) => {
  return (
    <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30 shadow-sm shadow-gray-50">
      <div className="flex items-center">
        <button
          onClick={() => setIsOpen(true)}
          className="p-2 text-gray-500 lg:hidden rounded-lg hover:bg-gray-100 focus-visible:ring-primary-600"
          aria-label="Open navigation menu"
        >
          <Menu size={24} />
        </button>
        <div className="hidden md:flex items-center bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 w-80">
          <Search size={18} className="text-gray-400 mr-2" />
          <input type="text" placeholder="Search across ShipGen..." className="bg-transparent border-none text-sm w-full focus:ring-0 outline-none" aria-label="Search across ShipGen" />
        </div>
      </div>

      <div className="flex items-center space-x-2 md:space-x-4">
        <button className="p-2 text-gray-400 hover:text-gray-600 relative rounded-lg hover:bg-gray-100 focus-visible:ring-primary-600" aria-label="Notifications">
          <Bell size={20} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
        </button>
        <div className="h-8 w-px bg-gray-100"></div>
        <button className="flex items-center space-x-2 p-1 pl-2 pr-4 rounded-full border border-gray-100 hover:bg-gray-50 transition focus-visible:ring-primary-600" aria-label="Open settings">
          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500">
            <User size={18} />
          </div>
          <span className="text-xs font-bold text-gray-700 hidden sm:inline">Settings</span>
        </button>
      </div>
    </header>
  );
};

const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(() => {
    if (APP_MODE.disableAuth) {
      return DEFAULT_MOCK_USER;
    }
    const storedUser = localStorage.getItem('user');
    if (!storedUser) return null;
    try {
      const parsed = JSON.parse(storedUser) as { id?: string; email?: string; name?: string; role?: string; companyId?: string };
      return {
        id: String(parsed.id || ''),
        email: parsed.email || '',
        name: parsed.name || '',
        role: normalizeUserRole(parsed.role),
        companyId: parsed.companyId || 'default',
      };
    } catch {
      localStorage.removeItem('user');
      return null;
    }
  });
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const roleFallbackPath =
    currentUser?.role === UserRole.DRIVER || currentUser?.role === UserRole.FLEET_CUSTOMER
      ? '/logistics/orders'
      : '/dashboard';

  useEffect(() => {
    if (APP_MODE.disableAuth) {
      setCurrentUser(DEFAULT_MOCK_USER);
    }
  }, []);

  const handleLogout = async () => {
    if (APP_MODE.disableAuth) {
      setCurrentUser(DEFAULT_MOCK_USER);
      return;
    }

    setCurrentUser(null);
    await logout();
  };

  const ProtectedLayout: React.FC = () => (
    (() => {
      const location = useLocation();
      const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';

      if (isEmbedded) {
        return (
          <div className="min-h-screen bg-white">
            <main className="min-h-screen overflow-y-auto p-4">
              <Outlet />
            </main>
          </div>
        );
      }

      return (
        <div className="flex flex-col min-h-screen bg-slate-50">
          <div className="flex flex-1 min-h-0 overflow-hidden">
            <PremiumSidebar
              isMobileOpen={isSidebarOpen}
              onCloseMobile={() => setIsSidebarOpen(false)}
              onLogout={handleLogout}
              currentUser={currentUser}
              isCollapsed={isSidebarCollapsed}
            />
            <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
              <TopNavbar
                onToggleSidebar={() => {
                  if (window.innerWidth >= 1024) {
                    setIsSidebarCollapsed((v) => !v);
                  } else {
                    setIsSidebarOpen(true);
                  }
                }}
                user={currentUser ? { name: currentUser.name, email: currentUser.email } : null}
                onLogout={handleLogout}
              />
              <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-y-auto p-4 pb-12 lg:p-8 lg:pb-12">
                <Outlet />
              </main>
            </div>
          </div>
          <Footer />
        </div>
      );
    })()
  );

  const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
    if (APP_MODE.disableAuth) {
      return children;
    }

    const location = useLocation();
    const hasToken = !!(localStorage.getItem('token') || localStorage.getItem('accessToken'));

    if (!hasToken) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return children;
  };

  return (
    <ToastProvider>
      <Router>
        <ScrollToTopOnRouteChange />
        <Routes>
        <Route path="/" element={<Navigate to={(localStorage.getItem('token') || localStorage.getItem('accessToken')) ? '/dashboard' : '/login'} replace />} />
        <Route
          path="/login"
          element={
            APP_MODE.disableAuth ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login
                onLogin={(user) =>
                  setCurrentUser({
                    id: user.id,
                    email: user.email,
                    name: user.name,
                    role: normalizeUserRole(user.role),
                    companyId: user.companyId,
                  })
                }
              />
            )
          }
        />

        <Route
          element={
            <ProtectedRoute>
              <ProtectedLayout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route
            path="/dashboard"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <DashboardWrapper />
              </RoleGuard>
            }
          >
            <Route index element={<DashboardOverview />} />
          </Route>

          <Route
            path="/logistics"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <LogisticsLayout />
              </RoleGuard>
            }
          >
            <Route path="orders" element={<OrdersWrapper />}>
              <Route index element={<OrdersList />} />
              <Route path="dispatch-board" element={<DispatchBoard />} />
              <Route path=":id" element={<OrderDetail />} />
            </Route>
            <Route path="customers" element={<CustomersList />} />
            <Route path="customers/new" element={<Navigate to="/logistics/customers" replace />} />
            <Route path="customers/:id/edit" element={<Navigate to="/logistics/customers" replace />} />
            <Route index element={<Navigate to="/logistics/orders" replace />} />
          </Route>

          {/* Fleet & Drivers */}
          <Route
            path="/fleet"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <FleetWrapper />
              </RoleGuard>
            }
          >
            <Route path="dashboard" element={<FleetDashboard />} />
            <Route path="fleets" element={<FleetsList />} />
            <Route path="service-areas" element={<ServiceAreasList />} />
            <Route path="zones" element={<ZonesList />} />
            <Route path="tracking-numbers" element={<TrackingNumbersList />} />
            <Route path="tracking-statuses" element={<TrackingStatusesList />} />
            <Route path="payloads" element={<PayloadsList />} />
            <Route path="payloads/:id" element={<PayloadDetail />} />
            <Route path="vehicles" element={<VehiclesList />} />
            <Route path="vehicles/:id" element={<VehicleDetail />} />
            <Route path="drivers" element={<DriversList />} />
            <Route path="drivers/:id" element={<DriverDetail />} />
            <Route path="entities" element={<EntitiesList />} />
            <Route path="contacts" element={<ContactsList />} />
            <Route path="contacts/:id" element={<ContactDetail />} />
            <Route path="places" element={<PlacesList />} />
            <Route path="places/:id" element={<PlaceDetail />} />
            <Route path="vendors" element={<VendorsList />} />
            <Route path="vendors/:id" element={<VendorDetail />} />
            <Route path="issues" element={<IssuesList />} />
            <Route path="issues/:id" element={<IssueDetail />} />
            <Route path="fuel-reports" element={<FuelReportsList />} />
            <Route path="fuel-reports/:id" element={<FuelReportDetail />} />
            <Route index element={<Navigate to="/fleet/dashboard" replace />} />
          </Route>

          {/* Warehouse */}
          <Route
            path="/warehouse"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <WarehouseWrapper />
              </RoleGuard>
            }
          >
            <Route path="zones" element={<ZonesManagement />} />
            <Route path="inventory" element={<InventoryList />} />
            <Route path="inventory/grn" element={<GRNProcess />} />
            <Route index element={<Navigate to="/warehouse/inventory" replace />} />
          </Route>

          {/* Billing */}
          <Route
            path="/billing"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <BillingWrapper />
              </RoleGuard>
            }
          >
            <Route path="invoices" element={<InvoicesList />} />
            <Route path="invoices/:id" element={<InvoiceDetail />} />
            <Route path="payments" element={<PaymentsList />} />
            <Route path="payments/record" element={<PaymentRecord />} />
            <Route index element={<Navigate to="/billing/invoices" replace />} />
          </Route>

          {/* Reports */}
          <Route
            path="/analytics"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <ReportsWrapper />
              </RoleGuard>
            }
          >
            <Route path="reports" element={<ReportsList />} />
            <Route path="reports/:id" element={<ReportDetail />} />
            <Route path="schedules" element={<SchedulesList />} />
            <Route path="schedule-items" element={<ScheduleItemsList />} />
            <Route path="schedule-templates" element={<ScheduleTemplatesList />} />
            <Route path="schedule-availability" element={<ScheduleAvailabilityList />} />
            <Route path="schedule-constraints" element={<ScheduleConstraintsList />} />
            <Route path="schedule-monitor" element={<ScheduleMonitorList />} />
            <Route path="schedule-monitor/:id" element={<ScheduleMonitorDetail />} />
            <Route path="transactions" element={<TransactionsList />} />
            <Route path="transactions/:id" element={<TransactionDetail />} />
            <Route path="api-credentials" element={<ApiCredentialsList />} />
            <Route path="api-events" element={<ApiEventsList />} />
            <Route path="api-events/:id" element={<ApiEventDetail />} />
            <Route path="api-request-logs" element={<ApiRequestLogsList />} />
            <Route path="api-request-logs/:id" element={<ApiRequestLogDetail />} />
            <Route path="custom-fields" element={<CustomFieldsList />} />
            <Route path="custom-field-values" element={<CustomFieldValuesList />} />
            <Route path="companies" element={<CompaniesList />} />
            <Route
              path="users"
              element={
                <RoleGuard
                  userRole={currentUser?.role ?? null}
                  requiredRole={[UserRole.ADMIN, UserRole.OPERATIONS_MANAGER]}
                  fallbackPath={roleFallbackPath}
                >
                  <UsersList />
                </RoleGuard>
              }
            />
            <Route path="comments" element={<CommentsList />} />
            <Route path="extensions" element={<ExtensionsList />} />
            <Route path="groups" element={<GroupsList />} />
            <Route path="notifications" element={<NotificationsList />} />
            <Route path="files" element={<FilesList />} />
            <Route path="devices" element={<DevicesList />} />
            <Route path="devices/:id" element={<DeviceDetail />} />
            <Route path="activities" element={<ActivitiesList />} />
            <Route path="activities/:id" element={<ActivityDetail />} />
            <Route path="outstanding" element={<OutstandingInvoices />} />
            <Route index element={<Navigate to="/analytics/reports" replace />} />
          </Route>

          {/* AI */}
          <Route
            path="/ai-assistant"
            element={
              <RoleGuard userRole={currentUser?.role || null} fallbackPath={roleFallbackPath}>
                <AIAssistant />
              </RoleGuard>
            }
          />

          {/* Profile is self-service for all authenticated users */}
          <Route path="/profile" element={<Profile />} />

          {/* /app aliases for real app modules (for redirect from public demo & login) */}
          <Route path="/app/dashboard" element={<Navigate to="/dashboard" replace />} />
          <Route path="/app/logistics/orders/*" element={<Navigate to="/logistics/orders" replace />} />
          <Route path="/app/logistics/customers/*" element={<Navigate to="/logistics/customers" replace />} />
          <Route path="/app/warehouse/*" element={<Navigate to="/warehouse" replace />} />
          <Route path="/app/fleet/*" element={<Navigate to="/fleet" replace />} />
          <Route path="/app/billing/*" element={<Navigate to="/billing" replace />} />
          <Route path="/app/analytics/*" element={<Navigate to="/analytics" replace />} />

          {/* Removed mock modules — keep bookmarks working */}
          <Route path="/master-data" element={<Navigate to="/dashboard" replace />} />
          <Route path="/live-operations/*" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="*"
            element={
              <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
                <Package size={64} className="opacity-20" />
                <div className="text-center">
                  <h2 className="text-xl font-bold">Module Under Development</h2>
                  <p className="text-sm">This section of the platform is currently being deployed.</p>
                </div>
                <Link to="/dashboard" className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition">
                  Back to Home
                </Link>
              </div>
            }
          />
        </Route>
        </Routes>
      </Router>
    </ToastProvider>
  );
};

export default App;
