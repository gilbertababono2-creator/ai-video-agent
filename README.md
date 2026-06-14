# AI Video Agent

AI Video Agent for generating and uploading faceless videos to **YouTube Shorts**, **TikTok**, and **Facebook Reels** with full automation.

## 🎯 Features

- **Video Generation**: Create 9:16 vertical videos with AI-powered content
- **Faceless Videos**: Stock footage, AI-generated visuals, animations, subtitles, voiceovers, and music
- **Multi-Platform Upload**: Automatically upload to YouTube Shorts, TikTok, and Facebook Reels
- **Metadata Management**: Platform-specific titles, captions, hashtags, and descriptions
- **Error Handling**: Graceful error handling with detailed logging
- **CLI Interface**: Command-line tools for easy operation

## 📋 MVP Scope

### Core Requirements
- ✅ Accept YouTube/TikTok/Reel links → download + clip segments
- ✅ Accept text prompt + optional reference images
- ✅ Generate/remix vertical 9:16 video (30s to 2+ minutes)
- ✅ Fully faceless: stock/AI clips, animations, subtitles, voiceover, music
- ✅ Auto-upload to TikTok, YouTube Shorts, and Facebook Reels
- ✅ Platform-specific metadata (title, caption, hashtags, description, privacy)

### Tech Stack
- **Python 3.9+**: Core language
- **FFmpeg + yt-dlp**: Download and video processing
- **MoviePy**: Video composition and rendering
- **OpenAI/Grok**: AI script generation
- **ElevenLabs**: Text-to-speech voiceovers
- **Flux/Runway**: AI visual generation
- **APIs**: 
  - YouTube Data API v3 (OAuth2)
  - TikTok Uploader (Playwright/cookies)
  - Facebook Graph API (Reels Publishing)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- FFmpeg installed (`apt-get install ffmpeg` or `brew install ffmpeg`)
- API keys for OpenAI, ElevenLabs, and respective platforms

### Installation

```bash
# Clone the repository
git clone https://github.com/gilbertababono2-creator/ai-video-agent.git
cd ai-video-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (if not already installed)
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

### Configuration

1. **Copy environment template**:
```bash
cp .env.example .env
```

2. **Fill in API keys** in `.env`:
```env
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
YOUTUBE_CLIENT_ID=your_id_here
YOUTUBE_CLIENT_SECRET=your_secret_here
FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

## 📖 Setup Guides

### YouTube Shorts Upload

1. **Get OAuth Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop application)
   - Download credentials as `youtube_credentials.json`
   - Place in project root

2. **Environment Variables**:
```env
YOUTUBE_CLIENT_ID=xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your_secret
```

### TikTok Upload

1. **Export Cookies**:
   - Install browser extension: [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndcbgoxzmacileapblaefnfofbc)
   - Login to TikTok in browser
   - Export cookies using extension
   - Save as `temp/tiktok_cookies.json`

2. **Environment Variables**:
```env
TIKTOK_COOKIES_PATH=./temp/tiktok_cookies.json
```

### Facebook Reels Upload

