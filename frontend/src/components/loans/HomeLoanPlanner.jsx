import React, { useState, useEffect } from 'react';
import { 
  Building2, Calculator, Shield, CheckCircle2, Sparkles, Download, 
  Info, AlertTriangle, ExternalLink, ArrowLeft, Loader2, Check, 
  FileText, Landmark
} from 'lucide-react';
import loanService from '../../services/loanService';
import { useAuth } from '../../context/AuthContext';
import { ProFeatureLockModal } from '../ProFeatureLockModal';

export default function HomeLoanPlanner({ property, onClose }) {
  const { user } = useAuth();
  const [showProLock, setShowProLock] = useState(false);
  const isPro = user?.role === 'ADMIN' || user?.subscription_status === 'ACTIVE';
  // Pre-populate based on actual selected property
  const propertyPrice = Number(property?.price || property?.price_inr || 0);
  const defaultDownPayment = Math.round(propertyPrice * 0.20); // 20% standard contribution
  const defaultLoanAmount = Math.max(0, propertyPrice - defaultDownPayment);

  // Form State
  const [fullName, setFullName] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [age, setAge] = useState(30);
  const [monthlyIncome, setMonthlyIncome] = useState(120000);
  const [employmentType, setEmploymentType] = useState('Salaried');
  const [existingEmi, setExistingEmi] = useState(0);
  const [downPayment, setDownPayment] = useState(defaultDownPayment);
  const [loanAmount, setLoanAmount] = useState(defaultLoanAmount);
  const [isManualLoanOverride, setIsManualLoanOverride] = useState(false);
  const [tenureYears, setTenureYears] = useState(20);

  // Filter & Sort State
  const [bankFilter, setBankFilter] = useState('ALL'); // ALL, Public Sector, Private, Housing Finance
  const [sortBy, setSortBy] = useState('EMI_ASC'); // EMI_ASC, RATE_ASC, INT_ASC, NAME_ASC
  const [selectedBankIds, setSelectedBankIds] = useState([]);

  // Async State
  const [loading, setLoading] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [error, setError] = useState('');
  const [comparisonResult, setComparisonResult] = useState(null);

  // Auto-update loan amount when down payment changes (unless user explicitly overrode)
  const handleDownPaymentChange = (val) => {
    const num = Math.max(0, Number(val) || 0);
    setDownPayment(num);
    if (!isManualLoanOverride && propertyPrice > 0) {
      setLoanAmount(Math.max(0, propertyPrice - num));
    }
  };

  const handlePercentageContribution = (pct) => {
    const calculatedDown = Math.round(propertyPrice * (pct / 100));
    setDownPayment(calculatedDown);
    setLoanAmount(Math.max(0, propertyPrice - calculatedDown));
    setIsManualLoanOverride(false);
  };

  const handleLoanAmountChange = (val) => {
    const num = Math.max(0, Number(val) || 0);
    setLoanAmount(num);
    setIsManualLoanOverride(true);
  };

  // Perform Calculation & Multi-Bank Comparison
  const handleCalculateAndCompare = async (e) => {
    if (e) e.preventDefault();
    if (!isPro) {
      setShowProLock(true);
      return;
    }

    // Validation
    if (!fullName.trim()) {
      setError('Please enter your full name.');
      return;
    }
    const cleanPhone = mobileNumber.replace(/[^0-9]/g, '');
    if (cleanPhone.length !== 10 || !['6','7','8','9'].includes(cleanPhone[0])) {
      setError('Please enter a valid 10-digit Indian mobile number.');
      return;
    }
    if (age < 18 || age > 75) {
      setError('Applicant age must be between 18 and 75 years.');
      return;
    }
    if (monthlyIncome <= 0) {
      setError('Monthly income must be greater than zero.');
      return;
    }
    if (downPayment < 0) {
      setError('Down payment cannot be negative.');
      return;
    }
    if (loanAmount <= 0) {
      setError('Loan amount must be greater than zero.');
      return;
    }
    if (downPayment >= propertyPrice) {
      setError('Down payment cannot equal or exceed the property price.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload = {
        property_id: property?.id || null,
        full_name: fullName.trim(),
        mobile_number: cleanPhone,
        age: Number(age),
        monthly_income: Number(monthlyIncome),
        employment_type: employmentType,
        existing_monthly_emi: Number(existingEmi) || 0.0,
        property_price: propertyPrice,
        down_payment: Number(downPayment),
        desired_loan_amount: Number(loanAmount),
        preferred_tenure_years: Number(tenureYears)
      };

      const result = await loanService.compareLoans(payload);
      setComparisonResult(result);
    } catch (err) {
      console.error('Loan comparison error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to calculate loan comparison.');
    } finally {
      setLoading(false);
    }
  };

  // Download PDF Report
  const handleDownloadPdf = async () => {
    if (!isPro) {
      setShowProLock(true);
      return;
    }
    if (!comparisonResult) return;
    setDownloadingPdf(true);
    try {
      const cleanPhone = mobileNumber.replace(/[^0-9]/g, '');
      const payload = {
        property_id: property?.id || null,
        full_name: fullName.trim() || 'Valued Applicant',
        mobile_number: cleanPhone || '9876543210',
        age: Number(age) || 30,
        monthly_income: Number(monthlyIncome) || 100000,
        employment_type: employmentType,
        existing_monthly_emi: Number(existingEmi) || 0.0,
        property_price: propertyPrice,
        down_payment: Number(downPayment),
        desired_loan_amount: Number(loanAmount),
        preferred_tenure_years: Number(tenureYears)
      };
      await loanService.downloadReportPdf(payload, property?.id);
    } catch (err) {
      console.error('PDF Download failed:', err);
      setError('Failed to download PDF report. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Initial calculation trigger when property mounted (PRO users only)
  useEffect(() => {
    if (propertyPrice > 0 && !comparisonResult && !loading && isPro) {
      setFullName('Prospective Buyer');
      setMobileNumber('9876543210');
      handleCalculateAndCompare();
    }
  }, [propertyPrice, isPro]);

  // Filtered and Sorted Bank List
  const displayedBanks = (comparisonResult?.bank_comparisons || []).filter((b) => {
    if (bankFilter === 'ALL') return true;
    return b.bank_type === bankFilter;
  }).sort((a, b) => {
    if (sortBy === 'EMI_ASC') return a.estimated_monthly_emi_min - b.estimated_monthly_emi_min;
    if (sortBy === 'RATE_ASC') return a.interest_rate_min - b.interest_rate_min;
    if (sortBy === 'INT_ASC') return a.total_interest_min - b.total_interest_min;
    if (sortBy === 'NAME_ASC') return a.bank_name.localeCompare(b.bank_name);
    return 0;
  });

  const toggleSelectBank = (id) => {
    if (selectedBankIds.includes(id)) {
      setSelectedBankIds(selectedBankIds.filter((item) => item !== id));
    } else {
      if (selectedBankIds.length >= 3) {
        // limit to 3
        setSelectedBankIds([...selectedBankIds.slice(1), id]);
      } else {
        setSelectedBankIds([...selectedBankIds, id]);
      }
    }
  };

  const selectedBanksData = (comparisonResult?.bank_comparisons || []).filter((b) => 
    selectedBankIds.includes(b.id)
  );

  return (
    <div className="w-full space-y-8 bg-slate-950/80 border border-slate-800 rounded-3xl p-6 md:p-8 backdrop-blur-xl relative shadow-2xl">
      {/* Module Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <span className="p-2.5 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 text-emerald-400">
              <Calculator className="w-6 h-6" />
            </span>
            <div>
              <h2 className="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2">
                Smart Home Loan & Bank Evaluation Engine
              </h2>
              <p className="text-xs text-slate-400">
                Property-linked mortgage calculation, indicative eligibility & multi-lender comparison
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-slate-900 border border-slate-700 text-slate-300 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span>Data Verified: October 2026</span>
          </span>
          {onClose && (
            <button 
              onClick={onClose}
              className="px-3 py-1 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>

      {/* Property Context Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-xs">
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Property</span>
          <span className="text-slate-200 font-semibold truncate block" title={property?.title || 'Selected Property'}>
            {property?.title ? property.title.slice(0, 35) + '...' : `Property #${property?.id || 'N/A'}`}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Locality & Type</span>
          <span className="text-slate-200 font-semibold block">
            {property?.locality || property?.location || 'Bengaluru'} ({property?.bhk ? `${property.bhk} BHK` : 'Apartment'})
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Listing Price</span>
          <span className="text-emerald-400 font-bold block text-sm">
            ₹{propertyPrice ? propertyPrice.toLocaleString('en-IN') : '0'}
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold tracking-wider">Super Built-up Area</span>
          <span className="text-slate-200 font-semibold block">
            {property?.area_sqft || property?.total_sqft || 'N/A'} sq.ft
          </span>
        </div>
      </div>

      {/* Interactive Input Form */}
      <form onSubmit={handleCalculateAndCompare} className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {/* Full Name */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Full Name</span>
              <span className="text-[10px] text-slate-500">Applicant</span>
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Rohan Sharma"
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>

          {/* Mobile Number */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Mobile Number</span>
              <span className="text-[10px] text-slate-500">10-Digit Indian</span>
            </label>
            <div className="relative">
              <span className="absolute left-3.5 top-2.5 text-xs text-slate-500 font-semibold">+91</span>
              <input
                type="tel"
                required
                maxLength={10}
                value={mobileNumber}
                onChange={(e) => setMobileNumber(e.target.value.replace(/[^0-9]/g, ''))}
                placeholder="9876543210"
                className="w-full pl-12 pr-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
              />
            </div>
          </div>

          {/* Age */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Applicant Age</span>
              <span className="text-[10px] text-slate-500">18 - 75 Yrs</span>
            </label>
            <input
              type="number"
              min={18}
              max={75}
              required
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>

          {/* Monthly Income */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Monthly Net Income (₹)</span>
              <span className="text-[10px] text-emerald-400 font-mono">₹{(Number(monthlyIncome) || 0).toLocaleString('en-IN')}</span>
            </label>
            <input
              type="number"
              min={10000}
              step={5000}
              required
              value={monthlyIncome}
              onChange={(e) => setMonthlyIncome(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>

          {/* Employment Type */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300">Employment Type</label>
            <select
              value={employmentType}
              onChange={(e) => setEmploymentType(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            >
              <option value="Salaried">Salaried (Corporate / Govt)</option>
              <option value="Self-employed">Self-Employed Professional</option>
              <option value="Business">Business Owner / Entrepreneur</option>
            </select>
          </div>

          {/* Existing Monthly EMI */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Existing Monthly EMI Obligations (₹)</span>
              <span className="text-[10px] text-slate-500">Auto / Personal loans</span>
            </label>
            <input
              type="number"
              min={0}
              step={1000}
              value={existingEmi}
              onChange={(e) => setExistingEmi(Number(e.target.value))}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>

          {/* Down Payment / Own Contribution */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-300">Own Contribution / Down Payment (₹)</label>
              <span className="text-[10px] text-emerald-400 font-mono">
                {propertyPrice > 0 ? `${((downPayment / propertyPrice) * 100).toFixed(0)}%` : '0%'}
              </span>
            </div>
            <input
              type="number"
              min={0}
              max={propertyPrice}
              step={50000}
              required
              value={downPayment}
              onChange={(e) => handleDownPaymentChange(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            />
            {/* Quick Percentage Chips */}
            <div className="flex items-center gap-1.5 pt-1">
              {[10, 20, 25, 30].map((pct) => (
                <button
                  type="button"
                  key={pct}
                  onClick={() => handlePercentageContribution(pct)}
                  className={`px-2 py-0.5 rounded-lg text-[10px] font-bold border transition-colors ${
                    Math.round((downPayment / (propertyPrice || 1)) * 100) === pct
                      ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  {pct}%
                </button>
              ))}
            </div>
          </div>

          {/* Desired Loan Amount */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-300">Required Principal Loan (₹)</label>
              <span className="text-[10px] text-brand-400 font-mono">
                ₹{(Number(loanAmount) || 0).toLocaleString('en-IN')}
              </span>
            </div>
            <input
              type="number"
              min={100000}
              step={50000}
              required
              value={loanAmount}
              onChange={(e) => handleLoanAmountChange(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-brand-500 transition-colors"
            />
            <span className="text-[10px] text-slate-500 block">
              Auto: Property Price (₹{propertyPrice.toLocaleString('en-IN')}) - Down Payment (₹{Number(downPayment).toLocaleString('en-IN')})
            </span>
          </div>

          {/* Preferred Tenure */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
              <span>Preferred Tenure</span>
              <span className="text-[10px] text-slate-400 font-mono">{tenureYears} Yrs ({tenureYears * 12} mo)</span>
            </label>
            <div className="grid grid-cols-6 gap-1">
              {[5, 10, 15, 20, 25, 30].map((yr) => (
                <button
                  type="button"
                  key={yr}
                  onClick={() => setTenureYears(yr)}
                  className={`py-2 rounded-xl text-xs font-bold border transition-colors ${
                    tenureYears === yr
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-emerald-400 shadow-md shadow-emerald-500/20'
                      : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
                  }`}
                >
                  {yr}y
                </button>
              ))}
            </div>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Row */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-slate-400" />
            <span>Standard compound interest EMI formula calculated dynamically in INR.</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
              <span>{loading ? 'Evaluating Lenders...' : 'Recalculate & Compare'}</span>
            </button>

            {comparisonResult && (
              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 hover:border-slate-600 font-bold text-xs transition-colors flex items-center justify-center gap-2"
              >
                {downloadingPdf ? <Loader2 className="w-4 h-4 animate-spin text-emerald-400" /> : <Download className="w-4 h-4 text-emerald-400" />}
                <span>{downloadingPdf ? 'Generating PDF...' : 'Download PDF Loan Report'}</span>
              </button>
            )}
          </div>
        </div>
      </form>

      {/* KPI Cards Strip (When Comparison Result Exists) */}
      {comparisonResult && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Principal Loan</span>
            <div className="text-lg md:text-xl font-extrabold text-white">
              ₹{(comparisonResult.loan_metrics?.loan_amount || 0).toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-500 block">
              Tenure: {comparisonResult.loan_metrics?.tenure_years} Years ({comparisonResult.loan_metrics?.tenure_years * 12} mo)
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Loan-To-Value (LTV)</span>
            <div className="text-lg md:text-xl font-extrabold text-amber-400 flex items-center gap-2">
              <span>{comparisonResult.loan_metrics?.actual_ltv_pct}%</span>
              <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                (comparisonResult.loan_metrics?.actual_ltv_pct || 0) <= (comparisonResult.loan_metrics?.rbi_max_ltv_pct || 80)
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
              }`}>
                {(comparisonResult.loan_metrics?.actual_ltv_pct || 0) <= (comparisonResult.loan_metrics?.rbi_max_ltv_pct || 80) ? 'RBI Compliant' : 'Above Benchmark'}
              </span>
            </div>
            <span className="text-[10px] text-slate-500 block">
              RBI Cap: {comparisonResult.loan_metrics?.rbi_max_ltv_pct}% for this price band
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Starting Monthly EMI</span>
            <div className="text-lg md:text-xl font-extrabold text-emerald-400">
              ₹{(comparisonResult.loan_metrics?.estimated_monthly_emi || 0).toLocaleString('en-IN')}
              <span className="text-xs text-slate-400 font-normal"> / mo</span>
            </div>
            <span className="text-[10px] text-slate-500 block">
              Baseline rate: {comparisonResult.loan_metrics?.baseline_rate_pct}% p.a.
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Interest Payable</span>
            <div className="text-lg md:text-xl font-extrabold text-indigo-400">
              ₹{(comparisonResult.loan_metrics?.total_interest || 0).toLocaleString('en-IN')}
            </div>
            <span className="text-[10px] text-slate-500 block">
              Total Outlay: ₹{(comparisonResult.loan_metrics?.total_repayment || 0).toLocaleString('en-IN')}
            </span>
          </div>
        </div>
      )}

      {/* Side-by-Side Comparison Modal/Drawer for Selected Banks (2-3 Banks) */}
      {selectedBanksData.length >= 2 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-brand-950/60 to-slate-900 border border-brand-500/30 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand-400" />
              <h3 className="text-sm font-extrabold text-white">
                Head-to-Head Comparison ({selectedBanksData.length} Lenders Selected)
              </h3>
            </div>
            <button
              onClick={() => setSelectedBankIds([])}
              className="text-xs text-slate-400 hover:text-white transition-colors"
            >
              Clear Selection
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {selectedBanksData.map((b) => (
              <div key={b.id} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white truncate">{b.bank_name}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-semibold">{b.bank_type}</span>
                </div>
                <div className="text-xs space-y-1 pt-1">
                  <div className="flex justify-between text-slate-400">
                    <span>Starting Rate:</span>
                    <span className="font-bold text-emerald-400">{b.interest_rate_min}% p.a.</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Monthly EMI:</span>
                    <span className="font-bold text-white">₹{b.estimated_monthly_emi_min.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Total Interest:</span>
                    <span className="font-mono text-slate-300">₹{b.total_interest_min.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Processing Fee:</span>
                    <span className="text-[10px] text-slate-300 truncate max-w-[140px]" title={b.processing_fee}>{b.processing_fee}</span>
                  </div>
                </div>
                {b.special_features && b.special_features.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80">
                    <span className="text-[10px] text-brand-400 font-bold block mb-1">Key Feature:</span>
                    <span className="text-[10px] text-slate-400 block">• {b.special_features[0]}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Multi-Bank Comparison Table */}
      {comparisonResult && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-extrabold text-white flex items-center gap-2">
                <span>Verified Lender Offerings ({displayedBanks.length} Available)</span>
                <span className="text-[10px] font-normal text-slate-400">Select up to 3 to compare</span>
              </h3>
            </div>

            {/* Filter & Sort Controls */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Type Filter */}
              <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-xl p-0.5">
                {[
                  { key: 'ALL', label: 'All' },
                  { key: 'Public Sector', label: 'PSU' },
                  { key: 'Private', label: 'Private' },
                  { key: 'Housing Finance', label: 'HFC' }
                ].map((tab) => (
                  <button
                    key={tab.key}
                    type="button"
                    onClick={() => setBankFilter(tab.key)}
                    className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-colors ${
                      bankFilter === tab.key
                        ? 'bg-brand-500 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Sort Selector */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-2.5 py-1 bg-slate-900 border border-slate-800 rounded-xl text-[10px] font-bold text-slate-300 focus:outline-none"
              >
                <option value="EMI_ASC">Sort: Lowest EMI</option>
                <option value="RATE_ASC">Sort: Lowest Rate</option>
                <option value="INT_ASC">Sort: Lowest Total Interest</option>
                <option value="NAME_ASC">Sort: Bank Name (A-Z)</option>
              </select>
            </div>
          </div>

          {/* Table Container */}
          <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/40">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/80 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-3 w-10 text-center">Compare</th>
                  <th className="py-3 px-3">Bank & Product</th>
                  <th className="py-3 px-3">Interest Rate</th>
                  <th className="py-3 px-3">Est. Monthly EMI</th>
                  <th className="py-3 px-3">Total Interest</th>
                  <th className="py-3 px-3">Indicative Eligibility</th>
                  <th className="py-3 px-3">Processing Fee</th>
                  <th className="py-3 px-3 text-right">Official Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {displayedBanks.map((b) => {
                  const isSelected = selectedBankIds.includes(b.id);
                  const isEligible = b.indicative_status_code === 'ELIGIBLE';

                  return (
                    <tr 
                      key={b.id} 
                      className={`hover:bg-slate-800/30 transition-colors ${isSelected ? 'bg-brand-500/5' : ''}`}
                    >
                      <td className="py-3 px-3 text-center">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleSelectBank(b.id)}
                          className="rounded border-slate-700 text-brand-500 focus:ring-0 cursor-pointer"
                        />
                      </td>

                      <td className="py-3 px-3">
                        <div className="font-bold text-white flex items-center gap-1.5">
                          <span>{b.bank_name}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-semibold ${
                            b.bank_type === 'Public Sector' 
                              ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' 
                              : b.bank_type === 'Private'
                              ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>
                            {b.bank_type}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400 block">{b.product_name}</span>
                      </td>

                      <td className="py-3 px-3">
                        <span className="font-bold text-emerald-400">{b.rate_display}</span>
                        <span className="text-[9px] text-slate-500 block">{b.rate_type}</span>
                      </td>

                      <td className="py-3 px-3">
                        <span className="font-extrabold text-white text-xs">
                          ₹{b.estimated_monthly_emi_min.toLocaleString('en-IN')}
                        </span>
                        <span className="text-[9px] text-slate-400 block">
                          Up to ₹{b.estimated_monthly_emi_max.toLocaleString('en-IN')}
                        </span>
                      </td>

                      <td className="py-3 px-3">
                        <span className="font-mono text-slate-300">
                          ₹{b.total_interest_min.toLocaleString('en-IN')}
                        </span>
                        <span className="text-[9px] text-slate-500 block">
                          Repay: ₹{b.total_repayment_min.toLocaleString('en-IN')}
                        </span>
                      </td>

                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold inline-flex items-center gap-1 ${
                          isEligible
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'
                        }`}>
                          <CheckCircle2 className="w-2.5 h-2.5" />
                          <span>{b.indicative_eligibility}</span>
                        </span>
                        <span className="text-[9px] text-slate-400 block pt-0.5 max-w-xs truncate" title={b.eligibility_notes}>
                          {b.eligibility_notes}
                        </span>
                      </td>

                      <td className="py-3 px-3 text-[10px] text-slate-300 max-w-[130px] truncate" title={b.processing_fee}>
                        {b.processing_fee}
                      </td>

                      <td className="py-3 px-3 text-right">
                        <a
                          href={b.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-[10px] font-semibold text-brand-400 hover:text-brand-300 hover:underline"
                        >
                          <span>{b.source_name.split(' ')[0]}</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                        <span className="text-[8px] text-slate-500 block">
                          Verified: {b.last_verified_date}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* "Why These Options?" Personalized Explanations */}
      {comparisonResult?.personalized_observations && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Why These Options? — Personalized Financial Observations
            </h3>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {comparisonResult.personalized_observations.map((obs, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                <span>{obs}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Statutory Financial Disclaimer */}
      <div className="p-4 rounded-2xl bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-300/80 flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-bold text-amber-300 block">Regulatory Compliance & Financial Disclaimer</span>
          <p className="leading-relaxed">
            All interest rates, EMI calculations, processing fees, and eligibility assessments shown are indicative 
            and based on verified public bank disclosures as of October 2026. 
            Cloud-Based Real Estate Analysis does not guarantee loan sanction. Final approval, applicable interest rates, 
            and loan terms are determined solely by the respective lending institution based on individual 
            CIBIL credit scoring, income verification, and legal title evaluation.
          </p>
        </div>
      </div>
      <ProFeatureLockModal
        isOpen={showProLock}
        onClose={() => setShowProLock(false)}
        featureName="Multi-Bank Loan Comparison & Mortgage PDF Report"
      />
    </div>
  );
}
