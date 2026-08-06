import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, X } from 'lucide-react';

export const BANGALORE_LOCALITIES = [
  "Koramangala", "HSR Layout", "Electronic City", "Whitefield", "Indiranagar",
  "Marathahalli", "Bellandur", "Sarjapur Road", "JP Nagar", "Jayanagar",
  "Banashankari", "Rajajinagar", "Malleshwaram", "Basavanagudi", "Hebbal",
  "Yelahanka", "KR Puram", "Mahadevapura", "Brookefield", "CV Raman Nagar",
  "Domlur", "Ulsoor", "RT Nagar", "Kalyan Nagar", "Banaswadi",
  "Hennur", "Nagawara", "Vijayanagar", "Yeshwanthpur", "Peenya",
  "Kengeri", "RR Nagar", "Bannerghatta Road", "BTM Layout", "Bommanahalli",
  "Silk Board", "Kadubeesanahalli", "Panathur", "Varthur", "Kadugodi",
  "Hoodi", "Sahakar Nagar", "Thanisandra", "Jakkur", "Devanahalli",
  "Mysore Road", "Chandapura", "Attibele", "Richmond Town", "Shivajinagar",
  "Frazer Town", "Cunningham Road", "Lavelle Road", "MG Road", "Cubbon Park",
  "AECS Layout", "Anekal", "Anjanapura", "Arekere", "Bagalur",
  "Balagere", "Basaveshwaranagar", "Begur", "Benson Town", "Bikasipura",
  "Brigade Road", "Carmelaram", "Channasandra", "Chikkabanavara", "Cookes Town",
  "Cox Town", "Dasarahalli", "Defense Colony", "Dollars Colony", "Electronic City Phase 2",
  "HBR Layout", "Horamavu", "Harlur", "Hegde Nagar", "Hulimavu",
  "ISRO Layout", "ITPL", "ITI Layout", "Jalahalli", "Jayanagar 4th Block",
  "Jigani", "JP Nagar 6th Phase", "Kasturi Nagar", "Kaggadasapura", "Kammanahalli",
  "Kanakapura Road", "Kengeri Satellite Town", "Kudlu Gate", "Kumaraswamy Layout", "Mathikere",
  "Nagarbhavi", "New BEL Road", "Padmanabhanagar", "RMV 2nd Stage", "Sadashivanagar",
  "Sanjay Nagar", "Seshadripuram", "Singasandra", "TC Palya", "Uttarahalli",
  "Vasanth Nagar", "Vidyaranyapura", "Vimanapura", "Wilson Garden"
];

export const BangaloreLocationAutocomplete = ({ 
  value, 
  onChange, 
  onSelect, 
  placeholder = "Search Koramangala, Whitefield, Electronic City, Chandapura, JP Nagar..." 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [filteredLocalities, setFilteredLocalities] = useState([]);
  const wrapperRef = useRef(null);

  useEffect(() => {
    if (!value || !value.trim()) {
      setFilteredLocalities(BANGALORE_LOCALITIES.slice(0, 12));
    } else {
      const q = value.toLowerCase().trim();
      const matches = BANGALORE_LOCALITIES.filter(loc => loc.toLowerCase().includes(q));
      setFilteredLocalities(matches);
    }
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (locality) => {
    onChange(locality);
    if (onSelect) onSelect(locality);
    setIsOpen(false);
  };

  return (
    <div ref={wrapperRef} className="relative w-full">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-brand-400">
          <Search className="w-5 h-5" />
        </div>
        <input
          type="text"
          value={value}
          onChange={(e) => {
            onChange(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full pl-12 pr-10 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 shadow-xl transition-all"
        />
        {value && (
          <button
            type="button"
            onClick={() => {
              onChange('');
              setIsOpen(true);
            }}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {isOpen && filteredLocalities.length > 0 && (
        <div className="absolute z-50 left-0 right-0 mt-2 bg-slate-900/95 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-h-64 overflow-y-auto backdrop-blur-xl">
          <div className="px-3 py-1.5 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-500">
            100+ Bangalore Localities ({filteredLocalities.length} matched)
          </div>
          {filteredLocalities.map((loc, idx) => (
            <button
              key={`${loc}-${idx}`}
              type="button"
              onClick={() => handleSelect(loc)}
              className="w-full text-left px-4 py-2.5 text-xs font-semibold text-slate-200 hover:bg-slate-800 hover:text-brand-300 flex items-center gap-2 border-b border-slate-800/40 last:border-none transition-colors"
            >
              <MapPin className="w-3.5 h-3.5 text-brand-400 flex-shrink-0" />
              <span>{loc}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