1. **Get Page Access Token**:
   - Go to [Meta Business Suite](https://business.facebook.com/)
   - Select your business account
   - Navigate to Settings → Accounts → Facebook Apps
   - Create or select your app
   - Go to Roles → Admin Roles
   - Generate a long-lived Page Access Token

2. **Get Page ID**:
   - Go to your Facebook page
   - Settings → Page Info
   - Copy your Page ID

3. **Environment Variables**:
```env
FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

## 📝 Usage

### Command-Line Interface

```bash
# Basic video generation
python -m agent.cli generate-and-upload \
  --prompt "Create a 45-second motivational video about AI tools" \
  --duration 45 \
  --output videos/output.mp4

# With uploads to all platforms
python -m agent.cli generate-and-upload \
  --prompt "Top 5 AI Tools 2026" \
  --urls "https://example.com/video.mp4" \
  --duration 45 \
  --youtube-title "These 5 AI Tools Will Change 2026 🔥 #Shorts" \
  --youtube-description "Check out the most amazing AI tools..." \
  --tiktok-caption "Mind-blowing AI tools! #AI #Tech" \
  --facebook-description "Epic AI tools you need in 2026" \
  --hashtags "#AI #Shorts #Reels #Tech" \
  --upload-youtube \
  --upload-tiktok \
  --upload-facebook

# Run demo
python -m agent.cli demo
```

### Python API

```python
from agent.video_generator import VideoGenerator
from agent.uploader import YouTubeUploader

# Generate video
generator = VideoGenerator()
video_path = generator.create_from_images(['image1.jpg', 'image2.jpg'])

# Add text
video_with_text = generator.add_text_overlay(video_path, "Your Text Here")

# Upload to YouTube
uploader = YouTubeUploader()
uploader.authenticate()
result = uploader.upload(
    video_path=video_with_text,
    title="My Video Title",
    description="Video description",
)
```

## 📁 Project Structure

```
ai-video-agent/
├── agent/
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── logger.py              # Logging setup
│   ├── cli.py                 # Command-line interface
│   ├── video_generator.py     # Core video generation
│   └── uploader/
│       ├── __init__.py
│       ├── youtube.py         # YouTube upload module
│       ├── tiktok.py          # TikTok upload module
│       └── facebook.py        # Facebook upload module
├── output/                    # Generated videos
├── downloads/                 # Downloaded sources
├── temp/                      # Temporary files
├── logs/                      # Application logs
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## ⚠️ Important Warnings

### Terms of Service
- **YouTube**: Automated uploads must comply with YouTube's automation policies
- **TikTok**: Cookie-based uploading may violate Terms of Service; use official API when available
- **Facebook**: Ensure you own the content or have proper licensing

### Rate Limits
- **YouTube Data API**: 10,000 quota units/day per project
- **TikTok**: Implement delays between uploads to avoid temporary bans
- **Facebook Graph API**: Subject to rate limiting; handle 429 responses gracefully

### Best Practices
- Always test with small videos first
- Implement proper error handling and retry logic
- Monitor quota usage and API responses
- Use appropriate delays between uploads
- Ensure content is original or properly licensed
- Keep API credentials secure (never commit .env)

## 🐛 Troubleshooting

### FFmpeg not found
```bash
# Install FFmpeg
brew install ffmpeg          # macOS
sudo apt-get install ffmpeg  # Linux
choco install ffmpeg         # Windows
```

### YouTube authentication fails
```bash
# Re-authenticate
rm youtube_token.pickle
python -m agent.cli generate-and-upload --prompt "test" --upload-youtube
```

### TikTok cookies expired
```bash
# Export fresh cookies
# Use browser extension to get new tiktok_cookies.json
cp tiktok_cookies.json temp/tiktok_cookies.json
```

### Facebook token invalid
```bash
# Get new long-lived token from Meta Business Suite
# Update FACEBOOK_PAGE_ACCESS_TOKEN in .env
```

## 📊 Pipeline Architecture

```
┌─────────────┐
│   Input     │  (prompt, URLs, metadata)
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Download Sources   │  (yt-dlp)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  AI Script/Plan     │  (OpenAI/Grok)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Generate Visuals    │  (Flux/Runway/Stock)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Video Composition   │  (MoviePy/FFmpeg)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Add Voiceover       │  (ElevenLabs/TTS)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Add Subtitles       │  (MoviePy)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Add Music/Effects   │  (FFmpeg)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Final Rendering     │  (9:16 MP4)
└──────┬──────────────┘
       │
       ▼
┌────────────────────��────────────┐
│   Multi-Platform Upload         │
├─────────────────────────────────┤
│ ├─ YouTube Shorts (Data API)    │
│ ├─ TikTok (tiktok-uploader)     │
│ └─ Facebook Reels (Graph API)   │
└─────────────────────────────────┘
       │
       ▼
┌──────────────┐
│   Output     │  (JSON log, URLs, IDs)
└──────────────┘
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- FFmpeg for video processing
- YouTube, TikTok, and Facebook for their APIs
- MoviePy for Python video composition
- OpenAI and ElevenLabs for AI capabilities

## 📧 Support

For issues, questions, or suggestions:
- Open a GitHub Issue
- Check existing documentation
- Review error logs in `logs/` directory

---

**⚡ Status**: MVP Development in Progress

**Current Phase**: Foundation & Project Setup

**Next Steps**:
1. Core video generation pipeline
2. YouTube Shorts upload integration
3. TikTok upload integration
4. Facebook Reels upload integration
5. Full AI orchestration
