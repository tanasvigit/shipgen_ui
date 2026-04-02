export const mockAuthUser = {
  id: 'USR-ADMIN-1',
  name: 'ShipGen Admin',
  email: 'admin@shipgen.local',
  role: 'COMPANY_ADMIN',
  company_id: 'COMP-01',
};

export const buildMockLoginResponse = () => ({
  accessToken: `mock_access_${Date.now()}`,
  refreshToken: `mock_refresh_${Date.now()}`,
  user: mockAuthUser,
});
