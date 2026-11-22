// The picture that tastes of one ingredient — r1.
// Copies the pre-rendered entry.png (bundled in this repo) to /output/entry.png.
// Node 22, standard library only. No network, no randomness, no timestamps:
// two runs produce a byte-identical file.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const target = "/output/entry.png";

mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);
