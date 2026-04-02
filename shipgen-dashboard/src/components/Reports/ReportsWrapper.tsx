import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import SubNavigation from '../SubNavigation';

const ReportsWrapper: React.FC = () => {
  const location = useLocation();
  const isEmbedded = new URLSearchParams(location.search).get('embed') === '1';
  const currentPath = location.pathname;
  const isCompanyModule =
    currentPath === '/analytics/companies' ||
    currentPath.startsWith('/analytics/companies/');
  const scheduleModules = [
    {
      path: '/analytics/schedules',
      listLabel: 'Schedules List',
    },
    {
      path: '/analytics/schedule-items',
      listLabel: 'Schedule Items List',
    },
    {
      path: '/analytics/schedule-templates',
      listLabel: 'Schedule Templates List',
    },
    {
      path: '/analytics/schedule-availability',
      listLabel: 'Schedule Availability List',
    },
    {
      path: '/analytics/schedule-constraints',
      listLabel: 'Schedule Constraints List',
    },
    {
      path: '/analytics/schedule-monitor',
      listLabel: 'Schedule Monitor List',
    },
  ] as const;
  const activeScheduleModule = scheduleModules.find(
    (module) => currentPath === module.path || currentPath.startsWith(`${module.path}/`)
  );
  const apiIntegrationModules = [
    {
      path: '/analytics/api-credentials',
      listLabel: 'API Credentials List',
    },
    {
      path: '/analytics/api-events',
      listLabel: 'API Events List',
    },
    {
      path: '/analytics/api-request-logs',
      listLabel: 'API Request Logs List',
    },
    {
      path: '/analytics/extensions',
      listLabel: 'Extensions List',
    },
  ] as const;
  const activeApiIntegrationModule = apiIntegrationModules.find(
    (module) => currentPath === module.path || currentPath.startsWith(`${module.path}/`)
  );
  const systemConfigurationModules = [
    {
      path: '/analytics/custom-fields',
      listLabel: 'Custom Fields List',
    },
    {
      path: '/analytics/custom-field-values',
      listLabel: 'Custom Field Values List',
    },
    {
      path: '/analytics/files',
      listLabel: 'Files List',
    },
    {
      path: '/analytics/notifications',
      listLabel: 'Notifications List',
    },
  ] as const;
  const activeSystemConfigurationModule = systemConfigurationModules.find(
    (module) => currentPath === module.path || currentPath.startsWith(`${module.path}/`)
  );
  const usersAccessModules = [
    {
      path: '/analytics/users',
      listLabel: 'Users List',
    },
    {
      path: '/analytics/groups',
      listLabel: 'Groups List',
    },
  ] as const;
  const activeUsersAccessModule = usersAccessModules.find(
    (module) => currentPath === module.path || currentPath.startsWith(`${module.path}/`)
  );
  const reportsAnalyticsModules = [
    {
      path: '/analytics/reports',
      listLabel: 'Reports List',
    },
    {
      path: '/analytics/transactions',
      listLabel: 'Transactions List',
    },
  ] as const;
  const activeReportsAnalyticsModule = reportsAnalyticsModules.find(
    (module) => currentPath === module.path || currentPath.startsWith(`${module.path}/`)
  );

  const companyTabs = [
    { path: '/analytics/companies', label: 'Companies List', exact: true },
  ];
  const scheduleTabs = activeScheduleModule
    ? [
        { path: activeScheduleModule.path, label: activeScheduleModule.listLabel, exact: true },
        ...(activeScheduleModule.createPath
          ? [{ path: activeScheduleModule.createPath, label: activeScheduleModule.createLabel }]
          : []),
      ]
    : [];
  const apiIntegrationTabs = activeApiIntegrationModule
    ? [
        { path: activeApiIntegrationModule.path, label: activeApiIntegrationModule.listLabel, exact: true },
        ...(activeApiIntegrationModule.createPath
          ? [{ path: activeApiIntegrationModule.createPath, label: activeApiIntegrationModule.createLabel }]
          : []),
      ]
    : [];
  const systemConfigurationTabs = activeSystemConfigurationModule
    ? [
        { path: activeSystemConfigurationModule.path, label: activeSystemConfigurationModule.listLabel, exact: true },
        ...(activeSystemConfigurationModule.createPath
          ? [{ path: activeSystemConfigurationModule.createPath, label: activeSystemConfigurationModule.createLabel }]
          : []),
      ]
    : [];
  const usersAccessTabs = activeUsersAccessModule
    ? [
        { path: activeUsersAccessModule.path, label: activeUsersAccessModule.listLabel, exact: true },
        ...(activeUsersAccessModule.createPath
          ? [{ path: activeUsersAccessModule.createPath, label: activeUsersAccessModule.createLabel }]
          : []),
      ]
    : [];
  const reportsAnalyticsTabs = activeReportsAnalyticsModule
    ? [{ path: activeReportsAnalyticsModule.path, label: activeReportsAnalyticsModule.listLabel, exact: true }]
    : [];

  return (
    <div>
      {!isEmbedded && isCompanyModule ? <SubNavigation items={companyTabs} basePath="/analytics/companies" /> : null}
      {!isEmbedded && activeScheduleModule ? <SubNavigation items={scheduleTabs} basePath={activeScheduleModule.path} /> : null}
      {!isEmbedded && activeApiIntegrationModule ? (
        <SubNavigation items={apiIntegrationTabs} basePath={activeApiIntegrationModule.path} />
      ) : null}
      {!isEmbedded && activeSystemConfigurationModule ? (
        <SubNavigation items={systemConfigurationTabs} basePath={activeSystemConfigurationModule.path} />
      ) : null}
      {!isEmbedded && activeUsersAccessModule ? (
        <SubNavigation items={usersAccessTabs} basePath={activeUsersAccessModule.path} />
      ) : null}
      {!isEmbedded && activeReportsAnalyticsModule ? (
        <SubNavigation items={reportsAnalyticsTabs} basePath={activeReportsAnalyticsModule.path} />
      ) : null}
      <Outlet />
    </div>
  );
};

export default ReportsWrapper;
