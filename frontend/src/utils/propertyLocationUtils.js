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
      primaryTitle: 'Property',
      identitySubtitle: null,
      isResolved: false,
      isPartial: false,
      isUnresolved: true,
      identityConfidence: 'IDENTITY_UNRESOLVED',
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

  // 1. Identity Confidence from source record
  const identityConfidence = property.identity_confidence || 
    (property.building_name ? 'IDENTITY_RESOLVED' : (property.sub_locality ? 'IDENTITY_PARTIAL' : 'IDENTITY_UNRESOLVED'));

  const rawBuilding = (property.building_name || '').trim();
  const rawProject = (property.project_name || '').trim();
  const rawSociety = (property.society_name || property.society || '').trim();
  const rawTitle = (property.title || '').trim();

  const INVALID_BUILDING_NAMES = new Set([
    'sb', 'apartment', 'apartments', 'aparment', 'stand alone building',
    'standlone building', 'standalone building', 'villa', 'plot', 'land',
    'residential apartment', 'independent house', 'house', 'biotech park'
  ]);

  const isValidBuilding = (name) => {
    if (!name || isAnonymizedCode(name)) return false;
    const lower = name.toLowerCase().trim();
    if (INVALID_BUILDING_NAMES.has(lower)) return false;
    if (lower.includes(' village')) return false;
    const locLower = (property.locality || '').toLowerCase().trim();
    if (locLower && lower === locLower) return false;
    return true;
  };

  let resolvedBuilding = '';
  if (isValidBuilding(rawBuilding)) {
    resolvedBuilding = rawBuilding;
  } else if (isValidBuilding(rawProject)) {
    resolvedBuilding = rawProject;
  } else if (isValidBuilding(rawSociety)) {
    resolvedBuilding = rawSociety;
  } else if (identityConfidence === 'IDENTITY_RESOLVED' && isValidBuilding(rawTitle) && !/^\d+\s*bhk/i.test(rawTitle)) {
    resolvedBuilding = rawTitle;
  }

  const isResolved = Boolean(resolvedBuilding) && identityConfidence === 'IDENTITY_RESOLVED';
  const isPartial = !isResolved && (identityConfidence === 'IDENTITY_PARTIAL' || Boolean(property.sub_locality));
  const isUnresolved = !isResolved && !isPartial;

  // Title formulation: Truthful descriptive title e.g. "3 BHK Independent House in Koramangala"
  const bhkPrefix = property.bhk ? (property.bhk > 4 ? `${property.bhk} Bedroom ` : `${property.bhk} BHK `) : '';
  const typeStr = property.property_type && property.property_type !== 'Not specified' ? property.property_type : 'Apartment';
  const locPart = (property.locality || 'Bengaluru').trim();
  const propertyTypeTitle = `${bhkPrefix}${typeStr}`.trim();
  const truthfulListingTitle = locPart ? `${propertyTypeTitle} in ${locPart}` : propertyTypeTitle;

  const buildingName = isResolved ? resolvedBuilding : truthfulListingTitle;
  const primaryTitle = buildingName;
  const identitySubtitle = isUnresolved ? "Building name unavailable in source" : null;

  // 2. Sub-Locality / Locality / District Line
  const dist = (property.district || 'Bengaluru Urban').trim();
  const loc = (property.locality || dist).trim();
  const subLoc = (property.sub_locality || '').trim();
  
  let locationLine = '';
  if (subLoc && !loc.toLowerCase().includes(subLoc.toLowerCase())) {
    locationLine = `${subLoc}, ${loc}, ${dist}`;
  } else if (loc.toLowerCase().includes(dist.toLowerCase())) {
    locationLine = `${loc}, Karnataka`;
  } else {
    locationLine = `${loc}, ${dist}`;
  }

  // 3. Street / Road / Address Line
  const addr = (property.address || property.formatted_address || '').trim();
  let addressLine = '';
  if (property.street || property.road) {
    addressLine = [property.street, property.road].filter(Boolean).join(', ');
  } else if (addr) {
    const cleanAddr = addr.replace(/,\s*(bengaluru|bangalore|karnataka|india)\b/gi, '').trim();
    if (cleanAddr && cleanAddr.toLowerCase() !== loc.toLowerCase()) {
      addressLine = cleanAddr;
    }
  }

  // 4. Coordinate accuracy
  const isExact = property.coordinate_confidence === 'EXACT' || 
                  property.coordinate_status === 'EXACT' || 
                  property.coordinate_quality === 'EXACT';

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
    primaryTitle,
    identitySubtitle,
    isResolved,
    isPartial,
    isUnresolved,
    identityConfidence: isResolved ? 'IDENTITY_RESOLVED' : (isPartial ? 'IDENTITY_PARTIAL' : 'IDENTITY_UNRESOLVED'),
    locationLine,
    addressLine,
    fullAddress: property.formatted_address || addr || locationLine,
    isExact,
    coordinateAccuracy,
    coordinatesText,
    pricePerSqftText: pSqft,
    propertyType: typeStr,
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
