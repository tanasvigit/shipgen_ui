import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

interface SubNavItem {
  path: string;
  label: string;
  exact?: boolean;
}

interface SubNavigationProps {
  items: SubNavItem[];
  basePath: string;
}

const SubNavigation: React.FC<SubNavigationProps> = ({ items, basePath }) => {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <div className="mb-6 bg-white rounded-xl border border-gray-200 p-2">
      <div className="flex items-center space-x-1 overflow-x-auto">
        {items.map((item, idx) => {
          const isActive = item.exact
            ? currentPath === item.path
            : currentPath.startsWith(item.path);
          
          return (
            <React.Fragment key={item.path}>
              <Link
                to={item.path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
              {idx < items.length - 1 && (
                <ChevronRight size={16} className="text-gray-400 flex-shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default SubNavigation;
