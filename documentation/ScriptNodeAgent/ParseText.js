const data = $input.first().json.text.replace(/[*#`{}\[\]]/g, '')

return [{ text: data }];
