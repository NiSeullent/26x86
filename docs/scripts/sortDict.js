const fs = require("fs");

// Ensure we are operating relative to the script's directory
process.chdir(__dirname);

const dictPath = "../dictionary/dictionary.txt";
const ocPath = "../dictionary/opencorekeys.txt";

console.log("Wörterbücher lesen...");
console.log("Reading dictionaries...");

// Helper to read file, split by newline, and filter empty lines
const readToSet = (filePath) => {
    const content = fs.readFileSync(filePath, { encoding: "utf8" });
    return new Set(content.split("\n").filter(line => line !== ""));
};

// Loading data directly into Sets instantly deduplicates it
const dictSet = readToSet(dictPath);
const ocSet = readToSet(ocPath);

console.log("Filtern und Aussortierung...");
console.log("Filtering and Sorting...");

// High-speed subtraction: Instantly drop OpenCore keys from main dictionary
for (const key of ocSet) {
    dictSet.delete(key);
}

// Convert back to arrays and sort alphabetically (Standard ASCII/UTF-16 order)
const sortedDict = Array.from(dictSet).sort();
const sortedOc = Array.from(ocSet).sort();

console.log("Dateien schreiben...");
console.log("Writing files...");
fs.writeFileSync(dictPath, sortedDict.join("\n"));
fs.writeFileSync(ocPath, sortedOc.join("\n"));

console.log("Done!");
