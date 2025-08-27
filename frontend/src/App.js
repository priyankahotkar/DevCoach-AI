import React, { useState } from 'react';
import './App.css';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { toast } from 'sonner';
import { Toaster } from './components/ui/sonner';
import { 
  Github, 
  Code2, 
  Trophy, 
  Target, 
  BookOpen, 
  Zap,
  Users,
  Star,
  GitBranch,
  Calendar,
  TrendingUp,
  Lightbulb,
  CheckCircle2,
  Clock,
  ExternalLink,
  User,
  Activity,
  Award
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [formData, setFormData] = useState({
    github_username: '',
    leetcode_username: '',
    codeforces_username: '',
    goal: 'Improve programming skills',
    domain: 'General Software Development'
  });
  
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAnalyze = async () => {
    if (!formData.github_username && !formData.leetcode_username && !formData.codeforces_username) {
      toast.error('Please enter at least one username');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/analyze-profile`, {
        github_username: formData.github_username || null,
        leetcode_username: formData.leetcode_username || null,
        codeforces_username: formData.codeforces_username || null,
        goal: formData.goal,
        domain: formData.domain
      });

      setAnalysisResult(response.data);
      toast.success('Analysis complete! Check your personalized recommendations below.');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Failed to analyze profile. Please check your usernames and try again.');
    } finally {
      setLoading(false);
    }
  };

  const ActivityCard = ({ platform, data, icon: Icon }) => {
    if (data.error) {
      return (
        <Card className="border-red-200 bg-red-50">
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <Icon className="h-5 w-5 text-red-600" />
              <CardTitle className="text-red-800">{platform}</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-red-600 text-sm">Error: {data.error}</p>
          </CardContent>
        </Card>
      );
    }

    const renderPlatformStats = () => {
      switch (platform) {
        case 'GitHub':
          return (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{data.profile?.public_repos || 0}</div>
                  <div className="text-sm text-gray-600">Repositories</div>
                </div>
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{data.activity?.total_stars || 0}</div>
                  <div className="text-sm text-gray-600">Total Stars</div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Top Languages</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(data.activity?.top_languages || {}).map(([lang, count]) => (
                    <Badge key={lang} variant="secondary" className="text-xs">
                      {lang} ({count})
                    </Badge>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Recent Activity</h4>
                <p className="text-sm text-gray-600">
                  {data.activity?.recent_commits || 0} commits in recent activity
                </p>
              </div>
            </div>
          );
        
        case 'Codeforces':
          return (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{data.activity?.current_rating || 0}</div>
                  <div className="text-sm text-gray-600">Current Rating</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{data.activity?.problems_solved || 0}</div>
                  <div className="text-sm text-gray-600">Problems Solved</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Rank:</span> {data.profile?.rank || 'unrated'}
                </div>
                <div>
                  <span className="font-medium">Contests:</span> {data.activity?.contests_participated || 0}
                </div>
              </div>
            </div>
          );
        
        case 'LeetCode':
          return (
            <div className="space-y-4">
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-sm text-gray-600">
                  {data.activity?.note || 'LeetCode data integration pending'}
                </div>
              </div>
            </div>
          );
        
        default:
          return <div>No data available</div>;
      }
    };

    return (
      <Card className="hover:shadow-lg transition-shadow duration-300">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon className="h-5 w-5 text-gray-700" />
              <CardTitle className="text-gray-900">{platform}</CardTitle>
            </div>
            <Badge variant="outline" className="text-xs">
              @{data.profile?.handle || data.profile?.username || formData[`${platform.toLowerCase()}_username`]}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {renderPlatformStats()}
        </CardContent>
      </Card>
    );
  };

  const RecommendationCard = ({ recommendation, index }) => {
    const getTypeIcon = (type) => {
      switch (type) {
        case 'project': return <GitBranch className="h-4 w-4" />;
        case 'problem': return <Code2 className="h-4 w-4" />;
        case 'skill': return <Zap className="h-4 w-4" />;
        case 'learning': return <BookOpen className="h-4 w-4" />;
        default: return <Lightbulb className="h-4 w-4" />;
      }
    };

    const getDifficultyColor = (difficulty) => {
      switch (difficulty) {
        case 'beginner': return 'bg-green-100 text-green-800';
        case 'intermediate': return 'bg-yellow-100 text-yellow-800';
        case 'advanced': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <Card className="hover:shadow-lg transition-all duration-300 border-l-4 border-l-blue-500">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              {getTypeIcon(recommendation.type)}
              <CardTitle className="text-lg text-gray-900">{recommendation.title}</CardTitle>
            </div>
            <div className="flex flex-col gap-2 items-end">
              <Badge className={getDifficultyColor(recommendation.difficulty)}>
                {recommendation.difficulty}
              </Badge>
              {recommendation.time_estimate && (
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  {recommendation.time_estimate}
                </div>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-700 leading-relaxed">{recommendation.description}</p>
          
          {recommendation.resources && recommendation.resources.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                <ExternalLink className="h-4 w-4" />
                Resources
              </h4>
              <div className="flex flex-wrap gap-2">
                {recommendation.resources.map((resource, idx) => (
                  <a
                    key={idx}
                    href={resource}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 px-2 py-1 rounded-md transition-colors"
                  >
                    {resource}
                  </a>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
              <Target className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Student Journey Guide</h1>
              <p className="text-gray-600">Personalized recommendations based on your coding activity</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!analysisResult ? (
          /* Input Form */
          <div className="max-w-3xl mx-auto">
            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader className="text-center pb-6">
                <CardTitle className="text-2xl text-gray-900">Connect Your Profiles</CardTitle>
                <CardDescription className="text-lg">
                  Enter your usernames to get AI-powered recommendations tailored to your coding journey
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-4">
                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <Github className="h-4 w-4" />
                      GitHub Username
                    </label>
                    <Input
                      placeholder="octocat"
                      value={formData.github_username}
                      onChange={(e) => handleInputChange('github_username', e.target.value)}
                      className="bg-white border-gray-200"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <Code2 className="h-4 w-4" />
                      LeetCode Username
                    </label>
                    <Input
                      placeholder="leetcoder"
                      value={formData.leetcode_username}
                      onChange={(e) => handleInputChange('leetcode_username', e.target.value)}
                      className="bg-white border-gray-200"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <Trophy className="h-4 w-4" />
                      Codeforces Username
                    </label>
                    <Input
                      placeholder="tourist"
                      value={formData.codeforces_username}
                      onChange={(e) => handleInputChange('codeforces_username', e.target.value)}
                      className="bg-white border-gray-200"
                    />
                  </div>
                </div>

                <Separator />

                <div className="grid gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Your Goal</label>
                    <Input
                      placeholder="e.g., Get better at algorithms, Learn web development"
                      value={formData.goal}
                      onChange={(e) => handleInputChange('goal', e.target.value)}
                      className="bg-white border-gray-200"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-700">Domain of Interest</label>
                    <Input
                      placeholder="e.g., Web Development, Machine Learning, Mobile Apps"
                      value={formData.domain}
                      onChange={(e) => handleInputChange('domain', e.target.value)}
                      className="bg-white border-gray-200"
                    />
                  </div>
                </div>

                <Button 
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium py-3 text-lg"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Analyzing Your Journey...
                    </>
                  ) : (
                    <>
                      <Zap className="h-5 w-5 mr-2" />
                      Generate AI Recommendations
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        ) : (
          /* Results */
          <div className="space-y-8">
            {/* Header with restart button */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">Your Personalized Analysis</h2>
                <p className="text-gray-600 mt-1">Based on your activity across platforms</p>
              </div>
              <Button 
                onClick={() => {
                  setAnalysisResult(null);
                  setFormData({
                    github_username: '',
                    leetcode_username: '',
                    codeforces_username: '',
                    goal: 'Improve programming skills',
                    domain: 'General Software Development'
                  });
                }}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Target className="h-4 w-4" />
                New Analysis
              </Button>
            </div>

            <Tabs defaultValue="activity" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="activity" className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Activity Overview
                </TabsTrigger>
                <TabsTrigger value="recommendations" className="flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  AI Recommendations
                </TabsTrigger>
              </TabsList>

              <TabsContent value="activity" className="space-y-6">
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {analysisResult.activity_data.github && (
                    <ActivityCard 
                      platform="GitHub" 
                      data={analysisResult.activity_data.github} 
                      icon={Github}
                    />
                  )}
                  {analysisResult.activity_data.leetcode && (
                    <ActivityCard 
                      platform="LeetCode" 
                      data={analysisResult.activity_data.leetcode} 
                      icon={Code2}
                    />
                  )}
                  {analysisResult.activity_data.codeforces && (
                    <ActivityCard 
                      platform="Codeforces" 
                      data={analysisResult.activity_data.codeforces} 
                      icon={Trophy}
                    />
                  )}
                </div>
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-6">
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Your Personalized Roadmap</h3>
                  <p className="text-gray-600">AI-generated recommendations to accelerate your progress</p>
                </div>
                
                <div className="grid gap-6">
                  {analysisResult.recommendations?.map((recommendation, index) => (
                    <RecommendationCard 
                      key={index} 
                      recommendation={recommendation} 
                      index={index}
                    />
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;