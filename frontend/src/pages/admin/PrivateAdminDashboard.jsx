import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield, Building2, Crown, Phone, Calendar, Clock, AlertTriangle, CheckCircle2,
  XCircle, Download, RefreshCw, Eye, LogOut, Search, Filter, Lock, Unlock,
  Mail, UserCheck, AlertCircle, FileText, ChevronLeft, ChevronRight, Check,
  Send, Sparkles, User, Tag, HelpCircle, Layers
} from 'lucide-react';
import adminService from '../../services/adminService';

export const PrivateAdminDashboard = () => {
  const navigate = useNavigate();
  const currentAdmin = adminService.getCurrentAdmin();

  // Authentication check
  useEffect(() => {
    if (!adminService.isAuthenticated()) {
      navigate('/admin/login');
    }
  }, [navigate]);

  // Tab State: 'properties' | 'leads' | 'visits' | 'audit'
  const [activeTab, setActiveTab] = useState('properties');

  // KPI Stats
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  // Properties State
  const [properties, setProperties] = useState([]);
  const [propPage, setPropPage] = useState(1);
  const [propTotalPages, setPropTotalPages] = useState(1);
  const [propTotal, setPropTotal] = useState(0);
  const [propSearch, setPropSearch] = useState('');
  const [propVisibility, setPropVisibility] = useState('ALL');
  const [propLoading, setPropLoading] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [ownerContactForm, setOwnerContactForm] = useState(null);
  const [ownerUpdating, setOwnerUpdating] = useState(false);

  // Leads State
  const [leads, setLeads] = useState([]);
  const [leadPage, setLeadPage] = useState(1);
  const [leadTotalPages, setLeadTotalPages] = useState(1);
  const [leadTotal, setLeadTotal] = useState(0);
  const [leadStatusFilter, setLeadStatusFilter] = useState('ALL');
  const [leadSearch, setLeadSearch] = useState('');
  const [leadLoading, setLeadLoading] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [actionMessage, setActionMessage] = useState({ text: '', type: '' });
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  // Site Visits State
  const [visits, setVisits] = useState([]);
  const [visitPage, setVisitPage] = useState(1);
  const [visitTotalPages, setVisitTotalPages] = useState(1);
  const [visitTotal, setVisitTotal] = useState(0);
  const [visitStatusFilter, setVisitStatusFilter] = useState('ALL');
  const [visitLoading, setVisitLoading] = useState(false);

  // Subscriptions State
  const [subscriptions, setSubscriptions] = useState([]);
  const [subLoading, setSubLoading] = useState(false);
  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);

  // 1. Fetch Stats
  const fetchStats = useCallback(async () => {
    try {
      setStatsLoading(true);
      const data = await adminService.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error fetching admin stats:', err);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // 2. Fetch Properties
  const fetchProperties = useCallback(async () => {
    try {
      setPropLoading(true);
      const params = {
        page: propPage,
        limit: 15,
        search: propSearch.trim() || undefined,
        visibility: propVisibility !== 'ALL' ? propVisibility : undefined
      };
      const data = await adminService.getProperties(params);
      setProperties(data.items || []);
      setPropTotal(data.total || 0);
      setPropTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Error fetching properties:', err);
    } finally {
      setPropLoading(false);
    }
  }, [propPage, propSearch, propVisibility]);

  // 3. Fetch Leads
  const fetchLeads = useCallback(async () => {
    try {
      setLeadLoading(true);
      const params = {
        page: leadPage,
        limit: 15,
        status: leadStatusFilter !== 'ALL' ? leadStatusFilter : undefined,
        search: leadSearch.trim() || undefined
      };
      const data = await adminService.getLeads(params);
      setLeads(data.items || []);
      setLeadTotal(data.total || 0);
      setLeadTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Error fetching leads:', err);
    } finally {
      setLeadLoading(false);
    }
  }, [leadPage, leadStatusFilter, leadSearch]);

  // 5. Fetch Subscriptions
  const fetchSubscriptions = useCallback(async () => {
    try {
      setSubLoading(true);
      const data = await adminService.getSubscriptions();
      setSubscriptions(data.subscriptions || []);
    } catch (err) {
      console.error('Error fetching admin subscriptions:', err);
    } finally {
      setSubLoading(false);
    }
  }, []);
  // 4. Fetch Site Visits
  const fetchVisits = useCallback(async () => {
    try {
      setVisitLoading(true);
      const params = {
        page: visitPage,
        limit: 15,
        status: visitStatusFilter !== 'ALL' ? visitStatusFilter : undefined
      };
      const data = await adminService.getSiteVisits(params);
      setVisits(data.items || []);
      setVisitTotal(data.total || 0);
      setVisitTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Error fetching visits:', err);
    } finally {
      setVisitLoading(false);
    }
  }, [visitPage, visitStatusFilter]);

  // 5. Fetch Audit Logs
  const fetchAuditLogs = useCallback(async () => {
    try {
      setAuditLoading(true);
      const data = await adminService.getAuditLogs(50);
      setAuditLogs(data || []);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    } finally {
      setAuditLoading(false);
    }
  }, []);

  // Initial Data Load
  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  useEffect(() => {
    if (activeTab === 'properties') fetchProperties();
    else if (activeTab === 'leads') fetchLeads();
    else if (activeTab === 'visits') fetchVisits();
    else if (activeTab === 'audit') fetchAuditLogs();
  }, [activeTab, fetchProperties, fetchLeads, fetchVisits, fetchAuditLogs]);

  // Handle Logout
  const handleLogout = () => {
    adminService.logout();
    navigate('/admin/login');
  };

  // Toggle Property Visibility
  const handleToggleVisibility = async (propertyId, currentStatus) => {
    const nextStatus = currentStatus === 'PRIVATE' ? 'PUBLIC' : 'PRIVATE';
    try {
      await adminService.toggleVisibility(propertyId, nextStatus);
      fetchProperties();
      fetchStats();
    } catch (err) {
      alert('Failed to update property visibility: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Open Property Details Drawer
  const handleOpenPropertyDetails = async (propertyId) => {
    try {
      const data = await adminService.getPropertyDetails(propertyId);
      setSelectedProperty(data);
      setOwnerContactForm(data.private_contact || {
        contact_name: '',
        contact_type: 'OWNER',
        phone: '',
        email: '',
        source: 'Manual Verification',
        verification_status: 'UNVERIFIED',
        permission_status: 'PENDING',
        notes: ''
      });
    } catch (err) {
      alert('Failed to load property details: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Save Owner Contact
  const handleSaveOwnerContact = async (e) => {
    e.preventDefault();
    if (!selectedProperty) return;
    try {
      setOwnerUpdating(true);
      await adminService.updateOwnerContact(selectedProperty.property.id, ownerContactForm);
      await handleOpenPropertyDetails(selectedProperty.property.id);
      fetchProperties();
      alert('Private owner contact updated successfully.');
    } catch (err) {
      alert('Failed to update owner contact: ' + (err.response?.data?.detail || err.message));
    } finally {
      setOwnerUpdating(false);
    }
  };

  // Open Lead Details Modal
  const handleOpenLeadDetails = async (leadId) => {
    setActionMessage({ text: '', type: '' });
    try {
      const data = await adminService.getLeadDetails(leadId);
      setSelectedLead(data);
    } catch (err) {
      alert('Failed to load lead details: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Approve Lead
  const handleApproveLead = async (leadId) => {
    try {
      await adminService.approveLead(leadId);
      await handleOpenLeadDetails(leadId);
      fetchLeads();
      fetchStats();
      setActionMessage({ text: 'Lead approved successfully (Status: VALID).', type: 'success' });
    } catch (err) {
      setActionMessage({ text: 'Failed to approve lead: ' + (err.response?.data?.detail || err.message), type: 'error' });
    }
  };

  // Reject Lead
  const handleRejectLead = async (leadId) => {
    try {
      await adminService.rejectLead(leadId);
      await handleOpenLeadDetails(leadId);
      fetchLeads();
      fetchStats();
      setActionMessage({ text: 'Lead rejected (Status: CLOSED).', type: 'info' });
    } catch (err) {
      setActionMessage({ text: 'Failed to reject lead: ' + (err.response?.data?.detail || err.message), type: 'error' });
    }
  };

  // Mark Lead as Spam
  const handleMarkSpam = async (leadId) => {
    try {
      await adminService.markLeadSpam(leadId);
      await handleOpenLeadDetails(leadId);
      fetchLeads();
      fetchStats();
      setActionMessage({ text: 'Lead flagged as SPAM (invalid/rubbish).', type: 'warning' });
    } catch (err) {
      setActionMessage({ text: 'Failed to mark spam: ' + (err.response?.data?.detail || err.message), type: 'error' });
    }
  };

  // Send Lead to Owner
  const handleSendLeadToOwner = async (leadId) => {
    try {
      const result = await adminService.sendLeadToOwner(leadId);
      await handleOpenLeadDetails(leadId);
      fetchLeads();
      if (result.status === 'NOT_CONFIGURED') {
        setActionMessage({
          text: `Owner notification channel not configured. Lead is stored safely in database. Owner Contact: ${result.owner_contact?.name} (${result.owner_contact?.phone || 'No phone'}).`,
          type: 'warning'
        });
      } else if (result.success) {
        setActionMessage({ text: result.message, type: 'success' });
      } else {
        setActionMessage({ text: result.message, type: 'error' });
      }
    } catch (err) {
      setActionMessage({ text: 'Failed to send lead: ' + (err.response?.data?.detail || err.message), type: 'error' });
    }
  };

  // Download Lead PDF
  const handleDownloadPdf = async (leadId, leadCode) => {
    try {
      setDownloadingPdf(true);
      await adminService.downloadLeadPdf(leadId, leadCode);
    } catch (err) {
      alert('Failed to generate PDF: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Update Site Visit Status
  const handleUpdateVisitStatus = async (visitId, newStatus) => {
    try {
      await adminService.updateSiteVisit(visitId, { status: newStatus });
      fetchVisits();
      fetchStats();
    } catch (err) {
      alert('Failed to update site visit: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-purple-500 selection:text-white">
      {/* 1. TOP SECURE ADMIN HEADER */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-brand-500 p-0.5 shadow-md shadow-purple-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-purple-400" />
            </div>
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-white font-outfit flex items-center gap-2">
              <span>🔐 GeoSmart Private Property & Lead Dashboard</span>
            </h1>
            <div className="flex items-center gap-2 text-[11px] text-slate-400">
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Authenticated Private Portal
              </span>
              <span>•</span>
              <span className="font-mono text-slate-500">{currentAdmin?.email || 'admin@geosmart.ai'}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={() => {
              fetchStats();
              if (activeTab === 'properties') fetchProperties();
              if (activeTab === 'leads') fetchLeads();
              if (activeTab === 'visits') fetchVisits();
              if (activeTab === 'audit') fetchAuditLogs();
            }}
            title="Refresh Live Data"
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer border border-slate-700/60"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleLogout}
            className="px-3.5 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 font-semibold text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* 2. MAIN CONTAINER */}
      <main className="flex-1 px-4 sm:px-8 py-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* KPI SUMMARY CARDS (10 METRICS DIRECT FROM DB) */}
        <section className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Live System Intelligence Metrics
            </h3>
            {statsLoading && <span className="text-[10px] text-slate-500 font-mono">Syncing database...</span>}
          </div>

          {/* REQUIRED SECTION 11: TELEPHONY & CALL METRICS */}
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
            {/* Card 1: Total Calls */}
            <div className="glass-card p-3.5 rounded-2xl border border-purple-500/20 bg-purple-950/10 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase text-purple-300">Total Calls</span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-purple-300 font-mono">{stats?.total_calls ?? stats?.owner_callbacks ?? '—'}</span>
                <Phone className="w-4 h-4 text-purple-400" />
              </div>
            </div>

            {/* Card 2: Completed Calls */}
            <div className="glass-card p-3.5 rounded-2xl border border-emerald-500/20 bg-emerald-950/10 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase text-emerald-300">Completed Calls</span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-emerald-400 font-mono">{stats?.completed_calls ?? '0'}</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
            </div>

            {/* Card 3: Failed / Telephony Unconfigured */}
            <div className="glass-card p-3.5 rounded-2xl border border-amber-500/20 bg-amber-950/10 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase text-amber-300">Failed / Unconfig</span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-amber-400 font-mono">{stats?.failed_calls ?? '0'}</span>
                <AlertCircle className="w-4 h-4 text-amber-400" />
              </div>
            </div>

            {/* Card 4: New Leads */}
            <div className="glass-card p-3.5 rounded-2xl border border-indigo-500/20 bg-indigo-950/10 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase text-indigo-300">New Leads</span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-indigo-400 font-mono">{stats?.new_leads ?? stats?.new_requests ?? '—'}</span>
                <Sparkles className="w-4 h-4 text-indigo-400" />
              </div>
            </div>

            {/* Card 5: Site Visit Requests */}
            <div className="glass-card p-3.5 rounded-2xl border border-sky-500/20 bg-sky-950/10 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase text-sky-300">Site Visit Requests</span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-sky-400 font-mono">{stats?.site_visit_requests ?? '—'}</span>
                <Calendar className="w-4 h-4 text-sky-400" />
              </div>
            </div>

            {/* Card 6: Leads Needing Review */}
            <div className="glass-card p-3.5 rounded-2xl border border-yellow-500/20 bg-yellow-950/10 flex flex-col justify-between">
              <span className="text-[10px] font-bold uppercase text-yellow-300">Needs Review</span>
              <div className="mt-1 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-yellow-400 font-mono">{stats?.leads_needing_review ?? stats?.pending_review ?? '—'}</span>
                <Clock className="w-4 h-4 text-yellow-400" />
              </div>
            </div>
          </div>
        </section>

        {/* 3. TABS NAVIGATION */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('properties')}
            className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'properties'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Building2 className="w-4 h-4" />
            <span>🏠 Property Listings</span>
          </button>

          <button
            onClick={() => setActiveTab('leads')}
            className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'leads'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Phone className="w-4 h-4" />
            <span>📞 AI Leads & User Requests</span>
          </button>

          <button
            onClick={() => setActiveTab('visits')}
            className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'visits'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Calendar className="w-4 h-4" />
            <span>📅 Site Visits</span>
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'audit'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>🛡️ Audit Log</span>
          </button>
          <button
            onClick={() => setActiveTab('subscriptions')}
            className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center gap-2 cursor-pointer ${
              activeTab === 'subscriptions'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/25'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Crown className="w-4 h-4 text-amber-400" />
            <span>💳 PropPulse Pro Subscriptions</span>
          </button>
        </div>

        {/* 4. TAB CONTENT: PROPERTIES */}
        {activeTab === 'properties' && (
          <div className="space-y-4">
            {/* Filter Controls */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <div className="relative flex-1 sm:w-72">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search by ID, name, locality..."
                    value={propSearch}
                    onChange={(e) => {
                      setPropSearch(e.target.value);
                      setPropPage(1);
                    }}
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div className="flex items-center gap-1.5">
                  {['ALL', 'PUBLIC', 'PRIVATE'].map((vis) => (
                    <button
                      key={vis}
                      onClick={() => {
                        setPropVisibility(vis);
                        setPropPage(1);
                      }}
                      className={`px-3 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                        propVisibility === vis
                          ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20'
                          : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                      }`}
                    >
                      {vis}
                    </button>
                  ))}
                </div>
              </div>

              <div className="text-xs text-slate-400 font-mono">
                Showing {properties.length} of {propTotal} properties
              </div>
            </div>

            {/* Properties Table */}
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase font-semibold">
                    <th className="py-3 px-4">ID</th>
                    <th className="py-3 px-4">Property</th>
                    <th className="py-3 px-4">Location</th>
                    <th className="py-3 px-4">Config</th>
                    <th className="py-3 px-4">Price</th>
                    <th className="py-3 px-4">Visibility</th>
                    <th className="py-3 px-4">Owner / Agent</th>
                    <th className="py-3 px-4">Images</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {propLoading ? (
                    <tr>
                      <td colSpan="9" className="py-8 text-center text-slate-500">
                        Loading properties from database...
                      </td>
                    </tr>
                  ) : properties.length === 0 ? (
                    <tr>
                      <td colSpan="9" className="py-8 text-center text-slate-500">
                        No properties found matching filters.
                      </td>
                    </tr>
                  ) : (
                    properties.map((p) => {
                      const isPrivate = p.visibility_status === 'PRIVATE';
                      const owner = p.private_contact;
                      return (
                        <tr key={p.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-slate-300">#{p.id}</td>
                          <td className="py-3 px-4 font-medium text-white max-w-xs truncate">
                            {p.title}
                          </td>
                          <td className="py-3 px-4 text-slate-300">{p.locality || 'Bengaluru'}</td>
                          <td className="py-3 px-4 text-slate-400">
                            {p.bhk} BHK • {p.property_type}
                          </td>
                          <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                            ₹{p.price ? (p.price / 100000).toFixed(1) + ' L' : 'N/A'}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider inline-flex items-center gap-1 border ${
                                isPrivate
                                  ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                                  : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                              }`}
                            >
                              {isPrivate ? <Lock className="w-2.5 h-2.5" /> : <Unlock className="w-2.5 h-2.5" />}
                              <span>{p.visibility_status}</span>
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            {owner ? (
                              <div className="space-y-0.5">
                                <span className="font-semibold text-slate-200 block truncate max-w-[140px]">
                                  {owner.contact_name}
                                </span>
                                <span
                                  className={`text-[9px] font-bold uppercase px-1.5 py-0.2 rounded border ${
                                    owner.verification_status === 'VERIFIED'
                                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                                  }`}
                                >
                                  {owner.verification_status} ({owner.contact_type})
                                </span>
                              </div>
                            ) : (
                              <span className="text-slate-500 italic">Unassigned</span>
                            )}
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-400">{p.image_count} imgs</td>
                          <td className="py-3 px-4 text-right space-x-2">
                            {/* Visibility Toggle Button */}
                            <button
                              onClick={() => handleToggleVisibility(p.id, p.visibility_status)}
                              className={`px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all border cursor-pointer ${
                                isPrivate
                                  ? 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                                  : 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border-amber-500/30'
                              }`}
                            >
                              {isPrivate ? 'Make Public' : 'Make Private'}
                            </button>

                            {/* View Property Details & Contact Drawer */}
                            <button
                              onClick={() => handleOpenPropertyDetails(p.id)}
                              className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 transition-all cursor-pointer"
                            >
                              Manage
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {propTotalPages > 1 && (
              <div className="flex items-center justify-between py-2 text-xs">
                <span className="text-slate-400">
                  Page {propPage} of {propTotalPages}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    disabled={propPage <= 1}
                    onClick={() => setPropPage((p) => Math.max(1, p - 1))}
                    className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    disabled={propPage >= propTotalPages}
                    onClick={() => setPropPage((p) => Math.min(propTotalPages, p + 1))}
                    className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 5. TAB CONTENT: LEADS & REQUESTS */}
        {activeTab === 'leads' && (
          <div className="space-y-4">
            {/* Filter Pills & Search */}
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="relative flex-1 w-full sm:w-72">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search by lead code, phone, name, property..."
                    value={leadSearch}
                    onChange={(e) => {
                      setLeadSearch(e.target.value);
                      setLeadPage(1);
                    }}
                    className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div className="text-xs text-slate-400 font-mono">
                  Showing {leads.length} of {leadTotal} leads
                </div>
              </div>

              {/* Status Filter Pills */}
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                {[
                  'ALL', 'NEW', 'CONTACTED', 'INTERESTED',
                  'SITE_VISIT_REQUESTED', 'FOLLOW_UP', 'CLOSED', 'SPAM', 'INVALID'
                ].map((st) => (
                  <button
                    key={st}
                    onClick={() => {
                      setLeadStatusFilter(st);
                      setLeadPage(1);
                    }}
                    className={`px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
                      leadStatusFilter === st
                        ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20'
                        : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                    }`}
                  >
                    {st.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Leads Table */}
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase font-semibold">
                    <th className="py-3 px-4">Lead Code</th>
                    <th className="py-3 px-4">Lead Name & Phone</th>
                    <th className="py-3 px-4">Property</th>
                    <th className="py-3 px-4">Budget / BHK</th>
                    <th className="py-3 px-4">Loan</th>
                    <th className="py-3 px-4">Site Visit</th>
                    <th className="py-3 px-4">Validation</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {leadLoading ? (
                    <tr>
                      <td colSpan="9" className="py-8 text-center text-slate-500">
                        Loading AI leads from private database...
                      </td>
                    </tr>
                  ) : leads.length === 0 ? (
                    <tr>
                      <td colSpan="9" className="py-8 text-center text-slate-500">
                        No AI leads found.
                      </td>
                    </tr>
                  ) : (
                    leads.map((l) => {
                      const isSpam = l.validation_status === 'SPAM' || l.lead_status === 'SPAM';
                      return (
                        <tr key={l.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-slate-300">
                            {l.lead_code}
                            {l.is_duplicate && (
                              <span className="block mt-0.5 text-[9px] font-bold text-amber-400 bg-amber-500/10 px-1 py-0.2 rounded border border-amber-500/30">
                                ⚠️ DUPLICATE
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-semibold text-white block">{l.name}</span>
                            <span className="font-mono text-slate-400 text-[11px]">{l.phone}</span>
                          </td>
                          <td className="py-3 px-4 text-slate-300 max-w-xs truncate">
                            {l.property_name}
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-300">
                            {l.budget} • {l.bhk}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                l.loan_required === 'YES'
                                  ? 'bg-emerald-500/10 text-emerald-400'
                                  : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              {l.loan_required}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            {l.site_visit_requested ? (
                              <span className="text-[10px] text-accent-300 font-semibold flex items-center gap-1">
                                <Calendar className="w-3 h-3 text-accent-400" />
                                {l.site_visit_date || 'Requested'}
                              </span>
                            ) : (
                              <span className="text-slate-500 text-[10px]">No</span>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border ${
                                l.validation_status === 'VALID'
                                  ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                                  : isSpam
                                  ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                                  : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                              }`}
                            >
                              {l.validation_status}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-bold text-slate-200 text-[11px]">
                              {l.lead_status.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => handleOpenLeadDetails(l.id)}
                              className="px-3 py-1 rounded-lg text-[11px] font-bold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-sm transition-all cursor-pointer"
                            >
                              Review Lead
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {leadTotalPages > 1 && (
              <div className="flex items-center justify-between py-2 text-xs">
                <span className="text-slate-400">
                  Page {leadPage} of {leadTotalPages}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    disabled={leadPage <= 1}
                    onClick={() => setLeadPage((p) => Math.max(1, p - 1))}
                    className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    disabled={leadPage >= leadTotalPages}
                    onClick={() => setLeadPage((p) => Math.min(leadTotalPages, p + 1))}
                    className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 6. TAB CONTENT: SITE VISITS */}
        {activeTab === 'visits' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
              <div className="flex items-center gap-2">
                {['ALL', 'REQUESTED', 'CONFIRMED', 'COMPLETED', 'CANCELLED'].map((st) => (
                  <button
                    key={st}
                    onClick={() => {
                      setVisitStatusFilter(st);
                      setVisitPage(1);
                    }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      visitStatusFilter === st
                        ? 'bg-purple-600 text-white shadow-md shadow-purple-500/20'
                        : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>
              <span className="text-xs text-slate-400 font-mono">
                {visits.length} of {visitTotal} appointments
              </span>
            </div>

            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase font-semibold">
                    <th className="py-3 px-4">Code</th>
                    <th className="py-3 px-4">Lead Name</th>
                    <th className="py-3 px-4">Phone</th>
                    <th className="py-3 px-4">Property</th>
                    <th className="py-3 px-4">Schedule</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Admin Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {visitLoading ? (
                    <tr>
                      <td colSpan="7" className="py-8 text-center text-slate-500">
                        Loading site visits...
                      </td>
                    </tr>
                  ) : visits.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="py-8 text-center text-slate-500">
                        No site visit appointments scheduled.
                      </td>
                    </tr>
                  ) : (
                    visits.map((v) => (
                      <tr key={v.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4 font-mono font-bold text-slate-300">
                          {v.appointment_code}
                        </td>
                        <td className="py-3 px-4 font-semibold text-white">{v.user_name}</td>
                        <td className="py-3 px-4 font-mono text-slate-400">{v.user_phone}</td>
                        <td className="py-3 px-4 text-slate-300 max-w-xs truncate">
                          {v.property_name}
                        </td>
                        <td className="py-3 px-4 text-slate-300 font-medium">
                          {v.visit_date} • {v.visit_time}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border ${
                              v.status === 'CONFIRMED'
                                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                                : v.status === 'COMPLETED'
                                ? 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                                : v.status === 'CANCELLED'
                                ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                                : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                            }`}
                          >
                            {v.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right space-x-1.5">
                          {v.status !== 'CONFIRMED' && v.status !== 'COMPLETED' && (
                            <button
                              onClick={() => handleUpdateVisitStatus(v.id, 'CONFIRMED')}
                              className="px-2 py-1 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-[10px] font-bold cursor-pointer"
                            >
                              Confirm
                            </button>
                          )}
                          {v.status === 'CONFIRMED' && (
                            <button
                              onClick={() => handleUpdateVisitStatus(v.id, 'COMPLETED')}
                              className="px-2 py-1 rounded bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/30 text-[10px] font-bold cursor-pointer"
                            >
                              Complete
                            </button>
                          )}
                          {v.status !== 'CANCELLED' && v.status !== 'COMPLETED' && (
                            <button
                              onClick={() => handleUpdateVisitStatus(v.id, 'CANCELLED')}
                              className="px-2 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 text-[10px] font-bold cursor-pointer"
                            >
                              Cancel
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 7. TAB CONTENT: AUDIT LOG */}
        {activeTab === 'audit' && (
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Administrative Audit Logs (Recent Actions)
              </span>
              <span className="text-xs text-slate-500 font-mono">
                {auditLogs.length} logged events
              </span>
            </div>

            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400 uppercase font-semibold">
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Admin Email</th>
                    <th className="py-3 px-4">Action</th>
                    <th className="py-3 px-4">Target Entity</th>
                    <th className="py-3 px-4">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditLoading ? (
                    <tr>
                      <td colSpan="5" className="py-8 text-center text-slate-500">
                        Loading audit logs...
                      </td>
                    </tr>
                  ) : auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="py-8 text-center text-slate-500">
                        No audit logs recorded yet.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 font-semibold text-slate-300">{log.admin_email}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20 font-mono font-bold text-[10px]">
                            {log.action}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-300 font-medium">
                          {log.entity_type} #{log.entity_id}
                        </td>
                        <td className="py-3 px-4 text-slate-400 max-w-md truncate">
                          {log.details}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 7. TAB CONTENT: PROPULSE PRO SUBSCRIPTIONS */}
        {activeTab === 'subscriptions' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-3xl border border-slate-800 bg-slate-900/30">
              <div>
                <h3 className="text-base font-bold text-white font-outfit flex items-center gap-2">
                  <Crown className="w-5 h-5 text-amber-400" />
                  PropPulse Pro Subscriber Roster
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Active recurring accounts, payment references, and real-time subscription lifecycle audits.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={fetchSubscriptions}
                  disabled={subLoading}
                  className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white text-xs font-semibold flex items-center gap-2"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${subLoading ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>
            </div>

            {/* Subscriptions Table */}
            <div className="glass-card rounded-3xl border border-slate-800 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                    <tr>
                      <th className="py-3.5 px-4 font-semibold">User</th>
                      <th className="py-3.5 px-4 font-semibold">Plan</th>
                      <th className="py-3.5 px-4 font-semibold">Status</th>
                      <th className="py-3.5 px-4 font-semibold">Amount</th>
                      <th className="py-3.5 px-4 font-semibold">Razorpay Payment ID</th>
                      <th className="py-3.5 px-4 font-semibold">Order / Sub ID</th>
                      <th className="py-3.5 px-4 font-semibold">Activated</th>
                      <th className="py-3.5 px-4 font-semibold">Expires</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {subscriptions.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500 italic">
                          {subLoading ? 'Loading subscriptions...' : 'No subscriptions recorded yet.'}
                        </td>
                      </tr>
                    ) : (
                      subscriptions.map((sub) => (
                        <tr key={sub.id} className="hover:bg-slate-900/40 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-semibold text-white">{sub.user_name}</div>
                            <div className="text-[11px] text-slate-400 font-mono">{sub.user_email}</div>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              sub.plan === 'PRO' ? 'bg-amber-500/10 text-amber-300 border border-amber-500/30' : 'bg-slate-800 text-slate-400'
                            }`}>
                              {sub.plan}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              sub.subscription_status === 'ACTIVE'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                : sub.subscription_status === 'CANCELLED'
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                                : 'bg-slate-800 text-slate-400'
                            }`}>
                              {sub.subscription_status}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono font-semibold text-slate-200">
                            ₹{sub.plan_amount} {sub.currency}
                          </td>
                          <td className="py-3 px-4 font-mono text-[11px] text-slate-300">
                            {sub.razorpay_payment_id || 'N/A'}
                          </td>
                          <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                            {sub.razorpay_order_id || sub.razorpay_subscription_id || 'N/A'}
                          </td>
                          <td className="py-3 px-4 text-slate-400">
                            {sub.start_date ? new Date(sub.start_date).toLocaleDateString() : '—'}
                          </td>
                          <td className="py-3 px-4 text-slate-400">
                            {sub.end_date ? new Date(sub.end_date).toLocaleDateString() : 'Permanent'}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* 8. PROPERTY MANAGEMENT MODAL / DRAWER */}
      {selectedProperty && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
          <div className="glass-card w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6 rounded-3xl border border-slate-800 bg-slate-900 shadow-2xl space-y-6 relative">
            <button
              onClick={() => setSelectedProperty(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white cursor-pointer"
            >
              <XCircle className="w-6 h-6" />
            </button>

            <div className="space-y-1">
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">
                Property #{selectedProperty.property.id} • Private Management
              </span>
              <h3 className="text-xl font-bold text-white font-outfit">
                {selectedProperty.property.title}
              </h3>
              <p className="text-xs text-slate-400">
                {selectedProperty.property.address}
              </p>
            </div>

            {/* Quick Specs */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-xs">
              <div>
                <span className="text-slate-500 block text-[10px]">Price:</span>
                <span className="font-bold text-emerald-400 font-mono">
                  ₹{selectedProperty.property.price?.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Config:</span>
                <span className="font-bold text-slate-200">
                  {selectedProperty.property.bhk} BHK • {selectedProperty.property.property_type}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Area:</span>
                <span className="font-bold text-slate-200">
                  {selectedProperty.property.area_sqft} sq.ft
                </span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Visibility:</span>
                <span className={`font-bold ${selectedProperty.property.visibility_status === 'PRIVATE' ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {selectedProperty.property.visibility_status}
                </span>
              </div>
            </div>

            {/* Private Owner / Agent Contact Form */}
            <form onSubmit={handleSaveOwnerContact} className="p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <Shield className="w-4 h-4 text-purple-400" />
                  <span>Private Owner / Agent Contact Details (Protected)</span>
                </h4>
                <span className="text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 font-semibold">
                  Admin Eyes Only
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Contact Name:</label>
                  <input
                    type="text"
                    required
                    value={ownerContactForm?.contact_name || ''}
                    onChange={(e) => setOwnerContactForm({ ...ownerContactForm, contact_name: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white"
                  />
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Contact Type:</label>
                  <select
                    value={ownerContactForm?.contact_type || 'OWNER'}
                    onChange={(e) => setOwnerContactForm({ ...ownerContactForm, contact_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white"
                  >
                    <option value="OWNER">OWNER</option>
                    <option value="AGENT">AGENT</option>
                    <option value="BUILDER">BUILDER</option>
                    <option value="BROKER">BROKER</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Private Phone Number:</label>
                  <input
                    type="text"
                    value={ownerContactForm?.phone || ''}
                    onChange={(e) => setOwnerContactForm({ ...ownerContactForm, phone: e.target.value })}
                    placeholder="+91 98450 12345"
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono"
                  />
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Private Email:</label>
                  <input
                    type="email"
                    value={ownerContactForm?.email || ''}
                    onChange={(e) => setOwnerContactForm({ ...ownerContactForm, email: e.target.value })}
                    placeholder="owner@example.com"
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-mono"
                  />
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Verification Status:</label>
                  <select
                    value={ownerContactForm?.verification_status || 'UNVERIFIED'}
                    onChange={(e) => setOwnerContactForm({ ...ownerContactForm, verification_status: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white font-bold"
                  >
                    <option value="VERIFIED">VERIFIED (Authorized for Lead Dispatch)</option>
                    <option value="UNVERIFIED">UNVERIFIED (Do not send leads)</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Source / Verification Note:</label>
                  <input
                    type="text"
                    value={ownerContactForm?.source || ''}
                    onChange={(e) => setOwnerContactForm({ ...ownerContactForm, source: e.target.value })}
                    placeholder="e.g. Title Deed / Direct Verification"
                    className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={ownerUpdating}
                  className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 font-bold text-xs text-white shadow-md shadow-purple-500/20 cursor-pointer disabled:opacity-50"
                >
                  {ownerUpdating ? 'Saving...' : 'Save Private Contact Details'}
                </button>
              </div>
            </form>

            {/* Leads associated with this property */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Inquiries & Leads for this Property ({selectedProperty.leads?.length || 0})
              </h4>
              {selectedProperty.leads?.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No inquiries received yet.</p>
              ) : (
                <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                  {selectedProperty.leads?.map((ld) => (
                    <div
                      key={ld.id}
                      className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-white">{ld.name}</span>
                        <span className="font-mono text-slate-400 ml-2">{ld.phone}</span>
                        <span className="text-slate-400 ml-2">Budget: {ld.budget}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        {ld.lead_status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 9. LEAD REVIEW MODAL */}
      {selectedLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
          <div className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 rounded-3xl border border-slate-800 bg-slate-900 shadow-2xl space-y-5 relative">
            <button
              onClick={() => setSelectedLead(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white cursor-pointer"
            >
              <XCircle className="w-6 h-6" />
            </button>

            {/* Lead Header */}
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded bg-purple-500/20 text-purple-300 font-mono font-bold text-xs border border-purple-500/30">
                  {selectedLead.lead.lead_code}
                </span>
                {selectedLead.lead.is_duplicate && (
                  <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold text-xs border border-amber-500/30 flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    <span>POSSIBLE DUPLICATE LEAD</span>
                  </span>
                )}
              </div>
              <h3 className="text-xl font-bold text-white font-outfit">
                Lead: {selectedLead.lead.name}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Phone: <strong className="text-white">{selectedLead.lead.phone}</strong> • Property: {selectedLead.lead.property_name}
              </p>
            </div>

            {/* Action Feedback Banner */}
            {actionMessage.text && (
              <div className={`p-3 rounded-xl text-xs flex items-start gap-2 border ${
                actionMessage.type === 'success'
                  ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                  : actionMessage.type === 'warning'
                  ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                  : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
              }`}>
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{actionMessage.text}</span>
              </div>
            )}

            {/* Buyer Requirements Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs">
              <div>
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Intent:</span>
                <span className="font-bold text-white">{selectedLead.lead.buy_or_rent}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Budget:</span>
                <span className="font-bold text-emerald-400 font-mono">{selectedLead.lead.budget}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase font-bold">BHK Config:</span>
                <span className="font-bold text-white">{selectedLead.lead.bhk}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Home Loan Required:</span>
                <span className="font-bold text-slate-200">{selectedLead.lead.loan_required}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Purchase Timeline:</span>
                <span className="font-bold text-slate-200">{selectedLead.lead.purchase_timeline}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Validation Status:</span>
                <span className={`font-bold ${selectedLead.lead.validation_status === 'VALID' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {selectedLead.lead.validation_status}
                </span>
              </div>
            </div>

            {/* Telephony Metadata Box */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3.5 rounded-2xl bg-slate-950 border border-slate-800 text-[11px] font-mono">
              <div>
                <span className="text-[10px] text-slate-500 uppercase block font-sans font-bold">Call Status</span>
                <span className={`font-bold ${
                  ['completed', 'COMPLETED'].includes(selectedLead.lead.call_status)
                    ? 'text-emerald-400'
                    : ['calling', 'CALLING'].includes(selectedLead.lead.call_status)
                    ? 'text-purple-400'
                    : 'text-amber-400'
                }`}>
                  {selectedLead.lead.call_status || 'COMPLETED'}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase block font-sans font-bold">Call Duration</span>
                <span className="text-white font-bold">{selectedLead.lead.call_duration_seconds ? `${selectedLead.lead.call_duration_seconds}s` : 'N/A'}</span>
              </div>
              <div className="col-span-2">
                <span className="text-[10px] text-slate-500 uppercase block font-sans font-bold">Twilio Call SID</span>
                <span className="text-purple-300 font-bold break-all">{selectedLead.lead.call_sid || 'Direct Registered (No SID)'}</span>
              </div>
            </div>

            {/* AI Call Factual Summary */}
            <div className="space-y-1.5 p-4 rounded-2xl bg-purple-950/20 border border-purple-500/20">
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-purple-400" />
                <span>AI Call Consultation Summary (Factual Extract)</span>
              </span>
              <p className="text-xs text-slate-200 leading-relaxed font-sans">
                {selectedLead.lead.call_summary || 'No transcript available.'}
              </p>
            </div>

            {/* Conversation Transcript (if recorded) */}
            {selectedLead.lead.transcript && (
              <div className="space-y-1.5 p-3.5 rounded-2xl bg-slate-950 border border-slate-800 text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block font-mono">
                  Telephone Conversation Transcript:
                </span>
                <pre className="text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-40 overflow-y-auto bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/80">
                  {selectedLead.lead.transcript}
                </pre>
              </div>
            )}

            {/* Site Visit & Owner Callback Status */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Site Visit:</span>
                {selectedLead.lead.site_visit_requested ? (
                  <span className="text-emerald-400 font-bold">
                    Requested for {selectedLead.lead.site_visit_date || 'Upcoming'} at {selectedLead.lead.site_visit_time || '11:00 AM'}
                  </span>
                ) : (
                  <span className="text-slate-500">Not requested</span>
                )}
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Owner Contact Dispatch:</span>
                <span className="text-slate-300 font-medium">
                  {selectedLead.lead.owner_sent_status === 'NOT_CONFIGURED' ? (
                    <span className="text-amber-400">Not Configured (Safely Stored)</span>
                  ) : (
                    selectedLead.lead.owner_sent_status
                  )}
                </span>
              </div>
            </div>

            {/* Target Verified Owner Details */}
            {selectedLead.owner_contact && (
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Target Verified Owner:</span>
                  <span className="font-bold text-white">{selectedLead.owner_contact.contact_name}</span>
                  <span className="text-slate-400 ml-2 font-mono">{selectedLead.owner_contact.phone}</span>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  selectedLead.owner_contact.verification_status === 'VERIFIED'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                }`}>
                  {selectedLead.owner_contact.verification_status}
                </span>
              </div>
            )}

            {/* Admin Human Review Actions */}
            <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleApproveLead(selectedLead.lead.id)}
                  className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/20 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Approve Lead</span>
                </button>

                <button
                  onClick={() => handleRejectLead(selectedLead.lead.id)}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs border border-slate-700 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Reject</span>
                </button>

                <button
                  onClick={() => handleMarkSpam(selectedLead.lead.id)}
                  className="px-3 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 font-bold text-xs border border-rose-500/30 transition-all cursor-pointer"
                >
                  Mark Spam
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleSendLeadToOwner(selectedLead.lead.id)}
                  className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Send to Owner</span>
                </button>

                <button
                  onClick={() => handleDownloadPdf(selectedLead.lead.id, selectedLead.lead.lead_code)}
                  disabled={downloadingPdf}
                  className="px-3.5 py-2 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 font-bold text-xs border border-purple-500/30 transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>{downloadingPdf ? 'Exporting...' : 'Download PDF'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PrivateAdminDashboard;
