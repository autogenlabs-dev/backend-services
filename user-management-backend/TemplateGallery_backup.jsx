'use client';
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Grid3X3, List, Star, Download, Eye, Code, Trash2, Edit } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { marketplaceApi } from '../../../lib/marketplaceApi';
import { useAuth } from '../../../contexts/AuthContext';
import { useNotification } from '../../../contexts/NotificationContext';

const TemplateGallery = () => {
  const { user } = useAuth();
  const { showSuccess, showError } = useNotification();
  const [mounted, setMounted] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedType, setSelectedType] = useState('All');
  const [selectedPlan, setSelectedPlan] = useState('All');
  const [sortBy, setSortBy] = useState('popular');
  const [viewMode, setViewMode] = useState('grid');
  const [filteredTemplates, setFilteredTemplates] = useState([]);
  const [showMyContent, setShowMyContent] = useState(false);

  // Check if user can create templates (developer or admin)
  const canCreateTemplates = user?.role === 'developer' || user?.role === 'admin';
  
  // Check if user can see My Templates section (developer or admin)
  const canSeeMyTemplates = user?.role === 'developer' || user?.role === 'admin';
  
  // Helper function to check if edit/delete icons should be shown
  const shouldShowEditDelete = (template) => {
    const isAdmin = user?.role === 'admin';
    const isDeveloper = user?.role === 'developer';
    const isUser = user?.role === 'user' || !user?.role;
    
    // Users can never edit/delete
    if (isUser) return false;
    
    // Admin can edit/delete any template
    if (isAdmin) return true;
    
    // Developer can only edit/delete their own templates if not approved
    if (isDeveloper) {
      const templateUserId = template.user_id || template.userId || template.creator_id;
      const currentUserId = user?.id || user?._id;
      const isOwnTemplate = String(templateUserId) === String(currentUserId);
      const isApproved = template.status === 'approved' || template.approval_status === 'approved';
      
      // Developer can edit/delete own templates only if not approved
      return isOwnTemplate && !isApproved;
    }
    
    return false;
  };
  
  // Debug logging
  console.log('ðŸ” TemplateGallery Debug:', {
    user,
    userRole: user?.role,
    canCreateTemplates,
    canSeeMyTemplates,
    showMyContent,
    isAdmin: user?.role === 'admin',
    isDeveloper: user?.role === 'developer'
  });

  // Template categories
  const templateCategories = [
    'Dashboard',
    'Landing Page',
    'E-commerce',
    'Portfolio',
    'Blog',
    'Business',
    'Creative',
    'Admin Panel',
    'SaaS',
    'Educational',
    'Healthcare',
    'Finance',
    'Real Estate',
    'Food & Restaurant',
    'Travel',
    'Technology',
    'Other'
  ];

  useEffect(() => {
    setMounted(true);
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let response;
      if (showMyContent && canSeeMyTemplates) {
        // Use dedicated endpoint for user's own templates
        response = await marketplaceApi.getUserTemplates({
          limit: 100,
          skip: 0
        });
      } else {
        // Use main endpoint for all approved templates
        response = await marketplaceApi.getTemplates({
          limit: 100,
          sort_by: 'popular'
        });
      }
      
      setTemplates(response.templates || []);
      setFilteredTemplates(response.templates || []);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
      setError('Failed to load templates. Please try again.');
      setTemplates([]);
      setFilteredTemplates([]);
    } finally {
      setLoading(false);
    }
  };

  // Refetch when showMyContent changes
  useEffect(() => {
    if (mounted) {
      fetchTemplates();
    }
  }, [showMyContent]);

  // Filter and sort templates
  useEffect(() => {
    let filtered = templates.filter(template => {
      const matchesSearch = template.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           template.description?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || template.category === selectedCategory;
      // Note: Backend API might use different field names
      const matchesDifficulty = selectedDifficulty === 'All' || template.difficulty_level === selectedDifficulty;
      const matchesType = selectedType === 'All' || template.item_type === selectedType;
      const matchesPlan = selectedPlan === 'All' || 
                         (selectedPlan === 'Free' && (template.plan_type === 'Free' || template.planType === 'Free'));

      return matchesSearch && matchesCategory && matchesDifficulty && matchesType && matchesPlan;
    });

    // Sort templates
    switch (sortBy) {
      case 'popular':
        filtered.sort((a, b) => (b.download_count || 0) - (a.download_count || 0));
        break;
      case 'rating':
        filtered.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0));
        break;
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
        break;
      default:
        break;
    }

    setFilteredTemplates(filtered);
  }, [templates, searchTerm, selectedCategory, selectedDifficulty, selectedType, selectedPlan, sortBy]);

  const getDifficultyColor = (level) => {
    switch (level) {
      case 'Easy': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Tough': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getPlanColor = (planType) => {
    return planType === 'Free' 
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
      : 'bg-purple-500/20 text-purple-400 border-purple-500/30';
  };

  const handleDelete = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      await marketplaceApi.deleteTemplate(templateId);
      // Refresh the templates list
      fetchTemplates();
      showSuccess('Template deleted successfully!');
    } catch (error) {
      console.error('Failed to delete template:', error);
      showError('Failed to delete template. Please try again.');
    }
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <section className="relative w-full bg-[linear-gradient(180deg,#0D0B12_0%,#040406_100%)] text-white py-20">
        <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-8">
          <div className="text-center">
            <div className="w-12 h-12 bg-gray-300 rounded-full animate-pulse mx-auto"></div>
            <p className="text-gray-400 mt-4">Loading templates...</p>
          </div>
        </div>
      </section>
    );
  }

  // Loading state
  if (loading) {
    return (
      <section className="relative w-full bg-[linear-gradient(180deg,#0D0B12_0%,#040406_100%)] text-white py-20">
        <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-8">
          <div className="text-center">
            <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full animate-spin mx-auto">
              <div className="w-full h-full rounded-full border-2 border-white/20 border-t-white"></div>
            </div>
            <p className="text-gray-400 mt-4">Loading templates...</p>
          </div>
        </div>
      </section>
    );
  }

  // Error state
  if (error) {
    return (
      <section className="relative w-full bg-[linear-gradient(180deg,#0D0B12_0%,#040406_100%)] text-white py-20">
        <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-red-400 text-2xl">âš </span>
            </div>
            <h3 className="text-xl font-semibold text-red-400 mb-2">Failed to load templates</h3>
            <p className="text-gray-400 mb-4">{error}</p>
            <button 
              onClick={fetchTemplates}
              className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative w-full bg-[linear-gradient(180deg,#0D0B12_0%,#040406_100%)] text-white py-20">
      
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-r from-emerald-500/5 to-teal-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-gradient-to-r from-indigo-500/5 to-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-8">
        
        {/* Section Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex flex-col items-center justify-between mb-6 md:flex-row">
            <div className="text-center md:text-left mb-4 md:mb-0">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                {showMyContent ? 'My ' : ''}Template{' '}
                <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                  Library
                </span>
              </h2>
              <p className="text-lg text-gray-400 max-w-2xl">
                {showMyContent 
                  ? 'Manage your submitted templates and track their approval status'
                  : 'Discover our curated collection of beautiful, modern UI templates with live previews'
                }
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Templates/My Templates Toggle for Developers and Admins */}
              {canSeeMyTemplates && (
                <div className="flex rounded-lg bg-white/10 p-1">
                  <button
                    onClick={() => setShowMyContent(false)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      !showMyContent 
                        ? 'bg-emerald-600 text-white' 
                        : 'text-gray-300 hover:text-white'
                    }`}
                  >
                    Templates
                  </button>
                  <button
                    onClick={() => setShowMyContent(true)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      showMyContent 
                        ? 'bg-emerald-600 text-white' 
                        : 'text-gray-300 hover:text-white'
                    }`}
                  >
                    My Templates
                  </button>
                </div>
              )}
              
              {/* Create Template Button - Only for Developers and Admins */}
              {canCreateTemplates && (
                <Link href="/templates/create">
                  <button className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-emerald-500/25 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Create Template
                  </button>
                </Link>
              )}
            </div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {/* Search Bar */}
          <div className="relative mb-6">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50"
            />
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-6">
            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:border-blue-500/50"
            >
              <option value="All" className="bg-gray-800">All Categories</option>
              {templateCategories.map(category => (
                <option key={category} value={category} className="bg-gray-800">
                  {category}
                </option>
              ))}
            </select>

            {/* Difficulty Filter */}
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:border-blue-500/50"
            >
              <option value="All" className="bg-gray-800">All Levels</option>
              <option value="Easy" className="bg-gray-800">Easy</option>
              <option value="Medium" className="bg-gray-800">Medium</option>
              <option value="Tough" className="bg-gray-800">Tough</option>
            </select>

            {/* Type Filter */}
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:border-blue-500/50"
            >
              <option value="All" className="bg-gray-800">All Types</option>
              <option value="React" className="bg-gray-800">React</option>
              <option value="Vue" className="bg-gray-800">Vue</option>
              <option value="Angular" className="bg-gray-800">Angular</option>
              <option value="HTML/CSS" className="bg-gray-800">HTML/CSS</option>
            </select>

            {/* Plan Filter */}
            <select
              value={selectedPlan}
              onChange={(e) => setSelectedPlan(e.target.value)}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:border-blue-500/50"
            >
              <option value="All" className="bg-gray-800">All Plans</option>
              <option value="Free" className="bg-gray-800">Free</option>
            </select>

            {/* Sort Filter */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white focus:outline-none focus:border-blue-500/50"
            >
              <option value="popular" className="bg-gray-800">Most Popular</option>
              <option value="rating" className="bg-gray-800">Highest Rated</option>
              <option value="newest" className="bg-gray-800">Newest</option>
            </select>

            {/* View Mode Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`flex-1 p-3 rounded-xl transition-all duration-300 ${
                  viewMode === 'grid' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white/10 text-gray-400 hover:bg-white/15'
                }`}
              >
                <Grid3X3 className="w-5 h-5 mx-auto" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`flex-1 p-3 rounded-xl transition-all duration-300 ${
                  viewMode === 'list' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white/10 text-gray-400 hover:bg-white/15'
                }`}
              >
                <List className="w-5 h-5 mx-auto" />
              </button>
            </div>
          </div>

          {/* Results Count */}
          <div className="text-sm text-gray-400">
            Showing {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''}
          </div>
        </motion.div>

        {/* Templates Layout - 2 LARGE CARDS PER ROW */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {filteredTemplates.map((template, index) => (
            <motion.div
              key={String(template.id || template._id)}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, delay: (index % 8) * 0.1 }}
              whileHover={{ scale: 1.02, y: -5 }}
              className="group w-full cursor-pointer"
            >
              <div className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl overflow-hidden transition-all duration-500 hover:bg-white/10 hover:border-white/20 hover:shadow-2xl hover:shadow-blue-500/10">
                
                {/* Template Image Preview - Full Card */}
                <div className="relative w-full h-80 bg-gradient-to-br from-gray-800 to-gray-900 overflow-hidden">
                  {template.preview_images && template.preview_images.length > 0 ? (
                    /* Cloudinary preview image */
                    <Image
                      src={template.preview_images[0]}
                      alt={template.title}
                      fill
                      className="object-cover transition-all duration-700 group-hover:scale-110"
                      sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                    />
                  ) : template.live_demo_url ? (
                    /* Screenshot preview from backend API if no Cloudinary image */
                    <Image
                      src={`${process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'}/api/screenshot?url=${encodeURIComponent(template.live_demo_url)}&width=800&height=600`}
                      alt={template.title}
                      fill
                      className="object-cover transition-all duration-700 group-hover:scale-110"
                      sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  ) : (
                    // Fallback display when no image
                    <div className="absolute inset-0 flex items-center justify-center text-white p-6">
                      <div className="text-center">
                        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                          <Code className="w-8 h-8" />
                        </div>
                        <p className="text-xs text-gray-400">No Preview</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Dark overlay for better text visibility */}
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-all duration-300"></div>
                  
                  {/* View Details Icon - Top Right Corner */}
                  {shouldShowEditDelete(template) ? (
                    /* Show Edit and Delete icons for authorized users */
                    <div className="absolute top-3 right-3 flex gap-2 z-10">
                      <Link href={`/templates/${String(template.id || template._id)}`} onClick={(e) => e.stopPropagation()}>
                        <button className="w-8 h-8 bg-white/20 backdrop-blur-md border border-white/30 rounded-full flex items-center justify-center text-white hover:bg-white/30 hover:scale-110 transition-all duration-300 group/btn">
                          <Eye className="w-4 h-4 group-hover/btn:scale-110 transition-transform duration-200" />
                        </button>
                      </Link>
                      <Link href={`/templates/${String(template.id || template._id)}/edit`} onClick={(e) => e.stopPropagation()}>
                        <button className="w-8 h-8 bg-blue-500/20 backdrop-blur-md border border-blue-500/30 rounded-full flex items-center justify-center text-blue-300 hover:bg-blue-500/30 hover:scale-110 transition-all duration-300 group/btn">
                          <Edit className="w-4 h-4 group-hover/btn:scale-110 transition-transform duration-200" />
                        </button>
                      </Link>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(template.id || template._id);
                        }}
                        className="w-8 h-8 bg-red-500/20 backdrop-blur-md border border-red-500/30 rounded-full flex items-center justify-center text-red-300 hover:bg-red-500/30 hover:scale-110 transition-all duration-300 group/btn"
                      >
                        <Trash2 className="w-4 h-4 group-hover/btn:scale-110 transition-transform duration-200" />
                      </button>
                    </div>
                  ) : (
                    /* Show only View icon */
                    <Link href={`/templates/${String(template.id || template._id)}`} onClick={(e) => e.stopPropagation()}>
                      <button className="absolute top-3 right-3 w-8 h-8 bg-white/20 backdrop-blur-md border border-white/30 rounded-full flex items-center justify-center text-white hover:bg-white/30 hover:scale-110 transition-all duration-300 z-10 group/btn">
                        <Eye className="w-4 h-4 group-hover/btn:scale-110 transition-transform duration-200" />
                      </button>
                    </Link>
                  )}

                  {/* Status Badge - If pending/rejected */}
                  {(() => {
                    const status = template.status || template.approval_status;
                    return status && status !== 'approved' && (
                      <div className="absolute bottom-3 left-3 z-10">
                        <span className={`px-2 py-1 text-xs font-bold rounded-full shadow-lg ${
                          status === 'pending' || status === 'pending_approval'
                            ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                            : 'bg-red-500/20 text-red-400 border-red-500/30'
                        }`}>
                          {status}
                        </span>
                      </div>
                    );
                  })()}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* No Results */}
        {filteredTemplates.length === 0 && (
          <motion.div
            className="text-center py-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="w-24 h-24 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <Search className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">No Templates Found</h3>
            <p className="text-gray-400 mb-8">Try adjusting your search criteria or filters</p>
            <button 
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('All');
                setSelectedDifficulty('All');
                setSelectedType('All');
                setSelectedPlan('All');
              }}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-semibold rounded-xl transition-all duration-300 hover:scale-105"
            >
              Clear All Filters
            </button>
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default TemplateGallery;


