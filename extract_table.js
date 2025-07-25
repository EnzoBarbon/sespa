#!/usr/bin/env node
// extract_situaciones.js
// Node.js only: run as `node extract_table.js ./data/vida_laboral\ \(2\).pdf`
// deno run --allow-read extract_situaciones.ts ./vida_laboral.pdf > situaciones.json

const { PdfReader } = require("pdfreader");

// Remove TypeScript interface and types
// async function extraerSituaciones(pdfPath: string): Promise<Fila[]> {
async function extraerSituaciones(pdfPath) {
  // rows[page][y] = { xCoord: string }
  const rows = {};

  await new Promise((resolve, reject) => {
    let resolved = false;
    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        console.error(
          "[WARN] parseFileItems did not finish, resolving by timeout"
        );
        resolve();
      }
    }, 10000); // 10 seconds fallback
    new PdfReader().parseFileItems(pdfPath, (err, item) => {
      if (err) {
        clearTimeout(timeout);
        return reject(err);
      }
      if (!item) {
        clearTimeout(timeout);
        if (!resolved) {
          resolved = true;
          console.log("[INFO] parseFileItems finished (item == null)");
          resolve(); // ↩︎ fin de fichero
        }
        return;
      }
      // Only process text items with x and y coordinates
      if (
        typeof item === "object" &&
        item !== null &&
        "text" in item &&
        typeof item.x === "number" &&
        typeof item.y === "number"
      ) {
        const page = item.page ?? 0;
        const y = item.y;
        const x = item.x;
        const text = item.text;
        rows[page] ??= {};
        rows[page][y] ??= {};
        rows[page][y][x] = text; // agrupamos por coordenadas
      }
    });
  });

  const registros = [];

  const pagSorted = Object.keys(rows)
    .map(Number)
    .sort((a, b) => a - b);
  for (const p of pagSorted) {
    const ySorted = Object.keys(rows[p])
      .map(Number)
      .sort((a, b) => a - b);

    for (const y of ySorted) {
      const xSorted = Object.keys(rows[p][y])
        .map(Number)
        .sort((a, b) => a - b);
      const linea = xSorted.map((x) => rows[p][y][x]).join(" ");

      // partimos la fila en columnas: 2+ espacios = separador
      const cols = linea.split(/\s{2,}/).map((c) => c.trim());

      // detecta filas que realmente pertenecen a la tabla
      if (/^(GENERAL|ESPECIAL|AUT[ÓO]NOMOS|RETA)/i.test(cols[0] ?? "")) {
        // Extract all date-like fields
        const dateRegex = /\d{2}\.\d{2}\.\d{4}/g;
        const dates = linea.match(dateRegex) || [];
        const fechaAlta = dates[0] || "";
        const fechaEfectoAlta = dates[1] || "";
        const fechaBaja = dates[2] || "";

        // Remove dates from the line for further splitting
        let rest = linea;
        dates.forEach((date) => {
          rest = rest.replace(date, "");
        });
        // Remove extra spaces
        rest = rest.replace(/\s{2,}/g, " ").trim();
        const restCols = rest
          .split(/\s{2,}|\s{1,}/)
          .map((c) => c.trim())
          .filter(Boolean);

        // Assign other fields as best as possible
        // Try to extract regimen, codigoEmpresa, empresa, ct, ctpPct, gc, dias
        // We'll use the original cols for some fields, but prioritize restCols for company/codes
        const regimen = cols[0] || "";
        const codigoEmpresa = restCols[1] || "";
        const empresa = restCols[2] || "";
        const ct = restCols[3] || "";
        const ctpPct = restCols[4] || "";
        const gc = restCols[5] || "";
        const dias = restCols[6] || "";

        registros.push({
          regimen,
          codigoEmpresa,
          empresa,
          fechaAlta,
          fechaEfectoAlta,
          fechaBaja,
          ct,
          ctpPct,
          gc,
          dias,
        });
      }
    }
  }

  return registros;
}

// Node.js compatibility: use process.argv instead of Deno.args
// Run as: node extract_table.js ./data/vida_laboral\ \(2\).pdf
if (require.main === module) {
  const pdf = process.argv[2] ?? "./vida_laboral.pdf";
  extraerSituaciones(pdf).then((filas) => {
    // Imprime JSON “bonito”; cámbialo a CSV/persistencia si lo necesitas
    console.log(JSON.stringify(filas, null, 2));
  });
}
