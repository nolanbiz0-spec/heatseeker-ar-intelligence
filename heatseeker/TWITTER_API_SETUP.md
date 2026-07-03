# Twitter API v2 Setup Guide for A&R Intelligence

## IMMEDIATE SETUP REQUIRED

### 1. Apply for Twitter API v2 Access
**URL:** https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api

**Application Details:**
- **Use Case:** Research / Academic
- **Description:** "Music industry A&R intelligence for emerging artist discovery and viral content monitoring for commercial talent acquisition at Interscope Records/UMG."

### 2. Create Twitter Developer Project
**URL:** https://developer.twitter.com/en/portal/dashboard

**Project Setup:**
- **Project Name:** "Heatseeker A&R Intelligence"
- **Use Case:** Research
- **Description:** "Real-time monitoring of viral music content and emerging artist discovery for A&R intelligence at major record label."

### 3. Generate Bearer Token
1. Go to your project settings in Twitter Developer Portal
2. Navigate to "Keys and tokens"
3. Generate "Bearer Token" for API v2 access
4. Copy the token (starts with 'AAAAAAAAAAAAAAAAA')
5. Keep this secure - it provides API access

### 4. Set Environment Variable
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export TWITTER_BEARER_TOKEN='your_bearer_token_here'

# Or set for current session:
export TWITTER_BEARER_TOKEN='AAAAAAAAAAAAAAAAAAAAAA...'
```

### 5. Install Dependencies
```bash
cd /Users/nolan/heatseeker
pip install httpx asyncio python-dotenv
```

### 6. Run the Monitoring System
```bash
cd /Users/nolan/heatseeker
python heatseeker/twitter_ar_monitoring.py
```

## TWITTER API v2 FEATURES FOR A&R

### Real-Time Capabilities:
- **Search recency:** Last 7 days of tweets
- **Rate limits:** 300 requests per 15 minutes (generous for monitoring)
- **Tweet fields:** Engagement metrics, user data, timestamps
- **Filtering:** Geographic, language, engagement thresholds
- **Expansions:** User profiles, referenced tweets

### A&R-Optimized Search Queries:
```
("my song went viral" OR "going viral" OR "blew up overnight") -is:retweet
("TikTok viral" OR "viral on TikTok") -is:retweet
("unsigned artist" OR "independent artist") ("viral" OR "trending") -is:retweet
("500 comments" OR "comments going crazy") -is:retweet
("A&R reached out" OR "label interest") -is:retweet
```

### Geographic Scene Monitoring:
```
("#ATLmusic" OR "#ATLunderground") ("unsigned" OR "independent") -is:retweet
("#NYCindiemusic" OR "#BKscene") ("new artist" OR "breakthrough") -is:retweet
("#UKdrill" OR "#Londonmusic") ("unsigned" OR "independent") -is:retweet
```

## MONITORING SERVICE FEATURES

### Real-Time Discovery:
- **15-minute monitoring intervals** (optimal for API limits)
- **Confidence scoring** based on viral + independence signals
- **Urgency classification:** IMMEDIATE / HIGH / MEDIUM / LOW
- **Heatseeker integration** for independence verification

### Alert System:
- **IMMEDIATE:** Viral + unsigned + engagement velocity (6-hour response window)
- **HIGH:** Strong viral signals or industry interest (24-48 hour window)
- **MEDIUM:** Emerging signals worth monitoring (1-week tracking)

### A&R Intelligence Categories:
1. **Viral Breakthrough** - "my song went viral" detection
2. **Engagement Velocity** - Your 500+ comments/hour insight
3. **Ken Carson Opportunities** - Post-album genre momentum
4. **Industry Signals** - Competitive intelligence 
5. **Geographic Scenes** - Regional hotspot monitoring

## PRODUCTION DEPLOYMENT

### Environment Setup:
```bash
# Set Twitter credentials
export TWITTER_BEARER_TOKEN='your_token_here'

# Optional: Custom Heatseeker URL
export HEATSEEKER_API_URL='http://localhost:8000'
```

### Run Continuous Monitoring:
```bash
# Start 24/7 monitoring service
python heatseeker/twitter_ar_monitoring.py

# Or run in background
nohup python heatseeker/twitter_ar_monitoring.py > twitter_monitoring.log 2>&1 &
```

### Integration with Heatseeker:
The system automatically cross-references Twitter discoveries with Heatseeker's independence verification system, providing complete A&R intelligence.

## BUSINESS JUSTIFICATION FOR TWITTER API

### A&R Use Case Description:
"Music industry A&R intelligence system for emerging artist discovery and viral content monitoring. Used by A&R representatives at major record labels to identify unsigned artists experiencing viral breakthrough moments on social media platforms, enabling rapid talent acquisition before competitive bidding situations develop."

### Commercial Value:
- **Early viral detection** = optimal deal terms
- **Independence verification** = viable signing targets  
- **Competitive intelligence** = market awareness
- **Geographic discovery** = regional talent identification

### Research Classification:
The system qualifies as "research" under Twitter's academic/commercial research category as it involves:
- Social media trend analysis
- Music industry market research  
- Artist discovery and talent identification
- Viral content pattern recognition

## API COSTS & LIMITS

### Twitter API v2 Pricing:
- **Basic tier:** $100/month for enhanced access
- **Research track:** Often free for academic institutions
- **Commercial research:** Varies based on usage

### Rate Limits:
- **300 requests per 15 minutes** (search endpoint)
- **15-minute monitoring intervals** = optimal usage
- **10 tweets per request** = efficient discovery

### Cost vs Value:
- **API cost:** $100-300/month
- **Single viral signing value:** $500K-5M+  
- **ROI:** 1 successful discovery pays for years of API access

This Twitter integration transforms Heatseeker into a comprehensive real-time A&R intelligence system with professional-grade viral detection capabilities.