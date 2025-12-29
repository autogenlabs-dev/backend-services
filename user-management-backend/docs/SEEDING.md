# Database Seeding Guide

## Quick Start

```bash
# Seed the database (keeps existing data)
python seed_database.py

# Clear existing data and reseed
python seed_database.py --clear
```

## What Gets Seeded

### Templates (5 items)
1. **Modern SaaS Landing Page** - Next.js landing page
2. **E-Commerce Store** - Full e-commerce template with Stripe
3. **Admin Dashboard Pro** - Enterprise dashboard
4. **Portfolio Website** - Developer/designer portfolio
5. **Blog Platform** - Modern blog with MDX

### Components (5 items)
1. **Modern Button Set** - Accessible button components
2. **Advanced Data Table** - Enterprise data grid
3. **Modal Dialog System** - Accessible modals
4. **Form Components Kit** - Complete form library
5. **Chart Library Pro** - Data visualization

## All Data Features

- ✅ Approved status (visible immediately)
- ✅ Realistic ratings (4.5 - 4.9 stars)
- ✅ Download counts
- ✅ View counts
- ✅ Like counts
- ✅ GitHub repo URLs
- ✅ Live demo URLs
- ✅ Dependencies
- ✅ Tags for search
- ✅ Featured/popular flags

## View the Results

After seeding, check your application:

**Local**: http://localhost:3000/templates  
**Local**: http://localhost:3000/components  

**Production**: https://www.codemurf.com/templates  
**Production**: https://www.codemurf.com/components  

## Troubleshooting

**"No users found"**  
- Seed script will still work, just creates items without user_id
- Not a problem for display purposes

**"Connection timeout"**  
- Check your MongoDB connection string in `.env`
- Verify MongoDB Atlas is accessible

**"Duplicate key error"**  
- Use `--clear` flag to remove existing data first
- Or manually clear collections in MongoDB

## Adding More Data

To add more templates/components, edit `seed_database.py`:

1. Add new items to `templates_data` or `components_data` lists
2. Follow the same structure as existing items
3. Run the seed script again

## Database Collections

This script populates:
- `templates` - Template collection
- `components` - Component collection

Related collections (not seeded):
- `template_likes` - User likes
- `template_downloads` - Download tracking
- `template_views` - View tracking
- Similar collections for components
