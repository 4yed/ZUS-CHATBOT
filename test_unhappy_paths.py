import unittest
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

class TestUnhappyFlows(unittest.TestCase):

    def test_missing_query_param_for_products(self):
        """Test missing 'query' for /products."""
        response = requests.get(f"{BASE_URL}/products")
        self.assertEqual(response.status_code, 422, "Should return 422 for missing query.")

    def test_missing_query_param_for_outlets(self):
        """Test missing 'query' for /outlets."""
        response = requests.get(f"{BASE_URL}/outlets")
        self.assertEqual(response.status_code, 422, "Should return 422 for missing query.")

    def test_sql_injection_attempt(self):
        """Test SQL injection attempt."""
        malicious_query = "List outlets; DROP TABLE outlets;"
        response = requests.get(f"{BASE_URL}/outlets", params={'query': malicious_query})
        self.assertEqual(response.status_code, 200, "Should handle payload gracefully.")
        
        data = response.json()
        self.assertTrue(data['result']['success'], "Should not fail despite the attempt.")
        self.assertNotIn("DROP TABLE", data['result']['sql_query'], "Should not include malicious SQL.")
        
        response_after = requests.get(f"{BASE_URL}/outlets", params={'query': 'list outlets'})
        self.assertEqual(response_after.status_code, 200, "Table should still exist.")
        self.assertTrue(response_after.json()['result']['success'], "Valid query should still work.")
        
if __name__ == '__main__':
    unittest.main() 