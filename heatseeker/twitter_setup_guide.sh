#!/bin/bash
# Twitter API v2 Application Script - Complete Setup Guide
# Run this to get step-by-step Twitter API access for A&R intelligence

echo "🐦 TWITTER API v2 ACCESS - COMPLETE SETUP GUIDE"
echo "==============================================="
echo ""
echo "📋 STEP-BY-STEP TWITTER API APPLICATION:"
echo ""

echo "1️⃣ SIGN UP FOR TWITTER DEVELOPER ACCOUNT"
echo "----------------------------------------"
echo "🔗 Go to: https://developer.twitter.com/en/apply/user"
echo ""
echo "📝 Account Details to Use:"
echo "   • Use your existing Twitter account (@nolanbiz0 or create new)"
echo "   • Organization: Interscope Records / UMG"
echo "   • Country: United States"
echo "   • Use case: Academic research / Commercial research"
echo ""
echo "⏰ This takes 2-3 minutes to complete"
echo ""
read -p "Press Enter when you've completed Step 1..."
echo ""

echo "2️⃣ CREATE DEVELOPER PROJECT"
echo "---------------------------"
echo "🔗 Go to: https://developer.twitter.com/en/portal/dashboard"
echo ""
echo "📝 Project Setup:"
echo "   • Project Name: 'Heatseeker AR Intelligence'"
echo "   • Use Case: 'Making a bot' or 'Academic research'"
echo "   • Description: 'Music industry A&R intelligence system'"
echo ""
echo "🎯 Detailed Description to Copy/Paste:"
echo "--------------------------------------"
cat << 'EOF'
Music industry A&R intelligence system for emerging artist discovery and viral content monitoring. This system monitors Twitter for real-time signals of unsigned artists experiencing viral breakthrough moments on platforms like TikTok, enabling A&R representatives at record labels to identify and contact promising talent before competitive bidding situations develop. The research involves social media trend analysis, music industry market research, and viral content pattern recognition for commercial talent acquisition.

Key research objectives:
- Real-time detection of viral music content mentions
- Independent/unsigned artist identification and verification  
- Geographic music scene monitoring and regional talent discovery
- Competitive intelligence on industry interest in emerging artists
- Engagement velocity analysis for breakthrough moment identification

This academic/commercial research supports data-driven A&R decision making in the music industry.
EOF
echo ""
echo "⏰ This takes 3-5 minutes to complete"
echo ""
read -p "Press Enter when you've created the project..."
echo ""

echo "3️⃣ APPLY FOR ELEVATED ACCESS (ESSENTIAL TIER)"
echo "---------------------------------------------"
echo "🔗 In your project dashboard, click 'Apply for Elevated'"
echo ""
echo "📋 Application Questions & Answers:"
echo ""
echo "Q: How will you use the Twitter API or Twitter Data?"
echo "A: Copy this response:"
echo "---"
cat << 'EOF'
I will use the Twitter API v2 to monitor real-time social media conversations for music industry A&R intelligence. Specifically:

1. Search for tweets containing viral music breakthrough signals ("my song went viral", "TikTok blew up", etc.)
2. Identify unsigned/independent artists experiencing sudden popularity increases
3. Monitor geographic music scenes and regional talent emergence  
4. Track competitive intelligence signals (A&R interest, label meetings, etc.)
5. Analyze engagement velocity patterns that indicate breakthrough moments

The system will make approximately 200-300 API calls per day using the search/recent endpoint with 15-minute intervals. Data will be used for commercial talent acquisition research at a major record label (Interscope Records/UMG), helping identify promising unsigned artists before competitive situations develop.

No data will be stored permanently - only real-time analysis for immediate A&R decision making.
EOF
echo ""
echo "Q: Are you planning to analyze Twitter data?"
echo "A: Yes - Real-time analysis of viral music trends and artist breakthrough signals"
echo ""
echo "Q: Will your app use Tweet, Retweet, Like, Follow, or Direct Message functionality?"
echo "A: No - Read-only access for monitoring and analysis only"
echo ""
echo "Q: Do you plan to display Tweets or aggregate data about Twitter content outside Twitter?"
echo "A: Yes - Internal A&R dashboard showing viral artist alerts and breakthrough signals"
echo ""
echo "⏰ This application review takes 1-2 business days"
echo ""
read -p "Press Enter when you've submitted the Elevated Access application..."
echo ""

echo "4️⃣ GENERATE API KEYS (AFTER APPROVAL)"
echo "-------------------------------------"
echo "🔗 In your project dashboard: Keys and Tokens section"
echo ""
echo "🔑 Generate These Keys:"
echo "   • Bearer Token (most important for API v2)"
echo "   • API Key and Secret (backup authentication)"
echo "   • Access Token and Secret (if needed later)"
echo ""
echo "⚠️  SECURITY: Save these keys securely - they won't be shown again!"
echo ""
read -p "Press Enter when you've generated your API keys..."
echo ""

echo "5️⃣ SET UP ENVIRONMENT VARIABLES"
echo "-------------------------------"
echo "📝 Add this to your shell profile (~/.zshrc or ~/.bashrc):"
echo ""
echo "export TWITTER_BEARER_TOKEN='your_bearer_token_here'"
echo "export TWITTER_API_KEY='your_api_key_here'"
echo "export TWITTER_API_SECRET='your_api_secret_here'"
echo ""
echo "💻 Or set for current session:"
echo "export TWITTER_BEARER_TOKEN='AAAAAAAAAA...your_token'"
echo ""
read -p "Press Enter when you've set your environment variables..."
echo ""

echo "6️⃣ TEST THE INTEGRATION"
echo "-----------------------"
echo "🧪 Test the Twitter integration:"
echo ""
echo "cd /Users/nolan/heatseeker"
echo "python heatseeker/twitter_ar_monitoring.py"
echo ""
echo "✅ If successful, you'll see:"
echo "   '🐦 TWITTER API v2 A&R INTELLIGENCE SETUP'"
echo "   '✅ Twitter API Bearer Token found'"
echo "   '🚀 Starting A&R monitoring service...'"
echo ""

echo ""
echo "🎉 CONGRATULATIONS!"
echo "==================="
echo "Your Twitter A&R Intelligence system will be monitoring:"
echo ""
echo "🔍 Viral breakthrough moments in real-time"
echo "🎵 Unsigned artist discovery via social signals"  
echo "🌍 Geographic scene monitoring (Atlanta, NYC, LA, UK, etc.)"
echo "📊 Engagement velocity tracking (500+ comments/hour alerts)"
echo "🏢 Competitive intelligence (A&R interest, label meetings)"
echo "🎯 Post-Ken Carson rage rap opportunities"
echo ""
echo "💰 BUSINESS IMPACT:"
echo "   • API Cost: ~$100-300/month"
echo "   • Single Viral Signing Value: $500K-5M+"
echo "   • ROI: One discovery pays for years of monitoring"
echo ""
echo "🚀 The system runs 24/7 with 15-minute monitoring cycles"
echo "   and integrates with your existing Heatseeker intelligence."
echo ""
echo "Ready to find the next breakthrough artist before your competition! 🎤"