// pry smoke fixture — known seamed/welded/ambiguous cases for the TS classifier.
import { WebClient } from "@slack/web-api";
import OpenAI from "openai";
import { readFileSync } from "node:fs";

// WELDED clock — bare current-time read, input-sim NO (hard weld)
export function stampRaw(): string {
  return new Date().toISOString();
}

// SEAMED clock — default-param injection
export function stampInjected(now = new Date()): string {
  return now.toISOString();
}

// SEAMED clock — nullish-default injection
export function stampNullish(input: { now?: Date }): string {
  const t = input.now ?? new Date();
  return t.toISOString();
}

// NOT a boundary — new Date(arg) is deterministic parsing
export function parseTs(ms: number): string {
  return new Date(ms).toISOString();
}

// WELDED clock — Date.now() bare
export function idgen(): string {
  return `${Date.now()}-x`;
}

// WELDED llm — inline lazy singleton
let client: OpenAI | undefined;
export async function search(apiKey: string): Promise<unknown> {
  client ??= new OpenAI({ apiKey });
  return await client.responses.create({ model: "x", input: "y" });
}

// SEAMED slack — ctor-config DI, used via this.attr (one-hop)
export class Notifier {
  private webClient: WebClient;
  constructor(config: { webClient?: WebClient; botToken: string }) {
    this.webClient = config.webClient ?? new WebClient(config.botToken);
  }
  async notify(payload: unknown): Promise<void> {
    await this.webClient.chat.postMessage(payload as never);
  }
}

// SEAMED slack — receiver is a formal param (DI)
export async function postWith(webClient: WebClient, payload: unknown): Promise<void> {
  await webClient.chat.postMessage(payload as never);
}

// WELDED network — global fetch leaf, input-sim YES
export async function get(url: string): Promise<Response> {
  return await fetch(url);
}

// WELDED fileio (demand=false, input-redirectable) + WELDED env (demand=false)
export function load(path: string): string {
  const root = process.env.CEAL_ROOT;
  return readFileSync(path, "utf-8") + (root ?? "");
}
