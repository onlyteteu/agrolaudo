import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const rootDir = process.cwd();
const modelPath = process.argv[2] ?? path.join(rootDir, "templates", "relatorio-modelo.xlsx");
const outputDir = path.join(rootDir, "outputs", "inspection");

await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(modelPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table,drawing",
  include: "id,name,address,values,formulas,type,anchor",
  maxChars: 30000,
  tableMaxRows: 10,
  tableMaxCols: 10,
  tableMaxCellChars: 120,
});

console.log(summary.ndjson);

await fs.writeFile(path.join(outputDir, "model-summary.ndjson"), summary.ndjson, "utf8");

const previewSheetName = process.argv[3] ?? "Plan1";

const fullTable = await workbook.inspect({
  kind: "table",
  range: `${previewSheetName}!A1:N1090`,
  include: "values,formulas",
  maxChars: 800000,
  tableMaxRows: 1090,
  tableMaxCols: 14,
  tableMaxCellChars: 4000,
});

await fs.writeFile(path.join(outputDir, "model-values.ndjson"), fullTable.ndjson, "utf8");

const firstPreview = await workbook.render({
  sheetName: previewSheetName,
  autoCrop: "all",
  scale: 1,
  format: "png",
});

await fs.writeFile(
  path.join(outputDir, "relatorio-de-visita.png"),
  new Uint8Array(await firstPreview.arrayBuffer()),
);
