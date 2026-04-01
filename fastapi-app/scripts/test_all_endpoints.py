#!/usr/bin/env python3
"""
Comprehensive API endpoint testing script.
Tests all endpoints with valid test data and validates responses.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE_URL = "http://localhost:9001"
TEST_RESULTS: List[Dict[str, Any]] = []


class APITester:
    """Test all API endpoints."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.test_data: Dict[str, Any] = {}
        self.company_uuid: Optional[str] = None
        
    def login(self, email: str = "admin@techliv.net", password: str = "admin123") -> bool:
        """Login and get JWT token."""
        try:
            response = requests.post(
                f"{self.base_url}/int/v1/auth/login",
                json={"identity": email, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                return True
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_endpoint(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        expected_status: int = 200,
        description: str = ""
    ) -> Dict[str, Any]:
        """Test a single endpoint."""
        url = f"{self.base_url}{path}"
        result = {
            "method": method,
            "path": path,
            "description": description,
            "status": "pending",
            "status_code": None,
            "response": None,
            "error": None
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.get_headers(), timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=self.get_headers(), timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=self.get_headers(), timeout=10)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=self.get_headers(), timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.get_headers(), timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            result["status_code"] = response.status_code
            
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text
            
            if response.status_code == expected_status:
                result["status"] = "✅ PASS"
            else:
                result["status"] = "❌ FAIL"
                result["error"] = f"Expected {expected_status}, got {response.status_code}"
                
        except Exception as e:
            result["status"] = "❌ ERROR"
            result["error"] = str(e)
        
        TEST_RESULTS.append(result)
        return result
    
    def run_all_tests(self):
        """Run comprehensive endpoint tests."""
        print("🚀 Starting comprehensive API endpoint testing...\n")
        
        # Login first
        print("1. Authenticating...")
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return
        print("✅ Authentication successful\n")
        
        # Get bootstrap data to get company UUID
        bootstrap = requests.get(
            f"{self.base_url}/int/v1/auth/bootstrap",
            headers=self.get_headers()
        )
        if bootstrap.status_code == 200:
            bootstrap_data = bootstrap.json()
            if bootstrap_data.get("organizations"):
                self.company_uuid = bootstrap_data["organizations"][0]["uuid"]
        
        # Core IAM Tests
        print("2. Testing Core IAM endpoints...")
        self._test_users()
        self._test_companies()
        self._test_roles()
        self._test_permissions()
        
        # FleetOps Tests
        print("\n3. Testing FleetOps endpoints...")
        self._test_contacts()
        self._test_vendors()
        self._test_places()
        self._test_drivers()
        self._test_vehicles()
        self._test_orders()
        
        # Service Rates & Quotes
        print("\n4. Testing Service Rates & Quotes...")
        self._test_service_rates()
        self._test_service_quotes()
        
        # Devices & Telematics
        print("\n5. Testing Devices & Telematics...")
        self._test_devices()
        
        # Storefront
        print("\n6. Testing Storefront endpoints...")
        self._test_storefront_customers()
        self._test_storefront_products()
        self._test_storefront_carts()
        
        # Core Utilities
        print("\n7. Testing Core Utilities...")
        self._test_files()
        self._test_comments()
        self._test_settings()
        
        print("\n✅ All endpoint tests completed!")
        self._print_summary()
    
    def _test_users(self):
        """Test user endpoints."""
        # List users
        self.test_endpoint("GET", "/int/v1/users", description="List users")
        
        # Create user
        user_data = {
            "name": "Test User API",
            "email": "testuser@api.test",
            "phone": "+1555123456",
            "password": "Test123!",
            "company_uuid": self.company_uuid,
            "timezone": "UTC",
            "country": "US"
        }
        result = self.test_endpoint("POST", "/int/v1/users", user_data, 201, "Create user")
        if result.get("status") == "✅ PASS" and result.get("response"):
            user_uuid = result["response"].get("uuid")
            if user_uuid:
                # Get user
                self.test_endpoint("GET", f"/int/v1/users/{user_uuid}", description="Get user")
                # Update user
                self.test_endpoint("PATCH", f"/int/v1/users/{user_uuid}", {"name": "Updated Name"}, description="Update user")
    
    def _test_companies(self):
        """Test company endpoints."""
        # List companies
        self.test_endpoint("GET", "/int/v1/companies", description="List companies")
        
        # Create company
        company_data = {
            "name": "Test Company API",
            "description": "Test company created via API",
            "phone": "+1555987654",
            "currency": "USD",
            "country": "US",
            "timezone": "UTC"
        }
        result = self.test_endpoint("POST", "/int/v1/companies", company_data, 201, "Create company")
        if result.get("status") == "✅ PASS" and result.get("response"):
            company_uuid = result["response"].get("uuid")
            if company_uuid:
                # Get company
                self.test_endpoint("GET", f"/int/v1/companies/{company_uuid}", description="Get company")
    
    def _test_roles(self):
        """Test role endpoints."""
        self.test_endpoint("GET", "/int/v1/roles", description="List roles")
    
    def _test_permissions(self):
        """Test permission endpoints."""
        self.test_endpoint("GET", "/int/v1/permissions", description="List permissions")
    
    def _test_contacts(self):
        """Test contact endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/contacts", description="List contacts")
        
        contact_data = {
            "name": "API Test Contact",
            "email": "contact@api.test",
            "phone": "+1555111111",
            "type": "customer",
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/contacts", contact_data, 201, "Create contact")
        if result.get("status") == "✅ PASS" and result.get("response"):
            contact_uuid = result["response"].get("uuid")
            if contact_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/contacts/{contact_uuid}", description="Get contact")
    
    def _test_vendors(self):
        """Test vendor endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/vendors", description="List vendors")
        
        vendor_data = {
            "name": "API Test Vendor",
            "email": "vendor@api.test",
            "phone": "+1555222222",
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/vendors", vendor_data, 201, "Create vendor")
        if result.get("status") == "✅ PASS" and result.get("response"):
            vendor_uuid = result["response"].get("uuid")
            if vendor_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/vendors/{vendor_uuid}", description="Get vendor")
    
    def _test_places(self):
        """Test place endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/places", description="List places")
        
        place_data = {
            "name": "API Test Place",
            "street1": "123 Test St",
            "city": "Test City",
            "province": "TS",
            "postal_code": "12345",
            "country": "US",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/places", place_data, 201, "Create place")
        if result.get("status") == "✅ PASS" and result.get("response"):
            place_uuid = result["response"].get("uuid")
            if place_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/places/{place_uuid}", description="Get place")
    
    def _test_drivers(self):
        """Test driver endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/drivers", description="List drivers")
        
        driver_data = {
            "name": "API Test Driver",
            "phone": "+1555333333",
            "email": "driver@api.test",
            "license_number": "DL-API-001",
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/drivers", driver_data, 201, "Create driver")
        if result.get("status") == "✅ PASS" and result.get("response"):
            driver_uuid = result["response"].get("uuid")
            if driver_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/drivers/{driver_uuid}", description="Get driver")
    
    def _test_vehicles(self):
        """Test vehicle endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/vehicles", description="List vehicles")
        
        vehicle_data = {
            "name": "API Test Vehicle",
            "vin": "1TESTVIN123456789",
            "year": 2024,
            "make": "Test",
            "model": "Model X",
            "plate_number": "API-1234",
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/vehicles", vehicle_data, 201, "Create vehicle")
        if result.get("status") == "✅ PASS" and result.get("response"):
            vehicle_uuid = result["response"].get("uuid")
            if vehicle_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/vehicles/{vehicle_uuid}", description="Get vehicle")
    
    def _test_orders(self):
        """Test order endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/orders", description="List orders")
        
        order_data = {
            "internal_id": "API-ORD-001",
            "type": "delivery",
            "status": "pending",
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/orders", order_data, 201, "Create order")
        if result.get("status") == "✅ PASS" and result.get("response"):
            order_uuid = result["response"].get("uuid")
            if order_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/orders/{order_uuid}", description="Get order")
    
    def _test_service_rates(self):
        """Test service rate endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/service-rates", description="List service rates")
        
        rate_data = {
            "service_name": "API Test Rate",
            "service_type": "delivery",
            "base_fee": 500,
            "per_meter_flat_rate_fee": 10,
            "per_meter_unit": "m",
            "rate_calculation_method": "per_meter",
            "currency": "USD",
            "company_uuid": self.company_uuid
        }
        result = self.test_endpoint("POST", "/fleetops/v1/service-rates", rate_data, 201, "Create service rate")
        if result.get("status") == "✅ PASS" and result.get("response"):
            rate_uuid = result["response"].get("uuid")
            if rate_uuid:
                self.test_endpoint("GET", f"/fleetops/v1/service-rates/{rate_uuid}", description="Get service rate")
    
    def _test_service_quotes(self):
        """Test service quote endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/service-quotes", description="List service quotes")
    
    def _test_devices(self):
        """Test device endpoints."""
        self.test_endpoint("GET", "/fleetops/v1/devices", description="List devices")
    
    def _test_storefront_customers(self):
        """Test storefront customer endpoints."""
        self.test_endpoint("GET", "/storefront/v1/customers", description="List storefront customers")
    
    def _test_storefront_products(self):
        """Test storefront product endpoints."""
        self.test_endpoint("GET", "/storefront/v1/products", description="List storefront products")
    
    def _test_storefront_carts(self):
        """Test storefront cart endpoints."""
        self.test_endpoint("GET", "/storefront/v1/carts", description="List storefront carts")
    
    def _test_files(self):
        """Test file endpoints."""
        self.test_endpoint("GET", "/v1/files", description="List files")
    
    def _test_comments(self):
        """Test comment endpoints."""
        self.test_endpoint("GET", "/v1/comments", description="List comments")
    
    def _test_settings(self):
        """Test settings endpoints."""
        self.test_endpoint("GET", "/v1/settings/branding", description="Get branding settings")
    
    def _print_summary(self):
        """Print test summary."""
        total = len(TEST_RESULTS)
        passed = sum(1 for r in TEST_RESULTS if r["status"] == "✅ PASS")
        failed = sum(1 for r in TEST_RESULTS if r["status"] == "❌ FAIL")
        errors = sum(1 for r in TEST_RESULTS if r["status"] == "❌ ERROR")
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print("="*60)
        
        if failed > 0 or errors > 0:
            print("\n❌ Failed/Error Tests:")
            for result in TEST_RESULTS:
                if result["status"] in ["❌ FAIL", "❌ ERROR"]:
                    print(f"  {result['method']} {result['path']}")
                    print(f"    Status: {result['status']}")
                    if result.get("error"):
                        print(f"    Error: {result['error']}")


def main():
    """Main function."""
    tester = APITester()
    tester.run_all_tests()
    
    # Save results to JSON
    output_file = Path(__file__).parent.parent / "test_results.json"
    with open(output_file, "w") as f:
        json.dump(TEST_RESULTS, f, indent=2, default=str)
    print(f"\n📄 Test results saved to: {output_file}")


if __name__ == "__main__":
    main()

