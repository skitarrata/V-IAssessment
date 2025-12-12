const rawText =$input.first().json.output;

// Divide il testo in righe
const lines = rawText.split('\n');

// Crea oggetti con chiavi numerate (text1, text2, ...)
const output = {};
lines.map(line => line.trim())
     .filter(line => line !== '')
     .forEach((line, index) => {
         output[`text${index + 1}`] = line;
     });

return [output];
