import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Bell, LogOut, PanelLeft, Search, User, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/Button';

interface TopNavbarUser {
  name: string;
  email: string;
}

interface TopNavbarProps {
  onToggleSidebar: () => void;
  user: TopNavbarUser | null;
  onLogout: () => void;
}

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

const TopNavbar: React.FC<TopNavbarProps> = ({ onToggleSidebar, user, onLogout }) => {
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const initials = useMemo(() => (user?.name ? user.name.slice(0, 1).toUpperCase() : 'U'), [user]);

  useEffect(() => {
    if (!isUserMenuOpen) return;

    const onMouseDown = (event: MouseEvent) => {
      const el = userMenuRef.current;
      if (el && !el.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [isUserMenuOpen]);

  return (
    <header className="sticky top-0 z-30 border-b border-border/80 bg-white/80 px-4 backdrop-blur-md lg:px-8">
      <div className="mx-auto flex h-16 max-w-[1600px] items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <button
            type="button"
            onClick={onToggleSidebar}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-white text-secondary-600 transition-all duration-200 hover:bg-secondary-50"
            aria-label="Toggle sidebar"
          >
            <PanelLeft size={18} />
          </button>

          <div className="hidden h-11 w-[280px] items-center rounded-[10px] border border-[#E5E7EB] bg-[#F9FAFB] px-3 text-secondary-600 transition-all duration-200 ease-out focus-within:border-[#3B82F6] focus-within:bg-white focus-within:shadow-[0_0_0_2px_rgba(59,130,246,0.15)] sm:flex md:w-[340px] lg:w-[380px]">
            <Search size={17} className="ml-0.5 shrink-0 text-[#9CA3AF]" />
            <input
              type="text"
              placeholder="Search orders, drivers"
              className="h-full w-full bg-transparent px-3 text-sm text-neutral-900 placeholder:text-[#9CA3AF] focus:outline-none focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0"
              aria-label="Search in ShipGen"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => navigate('/analytics/notifications')}
            className="relative inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-white text-secondary-600 transition-all duration-200 hover:bg-secondary-50"
            aria-label="Notifications"
          >
            <Bell size={17} />
            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-danger-600 ring-2 ring-white" />
          </button>

          <div ref={userMenuRef} className="relative">
            <button
              type="button"
              onClick={() => setIsUserMenuOpen((open) => !open)}
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-white px-2 py-1.5 transition-all duration-200 hover:bg-secondary-50"
              aria-label="Open user menu"
              aria-expanded={isUserMenuOpen}
              aria-haspopup="true"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary-100 text-xs font-semibold text-primary-700">
                {initials}
              </div>
              <span className="hidden text-sm font-medium text-neutral-900 sm:inline">{user?.name ?? 'User'}</span>
              <ChevronDown size={15} className={cn('text-secondary-500 transition-transform duration-200', isUserMenuOpen && 'rotate-180')} />
            </button>

            {isUserMenuOpen ? (
              <div
                className="absolute right-0 top-11 z-40 w-56 origin-top-right rounded-xl border border-border bg-white p-2 shadow-card-soft transition ease-out duration-150 animate-scale-in"
                role="menu"
                aria-orientation="vertical"
              >
                <div className="mb-2 rounded-lg bg-secondary-50 px-3 py-2">
                  <p className="truncate text-sm font-semibold text-neutral-900">{user?.name ?? 'User'}</p>
                  <p className="truncate text-xs text-secondary-500">{user?.email ?? 'user@shipgen.com'}</p>
                </div>
                <Button
                  variant="ghost"
                  fullWidth
                  className="justify-start"
                  role="menuitem"
                  onClick={() => {
                    navigate('/analytics/profile');
                    setIsUserMenuOpen(false);
                  }}
                >
                  <User size={16} />
                  Profile
                </Button>
                <Button
                  variant="ghost"
                  fullWidth
                  className="justify-start text-danger-600 hover:bg-danger-50 hover:text-danger-700"
                  role="menuitem"
                  onClick={() => {
                    setIsUserMenuOpen(false);
                    onLogout();
                  }}
                  data-testid="navbar-logout"
                >
                  <LogOut size={16} />
                  Sign out
                </Button>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
};

export default TopNavbar;
