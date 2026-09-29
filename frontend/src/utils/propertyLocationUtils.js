/**
 * Canonical Property Building Identity & Exact Map Navigation Utility.
 * Enforces real-world data hierarchy:
 * 1. Building / Project / Society name first
 * 2. Sub-locality / Locality, Bengaluru second
 * 3. Street / Road / Full Address third
 * 4. Exact coordinates vs Approximate locality badge
 * 5. Real browser geolocation routing (Origin: User -> Destination: Property)
 */

export const isAnonymizedCode = (str) => {
  if (!str) return true;
  const s = String(str).trim();
  if (s.includes('—') || s.includes('BHK') || s.includes('Bedroom')) return false;
  const common = [
    'apartment', 'flat', 'villa', 'house', 'park', 'green', 'view', 
    'heights', 'residency', 'nest', 'layout', 'garden', 'enclave', 'city', 
    'town', 'court', 'palace', 'manor', 'prestige', 'sobha', 'salarpuria', 
    'brigade', 'godrej', 'assetz', 'puravankara', 'l&t', 'embassy', 'shriram', 
    'mantri', 'dharani', 'signature', 'century', 'provident', 'casagrand', 
    'sukhi', 'elgin', 'scion', 'dra', 'mahindra'
  ];
  const sLower = s.toLowerCase();
  if (common.some(w => sLower.includes(w))) return false;
  // Match 4-10 char hash like ArsiaEx, Oreldhi, Betatsi, SollyCl
  return /^[A-Za-z0-9]{4,12}$/.test(s);
};

export const resolvePropertyDisplay = (property) => {
  if (!property) {
    return {
      buildingName: 'Property',
      locationLine: 'Bengaluru, Karnataka',
      addressLine: '',
      fullAddress: 'Bengaluru, Karnataka',
      isExact: false,
      coordinateAccuracy: 'Approximate locality location',
      coordinatesText: '',
      pricePerSqftText: '',
      propertyType: 'Property'
    };
  }

  // 1. Resolve Building / Project Name
  const rawTitle = (property.title || '').trim();
  const rawSociety = (property.society || '').trim();
  const rawBuilding = (property.building_name || '').trim();
  const rawProject = (property.project_name || '').trim();

  let buildingName = '';

  // Check explicit building/project/society fields first
  if (rawBuilding && !isAnonymizedCode(rawBuilding)) {
    buildingName = rawBuilding;
  } else if (rawProject && !isAnonymizedCode(rawProject)) {
    buildingName = rawProject;
  } else if (rawSociety && rawSociety.toLowerCase() !== 'none' && !isAnonymizedCode(rawSociety)) {
    buildingName = rawSociety;
  } else if (rawTitle && !rawTitle.toLowerCase().startsWith('property in') && !/^\d+\s*bhk\s+in\s+/i.test(rawTitle)) {
    // If title has a genuine building name like "Prestige Lakeside Habitat" or "Sobha Koramangala 2BHK Apartment"
    buildingName = rawTitle;
  }

  // If no genuine building name exists in source, formulate honest property-type title
  // RULE: NEVER use only "Koramangala" as property name!
  if (!buildingName || buildingName.toLowerCase() === (property.locality || '').toLowerCase() || isAnonymizedCode(buildingName)) {
    const bhkPrefix = property.bhk ? `${property.bhk} BHK ` : '';
    const typeStr = property.property_type && property.property_type !== 'Not specified' ? property.property_type : 'Residential Property';
    buildingName = `${bhkPrefix}${typeStr}`.trim();
  }

  // 2. Resolve Sub-Locality / Locality Line
  const loc = (property.locality || 'Bengaluru').trim();
  const subLoc = (property.sub_locality || '').trim();
  
  let locationLine = '';
  if (subLoc && !loc.toLowerCase().includes(subLoc.toLowerCase())) {
    locationLine = `${subLoc}, ${loc}, Bengaluru`;
  } else if (loc.toLowerCase().includes('bengaluru') || loc.toLowerCase().includes('bangalore')) {
    locationLine = loc;
  } else {
    locationLine = `${loc}, Bengaluru`;
  }

  // 3. Resolve Specific Street / Road / Address Line
  const addr = (property.address || '').trim();
  let addressLine = '';
  if (addr) {
    // Check if address has additional specific details beyond just the locality name
    const cleanAddr = addr.replace(/,\s*(bengaluru|bangalore|karnataka|india)\b/gi, '').trim();
    if (cleanAddr && cleanAddr.toLowerCase() !== loc.toLowerCase()) {
      addressLine = addr;
    }
  }

  // 4. Coordinate accuracy evaluation
  const isExact = property.coordinate_status === 'EXACT' || 
                  property.coordinate_quality === 'EXACT' ||
                  property.coordinate_confidence === 'EXACT';

  const coordinateAccuracy = isExact 
    ? 'Exact property location' 
    : 'Approximate locality location';

  const lat = property.latitude ? Number(property.latitude).toFixed(6) : null;
  const lon = property.longitude ? Number(property.longitude).toFixed(6) : null;
  const coordinatesText = (lat && lon) ? `Lat: ${lat}, Lon: ${lon}` : '';

  const pSqft = property.price_per_sqft 
    ? `₹${Math.round(property.price_per_sqft).toLocaleString('en-IN')}/sq.ft` 
    : (property.price && property.area_sqft 
        ? `₹${Math.round(property.price / property.area_sqft).toLocaleString('en-IN')}/sq.ft` 
        : '');

  return {
    buildingName,
    locationLine,
    addressLine,
    fullAddress: addr || locationLine,
    isExact,
    coordinateAccuracy,
    coordinatesText,
    pricePerSqftText: pSqft,
    propertyType: property.property_type || 'Property',
    lat: property.latitude,
    lon: property.longitude
  };
};

