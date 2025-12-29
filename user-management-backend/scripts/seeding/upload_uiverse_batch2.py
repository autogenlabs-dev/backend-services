"""
Upload additional UIverse components - Batch 2
New categories: Forms, Radio Buttons, Patterns, Tooltips + More Buttons/Cards
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone

MONGODB_URL = "mongodb://admin:password123@51.20.108.69:27017/user_management_db?authSource=admin"

COMPONENTS_BATCH2 = [
    # FORMS (5)
    {"name": "Login Form Dark", "category": "Forms", "tags": ["login", "auth", "dark"],
     "html": '<form class="login-form"><h2>Login</h2><div class="input-box"><input type="email" placeholder="Email"><span class="icon">📧</span></div><div class="input-box"><input type="password" placeholder="Password"><span class="icon">🔒</span></div><button type="submit">Sign In</button><p class="register">No account? <a href="#">Register</a></p></form>',
     "css": """.login-form{width:320px;padding:40px;background:#1a1a2e;border-radius:20px;color:#fff}.login-form h2{text-align:center;margin-bottom:30px;font-size:28px}.input-box{position:relative;margin-bottom:20px}.input-box input{width:100%;padding:15px 45px 15px 15px;background:#16213e;border:2px solid #1f4068;border-radius:10px;color:#fff;font-size:14px;outline:none;transition:.3s}.input-box input:focus{border-color:#667eea}.input-box .icon{position:absolute;right:15px;top:50%;transform:translateY(-50%)}.login-form button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-size:16px;font-weight:600;cursor:pointer;margin-top:10px}.register{text-align:center;margin-top:20px;font-size:14px;opacity:.7}.register a{color:#667eea}"""},
    
    {"name": "Contact Form Glass", "category": "Forms", "tags": ["contact", "glass", "message"],
     "html": '<form class="contact-form"><h3>Get in Touch</h3><input type="text" placeholder="Name"><input type="email" placeholder="Email"><textarea placeholder="Message"></textarea><button>Send Message</button></form>',
     "css": """.contact-form{width:340px;padding:35px;background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border-radius:20px;border:1px solid rgba(255,255,255,.2);color:#fff}.contact-form h3{margin-bottom:25px;font-size:24px}.contact-form input,.contact-form textarea{width:100%;padding:14px;margin-bottom:15px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:10px;color:#fff;font-size:14px;outline:none}.contact-form input:focus,.contact-form textarea:focus{border-color:#667eea}.contact-form textarea{height:100px;resize:none}.contact-form button{width:100%;padding:14px;background:#667eea;border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer}"""},
    
    {"name": "Subscribe Form", "category": "Forms", "tags": ["subscribe", "newsletter", "email"],
     "html": '<form class="subscribe-form"><h4>Subscribe to Newsletter</h4><p>Get the latest updates</p><div class="input-row"><input type="email" placeholder="Your email"><button>→</button></div></form>',
     "css": """.subscribe-form{width:360px;padding:30px;background:#16213e;border-radius:16px;color:#fff;text-align:center}.subscribe-form h4{font-size:20px;margin-bottom:8px}.subscribe-form p{opacity:.6;font-size:14px;margin-bottom:20px}.input-row{display:flex;gap:10px}.input-row input{flex:1;padding:14px 18px;background:#1a1a2e;border:2px solid #1f4068;border-radius:10px;color:#fff;outline:none}.input-row input:focus{border-color:#667eea}.input-row button{padding:14px 20px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-size:18px;cursor:pointer}"""},
    
    {"name": "Search Form Expanded", "category": "Forms", "tags": ["search", "filter", "advanced"],
     "html": '<form class="search-form"><div class="search-main"><input type="text" placeholder="Search anything..."><button class="search-btn">🔍</button></div><div class="filters"><span class="chip active">All</span><span class="chip">Images</span><span class="chip">Videos</span><span class="chip">Docs</span></div></form>',
     "css": """.search-form{width:400px;padding:25px;background:#1a1a2e;border-radius:16px}.search-main{display:flex;gap:10px;margin-bottom:15px}.search-main input{flex:1;padding:14px 18px;background:#16213e;border:2px solid #1f4068;border-radius:12px;color:#fff;font-size:14px;outline:none}.search-main input:focus{border-color:#667eea}.search-btn{padding:14px 18px;background:#667eea;border:none;border-radius:12px;cursor:pointer;font-size:16px}.filters{display:flex;gap:10px}.chip{padding:8px 16px;background:#16213e;border-radius:20px;color:#fff;font-size:12px;cursor:pointer;transition:.3s}.chip.active,.chip:hover{background:#667eea}"""},
    
    {"name": "Credit Card Form", "category": "Forms", "tags": ["payment", "credit", "checkout"],
     "html": '<form class="card-form"><div class="card-preview"><span class="card-number">•••• •••• •••• ••••</span><div class="card-info"><span>CARD HOLDER</span><span>MM/YY</span></div></div><input type="text" placeholder="Card Number" maxlength="19"><div class="row"><input type="text" placeholder="MM/YY"><input type="text" placeholder="CVV"></div><button>Pay Now</button></form>',
     "css": """.card-form{width:320px;padding:25px;background:#1a1a2e;border-radius:16px;color:#fff}.card-preview{padding:25px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;margin-bottom:20px}.card-number{font-size:18px;letter-spacing:3px}.card-info{display:flex;justify-content:space-between;margin-top:20px;font-size:10px;opacity:.8}.card-form input{width:100%;padding:14px;margin-bottom:12px;background:#16213e;border:2px solid #1f4068;border-radius:10px;color:#fff;outline:none}.card-form input:focus{border-color:#667eea}.row{display:flex;gap:12px}.row input{flex:1}.card-form button{width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer;margin-top:5px}"""},

    # RADIO BUTTONS (5)
    {"name": "Pill Radio", "category": "Radio Buttons", "tags": ["pill", "rounded", "modern"],
     "html": '<div class="pill-radio"><label><input type="radio" name="plan" checked><span>Monthly</span></label><label><input type="radio" name="plan"><span>Yearly</span></label></div>',
     "css": """.pill-radio{display:flex;background:#16213e;border-radius:30px;padding:5px}.pill-radio label{flex:1;text-align:center;cursor:pointer}.pill-radio input{display:none}.pill-radio span{display:block;padding:12px 24px;border-radius:25px;color:#fff;font-size:14px;transition:.3s}.pill-radio input:checked+span{background:linear-gradient(135deg,#667eea,#764ba2)}"""},
    
    {"name": "Card Radio", "category": "Radio Buttons", "tags": ["card", "selectable", "option"],
     "html": '<div class="card-radio"><label><input type="radio" name="size" checked><div class="card"><span class="size">S</span><span class="label">Small</span></div></label><label><input type="radio" name="size"><div class="card"><span class="size">M</span><span class="label">Medium</span></div></label><label><input type="radio" name="size"><div class="card"><span class="size">L</span><span class="label">Large</span></div></label></div>',
     "css": """.card-radio{display:flex;gap:12px}.card-radio label{cursor:pointer}.card-radio input{display:none}.card-radio .card{width:80px;padding:20px 15px;background:#16213e;border:2px solid #1f4068;border-radius:12px;text-align:center;color:#fff;transition:.3s}.card-radio .size{display:block;font-size:24px;font-weight:bold;margin-bottom:5px}.card-radio .label{font-size:12px;opacity:.7}.card-radio input:checked+.card{border-color:#667eea;background:rgba(102,126,234,.1)}"""},
    
    {"name": "Circle Radio", "category": "Radio Buttons", "tags": ["circle", "dot", "minimal"],
     "html": '<div class="circle-radio"><label><input type="radio" name="opt" checked><span class="circle"></span>Option 1</label><label><input type="radio" name="opt"><span class="circle"></span>Option 2</label><label><input type="radio" name="opt"><span class="circle"></span>Option 3</label></div>',
     "css": """.circle-radio{display:flex;flex-direction:column;gap:15px}.circle-radio label{display:flex;align-items:center;gap:12px;color:#fff;cursor:pointer}.circle-radio input{display:none}.circle-radio .circle{width:22px;height:22px;border:2px solid #444;border-radius:50%;position:relative;transition:.3s}.circle-radio .circle::after{content:'';position:absolute;inset:4px;background:#667eea;border-radius:50%;transform:scale(0);transition:.2s}.circle-radio input:checked+.circle{border-color:#667eea}.circle-radio input:checked+.circle::after{transform:scale(1)}"""},
    
    {"name": "Image Radio", "category": "Radio Buttons", "tags": ["image", "visual", "icon"],
     "html": '<div class="image-radio"><label><input type="radio" name="theme" checked><div class="box"><span>🌙</span><p>Dark</p></div></label><label><input type="radio" name="theme"><div class="box"><span>☀️</span><p>Light</p></div></label><label><input type="radio" name="theme"><div class="box"><span>🎨</span><p>Custom</p></div></label></div>',
     "css": """.image-radio{display:flex;gap:15px}.image-radio label{cursor:pointer}.image-radio input{display:none}.image-radio .box{width:90px;padding:20px;background:#16213e;border:2px solid #1f4068;border-radius:16px;text-align:center;color:#fff;transition:.3s}.image-radio .box span{font-size:32px;display:block;margin-bottom:10px}.image-radio .box p{font-size:12px;margin:0;opacity:.8}.image-radio input:checked+.box{border-color:#667eea;background:rgba(102,126,234,.15)}"""},
    
    {"name": "Inline Radio", "category": "Radio Buttons", "tags": ["inline", "horizontal", "compact"],
     "html": '<div class="inline-radio"><label><input type="radio" name="color" checked><span style="background:#667eea"></span></label><label><input type="radio" name="color"><span style="background:#ff6b6b"></span></label><label><input type="radio" name="color"><span style="background:#4ade80"></span></label><label><input type="radio" name="color"><span style="background:#fbbf24"></span></label></div>',
     "css": """.inline-radio{display:flex;gap:12px}.inline-radio label{cursor:pointer}.inline-radio input{display:none}.inline-radio span{display:block;width:36px;height:36px;border-radius:50%;border:3px solid transparent;transition:.2s}.inline-radio input:checked+span{border-color:#fff;transform:scale(1.1)}"""},

    # PATTERNS/BACKGROUNDS (5)
    {"name": "Gradient Mesh", "category": "Patterns", "tags": ["gradient", "mesh", "background"],
     "html": '<div class="gradient-mesh"></div>',
     "css": """.gradient-mesh{width:300px;height:200px;border-radius:20px;background:linear-gradient(45deg,#ff006680,#8338ec80,#3a86ff80);background-size:200% 200%;animation:mesh 5s ease infinite}@keyframes mesh{0%,100%{background-position:0 50%}50%{background-position:100% 50%}}"""},
    
    {"name": "Animated Grid", "category": "Patterns", "tags": ["grid", "animated", "tech"],
     "html": '<div class="animated-grid"></div>',
     "css": """.animated-grid{width:300px;height:200px;border-radius:16px;background-image:linear-gradient(rgba(102,126,234,.2) 1px,transparent 1px),linear-gradient(90deg,rgba(102,126,234,.2) 1px,transparent 1px);background-size:30px 30px;background-position:0 0;animation:grid-move 3s linear infinite}@keyframes grid-move{to{background-position:30px 30px}}"""},
    
    {"name": "Dots Pattern", "category": "Patterns", "tags": ["dots", "polka", "subtle"],
     "html": '<div class="dots-pattern"></div>',
     "css": """.dots-pattern{width:300px;height:200px;border-radius:16px;background-color:#1a1a2e;background-image:radial-gradient(#667eea 1px,transparent 1px);background-size:20px 20px}"""},
    
    {"name": "Diagonal Lines", "category": "Patterns", "tags": ["diagonal", "lines", "stripe"],
     "html": '<div class="diagonal-lines"></div>',
     "css": """.diagonal-lines{width:300px;height:200px;border-radius:16px;background:repeating-linear-gradient(45deg,#16213e,#16213e 10px,#1a1a2e 10px,#1a1a2e 20px)}"""},
    
    {"name": "Noise Texture", "category": "Patterns", "tags": ["noise", "texture", "grain"],
     "html": '<div class="noise-texture"></div>',
     "css": """.noise-texture{width:300px;height:200px;border-radius:16px;background:linear-gradient(135deg,#667eea,#764ba2);position:relative}.noise-texture::after{content:'';position:absolute;inset:0;border-radius:16px;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");opacity:.1}"""},

    # TOOLTIPS (5)
    {"name": "Hover Tooltip", "category": "Tooltips", "tags": ["hover", "info", "simple"],
     "html": '<div class="tooltip-wrap"><button class="tooltip-btn">Hover Me</button><span class="tooltip">This is a tooltip!</span></div>',
     "css": """.tooltip-wrap{position:relative;display:inline-block}.tooltip-btn{padding:12px 24px;background:#667eea;border:none;border-radius:8px;color:#fff;cursor:pointer}.tooltip{position:absolute;bottom:120%;left:50%;transform:translateX(-50%);padding:10px 15px;background:#1a1a2e;color:#fff;font-size:13px;border-radius:8px;white-space:nowrap;opacity:0;visibility:hidden;transition:.3s}.tooltip::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#1a1a2e}.tooltip-wrap:hover .tooltip{opacity:1;visibility:visible}"""},
    
    {"name": "Arrow Tooltip", "category": "Tooltips", "tags": ["arrow", "popup", "info"],
     "html": '<div class="arrow-tip"><span class="icon">ℹ️</span><div class="tip-content">Helpful information appears here</div></div>',
     "css": """.arrow-tip{position:relative;display:inline-block;cursor:pointer}.arrow-tip .icon{font-size:20px}.tip-content{position:absolute;bottom:130%;left:50%;transform:translateX(-50%) scale(.9);padding:12px 16px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-size:13px;border-radius:10px;min-width:180px;text-align:center;opacity:0;visibility:hidden;transition:.3s}.tip-content::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:8px solid transparent;border-top-color:#764ba2}.arrow-tip:hover .tip-content{opacity:1;visibility:visible;transform:translateX(-50%) scale(1)}"""},
    
    {"name": "Error Tooltip", "category": "Tooltips", "tags": ["error", "warning", "validation"],
     "html": '<div class="error-tip"><input type="text" placeholder="Email" class="error-input"><span class="tip-error">Please enter a valid email</span></div>',
     "css": """.error-tip{position:relative;width:250px}.error-input{width:100%;padding:12px;background:#16213e;border:2px solid #ff6b6b;border-radius:8px;color:#fff;outline:none}.tip-error{position:absolute;top:100%;left:0;margin-top:8px;padding:10px 14px;background:#ff6b6b;color:#fff;font-size:12px;border-radius:8px}.tip-error::before{content:'';position:absolute;bottom:100%;left:20px;border:6px solid transparent;border-bottom-color:#ff6b6b}"""},
    
    {"name": "Progress Tooltip", "category": "Tooltips", "tags": ["progress", "status", "percent"],
     "html": '<div class="progress-tip"><div class="bar"><div class="fill" style="width:65%"></div></div><span class="tip-value">65%</span></div>',
     "css": """.progress-tip{position:relative;width:200px}.bar{height:8px;background:#16213e;border-radius:4px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:4px;position:relative}.tip-value{position:absolute;top:-30px;left:65%;transform:translateX(-50%);padding:5px 10px;background:#1a1a2e;color:#fff;font-size:12px;border-radius:6px}.tip-value::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:5px solid transparent;border-top-color:#1a1a2e}"""},
    
    {"name": "Copy Tooltip", "category": "Tooltips", "tags": ["copy", "clipboard", "feedback"],
     "html": '<button class="copy-btn"><span class="copy-icon">📋</span><span class="copy-text">Copy</span><span class="copied-tip">Copied!</span></button>',
     "css": """.copy-btn{position:relative;display:flex;align-items:center;gap:8px;padding:10px 20px;background:#16213e;border:2px solid #1f4068;border-radius:8px;color:#fff;cursor:pointer;transition:.3s}.copy-btn:hover{border-color:#667eea}.copied-tip{position:absolute;top:-35px;left:50%;transform:translateX(-50%);padding:6px 12px;background:#4ade80;color:#000;font-size:12px;border-radius:6px;opacity:0;transition:.3s}.copy-btn:active .copied-tip{opacity:1}"""},

    # MORE BUTTONS (5)
    {"name": "Split Button", "category": "Buttons", "tags": ["split", "dropdown", "action"],
     "html": '<div class="split-btn"><button class="main">Save</button><button class="drop">▼</button></div>',
     "css": """.split-btn{display:flex}.split-btn .main{padding:12px 24px;background:#667eea;border:none;border-radius:8px 0 0 8px;color:#fff;font-weight:600;cursor:pointer}.split-btn .drop{padding:12px 14px;background:#5a52d5;border:none;border-radius:0 8px 8px 0;color:#fff;cursor:pointer;border-left:1px solid rgba(255,255,255,.2)}.split-btn button:hover{filter:brightness(1.1)}"""},
    
    {"name": "Icon Button", "category": "Buttons", "tags": ["icon", "floating", "fab"],
     "html": '<button class="icon-btn">+</button>',
     "css": """.icon-btn{width:56px;height:56px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:50%;color:#fff;font-size:28px;cursor:pointer;box-shadow:0 4px 15px rgba(102,126,234,.4);transition:.3s}.icon-btn:hover{transform:scale(1.1);box-shadow:0 6px 20px rgba(102,126,234,.5)}"""},
    
    {"name": "Text Button", "category": "Buttons", "tags": ["text", "link", "minimal"],
     "html": '<button class="text-btn">Learn More →</button>',
     "css": """.text-btn{padding:10px 0;background:none;border:none;color:#667eea;font-size:16px;cursor:pointer;position:relative}.text-btn::after{content:'';position:absolute;bottom:5px;left:0;width:0;height:2px;background:#667eea;transition:.3s}.text-btn:hover::after{width:100%}"""},
    
    {"name": "Loading Button", "category": "Buttons", "tags": ["loading", "spinner", "async"],
     "html": '<button class="loading-btn"><span class="spinner"></span>Processing...</button>',
     "css": """.loading-btn{display:flex;align-items:center;gap:10px;padding:14px 28px;background:#667eea;border:none;border-radius:10px;color:#fff;font-size:15px;cursor:wait}.spinner{width:18px;height:18px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"""},
    
    {"name": "Outline Button", "category": "Buttons", "tags": ["outline", "border", "ghost"],
     "html": '<button class="outline-btn">Get Started</button>',
     "css": """.outline-btn{padding:14px 32px;background:transparent;border:2px solid #667eea;border-radius:10px;color:#667eea;font-size:15px;font-weight:600;cursor:pointer;transition:.3s}.outline-btn:hover{background:#667eea;color:#fff}"""},

    # MORE CARDS (5)
    {"name": "Team Card", "category": "Cards", "tags": ["team", "member", "about"],
     "html": '<div class="team-card"><div class="avatar"></div><h3>Alex Smith</h3><p class="role">Lead Developer</p><div class="socials"><span>🐦</span><span>💼</span><span>📧</span></div></div>',
     "css": """.team-card{width:240px;padding:30px;background:#1a1a2e;border-radius:20px;text-align:center;color:#fff}.team-card .avatar{width:100px;height:100px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2)}.team-card h3{font-size:20px;margin-bottom:5px}.team-card .role{opacity:.6;font-size:14px;margin-bottom:20px}.socials{display:flex;justify-content:center;gap:15px}.socials span{width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:#16213e;border-radius:50%;cursor:pointer;transition:.3s}.socials span:hover{background:#667eea}"""},
    
    {"name": "Event Card", "category": "Cards", "tags": ["event", "calendar", "date"],
     "html": '<div class="event-card"><div class="date"><span class="day">28</span><span class="month">DEC</span></div><div class="info"><h4>Tech Conference 2024</h4><p>📍 New York City</p><p>⏰ 10:00 AM</p></div></div>',
     "css": """.event-card{display:flex;gap:20px;padding:20px;background:#1a1a2e;border-radius:16px;color:#fff;width:300px}.event-card .date{width:70px;height:70px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center}.event-card .day{font-size:24px;font-weight:bold}.event-card .month{font-size:12px;opacity:.8}.event-card .info h4{margin-bottom:10px}.event-card .info p{font-size:13px;opacity:.7;margin:5px 0}"""},
    
    {"name": "Music Card", "category": "Cards", "tags": ["music", "player", "audio"],
     "html": '<div class="music-card"><div class="cover"></div><div class="info"><h4>Song Title</h4><p>Artist Name</p></div><div class="controls"><span>⏮</span><span class="play">▶</span><span>⏭</span></div><div class="progress"><div class="bar"></div></div></div>',
     "css": """.music-card{width:280px;padding:20px;background:#1a1a2e;border-radius:20px;color:#fff}.music-card .cover{height:200px;background:linear-gradient(135deg,#434343,#000000);border-radius:16px;margin-bottom:20px}.music-card .info{text-align:center;margin-bottom:20px}.music-card .info h4{margin-bottom:5px}.music-card .info p{opacity:.6;font-size:14px}.controls{display:flex;justify-content:center;gap:30px;margin-bottom:20px;font-size:24px}.controls span{cursor:pointer;transition:.3s}.controls .play{width:50px;height:50px;background:#667eea;border-radius:50%;display:flex;align-items:center;justify-content:center}.progress{height:4px;background:#16213e;border-radius:2px}.progress .bar{width:40%;height:100%;background:#667eea;border-radius:2px}"""},
    
    {"name": "Weather Card", "category": "Cards", "tags": ["weather", "forecast", "temperature"],
     "html": '<div class="weather-card"><div class="header"><span class="city">New York</span><span class="date">Mon, Dec 28</span></div><div class="main"><span class="icon">☀️</span><span class="temp">24°</span></div><div class="details"><div><span>💨</span>12 km/h</div><div><span>💧</span>45%</div><div><span>🌡</span>28°</div></div></div>',
     "css": """.weather-card{width:260px;padding:25px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:24px;color:#fff}.weather-card .header{display:flex;justify-content:space-between;margin-bottom:30px}.weather-card .city{font-weight:600}.weather-card .date{opacity:.8;font-size:14px}.weather-card .main{display:flex;align-items:center;justify-content:center;gap:20px;margin-bottom:30px}.weather-card .icon{font-size:64px}.weather-card .temp{font-size:56px;font-weight:300}.weather-card .details{display:flex;justify-content:space-around;padding-top:20px;border-top:1px solid rgba(255,255,255,.2)}.weather-card .details div{text-align:center;font-size:14px}.weather-card .details span{display:block;margin-bottom:5px}"""},
    
    {"name": "File Card", "category": "Cards", "tags": ["file", "document", "upload"],
     "html": '<div class="file-card"><div class="icon">📄</div><div class="info"><h4>document.pdf</h4><p>2.4 MB • Dec 28, 2024</p></div><div class="actions"><button>📥</button><button>🗑️</button></div></div>',
     "css": """.file-card{display:flex;align-items:center;gap:15px;padding:16px 20px;background:#1a1a2e;border-radius:12px;color:#fff;width:320px}.file-card .icon{font-size:36px}.file-card .info{flex:1}.file-card .info h4{font-size:15px;margin-bottom:4px}.file-card .info p{font-size:12px;opacity:.6}.file-card .actions{display:flex;gap:8px}.file-card .actions button{width:36px;height:36px;background:#16213e;border:none;border-radius:8px;cursor:pointer;transition:.3s}.file-card .actions button:hover{background:#667eea}"""},
]


