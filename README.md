# AI Newspaper Agent

A browser-based application that automates the journalistic process through a structured three-stage LLM pipeline. The system accepts a user-provided topic, conducts research using DeepSeek, generates an article draft using OpenAI, and produces a polished final version using Google Gemini.

## 🎯 Project Vision

To create an interactive platform that demonstrates the capabilities of multiple LLMs working in sequence to produce high-quality journalistic content, while providing users with insight into each step of the automated writing process.

## 🏗️ System Architecture

### Three-Stage Pipeline

1. **Research Stage (DeepSeek)**: Comprehensive topic research and fact-gathering
2. **Draft Stage (OpenAI)**: Initial article creation based on research
3. **Edit Stage (Google Gemini)**: Final polishing and publication-ready formatting

### Technical Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3
- **Backend**: Python 3.10+, FastAPI, Uvicorn ASGI server
- **LLM Orchestration**: LangChain
- **LLM Providers**: OpenAI GPT-4, DeepSeek Chat, Google Gemini Pro

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- API keys for OpenAI, DeepSeek, and Google Gemini

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_newspaper_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4/GPT-3.5 | Yes |
| `DEEPSEEK_API_KEY` | DeepSeek API key for research | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key for editing | Yes |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |
| `DEBUG` | Debug mode (default: False) | No |

### API Key Setup

1. **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **DeepSeek**: Get your API key from [DeepSeek Platform](https://platform.deepseek.com/)
3. **Google Gemini**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 📖 Usage

1. **Enter a Topic**: Input any topic you'd like to write about
2. **Select Length**: Choose from Short (800 words), Medium (1200 words), or Long (1500 words)
3. **Generate Article**: Click "Generate Article" to start the three-stage pipeline
4. **View Results**: Watch as each stage completes and displays its output

### Example Topics

- "Artificial Intelligence in Healthcare"
- "Climate Change Solutions"
- "Space Exploration Advances"
- "Renewable Energy Trends"
- "Cybersecurity in 2024"

## 🎨 Features

### Modern Web Interface
- Responsive Bootstrap 5.3 design
- Real-time progress tracking
- Interactive stage-by-stage results display
- Mobile-friendly layout

### LLM Orchestration
- Sequential pipeline execution
- Error handling and fallback mechanisms
- Processing time tracking
- Full transparency in each stage

### Educational Value
- View intermediate processing steps
- Understand each LLM's role
- Learn about automated journalism workflows

## 🔍 API Endpoints

### `GET /`
Serves the main application interface.

### `POST /generate-article`
Generates a newspaper article using the three-stage pipeline.

**Request Body:**
```json
{
  "topic": "string",
  "max_length": 1200
}
```

**Response:**
```json
{
  "topic": "string",
  "research_stage": {
    "status": "success|error|skipped",
    "message": "string",
    "research_data": "string",
    "llm_used": "string"
  },
  "draft_stage": {
    "status": "success|error|skipped",
    "message": "string",
    "draft_content": "string",
    "llm_used": "string"
  },
  "final_stage": {
    "status": "success|error|skipped",
    "message": "string",
    "final_content": "string",
    "llm_used": "string"
  },
  "processing_time": 45.67
}
```

### `GET /health`
Health check endpoint.

## 🛠️ Development

### Project Structure

```
ai_newspaper_agent/
├── main.py                 # FastAPI application entry point
├── newspaper_pipeline.py   # Core LLM orchestration logic
├── requirements.txt        # Python dependencies
├── env_example.txt        # Environment variables template
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── app.js         # Frontend JavaScript
└── README.md              # This file
```

### Adding New LLM Providers

1. Create a new LLM wrapper class in `newspaper_pipeline.py`
2. Add the new stage to the pipeline
3. Update the frontend to display the new stage
4. Add environment variable configuration

### Customizing the Pipeline

The pipeline can be easily extended by:
- Adding new stages
- Modifying existing prompts
- Changing LLM models
- Adding preprocessing/postprocessing steps

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all API keys are correctly set in the `.env` file
2. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
3. **Port Conflicts**: Change the port in the `.env` file if 8000 is already in use
4. **Rate Limiting**: Some APIs have rate limits; consider adding delays between requests

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your `.env` file for detailed error logging.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub

## 🔮 Future Enhancements

- [ ] Support for additional LLM providers
- [ ] Article templates and styles
- [ ] Export functionality (PDF, Word)
- [ ] User authentication and article history
- [ ] Real-time collaboration features
- [ ] Advanced prompt customization
- [ ] Multi-language support
