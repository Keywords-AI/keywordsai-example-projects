import { BaseEmbedding } from "llamaindex";

const DIMENSIONS = 8;

function textToVector(text: string): number[] {
  const vector = Array.from({ length: DIMENSIONS }, () => 0);
  for (let index = 0; index < text.length; index += 1) {
    const bucket = index % DIMENSIONS;
    vector[bucket] += text.charCodeAt(index) / 255;
  }
  const length = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
  return length === 0 ? vector : vector.map((value) => value / length);
}

export class DeterministicEmbedding extends BaseEmbedding {
  embedInfo = {
    dimensions: DIMENSIONS,
  };

  constructor() {
    super();
  }

  async getTextEmbedding(text: string): Promise<number[]> {
    return textToVector(text);
  }

  override getTextEmbeddings = async (texts: string[]): Promise<number[][]> =>
    Promise.all(texts.map((text) => this.getTextEmbedding(text)));

  override async getQueryEmbedding(query: any): Promise<number[]> {
    const text = typeof query === "string" ? query : JSON.stringify(query);
    return this.getTextEmbedding(text);
  }
}