async def main():
    print("=" * 60)
    print("🎨 UIverse Components - Batch 2")
    print("=" * 60)
    print(f"Components to upload: {len(COMPONENTS_BATCH2)}")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.user_management_db
    collection = db.components
    
    user = await db.users.find_one({})
    user_id = user["_id"] if user else ObjectId("000000000000000000000001")
    
    added, skipped = 0, 0
    
    for comp in COMPONENTS_BATCH2:
        existing = await collection.find_one({"name": comp["name"]})
        if existing:
            print(f"  ⏭️ Exists: {comp['name']}")
            skipped += 1
            continue
        
        doc = {
            "_id": ObjectId(),
            "name": comp["name"],
            "title": comp["name"],
            "category": comp["category"],
            "type": comp["category"],
            "language": "CSS",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": f"Beautiful {comp['category'].lower()} component",
            "full_description": f"A stunning {comp['name']} from UIverse collection",
            "developer_name": "UIverse Community",
            "developer_experience": "Community",
            "html_code": comp["html"],
            "css_code": comp["css"],
            "preview_code": f"{comp['html']}\n<style>\n{comp['css']}\n</style>",
            "code": comp["html"],
            "tags": comp["tags"],
            "views": 0,
            "downloads": 0,
            "likes": 0,
            "rating": 4.5,
            "is_active": True,
            "approval_status": "approved",
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        await collection.insert_one(doc)
        print(f"  ✅ Added: {comp['name']} ({comp['category']})")
        added += 1
    
    total = await collection.count_documents({})
    print(f"\n📊 Added: {added} | Skipped: {skipped} | Total: {total}")
    client.close()
    print("🎉 Done!")


if __name__ == "__main__":
    asyncio.run(main())
