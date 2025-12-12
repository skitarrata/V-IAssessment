function cleanObject(obj) {
  // Gestione di valori null/undefined
  if (obj === null || obj === undefined) {
    return undefined;
  }
  
  // Gestione degli array
  if (Array.isArray(obj)) {
    const cleanedArray = obj.map(cleanObject).filter(item => item !== undefined);
    return cleanedArray.length === 0 ? undefined : cleanedArray;
  }
  
  // Gestione degli oggetti
  if (typeof obj === 'object') {
    const cleanedObj = {};
    for (const [key, value] of Object.entries(obj)) {
      const cleanedValue = cleanObject(value);
      if (cleanedValue !== undefined) {
        cleanedObj[key] = cleanedValue;
      }
    }
    return Object.keys(cleanedObj).length === 0 ? undefined : cleanedObj;
  }
  
  // Gestione stringhe vuote
  if (obj === '') {
    return undefined;
  }
  
  // Mantieni altri valori (boolean, numeri, stringe non vuote)
  return obj;
}

const cleaned = cleanObject($input.first().json.output);
const result = cleaned !== undefined ? [cleaned] : [];

return result;
