import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const workbookPath = process.argv[2];
const outputDir = process.argv[3] ?? path.join(process.cwd(), "outputs", "verification");
const sheetName = process.argv[4] ?? "Plan1";

if (!workbookPath) {
  throw new Error("Use: node scripts/render-ranges.mjs <workbook.xlsx> [outputDir] [sheetName]");
}

await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
await fs.writeFile(path.join(outputDir, "formula-errors.ndjson"), errors.ndjson, "utf8");

const ranges = [
  ["cabecalho", "A1:N35"],
  ["corpo", "A36:N205"],
  ["fotos-1", "A206:N270"],
];

for (const [name, range] of ranges) {
  const preview = await workbook.render({
    sheetName,
    range,
    scale: 1,
    format: "png",
  });
  await fs.writeFile(
    path.join(outputDir, `${name}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

console.log(`Rendered ${ranges.length} previews to ${outputDir}`);
