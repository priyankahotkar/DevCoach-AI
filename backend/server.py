from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import aiohttp
import google.generativeai as genai
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configure Google AI
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Data Models
class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_analyzed: Optional[datetime] = None

class UserProfileCreate(BaseModel):
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None

class ActivityStats(BaseModel):
    platform: str
    username: str
    stats: Dict[str, Any]
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    recommendations: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalyzeProfileRequest(BaseModel):
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    goal: Optional[str] = "Improve programming skills"
    domain: Optional[str] = "General Software Development"

# Platform Data Fetchers
class PlatformDataFetcher:
    
    @staticmethod
    async def fetch_github_stats(username: str) -> Dict[str, Any]:
        """Fetch GitHub user statistics and recent activity"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get user info
                user_url = f"https://api.github.com/users/{username}"
                async with session.get(user_url) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=404, detail=f"GitHub user {username} not found")
                    user_data = await response.json()
                
                # Get repositories
                repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10"
                async with session.get(repos_url) as response:
                    repos_data = await response.json() if response.status == 200 else []
                
                # Get events (recent activity)
                events_url = f"https://api.github.com/users/{username}/events?per_page=30"
                async with session.get(events_url) as response:
                    events_data = await response.json() if response.status == 200 else []
                
                # Process data
                languages = {}
                total_stars = 0
                recent_commits = 0
                
                for repo in repos_data:
                    if repo.get('stargazers_count'):
                        total_stars += repo['stargazers_count']
                    if repo.get('language'):
                        languages[repo['language']] = languages.get(repo['language'], 0) + 1
                
                for event in events_data:
                    if event.get('type') == 'PushEvent':
                        recent_commits += len(event.get('payload', {}).get('commits', []))
                
                return {
                    'profile': {
                        'name': user_data.get('name'),
                        'public_repos': user_data.get('public_repos', 0),
                        'followers': user_data.get('followers', 0),
                        'following': user_data.get('following', 0),
                        'created_at': user_data.get('created_at'),
                        'bio': user_data.get('bio')
                    },
                    'activity': {
                        'total_stars': total_stars,
                        'recent_commits': recent_commits,
                        'top_languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]),
                        'recent_repos': [{'name': repo['name'], 'language': repo.get('language')} for repo in repos_data[:5]]
                    }
                }
        except Exception as e:
            logger.error(f"Error fetching GitHub data for {username}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error fetching GitHub data: {str(e)}")

    @staticmethod
    async def fetch_leetcode_stats(username: str) -> Dict[str, Any]:
        """Fetch LeetCode user statistics using unofficial API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Use the provided LeetCode API
                leetcode_url = f"https://leetcode-api-pied.vercel.app/user/{username}"
                async with session.get(leetcode_url) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=404, detail=f"LeetCode user {username} not found")
                    
                    data = await response.json()
                    
                    # Extract relevant information from the API response
                    profile_data = data.get('profile', {})
                    submit_stats = data.get('submitStats', {})
                    
                    # Parse solved problems statistics
                    ac_submission = submit_stats.get('acSubmissionNum', [])
                    total_solved = 0
                    easy_solved = 0
                    medium_solved = 0
                    hard_solved = 0
                    
                    for stat in ac_submission:
                        difficulty = stat.get('difficulty', '').lower()
                        count = stat.get('count', 0)
                        if difficulty == 'all':
                            total_solved = count
                        elif difficulty == 'easy':
                            easy_solved = count
                        elif difficulty == 'medium':
                            medium_solved = count
                        elif difficulty == 'hard':
                            hard_solved = count
                    
                    # Calculate acceptance rate
                    total_submissions = submit_stats.get('totalSubmissionNum', [])
                    total_accepted = next((item.get('count', 0) for item in total_submissions if item.get('difficulty') == 'All'), 0)
                    total_submitted = next((item.get('submissions', 0) for item in total_submissions if item.get('difficulty') == 'All'), 1)
                    acceptance_rate = round((total_accepted / max(total_submitted, 1)) * 100, 1) if total_submitted > 0 else 0
                    
                    return {
                        'profile': {
                            'username': username,
                            'real_name': profile_data.get('realName', 'Unknown'),
                            'ranking': profile_data.get('ranking', 'N/A'),
                            'reputation': profile_data.get('reputation', 0),
                            'github_link': profile_data.get('githubUrl', ''),
                            'twitter_link': profile_data.get('twitterUrl', ''),
                            'linkedin_link': profile_data.get('linkedinUrl', ''),
                            'about_me': profile_data.get('aboutMe', '')
                        },
                        'activity': {
                            'total_solved': total_solved,
                            'easy_solved': easy_solved,
                            'medium_solved': medium_solved,
                            'hard_solved': hard_solved,
                            'acceptance_rate': f"{acceptance_rate}%",
                            'total_submissions': total_accepted,
                            'contribution_points': profile_data.get('contributionPoints', 0),
                            'reputation': profile_data.get('reputation', 0)
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching LeetCode data for {username}: {str(e)}")
            return {
                'profile': {'username': username},
                'activity': {'note': 'Unable to fetch LeetCode data'},
                'error': str(e)
            }

    @staticmethod
    async def fetch_codeforces_stats(username: str) -> Dict[str, Any]:
        """Fetch Codeforces user statistics using official API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get user info
                user_url = f"https://codeforces.com/api/user.info?handles={username}"
                async with session.get(user_url) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=404, detail=f"Codeforces user {username} not found")
                    user_response = await response.json()
                    
                    if user_response['status'] != 'OK':
                        raise HTTPException(status_code=404, detail=f"Codeforces user {username} not found")
                    
                    user_data = user_response['result'][0]
                
                # Get user rating history
                rating_url = f"https://codeforces.com/api/user.rating?handle={username}"
                async with session.get(rating_url) as response:
                    rating_data = []
                    if response.status == 200:
                        rating_response = await response.json()
                        if rating_response['status'] == 'OK':
                            rating_data = rating_response['result']
                
                # Get user submissions (last 100)
                submissions_url = f"https://codeforces.com/api/user.status?handle={username}&from=1&count=100"
                async with session.get(submissions_url) as response:
                    submissions_data = []
                    if response.status == 200:
                        submissions_response = await response.json()
                        if submissions_response['status'] == 'OK':
                            submissions_data = submissions_response['result']
                
                # Process submissions
                solved_problems = set()
                for submission in submissions_data:
                    if submission.get('verdict') == 'OK':
                        problem_id = f"{submission['problem']['contestId']}-{submission['problem']['index']}"
                        solved_problems.add(problem_id)
                
                current_rating = user_data.get('rating', 0)
                max_rating = user_data.get('maxRating', 0)
                
                return {
                    'profile': {
                        'handle': user_data.get('handle'),
                        'first_name': user_data.get('firstName', ''),
                        'last_name': user_data.get('lastName', ''),
                        'country': user_data.get('country', ''),
                        'city': user_data.get('city', ''),
                        'organization': user_data.get('organization', ''),
                        'rank': user_data.get('rank', 'unrated'),
                        'max_rank': user_data.get('maxRank', 'unrated')
                    },
                    'activity': {
                        'current_rating': current_rating,
                        'max_rating': max_rating,
                        'contests_participated': len(rating_data),
                        'problems_solved': len(solved_problems),
                        'total_submissions': len(submissions_data),
                        'recent_activity': 'Active' if submissions_data else 'Inactive'
                    }
                }
        except Exception as e:
            logger.error(f"Error fetching Codeforces data for {username}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error fetching Codeforces data: {str(e)}")

# AI Recommendation Engine
class AIRecommendationEngine:
    
    @staticmethod
    async def generate_recommendations(activity_data: Dict[str, Any], goal: str, domain: str) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations based on user activity"""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Prepare context for AI
            context = f"""
            User's Programming Activity Analysis:
            
            Goal: {goal}
            Domain: {domain}
            
            Activity Data:
            {json.dumps(activity_data, indent=2, default=str)}
            
            Based on this data, provide 5-7 specific, actionable recommendations for improving their programming skills.
            Focus on concrete next steps, specific problems to solve, projects to build, or skills to learn.
            
            Format your response as a JSON array with objects containing:
            - "type": "project" | "problem" | "skill" | "learning"
            - "title": Brief title of the recommendation
            - "description": Detailed description
            - "difficulty": "beginner" | "intermediate" | "advanced"
            - "time_estimate": Estimated time to complete
            - "resources": Array of helpful links or resources
            """
            
            response = await asyncio.to_thread(model.generate_content, context)
            
            # Parse AI response
            try:
                # Extract JSON from response
                response_text = response.text
                # Find JSON in the response (it might be wrapped in markdown)
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                else:
                    # Fallback to structured recommendations
                    recommendations = AIRecommendationEngine._create_fallback_recommendations(activity_data, goal, domain)
                
                return recommendations
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured recommendations
                return AIRecommendationEngine._create_fallback_recommendations(activity_data, goal, domain)
                
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            return AIRecommendationEngine._create_fallback_recommendations(activity_data, goal, domain)
    
    @staticmethod
    def _create_fallback_recommendations(activity_data: Dict[str, Any], goal: str, domain: str) -> List[Dict[str, Any]]:
        """Create fallback recommendations if AI generation fails"""
        recommendations = []
        
        # Analyze GitHub activity
        github_data = activity_data.get('github', {})
        if github_data and github_data.get('activity'):
            languages = github_data['activity'].get('top_languages', {})
            if not languages:
                recommendations.append({
                    "type": "project",
                    "title": "Start Your First Repository",
                    "description": "Create your first GitHub repository with a simple project in your preferred programming language",
                    "difficulty": "beginner",
                    "time_estimate": "2-3 hours",
                    "resources": ["https://github.com", "https://docs.github.com/en/get-started"]
                })
        
        # Analyze Codeforces activity
        codeforces_data = activity_data.get('codeforces', {})
        if codeforces_data and codeforces_data.get('activity'):
            rating = codeforces_data['activity'].get('current_rating', 0)
            if rating < 1200:
                recommendations.append({
                    "type": "problem",
                    "title": "Solve Basic Algorithms Problems",
                    "description": "Practice fundamental algorithms and data structures on Codeforces",
                    "difficulty": "beginner",
                    "time_estimate": "1 hour daily",
                    "resources": ["https://codeforces.com/problemset"]
                })
        
        # Add domain-specific recommendations
        if "web" in domain.lower():
            recommendations.append({
                "type": "project",
                "title": "Build a Full-Stack Web Application",
                "description": f"Create a complete web application to enhance your {domain} skills",
                "difficulty": "intermediate",
                "time_estimate": "2-4 weeks",
                "resources": ["https://developer.mozilla.org", "https://reactjs.org"]
            })
        
        # Ensure we have at least some recommendations
        if not recommendations:
            recommendations = [
                {
                    "type": "learning",
                    "title": "Master Data Structures and Algorithms",
                    "description": "Build a strong foundation in computer science fundamentals",
                    "difficulty": "intermediate",
                    "time_estimate": "3-6 months",
                    "resources": ["https://leetcode.com", "https://codeforces.com"]
                },
                {
                    "type": "project", 
                    "title": "Build a Portfolio Project",
                    "description": "Create a project that showcases your skills in your domain of interest",
                    "difficulty": "intermediate",
                    "time_estimate": "2-4 weeks",
                    "resources": ["https://github.com"]
                }
            ]
        
        return recommendations

# API Endpoints
@api_router.post("/analyze-profile")
async def analyze_user_profile(request: AnalyzeProfileRequest):
    """Analyze user profile across platforms and generate AI recommendations"""
    try:
        activity_data = {}
        
        # Fetch data from each platform
        if request.github_username:
            try:
                github_stats = await PlatformDataFetcher.fetch_github_stats(request.github_username)
                activity_data['github'] = github_stats
            except Exception as e:
                activity_data['github'] = {'error': str(e)}
        
        if request.leetcode_username:
            try:
                leetcode_stats = await PlatformDataFetcher.fetch_leetcode_stats(request.leetcode_username)
                activity_data['leetcode'] = leetcode_stats
            except Exception as e:
                activity_data['leetcode'] = {'error': str(e)}
        
        if request.codeforces_username:
            try:
                codeforces_stats = await PlatformDataFetcher.fetch_codeforces_stats(request.codeforces_username)
                activity_data['codeforces'] = codeforces_stats
            except Exception as e:
                activity_data['codeforces'] = {'error': str(e)}
        
        # Generate AI recommendations
        recommendations = await AIRecommendationEngine.generate_recommendations(
            activity_data, request.goal, request.domain
        )
        
        # Store in database
        user_profile = UserProfile(
            github_username=request.github_username,
            leetcode_username=request.leetcode_username, 
            codeforces_username=request.codeforces_username,
            last_analyzed=datetime.now(timezone.utc)
        )
        
        # Prepare for MongoDB storage
        profile_dict = user_profile.dict()
        profile_dict['created_at'] = profile_dict['created_at'].isoformat()
        profile_dict['last_analyzed'] = profile_dict['last_analyzed'].isoformat()
        
        await db.user_profiles.insert_one(profile_dict)
        
        # Store recommendations
        ai_recommendation = AIRecommendation(
            user_id=user_profile.id,
            recommendations=recommendations
        )
        
        rec_dict = ai_recommendation.dict()
        rec_dict['generated_at'] = rec_dict['generated_at'].isoformat()
        
        await db.ai_recommendations.insert_one(rec_dict)
        
        return {
            'user_id': user_profile.id,
            'activity_data': activity_data,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing profile: {str(e)}")

@api_router.get("/user/{user_id}")
async def get_user_analysis(user_id: str):
    """Get stored user analysis and recommendations"""
    try:
        # Get user profile
        profile = await db.user_profiles.find_one({'id': user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get latest recommendations
        recommendations = await db.ai_recommendations.find_one(
            {'user_id': user_id}, 
            sort=[('generated_at', -1)]
        )
        
        return {
            'profile': profile,
            'recommendations': recommendations['recommendations'] if recommendations else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving user data: {str(e)}")

@api_router.get("/")
async def root():
    return {"message": "AI Student Activity Recommender API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()