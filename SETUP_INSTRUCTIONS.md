# AI Newspaper Agent - Setup Instructions

## 🎉 Project Complete!

Your AI Newspaper Agent is ready to use! Here's how to get it running:

## 📋 Quick Setup Checklist

### 1. Install Dependencies
```bash
cd ai_newspaper_agent
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Add your API keys to the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 3. Get API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up/Login to your account
3. Create a new API key
4. Copy the key to your `.env` file

#### DeepSeek API Key
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up/Login to your account
3. Navigate to API section
4. Create a new API key
5. Copy the key to your `.env` file

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign up/Login with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### 4. Start the Application

#### Option A: Using the startup script (Recommended)
```bash
python3 start.py
```

#### Option B: Direct execution
```bash
python3 main.py
```

#### Option C: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Application
Open your browser and navigate to: **http://localhost:8000**

## 🧪 Testing the Setup

Run the test script to verify everything is working:
```bash
python3 test_app.py
```

This will:
- ✅ Check all imports
- ✅ Verify API key configuration
- ✅ Test the complete pipeline (if API keys are configured)

## 🎯 How to Use

1. **Enter a Topic**: Type any topic you want to write about
2. **Select Length**: Choose from Short (800), Medium (1200), or Long (1500) words
3. **Generate Article**: Click the "Generate Article" button
4. **Watch the Magic**: See the three-stage pipeline in action:
   - 🔍 **Research Stage**: DeepSeek gathers comprehensive information
   - ✍️ **Draft Stage**: OpenAI creates the initial article
   - ✨ **Edit Stage**: Google Gemini polishes the final version

## 📁 Project Structure

```
ai_newspaper_agent/
├── main.py                 # FastAPI application
├── newspaper_pipeline.py   # LLM orchestration logic
├── start.py               # Convenient startup script
├── test_app.py            # Test and validation script
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables template
├── README.md             # Complete documentation
├── SETUP_INSTRUCTIONS.md # This file
├── templates/
│   └── index.html        # Main web interface
└── static/
    ├── css/
    │   └── style.css     # Custom styling
    └── js/
        └── app.js        # Frontend JavaScript
```

## 🔧 Configuration Options

### Environment Variables
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: False)

### Customization
- Modify prompts in `newspaper_pipeline.py`
- Adjust styling in `static/css/style.css`
- Enhance UI in `templates/index.html`

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **API key errors**
   - Double-check your `.env` file
   - Ensure API keys are valid and have sufficient credits

3. **Port already in use**
   - Change the port in `.env` file
   - Or kill the process using port 8000

4. **Rate limiting**
   - Some APIs have rate limits
   - Wait a few minutes between requests

### Getting Help

1. Check the main `README.md` for detailed documentation
2. Run `python3 test_app.py` to diagnose issues
3. Check the console output for error messages

## 🎉 You're All Set!

Your AI Newspaper Agent is now ready to create amazing articles using the power of three different LLMs working in sequence. Enjoy exploring the future of automated journalism!

## 🚀 Next Steps

- Try different topics and see how each LLM contributes
- Experiment with different article lengths
- Customize the prompts for your specific needs
- Share your generated articles and get feedback

Happy writing! 📰✨
