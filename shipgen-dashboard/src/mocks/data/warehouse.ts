export const mockWarehouses = [
  { id: 'WH-01', name: 'Mumbai Hub', location: 'Mumbai' },
  { id: 'WH-02', name: 'Bengaluru DC', location: 'Bengaluru' },
];

export const mockZones = [
  { id: 'ZN-01', warehouseId: 'WH-01', name: 'Cold Zone A' },
  { id: 'ZN-02', warehouseId: 'WH-02', name: 'General Zone B' },
];

export const mockRacks = [{ id: 'RK-01', zoneId: 'ZN-01', name: 'Rack 1' }];
export const mockBins = [{ id: 'BN-01', rackId: 'RK-01', name: 'Bin 1' }];

export const mockInventory = [
  { id: 'INV-01', sku: 'SKU-1001', name: 'Mobile Units', quantity: 150, warehouseId: 'WH-01' },
  { id: 'INV-02', sku: 'SKU-1002', name: 'Spare Parts', quantity: 90, warehouseId: 'WH-02' },
];
