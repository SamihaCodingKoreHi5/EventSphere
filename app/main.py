import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.database.base_class import Base
from app.database.session import engine
from app.middleware.logging import LoggingMiddleware
from app.routers import auth_router, events_router, rsvp_router, admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Auto-create tables (Ensures out-of-the-box operation. For production, Alembic is preferred)
    if "pytest" not in sys.modules:
        Base.metadata.create_all(bind=engine)
    
    # Seed default category and admin data here if needed (handled dynamically or via seeding scripts)
    yield
    # Shutdown (cleanup if needed)



app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A production-ready Event Management Platform Backend built with FastAPI and PostgreSQL.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(events_router, prefix=f"{settings.API_V1_STR}/events", tags=["Events"])
app.include_router(rsvp_router, prefix=f"{settings.API_V1_STR}/rsvp", tags=["RSVP System"])
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Administration"])



@app.get("/", response_class=HTMLResponse)
def index():
    """Renders a beautiful welcome landing page for the API."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EventSphere API Portal</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --accent-primary: #8b5cf6;
                --accent-secondary: #ec4899;
                --text-primary: #f8fafc;
                --text-secondary: #94a3b8;
            }
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            body {
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                padding: 2rem;
                overflow-x: hidden;
            }
            .grid-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.05) 1px, transparent 0);
                background-size: 40px 40px;
                z-index: -1;
            }
            .glow-effect {
                position: absolute;
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
                top: 10%;
                left: 10%;
                z-index: -1;
            }
            .container {
                max-width: 900px;
                width: 100%;
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 3rem;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                text-align: center;
            }
            h1 {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 3.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
            }
            p.tagline {
                font-size: 1.25rem;
                color: var(--text-secondary);
                margin-bottom: 2.5rem;
            }
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1.5rem;
                margin-bottom: 3rem;
                text-align: left;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 1.5rem;
                transition: transform 0.2s ease, border-color 0.2s ease;
            }
            .feature-card:hover {
                transform: translateY(-4px);
                border-color: var(--accent-primary);
            }
            .feature-card h3 {
                margin-bottom: 0.5rem;
                color: var(--text-primary);
                font-weight: 600;
            }
            .feature-card p {
                font-size: 0.9rem;
                color: var(--text-secondary);
            }
            .cta-buttons {
                display: flex;
                gap: 1.5rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            .btn {
                display: inline-block;
                padding: 1rem 2rem;
                font-size: 1rem;
                font-weight: 600;
                text-decoration: none;
                border-radius: 12px;
                transition: all 0.2s ease;
            }
            .btn-primary {
                background: linear-gradient(135deg, var(--accent-primary) 0%, #7c3aed 100%);
                color: white;
                box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.3);
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 20px 25px -5px rgba(139, 92, 246, 0.4);
            }
            .btn-secondary {
                background: transparent;
                color: var(--text-primary);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.4);
                transform: translateY(-2px);
            }
            footer {
                margin-top: 3rem;
                font-size: 0.85rem;
                color: var(--text-secondary);
            }
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="glow-effect"></div>
        <div class="container">
            <h1>EventSphere</h1>
            <p class="tagline">Production-Ready Python Backend for Event Management</p>
            
            <div class="features-grid">
                <div class="feature-card">
                    <h3>🔐 JWT Security</h3>
                    <p>Bcrypt hashing, access token expirations, and secure dependency-based RBAC authentication.</p>
                </div>
                <div class="feature-card">
                    <h3>⚡ FastAPI CRUD</h3>
                    <p>Optimized endpoints for categories, event hosting, and owner validation logic.</p>
                </div>
                <div class="feature-card">
                    <h3>🎟️ RSVP System</h3>
                    <p>Handles capacity management, prevents double-booking, and runs relational integrity checks.</p>
                </div>
                <div class="feature-card">
                    <h3>✉️ Email Service</h3>
                    <p>Built-in triggers for confirmations and reminders via SMTP, Resend API, or Console logging.</p>
                </div>
            </div>

            <div class="cta-buttons">
                <a href="/docs" class="btn btn-primary">Swagger API Docs</a>
                <a href="/redoc" class="btn btn-secondary">ReDoc Explorer</a>
            </div>
            
            <footer>
                <p>EventSphere Platform API &bull; Python 3.11 &bull; PostgreSQL &bull; SQLAlchemy</p>
            </footer>
        </div>
    </body>
    </html>
    """
