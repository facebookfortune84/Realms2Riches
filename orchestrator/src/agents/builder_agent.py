import os
import json
import re
from datetime import datetime
from typing import Dict, Any
from orchestrator.src.core.config import settings
from orchestrator.src.logging.logger import get_logger
from orchestrator.src.core.models import Project

from orchestrator.src.core.llm_provider import llm_provider

logger = get_logger("BUILDER_AGENT")

class BuilderAgent:
    """
    The 'Famous Mode' agent capable of generating full-stack applications
    from natural language prompts.
    """
    
    def __init__(self, projects_root: str = "projects/generated"):
        self.projects_root = projects_root
        os.makedirs(self.projects_root, exist_ok=True)
        
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyzes the user's prompt to determine the app's architecture using LLM.
        """
        logger.info(f"Analyzing prompt: {prompt}")
        
        system_prompt = """
        You are a senior software architect. Analyze the user's request and output a JSON specification for a full-stack application.
        The JSON must follow this structure:
        {
            "name": "Project Name",
            "slug": "project-slug",
            "description": "Short description",
            "tech_stack": {
                "frontend": "react",
                "backend": "fastapi",
                "db": "postgres",
                "features": ["feature1", "feature2"]
            }
        }
        Common features: stripe_payments, product_catalog, user_auth, ai_integration, crypto_tracking.
        Return ONLY valid JSON.
        """
        
        try:
            response = llm_provider.generate_text(f"{system_prompt}\n\nUser Request: {prompt}")
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                spec = json.loads(json_match.group())
                logger.info(f"LLM generated spec: {spec['name']}")
                return spec
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")

        # Fallback to simple keyword matching
        logger.info("Falling back to keyword matching.")
        tech_stack = {
            "frontend": "react",
            "backend": "fastapi",
            "db": "postgres",
            "features": []
        }
        
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ["ecommerce", "store", "subscription", "payment", "stripe"]):
            tech_stack["features"].append("stripe_payments")
        
        if "crypto" in prompt_lower:
            tech_stack["features"].append("crypto_tracking")
            
        if "blog" in prompt_lower:
            tech_stack["features"].append("cms")
            
        return {
            "name": f"Project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "slug": f"project-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "description": prompt,
            "tech_stack": tech_stack
        }

    async def generate_project(self, project: Project, funnel_spec: Dict[str, Any] = None) -> str:
        """
        Generates the code for the given project.
        Returns the path to the generated project.
        """
        project_path = os.path.join(self.projects_root, project.slug)
        os.makedirs(project_path, exist_ok=True)
        
        logger.info(f"🏗️  Generating project '{project.name}' at {project_path}...")
        
        # 1. Structure Scaffolding
        await self._scaffold_structure(project_path)
        
        # 2. Backend Generation
        await self._generate_backend(project_path, project)
        
        # 3. Frontend Generation
        if funnel_spec:
            await self._generate_funnel_frontend(project_path, project, funnel_spec)
        else:
            await self._generate_frontend(project_path, project)
        
        # 4. Configuration (Env, Docker)
        await self._generate_config(project_path, project)
        
        return project_path

    async def _generate_funnel_frontend(self, base_path: str, project: Project, funnel_spec: Dict[str, Any]):
        """
        Generates a specific high-converting funnel frontend based on the Architect's spec.
        """
        src_path = os.path.join(base_path, "frontend", "src")
        
        # 1. Package.json & basic setup (reuse existing logic but tailored)
        pkg_json = {
            "name": project.slug,
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "react-scripts": "5.0.1",
                "framer-motion": "^10.16.4", # For high-end animations
                "lucide-react": "^0.292.0", # Icons
                "axios": "^1.6.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        with open(os.path.join(base_path, "frontend", "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg_json, f, indent=2)

        # 2. Components
        os.makedirs(os.path.join(src_path, "pages"), exist_ok=True)
        os.makedirs(os.path.join(src_path, "components"), exist_ok=True)

        # Landing Page
        landing_spec = next((p for p in funnel_spec.get("pages", []) if p["type"] == "landing_page"), {})
        landing_jsx = f"""
import React from 'react';
import {{ useNavigate }} from 'react-router-dom';
import {{ ArrowRight, CheckCircle }} from 'lucide-react';

