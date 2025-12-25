"""
Upload curated UIverse-style components to MongoDB.
Best components from each category with real HTML/CSS code.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone

MONGODB_URL = "mongodb://admin:password123@51.20.108.69:27017/user_management_db?authSource=admin"

COMPONENTS = [
    # BUTTONS (10)
    {"name": "Neon Pulse Button", "category": "Buttons", "tags": ["neon", "glow", "animated"],
     "html": '<button class="neon-btn">Click Me</button>',
     "css": """.neon-btn{padding:15px 30px;font-size:18px;color:#03e9f4;background:transparent;border:2px solid #03e9f4;border-radius:5px;cursor:pointer;text-transform:uppercase;letter-spacing:4px;box-shadow:0 0 5px #03e9f4,0 0 25px #03e9f4,inset 0 0 50px rgba(3,233,244,0.1);transition:.3s}.neon-btn:hover{background:#03e9f4;color:#050801;box-shadow:0 0 5px #03e9f4,0 0 50px #03e9f4,0 0 100px #03e9f4}"""},
    
    {"name": "Gradient Border Button", "category": "Buttons", "tags": ["gradient", "border", "modern"],
     "html": '<button class="gradient-btn"><span>Explore</span></button>',
     "css": """.gradient-btn{position:relative;padding:15px 35px;font-size:16px;color:#fff;background:#1a1a2e;border:none;border-radius:10px;cursor:pointer;overflow:hidden}.gradient-btn::before{content:'';position:absolute;inset:-3px;background:linear-gradient(45deg,#ff0080,#ff8c00,#40e0d0,#ff0080);background-size:400%;z-index:-1;border-radius:12px;animation:gradient 3s linear infinite}.gradient-btn::after{content:'';position:absolute;inset:2px;background:#1a1a2e;border-radius:8px;z-index:-1}@keyframes gradient{0%,100%{background-position:0 0}50%{background-position:100% 0}}"""},
    
    {"name": "3D Push Button", "category": "Buttons", "tags": ["3d", "push", "depth"],
     "html": '<button class="push-btn">Push Me</button>',
     "css": """.push-btn{padding:15px 40px;font-size:16px;font-weight:bold;color:#fff;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;cursor:pointer;box-shadow:0 6px 0 #4a4179,0 8px 15px rgba(0,0,0,.3);transition:.1s}.push-btn:active{box-shadow:0 2px 0 #4a4179;transform:translateY(4px)}"""},
    
    {"name": "Cyberpunk Button", "category": "Buttons", "tags": ["cyberpunk", "glitch", "futuristic"],
     "html": '<button class="cyber-btn">ENTER<span class="cyber-glitch"></span></button>',
     "css": """.cyber-btn{position:relative;padding:15px 30px;font-size:18px;font-family:monospace;color:#0ff;background:#000;border:2px solid #0ff;cursor:pointer;clip-path:polygon(0 0,100% 0,100% 70%,90% 100%,0 100%);transition:.3s}.cyber-btn:hover{background:#0ff;color:#000}.cyber-glitch{position:absolute;inset:0;background:#f0f;opacity:0;clip-path:polygon(0 0,100% 0,100% 45%,0 45%)}.cyber-btn:hover .cyber-glitch{animation:glitch .3s infinite}@keyframes glitch{0%,100%{opacity:0}50%{opacity:.5;transform:translateX(2px)}}"""},
    
    {"name": "Liquid Button", "category": "Buttons", "tags": ["liquid", "blob", "organic"],
     "html": '<button class="liquid-btn">Liquid</button>',
     "css": """.liquid-btn{padding:15px 35px;font-size:16px;color:#fff;background:linear-gradient(45deg,#405de6,#5851db,#833ab4);border:none;border-radius:50px;cursor:pointer;position:relative;overflow:hidden;transition:.5s}.liquid-btn::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,255,255,.3) 20%,transparent 50%);opacity:0;transition:.5s}.liquid-btn:hover::before{opacity:1;animation:ripple 1s}@keyframes ripple{to{transform:scale(2);opacity:0}}"""},
    
    {"name": "Minimal Line Button", "category": "Buttons", "tags": ["minimal", "line", "elegant"],
     "html": '<button class="line-btn">Submit</button>',
     "css": """.line-btn{padding:12px 30px;font-size:14px;color:#fff;background:transparent;border:none;cursor:pointer;position:relative}.line-btn::before,.line-btn::after{content:'';position:absolute;width:0;height:2px;background:#667eea;transition:.3s}.line-btn::before{top:0;left:0}.line-btn::after{bottom:0;right:0}.line-btn:hover::before,.line-btn:hover::after{width:100%}"""},
    
    {"name": "Neumorphic Button", "category": "Buttons", "tags": ["neumorphic", "soft", "3d"],
     "html": '<button class="neo-btn">Soft UI</button>',
     "css": """.neo-btn{padding:15px 35px;font-size:16px;color:#6d5dfc;background:#ecf0f3;border:none;border-radius:15px;cursor:pointer;box-shadow:6px 6px 10px #cbced1,-6px -6px 10px #fff;transition:.2s}.neo-btn:active{box-shadow:inset 4px 4px 10px #cbced1,inset -4px -4px 10px #fff}"""},
    
    {"name": "Glass Button", "category": "Buttons", "tags": ["glass", "blur", "transparent"],
     "html": '<button class="glass-btn">Glass Effect</button>',
     "css": """.glass-btn{padding:15px 30px;font-size:16px;color:#fff;background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.2);border-radius:10px;cursor:pointer;transition:.3s}.glass-btn:hover{background:rgba(255,255,255,.2);box-shadow:0 8px 32px rgba(31,38,135,.2)}"""},
    
    {"name": "Magnetic Button", "category": "Buttons", "tags": ["magnetic", "interactive", "hover"],
     "html": '<button class="magnetic-btn">Hover Me</button>',
     "css": """.magnetic-btn{padding:20px 40px;font-size:16px;color:#fff;background:#ff6b6b;border:none;border-radius:8px;cursor:pointer;transition:transform .3s cubic-bezier(.4,0,.2,1),box-shadow .3s}.magnetic-btn:hover{transform:scale(1.05);box-shadow:0 10px 40px rgba(255,107,107,.4)}"""},
    
    {"name": "Rainbow Button", "category": "Buttons", "tags": ["rainbow", "colorful", "animated"],
     "html": '<button class="rainbow-btn">Rainbow</button>',
     "css": """.rainbow-btn{padding:15px 35px;font-size:16px;color:#fff;background:linear-gradient(90deg,#ff0000,#ff7f00,#ffff00,#00ff00,#0000ff,#4b0082,#9400d3);background-size:400%;border:none;border-radius:25px;cursor:pointer;animation:rainbow 3s linear infinite}.rainbow-btn:hover{filter:brightness(1.2)}@keyframes rainbow{0%,100%{background-position:0}50%{background-position:100%}}"""},

    # CARDS (10)
    {"name": "Glass Card", "category": "Cards", "tags": ["glass", "blur", "modern"],
     "html": '<div class="glass-card"><div class="icon">🚀</div><h3>Glass Card</h3><p>Beautiful glassmorphism effect</p></div>',
     "css": """.glass-card{width:280px;padding:30px;background:rgba(255,255,255,.1);backdrop-filter:blur(10px);border-radius:20px;border:1px solid rgba(255,255,255,.2);text-align:center;color:#fff}.glass-card .icon{font-size:48px;margin-bottom:15px}.glass-card h3{margin-bottom:10px}.glass-card p{opacity:.8;font-size:14px}"""},
    
    {"name": "Hover Lift Card", "category": "Cards", "tags": ["hover", "lift", "shadow"],
     "html": '<div class="lift-card"><div class="img"></div><div class="content"><h3>Project</h3><p>Description here</p></div></div>',
     "css": """.lift-card{width:280px;background:#1a1a2e;border-radius:16px;overflow:hidden;transition:.3s;cursor:pointer}.lift-card:hover{transform:translateY(-10px);box-shadow:0 20px 40px rgba(0,0,0,.4)}.lift-card .img{height:160px;background:linear-gradient(135deg,#667eea,#764ba2)}.lift-card .content{padding:20px;color:#fff}.lift-card h3{margin-bottom:8px}.lift-card p{opacity:.7;font-size:14px}"""},
    
    {"name": "Profile Card", "category": "Cards", "tags": ["profile", "avatar", "social"],
     "html": '<div class="profile-card"><div class="avatar"></div><h3>John Doe</h3><p>Developer</p><div class="stats"><span>120 Posts</span><span>450 Followers</span></div></div>',
     "css": """.profile-card{width:260px;padding:30px;background:#1e1e30;border-radius:20px;text-align:center;color:#fff}.profile-card .avatar{width:80px;height:80px;margin:0 auto 15px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2)}.profile-card h3{margin-bottom:5px}.profile-card p{opacity:.6;font-size:14px;margin-bottom:20px}.profile-card .stats{display:flex;justify-content:space-around;padding-top:20px;border-top:1px solid rgba(255,255,255,.1)}.profile-card .stats span{font-size:12px;opacity:.8}"""},
    
    {"name": "Pricing Card", "category": "Cards", "tags": ["pricing", "plan", "subscription"],
     "html": '<div class="pricing-card"><h4>Pro Plan</h4><div class="price">$29<span>/mo</span></div><ul><li>Unlimited projects</li><li>Priority support</li><li>Custom domain</li></ul><button>Get Started</button></div>',
     "css": """.pricing-card{width:280px;padding:40px 30px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:20px;color:#fff;text-align:center}.pricing-card h4{font-size:14px;opacity:.8;margin-bottom:10px}.pricing-card .price{font-size:48px;font-weight:bold;margin-bottom:30px}.pricing-card .price span{font-size:16px;opacity:.7}.pricing-card ul{list-style:none;margin-bottom:30px;text-align:left}.pricing-card li{padding:10px 0;border-bottom:1px solid rgba(255,255,255,.1)}.pricing-card button{width:100%;padding:15px;background:#fff;color:#667eea;border:none;border-radius:10px;font-weight:bold;cursor:pointer}"""},
    
    {"name": "Feature Card", "category": "Cards", "tags": ["feature", "icon", "minimal"],
     "html": '<div class="feature-card"><div class="icon">⚡</div><h3>Fast Performance</h3><p>Lightning quick load times</p></div>',
     "css": """.feature-card{width:260px;padding:30px;background:#16213e;border-radius:16px;border:1px solid #1f4068;color:#fff;transition:.3s}.feature-card:hover{border-color:#667eea;transform:translateY(-5px)}.feature-card .icon{font-size:40px;margin-bottom:20px}.feature-card h3{margin-bottom:10px;font-size:18px}.feature-card p{opacity:.7;font-size:14px;line-height:1.6}"""},
    
    {"name": "Testimonial Card", "category": "Cards", "tags": ["testimonial", "quote", "review"],
     "html": '<div class="testimonial-card"><p>"Amazing product! Highly recommended."</p><div class="author"><div class="avatar"></div><div><strong>Sarah</strong><span>Designer</span></div></div></div>',
     "css": """.testimonial-card{width:300px;padding:30px;background:#1a1a2e;border-radius:16px;color:#fff}.testimonial-card p{font-size:16px;line-height:1.6;margin-bottom:20px;font-style:italic;opacity:.9}.testimonial-card .author{display:flex;align-items:center;gap:15px}.testimonial-card .avatar{width:50px;height:50px;border-radius:50%;background:linear-gradient(135deg,#ff6b6b,#feca57)}.testimonial-card strong{display:block}.testimonial-card span{font-size:12px;opacity:.6}"""},
    
    {"name": "Product Card", "category": "Cards", "tags": ["product", "ecommerce", "shop"],
     "html": '<div class="product-card"><div class="img"></div><div class="info"><h3>Product Name</h3><p class="price">$49.99</p><button>Add to Cart</button></div></div>',
     "css": """.product-card{width:260px;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.1)}.product-card .img{height:200px;background:linear-gradient(135deg,#a8edea,#fed6e3)}.product-card .info{padding:20px}.product-card h3{color:#333;margin-bottom:10px}.product-card .price{color:#667eea;font-size:20px;font-weight:bold;margin-bottom:15px}.product-card button{width:100%;padding:12px;background:#667eea;color:#fff;border:none;border-radius:8px;cursor:pointer}"""},
    
    {"name": "Blog Card", "category": "Cards", "tags": ["blog", "article", "post"],
     "html": '<div class="blog-card"><div class="img"></div><div class="content"><span class="tag">Design</span><h3>Modern UI Trends</h3><p>Discover the latest design trends...</p></div></div>',
     "css": """.blog-card{width:320px;background:#1a1a2e;border-radius:16px;overflow:hidden;color:#fff}.blog-card .img{height:180px;background:linear-gradient(135deg,#667eea,#764ba2)}.blog-card .content{padding:20px}.blog-card .tag{display:inline-block;padding:5px 12px;background:rgba(102,126,234,.2);color:#667eea;border-radius:20px;font-size:12px;margin-bottom:15px}.blog-card h3{margin-bottom:10px}.blog-card p{opacity:.7;font-size:14px;line-height:1.6}"""},
    
    {"name": "Stats Card", "category": "Cards", "tags": ["stats", "analytics", "dashboard"],
     "html": '<div class="stats-card"><div class="header"><span>Revenue</span><span class="trend">+12%</span></div><h2>$24,500</h2><div class="chart"></div></div>',
     "css": """.stats-card{width:260px;padding:25px;background:#1e1e30;border-radius:16px;color:#fff}.stats-card .header{display:flex;justify-content:space-between;margin-bottom:10px}.stats-card .header span{opacity:.6;font-size:14px}.stats-card .trend{color:#4ade80;opacity:1}.stats-card h2{font-size:32px;margin-bottom:20px}.stats-card .chart{height:60px;background:linear-gradient(90deg,rgba(102,126,234,.2),rgba(102,126,234,.5));border-radius:8px}"""},
    
    {"name": "Notification Card", "category": "Cards", "tags": ["notification", "alert", "toast"],
     "html": '<div class="notif-card"><div class="icon">✓</div><div class="text"><strong>Success!</strong><p>Your changes have been saved.</p></div><button class="close">×</button></div>',
     "css": """.notif-card{display:flex;align-items:center;gap:15px;padding:20px;background:#1a1a2e;border-left:4px solid #4ade80;border-radius:8px;color:#fff}.notif-card .icon{width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:rgba(74,222,128,.2);color:#4ade80;border-radius:50%;font-size:20px}.notif-card .text{flex:1}.notif-card strong{display:block;margin-bottom:5px}.notif-card p{opacity:.7;font-size:14px;margin:0}.notif-card .close{background:none;border:none;color:#fff;opacity:.5;font-size:24px;cursor:pointer}"""},

    # INPUTS (5)
    {"name": "Floating Label Input", "category": "Inputs", "tags": ["floating", "label", "form"],
     "html": '<div class="float-group"><input type="text" required><label>Email</label></div>',
     "css": """.float-group{position:relative;width:280px}.float-group input{width:100%;padding:15px;font-size:16px;color:#fff;background:transparent;border:2px solid #444;border-radius:8px;outline:none;transition:.3s}.float-group input:focus{border-color:#667eea}.float-group label{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#888;font-size:16px;pointer-events:none;transition:.3s;background:#0f0f0f;padding:0 5px}.float-group input:focus~label,.float-group input:valid~label{top:0;font-size:12px;color:#667eea}"""},
    
    {"name": "Underline Input", "category": "Inputs", "tags": ["underline", "minimal", "animated"],
     "html": '<div class="underline-group"><input type="text" required><label>Username</label><span class="line"></span></div>',
     "css": """.underline-group{position:relative;width:280px}.underline-group input{width:100%;padding:10px 0;font-size:16px;color:#fff;background:transparent;border:none;border-bottom:2px solid #444;outline:none}.underline-group label{position:absolute;left:0;top:10px;color:#888;font-size:16px;pointer-events:none;transition:.3s}.underline-group input:focus~label,.underline-group input:valid~label{top:-16px;font-size:12px;color:#03e9f4}.underline-group .line{position:absolute;bottom:0;left:50%;width:0;height:2px;background:#03e9f4;transition:.3s}.underline-group input:focus~.line{left:0;width:100%}"""},
    
    {"name": "Search Box", "category": "Inputs", "tags": ["search", "icon", "expandable"],
     "html": '<div class="search-box"><input type="text" placeholder="Search..."><button>🔍</button></div>',
     "css": """.search-box{display:flex;width:300px;background:#1a1a2e;border-radius:25px;overflow:hidden;border:2px solid transparent;transition:.3s}.search-box:focus-within{border-color:#667eea}.search-box input{flex:1;padding:12px 20px;font-size:14px;color:#fff;background:transparent;border:none;outline:none}.search-box input::placeholder{color:#666}.search-box button{padding:12px 20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;cursor:pointer}"""},
    
    {"name": "Password Input", "category": "Inputs", "tags": ["password", "toggle", "secure"],
     "html": '<div class="pass-group"><input type="password" placeholder="Password"><span class="toggle">👁</span></div>',
     "css": """.pass-group{position:relative;width:280px}.pass-group input{width:100%;padding:15px 50px 15px 15px;font-size:16px;color:#fff;background:#1a1a2e;border:2px solid #333;border-radius:10px;outline:none;transition:.3s}.pass-group input:focus{border-color:#667eea}.pass-group .toggle{position:absolute;right:15px;top:50%;transform:translateY(-50%);cursor:pointer;opacity:.5;transition:.3s}.pass-group .toggle:hover{opacity:1}"""},
    
    {"name": "Textarea", "category": "Inputs", "tags": ["textarea", "multiline", "message"],
     "html": '<div class="text-group"><textarea placeholder="Your message..."></textarea><span class="count">0/500</span></div>',
     "css": """.text-group{position:relative;width:300px}.text-group textarea{width:100%;height:120px;padding:15px;font-size:14px;color:#fff;background:#1a1a2e;border:2px solid #333;border-radius:12px;outline:none;resize:none;transition:.3s}.text-group textarea:focus{border-color:#667eea}.text-group textarea::placeholder{color:#666}.text-group .count{position:absolute;bottom:10px;right:15px;font-size:12px;color:#666}"""},

    # LOADERS (5)
    {"name": "Pulse Loader", "category": "Loaders", "tags": ["pulse", "dots", "simple"],
     "html": '<div class="pulse-loader"><span></span><span></span><span></span></div>',
     "css": """.pulse-loader{display:flex;gap:8px}.pulse-loader span{width:12px;height:12px;background:#667eea;border-radius:50%;animation:pulse 1.4s infinite}.pulse-loader span:nth-child(2){animation-delay:.2s}.pulse-loader span:nth-child(3){animation-delay:.4s}@keyframes pulse{0%,80%,100%{transform:scale(.6);opacity:.5}40%{transform:scale(1);opacity:1}}"""},
    
    {"name": "Spinner Ring", "category": "Loaders", "tags": ["spinner", "ring", "rotating"],
     "html": '<div class="ring-spinner"></div>',
     "css": """.ring-spinner{width:50px;height:50px;border:4px solid rgba(102,126,234,.2);border-top-color:#667eea;border-radius:50%;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"""},
    
    {"name": "Wave Loader", "category": "Loaders", "tags": ["wave", "bars", "animated"],
     "html": '<div class="wave-loader"><span></span><span></span><span></span><span></span><span></span></div>',
     "css": """.wave-loader{display:flex;gap:4px;align-items:center;height:40px}.wave-loader span{width:6px;height:100%;background:#667eea;border-radius:3px;animation:wave 1s ease-in-out infinite}.wave-loader span:nth-child(2){animation-delay:.1s}.wave-loader span:nth-child(3){animation-delay:.2s}.wave-loader span:nth-child(4){animation-delay:.3s}.wave-loader span:nth-child(5){animation-delay:.4s}@keyframes wave{0%,100%{height:20%}50%{height:100%}}"""},
    
    {"name": "Gradient Spinner", "category": "Loaders", "tags": ["gradient", "colorful", "spinner"],
     "html": '<div class="gradient-spinner"></div>',
     "css": """.gradient-spinner{width:50px;height:50px;border-radius:50%;background:conic-gradient(from 0deg,transparent,#667eea);animation:spin 1s linear infinite;position:relative}.gradient-spinner::after{content:'';position:absolute;inset:5px;background:#0f0f0f;border-radius:50%}@keyframes spin{to{transform:rotate(360deg)}}"""},
    
    {"name": "Bounce Loader", "category": "Loaders", "tags": ["bounce", "ball", "playful"],
     "html": '<div class="bounce-loader"><span></span></div>',
     "css": """.bounce-loader{position:relative;width:60px;height:60px}.bounce-loader span{position:absolute;width:20px;height:20px;background:#667eea;border-radius:50%;animation:bounce .6s ease-in-out infinite alternate}@keyframes bounce{from{transform:translateY(0);box-shadow:0 5px 10px rgba(102,126,234,.4)}to{transform:translateY(-30px);box-shadow:0 20px 20px rgba(102,126,234,.1)}}"""},

    # TOGGLES (5)
    {"name": "iOS Toggle", "category": "Toggle Switches", "tags": ["ios", "switch", "smooth"],
     "html": '<label class="ios-toggle"><input type="checkbox"><span class="slider"></span></label>',
     "css": """.ios-toggle{position:relative;display:inline-block;width:60px;height:34px}.ios-toggle input{opacity:0;width:0;height:0}.ios-toggle .slider{position:absolute;cursor:pointer;inset:0;background:#333;border-radius:34px;transition:.4s}.ios-toggle .slider::before{content:'';position:absolute;height:26px;width:26px;left:4px;bottom:4px;background:#fff;border-radius:50%;transition:.4s}.ios-toggle input:checked+.slider{background:linear-gradient(135deg,#667eea,#764ba2)}.ios-toggle input:checked+.slider::before{transform:translateX(26px)}"""},
    
    {"name": "Day/Night Toggle", "category": "Toggle Switches", "tags": ["day", "night", "theme"],
     "html": '<label class="dn-toggle"><input type="checkbox"><span class="track"><span class="thumb">🌙</span></span></label>',
     "css": """.dn-toggle{position:relative;display:inline-block;width:70px;height:36px}.dn-toggle input{opacity:0;width:0;height:0}.dn-toggle .track{position:absolute;cursor:pointer;inset:0;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:36px;transition:.4s}.dn-toggle .thumb{position:absolute;height:28px;width:28px;left:4px;top:4px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:.4s;font-size:16px}.dn-toggle input:checked+.track{background:linear-gradient(135deg,#ffecd2,#fcb69f)}.dn-toggle input:checked+.track .thumb{transform:translateX(34px);content:'☀️'}"""},
    
    {"name": "Neon Toggle", "category": "Toggle Switches", "tags": ["neon", "glow", "cyberpunk"],
     "html": '<label class="neon-toggle"><input type="checkbox"><span class="slider"></span></label>',
     "css": """.neon-toggle{position:relative;display:inline-block;width:60px;height:30px}.neon-toggle input{opacity:0;width:0;height:0}.neon-toggle .slider{position:absolute;cursor:pointer;inset:0;background:#1a1a2e;border:2px solid #333;border-radius:30px;transition:.4s}.neon-toggle .slider::before{content:'';position:absolute;height:22px;width:22px;left:2px;bottom:2px;background:#666;border-radius:50%;transition:.4s}.neon-toggle input:checked+.slider{border-color:#0ff;box-shadow:0 0 10px #0ff,0 0 20px #0ff}.neon-toggle input:checked+.slider::before{transform:translateX(30px);background:#0ff;box-shadow:0 0 10px #0ff}"""},
    
    {"name": "Minimal Toggle", "category": "Toggle Switches", "tags": ["minimal", "clean", "simple"],
     "html": '<label class="min-toggle"><input type="checkbox"><span class="track"></span></label>',
     "css": """.min-toggle{position:relative;display:inline-block;width:50px;height:24px}.min-toggle input{opacity:0;width:0;height:0}.min-toggle .track{position:absolute;cursor:pointer;inset:0;background:#e0e0e0;border-radius:24px;transition:.3s}.min-toggle .track::before{content:'';position:absolute;height:20px;width:20px;left:2px;top:2px;background:#fff;border-radius:50%;box-shadow:0 2px 5px rgba(0,0,0,.2);transition:.3s}.min-toggle input:checked+.track{background:#667eea}.min-toggle input:checked+.track::before{transform:translateX(26px)}"""},
    
    {"name": "3D Toggle", "category": "Toggle Switches", "tags": ["3d", "depth", "realistic"],
     "html": '<label class="toggle-3d"><input type="checkbox"><span class="slider"></span></label>',
     "css": """.toggle-3d{position:relative;display:inline-block;width:60px;height:34px}.toggle-3d input{opacity:0;width:0;height:0}.toggle-3d .slider{position:absolute;cursor:pointer;inset:0;background:#444;border-radius:34px;box-shadow:inset 0 2px 10px rgba(0,0,0,.5);transition:.4s}.toggle-3d .slider::before{content:'';position:absolute;height:26px;width:26px;left:4px;bottom:4px;background:linear-gradient(180deg,#fff,#e0e0e0);border-radius:50%;box-shadow:0 2px 5px rgba(0,0,0,.3);transition:.4s}.toggle-3d input:checked+.slider{background:linear-gradient(135deg,#667eea,#764ba2);box-shadow:inset 0 2px 10px rgba(0,0,0,.3)}.toggle-3d input:checked+.slider::before{transform:translateX(26px)}"""},

    # CHECKBOXES (5)
    {"name": "Animated Checkbox", "category": "Checkboxes", "tags": ["animated", "checkmark", "smooth"],
     "html": '<label class="anim-check"><input type="checkbox"><span class="mark"></span><span>Accept terms</span></label>',
     "css": """.anim-check{display:flex;align-items:center;gap:10px;cursor:pointer;color:#fff}.anim-check input{display:none}.anim-check .mark{width:24px;height:24px;border:2px solid #667eea;border-radius:6px;position:relative;transition:.3s}.anim-check .mark::after{content:'';position:absolute;left:7px;top:3px;width:6px;height:12px;border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg) scale(0);transition:.2s}.anim-check input:checked+.mark{background:linear-gradient(135deg,#667eea,#764ba2);border-color:transparent}.anim-check input:checked+.mark::after{transform:rotate(45deg) scale(1)}"""},
    
    {"name": "Circle Checkbox", "category": "Checkboxes", "tags": ["circle", "round", "modern"],
     "html": '<label class="circle-check"><input type="checkbox"><span class="circle"></span><span>Remember me</span></label>',
     "css": """.circle-check{display:flex;align-items:center;gap:10px;cursor:pointer;color:#fff}.circle-check input{display:none}.circle-check .circle{width:24px;height:24px;border:2px solid #444;border-radius:50%;position:relative;transition:.3s}.circle-check .circle::after{content:'';position:absolute;inset:4px;background:#667eea;border-radius:50%;transform:scale(0);transition:.2s}.circle-check input:checked+.circle{border-color:#667eea}.circle-check input:checked+.circle::after{transform:scale(1)}"""},
    
    {"name": "Cross Checkbox", "category": "Checkboxes", "tags": ["cross", "x", "delete"],
     "html": '<label class="cross-check"><input type="checkbox"><span class="box"></span><span>Delete item</span></label>',
     "css": """.cross-check{display:flex;align-items:center;gap:10px;cursor:pointer;color:#fff}.cross-check input{display:none}.cross-check .box{width:24px;height:24px;border:2px solid #ff6b6b;border-radius:6px;position:relative;transition:.3s}.cross-check .box::before,.cross-check .box::after{content:'';position:absolute;left:10px;top:4px;width:2px;height:14px;background:#ff6b6b;transform:scale(0);transition:.2s}.cross-check .box::before{transform:rotate(45deg) scale(0)}.cross-check .box::after{transform:rotate(-45deg) scale(0)}.cross-check input:checked+.box{background:#ff6b6b}.cross-check input:checked+.box::before{transform:rotate(45deg) scale(1);background:#fff}.cross-check input:checked+.box::after{transform:rotate(-45deg) scale(1);background:#fff}"""},
    
    {"name": "Bounce Checkbox", "category": "Checkboxes", "tags": ["bounce", "elastic", "fun"],
     "html": '<label class="bounce-check"><input type="checkbox"><span class="box"></span><span>Enable notifications</span></label>',
     "css": """.bounce-check{display:flex;align-items:center;gap:10px;cursor:pointer;color:#fff}.bounce-check input{display:none}.bounce-check .box{width:24px;height:24px;border:2px solid #4ade80;border-radius:6px;position:relative;transition:.2s}.bounce-check .box::after{content:'✓';position:absolute;left:3px;top:-2px;font-size:18px;color:#4ade80;transform:scale(0);transition:.3s cubic-bezier(.68,-.55,.27,1.55)}.bounce-check input:checked+.box::after{transform:scale(1)}.bounce-check input:checked+.box{animation:bounce-pop .4s}@keyframes bounce-pop{50%{transform:scale(1.2)}}"""},
    
    {"name": "Slide Checkbox", "category": "Checkboxes", "tags": ["slide", "horizontal", "smooth"],
     "html": '<label class="slide-check"><input type="checkbox"><span class="track"><span class="fill"></span></span><span>Active</span></label>',
     "css": """.slide-check{display:flex;align-items:center;gap:10px;cursor:pointer;color:#fff}.slide-check input{display:none}.slide-check .track{width:40px;height:24px;border:2px solid #444;border-radius:6px;position:relative;overflow:hidden}.slide-check .fill{position:absolute;left:-100%;top:0;width:100%;height:100%;background:linear-gradient(135deg,#667eea,#764ba2);transition:.3s}.slide-check input:checked+.track .fill{left:0}.slide-check input:checked+.track{border-color:#667eea}"""},
]


async def main():
    print("=" * 60)
    print("🎨 UIverse Component Uploader")
    print("=" * 60)
    print(f"Components to upload: {len(COMPONENTS)}")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.user_management_db
    collection = db.components
    
    # Get user_id
    user = await db.users.find_one({})
    user_id = user["_id"] if user else ObjectId("000000000000000000000001")
    
    added, skipped = 0, 0
    
    for comp in COMPONENTS:
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
