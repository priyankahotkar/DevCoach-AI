import requests
import sys
import json
from datetime import datetime

class AIStudentJourneyAPITester:
    def __init__(self, base_url="https://dev-journey-guide.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_analyze_profile_github_only(self):
        """Test profile analysis with GitHub username only"""
        data = {
            "github_username": "octocat",
            "goal": "Improve programming skills",
            "domain": "General Software Development"
        }
        return self.run_test(
            "Analyze Profile - GitHub Only",
            "POST",
            "analyze-profile",
            200,
            data=data,
            timeout=60  # AI generation might take longer
        )

    def test_analyze_profile_codeforces_only(self):
        """Test profile analysis with Codeforces username only"""
        data = {
            "codeforces_username": "tourist",
            "goal": "Master competitive programming",
            "domain": "Algorithms and Data Structures"
        }
        return self.run_test(
            "Analyze Profile - Codeforces Only",
            "POST",
            "analyze-profile",
            200,
            data=data,
            timeout=60
        )

    def test_analyze_profile_leetcode_only(self):
        """Test profile analysis with LeetCode username only - using real user 'lee215'"""
        data = {
            "leetcode_username": "lee215",
            "goal": "Improve problem solving",
            "domain": "Software Engineering"
        }
        success, response = self.run_test(
            "Analyze Profile - LeetCode Only (lee215)",
            "POST",
            "analyze-profile",
            200,
            data=data,
            timeout=60
        )
        
        # Validate LeetCode specific data structure
        if success and isinstance(response, dict):
            leetcode_data = response.get('activity_data', {}).get('leetcode', {})
            if 'error' not in leetcode_data:
                activity = leetcode_data.get('activity', {})
                profile = leetcode_data.get('profile', {})
                
                print(f"   📊 LeetCode Data Validation:")
                print(f"      Total Solved: {activity.get('total_solved', 'N/A')}")
                print(f"      Easy Solved: {activity.get('easy_solved', 'N/A')}")
                print(f"      Medium Solved: {activity.get('medium_solved', 'N/A')}")
                print(f"      Hard Solved: {activity.get('hard_solved', 'N/A')}")
                print(f"      Acceptance Rate: {activity.get('acceptance_rate', 'N/A')}")
                print(f"      Ranking: {profile.get('ranking', 'N/A')}")
                
                # Validate expected fields are present
                expected_activity_fields = ['total_solved', 'easy_solved', 'medium_solved', 'hard_solved', 'acceptance_rate']
                for field in expected_activity_fields:
                    if field in activity:
                        print(f"      ✅ {field}: Present")
                    else:
                        print(f"      ❌ {field}: Missing")
            else:
                print(f"   ❌ LeetCode Error: {leetcode_data.get('error')}")
        
        return success, response

    def test_analyze_profile_multiple_platforms(self):
        """Test profile analysis with multiple platforms"""
        data = {
            "github_username": "octocat",
            "codeforces_username": "tourist",
            "leetcode_username": "testuser",
            "goal": "Become a full-stack developer",
            "domain": "Web Development"
        }
        return self.run_test(
            "Analyze Profile - Multiple Platforms",
            "POST",
            "analyze-profile",
            200,
            data=data,
            timeout=90  # Multiple API calls + AI generation
        )

    def test_analyze_profile_invalid_github(self):
        """Test profile analysis with invalid GitHub username"""
        data = {
            "github_username": "this_user_definitely_does_not_exist_12345",
            "goal": "Test error handling",
            "domain": "Testing"
        }
        success, response = self.run_test(
            "Analyze Profile - Invalid GitHub",
            "POST",
            "analyze-profile",
            200,  # Should still return 200 but with error in response
            data=data,
            timeout=30
        )
        
        # Check if error is properly handled in response
        if success and isinstance(response, dict):
            github_data = response.get('activity_data', {}).get('github', {})
            if 'error' in github_data:
                print(f"   ✅ Error properly handled: {github_data['error']}")
            else:
                print(f"   ⚠️  Expected error in GitHub data but got: {github_data}")
        
        return success, response

    def test_analyze_profile_invalid_codeforces(self):
        """Test profile analysis with invalid Codeforces username"""
        data = {
            "codeforces_username": "invalid_user_12345",
            "goal": "Test error handling",
            "domain": "Testing"
        }
        success, response = self.run_test(
            "Analyze Profile - Invalid Codeforces",
            "POST",
            "analyze-profile",
            200,  # Should still return 200 but with error in response
            data=data,
            timeout=30
        )
        
        # Check if error is properly handled in response
        if success and isinstance(response, dict):
            cf_data = response.get('activity_data', {}).get('codeforces', {})
            if 'error' in cf_data:
                print(f"   ✅ Error properly handled: {cf_data['error']}")
            else:
                print(f"   ⚠️  Expected error in Codeforces data but got: {cf_data}")
        
        return success, response

    def test_analyze_profile_no_usernames(self):
        """Test profile analysis with no usernames (should fail validation)"""
        data = {
            "goal": "Test validation",
            "domain": "Testing"
        }
        # This should still work as the backend doesn't enforce username requirement
        return self.run_test(
            "Analyze Profile - No Usernames",
            "POST",
            "analyze-profile",
            200,
            data=data,
            timeout=30
        )

    def validate_analysis_response(self, response_data):
        """Validate the structure of analysis response"""
        required_fields = ['user_id', 'activity_data', 'recommendations', 'analysis_timestamp']
        
        print(f"\n🔍 Validating response structure...")
        for field in required_fields:
            if field in response_data:
                print(f"   ✅ {field}: Present")
            else:
                print(f"   ❌ {field}: Missing")
                return False
        
        # Validate recommendations structure
        recommendations = response_data.get('recommendations', [])
        if isinstance(recommendations, list) and len(recommendations) > 0:
            print(f"   ✅ Recommendations: {len(recommendations)} items")
            
            # Check first recommendation structure
            first_rec = recommendations[0]
            rec_fields = ['type', 'title', 'description', 'difficulty']
            for field in rec_fields:
                if field in first_rec:
                    print(f"   ✅ Recommendation.{field}: Present")
                else:
                    print(f"   ❌ Recommendation.{field}: Missing")
        else:
            print(f"   ⚠️  Recommendations: Empty or invalid")
        
        return True

def main():
    print("🚀 Starting AI Student Journey Guide API Tests")
    print("=" * 60)
    
    tester = AIStudentJourneyAPITester()
    
    # Test basic connectivity
    success, _ = tester.test_root_endpoint()
    if not success:
        print("❌ Basic connectivity failed. Stopping tests.")
        return 1
    
    # Test individual platform analysis
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL PLATFORMS")
    print("="*60)
    
    github_success, github_response = tester.test_analyze_profile_github_only()
    if github_success and isinstance(github_response, dict):
        tester.validate_analysis_response(github_response)
    
    cf_success, cf_response = tester.test_analyze_profile_codeforces_only()
    if cf_success and isinstance(cf_response, dict):
        tester.validate_analysis_response(cf_response)
    
    leetcode_success, leetcode_response = tester.test_analyze_profile_leetcode_only()
    
    # Test multiple platforms
    print("\n" + "="*60)
    print("TESTING MULTIPLE PLATFORMS")
    print("="*60)
    
    multi_success, multi_response = tester.test_analyze_profile_multiple_platforms()
    if multi_success and isinstance(multi_response, dict):
        tester.validate_analysis_response(multi_response)
    
    # Test error handling
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    tester.test_analyze_profile_invalid_github()
    tester.test_analyze_profile_invalid_codeforces()
    tester.test_analyze_profile_no_usernames()
    
    # Print final results
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())