const LandingPage = () => {{
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      {{/* HERO SECTION */}}
      <section className="bg-white py-20 px-6 text-center shadow-sm">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl font-extrabold tracking-tight mb-6 leading-tight text-indigo-900">
            {landing_spec.get('headline', 'Headline Missing')}
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            {landing_spec.get('subheadline', 'Subheadline Missing')}
          </p>
          <button 
            onClick={{() => navigate('/upsell')}}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-10 rounded-full text-lg shadow-xl transform transition hover:scale-105 flex items-center justify-center mx-auto"
          >
            {landing_spec.get('cta_text', 'Get Access Now')} <ArrowRight className="ml-2" />
          </button>
        </div>
      </section>

      {{/* BULLETS / STACK */}}
      <section className="py-16 px-6">
        <div className="max-w-3xl mx-auto bg-white p-10 rounded-2xl shadow-lg border border-gray-100">
          <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">Here is What You Get:</h2>
          <div className="space-y-4">
            {(landing_spec.get('bullets', []) or ['Benefit 1', 'Benefit 2']).map((bullet, i) => (
                f'<div key={{i}} className="flex items-start"><CheckCircle className="text-green-500 mr-3 mt-1 flex-shrink-0" /><div><span className="font-semibold text-lg">{{bullet}}</span></div></div>'
            )).replace("'", '"')}
          </div>
        </div>
      </section>
    </div>
  );
}};

export default LandingPage;
"""
        # Fix the f-string map loop which is complex to embed directly
        # Simplified replacement for the dynamic part above to ensure valid python string generation
        bullets_jsx = ""
        for bullet in landing_spec.get('bullets', ['Benefit 1', 'Benefit 2']):
            bullets_jsx += f"""
            <div className="flex items-start">
              <CheckCircle className="text-green-500 mr-3 mt-1 flex-shrink-0" />
              <p className="text-lg text-gray-700">{bullet}</p>
            </div>
"""
        landing_jsx = landing_jsx.replace(
            "{(landing_spec.get('bullets', []) or ['Benefit 1', 'Benefit 2']).map((bullet, i) => (f'<div key={{i}} className=\"flex items-start\"><CheckCircle className=\"text-green-500 mr-3 mt-1 flex-shrink-0\" /><div><span className=\"font-semibold text-lg\">{{bullet}}</span></div></div>')).replace(\"'\", '\"')}",
            bullets_jsx
        )

        with open(os.path.join(src_path, "pages", "LandingPage.js"), "w", encoding="utf-8") as f:
            f.write(landing_jsx)

        # Upsell Page
        upsell_spec = next((p for p in funnel_spec.get("pages", []) if p["type"] == "upsell_page"), {})
        upsell_jsx = f"""
import React from 'react';
import {{ useNavigate }} from 'react-router-dom';

const UpsellPage = () => {{
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-yellow-50 py-12 px-6 font-sans">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-2xl border-4 border-dashed border-red-500">
        <h2 className="text-red-600 font-bold text-center text-xl tracking-widest uppercase mb-4">Wait! Special One-Time Offer</h2>
        <h1 className="text-4xl font-extrabold text-center mb-6 text-gray-900">
          {upsell_spec.get('headline', 'Upgrade Your Order?')}
        </h1>
        
        <div className="prose prose-lg mx-auto text-gray-600 mb-8">
          <p>{upsell_spec.get('offer_description', 'Get the VIP package for just a little more.')}</p>
        </div>

        <div className="text-center mb-8">
          <span className="text-5xl font-bold text-green-600">{upsell_spec.get('price', '$97')}</span>
        </div>

        <div className="flex flex-col space-y-4">
          <button 
            onClick={{() => navigate('/thank-you')}}
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-4 rounded-lg text-xl shadow-lg"
          >
            {upsell_spec.get('cta_yes', 'Yes! Add to Order')}
          </button>
          <button 
            onClick={{() => navigate('/thank-you')}}
            className="text-gray-400 hover:text-gray-600 underline text-sm"
          >
            {upsell_spec.get('cta_no', 'No thanks, I hate success')}
          </button>
        </div>
      </div>
    </div>
  );
}};

export default UpsellPage;
"""
        with open(os.path.join(src_path, "pages", "UpsellPage.js"), "w", encoding="utf-8") as f:
            f.write(upsell_jsx)

        # Thank You Page
        thank_you_spec = next((p for p in funnel_spec.get("pages", []) if p["type"] == "thank_you_page"), {})
        ty_jsx = f"""
import React from 'react';

const ThankYouPage = () => {{
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 text-center">
      <h1 className="text-4xl font-bold text-green-600 mb-4">
        {thank_you_spec.get('headline', 'Order Complete!')}
      </h1>
      <p className="text-xl text-gray-600 max-w-lg">
        {thank_you_spec.get('next_steps', 'Check your email for access details.')}
      </p>
    </div>
  );
}};

export default ThankYouPage;
"""
        with open(os.path.join(src_path, "pages", "ThankYouPage.js"), "w", encoding="utf-8") as f:
            f.write(ty_jsx)

        # App.js Router
        app_js = """
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import UpsellPage from './pages/UpsellPage';
import ThankYouPage from './pages/ThankYouPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/upsell" element={<UpsellPage />} />
        <Route path="/thank-you" element={<ThankYouPage />} />
      </Routes>
    </Router>
  );
}