/**
 * Real browser geolocation navigation to exact property coordinates.
 * Requests navigator.geolocation.getCurrentPosition(...)
 * Origin: User's real GPS coordinates
 * Destination: Property's verified latitude & longitude
 */
export const navigateToProperty = (property, onStart = null, onComplete = null) => {
  if (!property || !property.latitude || !property.longitude) {
    alert("Property coordinates are unavailable for navigation.");
    return;
  }

  const destLat = property.latitude;
  const destLon = property.longitude;

  if (onStart) onStart();

  const openRoutingUrl = (originLat = null, originLon = null) => {
    let url;
    if (originLat !== null && originLon !== null) {
      url = `https://www.google.com/maps/dir/?api=1&origin=${originLat},${originLon}&destination=${destLat},${destLon}&travelmode=driving`;
    } else {
      // Fallback if browser permission is blocked or denied
      url = `https://www.google.com/maps/dir/?api=1&destination=${destLat},${destLon}`;
    }
    if (onComplete) onComplete();
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        openRoutingUrl(position.coords.latitude, position.coords.longitude);
      },
      (error) => {
        console.warn('Geolocation access not granted, opening destination map:', error.message);
        openRoutingUrl();
      },
      { timeout: 7000, enableHighAccuracy: true, maximumAge: 60000 }
    );
  } else {
    openRoutingUrl();
  }
};

/**
 * Open exact coordinates directly in OpenStreetMap
 */
export const openInOpenStreetMap = (property) => {
  if (!property || !property.latitude || !property.longitude) return;
  const url = `https://www.openstreetmap.org/?mlat=${property.latitude}&mlon=${property.longitude}#map=17/${property.latitude}/${property.longitude}`;
  window.open(url, '_blank', 'noopener,noreferrer');
};

/**
 * Open exact coordinates in Google Maps search
 */
export const openInGoogleMaps = (property) => {
  if (!property || !property.latitude || !property.longitude) return;
  const url = `https://www.google.com/maps/search/?api=1&query=${property.latitude},${property.longitude}`;
  window.open(url, '_blank', 'noopener,noreferrer');
};