export default App;
"""
        with open(os.path.join(src_path, "App.js"), "w", encoding="utf-8") as f:
            f.write(app_js)

        # Update index.html for Tailwind CDN (quickest way for generated apps without complex build)
        index_html = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project.name} | Sovereign Funnel</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
        with open(os.path.join(base_path, "frontend", "public", "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)

    async def _scaffold_structure(self, base_path: str):
        os.makedirs(os.path.join(base_path, "backend", "app"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "frontend", "src"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "frontend", "public"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "scripts"), exist_ok=True)

    async def _generate_backend(self, base_path: str, project: Project):
        # main.py
        main_py = f"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="{project.name}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {{"message": "Welcome to {project.name} API"}}

@app.get("/health")
def health_check():
    return {{"status": "ok"}}
"""
        with open(os.path.join(base_path, "backend", "app", "main.py"), "w", encoding="utf-8") as f:
            f.write(main_py)
            
        # requirements.txt
        reqs = "fastapi\nuvicorn\nsqlalchemy\npsycopg2-binary\nstripe\npython-multipart\n"
        with open(os.path.join(base_path, "backend", "requirements.txt"), "w", encoding="utf-8") as f:
            f.write(reqs)

        # Dockerfile
        dockerfile = """
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        with open(os.path.join(base_path, "backend", "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(dockerfile)

    async def _generate_frontend(self, base_path: str, project: Project):
        # package.json
        pkg_json = {
            "name": project.slug,
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "axios": "^1.6.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        with open(os.path.join(base_path, "frontend", "package.json"), "w", encoding="utf-8") as f:
            json.dump(pkg_json, f, indent=2)
            
        # public/index.html
        index_html = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project.name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
        with open(os.path.join(base_path, "frontend", "public", "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)

        # src/index.js
        index_js = """
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        with open(os.path.join(base_path, "frontend", "src", "index.js"), "w", encoding="utf-8") as f:
            f.write(index_js)

        # src/App.js
        app_js = f"""
import React, {{ useState, useEffect }} from 'react';

function App() {{
  const [message, setMessage] = useState('');

  useEffect(() => {{
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage('Backend not reachable'));
  }}, []);

  return (
    <div className="App" style={{{{ textAlign: 'center', padding: '50px', fontFamily: 'sans-serif' }}}}>
      <header className="App-header">
        <h1 style={{{{ color: '#2c3e50' }}}}>{project.name}</h1>
        <div style={{{{ padding: '30px', border: '2px solid #3498db', borderRadius: '10px', margin: '40px auto', maxWidth: '500px', backgroundColor: '#ecf0f1' }}}}>
          <p style={{{{ fontSize: '1.2rem' }}}}>🚀 API Status: <span style={{{{ fontWeight: 'bold' }}}}>{{message || 'Connecting...'}}</span></p>
        </div>
        <p>This application was generated autonomously by the <strong>Realms2Riches</strong> sovereign builder.</p>
        <button style={{{{ 
          padding: '15px 30px', 
          fontSize: '18px', 
          cursor: 'pointer', 
          backgroundColor: '#2ecc71', 
          color: 'white', 
          border: 'none', 
          borderRadius: '5px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}}}>
          Activate Monetization Stream
        </button>
      </header>
    </div>
  );
}}

export default App;
"""
        with open(os.path.join(base_path, "frontend", "src", "App.js"), "w", encoding="utf-8") as f:
            f.write(app_js)

        # Dockerfile
        dockerfile = """
FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
"""
        with open(os.path.join(base_path, "frontend", "Dockerfile"), "w", encoding="utf-8") as f:
            f.write(dockerfile)

    async def _generate_config(self, base_path: str, project: Project):
        # .env (using prod values where appropriate, but sanitizing)
        env_content = f"""
PROJECT_NAME={project.name}
ENV=production
# Stripe Keys (Injected from Orchestrator)
STRIPE_PUBLISHABLE_KEY={os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_placeholder')}
STRIPE_API_KEY={settings.STRIPE_API_KEY if settings.STRIPE_API_KEY else "sk_test_placeholder"}
"""
        with open(os.path.join(base_path, ".env"), "w", encoding="utf-8") as f:
            f.write(env_content)
            
        # Docker Compose
        docker_compose = """
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - .env
    environment:
      - WDS_SOCKET_PORT=0
"""
        with open(os.path.join(base_path, "docker-compose.yml"), "w", encoding="utf-8") as f:
            f.write(docker_compose)

        # README.md (Famous.ai style)
        readme = f"""
# {project.name}

> Generated by Realms2Riches Autonomous Builder

## Features
{chr(10).join([f'- {feat}' for feat in project.tech_stack.get('features', [])])}

## Sovereignty
This project is 100% yours. No platform lock-in.

## Deployment
1. `docker-compose up --build`
"""
        with open(os.path.join(base_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)
