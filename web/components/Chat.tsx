import { useState, useRef, useEffect, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Send } from "lucide-react";
import { Reveal } from "./utils";

const API = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

type Msg = { id: number; role: "user" | "assistant"; text: string };
type WireMsg = { role: "user" | "assistant"; text: string };

function toWire(msgs: Msg[]): WireMsg[] {
  return msgs.map(({ role, text }) => ({ role, text }));
}

async function streamChat(
  messages: WireMsg[],
  onToken: (text: string) => void,
  signal: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`stream failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      for (const line of event.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        let payload: { type: string; text?: string; message?: string };
        try {
          payload = JSON.parse(line.slice(6));
        } catch {
          continue;
        }
        if (payload.type === "token" && payload.text) {
          onToken(payload.text);
        } else if (payload.type === "error") {
          throw new Error(payload.message ?? "model error");
        }
      }
    }
  }
}

export default function Chat() {
  const [msgs, setMsgs] = useState<Msg[]>([
    {
      id: 0,
      role: "assistant",
      text: "Hello! I'm LLM, an experimental language model with 50 million parameters. I'm here for research and learning purposes. What would you like to explore?",
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  useEffect(() => () => abort.current?.abort(), []);

  async function send(e: FormEvent) {
    e.preventDefault();
    const clean = input.trim();
    if (!clean || typing) return;

    const userMsg: Msg = { id: Date.now(), role: "user", text: clean };
    const history = [...msgs, userMsg];
    setMsgs(history);
    setInput("");
    setTyping(true);
    setError(null);

    const assistant: Msg = { id: Date.now() + 1, role: "assistant", text: "" };
    setMsgs([...history, assistant]);

    const controller = new AbortController();
    abort.current = controller;

    const update = (delta: string) => {
      setMsgs((prev) =>
        prev.map((m) =>
          m.id === assistant.id ? { ...m, text: m.text + delta } : m,
        ),
      );
    };

    try {
      await streamChat(toWire(history), update, controller.signal);
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setMsgs((prev) =>
        prev.filter((m) => m.id !== assistant.id || m.text.length > 0),
      );
      setError("Model unavailable. Try again in a moment.");
    } finally {
      abort.current = null;
      setTyping(false);
    }
  }

  const bubble = (role: "user" | "assistant") =>
    role === "user"
      ? "bg-brand text-[#F9C25B] rounded-br-md"
      : "bg-neutral/10 text-neutral rounded-bl-md";

  return (
    <section id="chat" className="py-24 px-4">
      <div className="max-w-2xl mx-auto">
        <Reveal>
          <div className="text-center mb-12">
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4 text-brand">
              Try LLM
            </h2>
            <p className="text-neutral text-lg font-light">
              Live inference — tokens stream back from the model server.
            </p>
          </div>
        </Reveal>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="rounded-3xl border border-brand/10 bg-white shadow-xl shadow-brand/5 overflow-hidden"
        >
          <div className="h-[500px] overflow-y-auto p-6 space-y-4">
            <AnimatePresence>
              {msgs.map((m) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`max-w-[80%] px-5 py-3 rounded-2xl text-sm leading-relaxed ${bubble(m.role)} whitespace-pre-wrap`}>
                    {m.text || "\u00a0"}
                  </div>
                </motion.div>
              ))}
              {typing && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-neutral/10 rounded-2xl rounded-bl-md px-5 py-3 flex gap-1">
                    {[0, 150, 300].map((d) => (
                      <span
                        key={d}
                        className="w-2 h-2 rounded-full bg-neutral/30 animate-bounce"
                        style={{ animationDelay: `${d}ms` }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            {error && (
              <p className="text-center text-xs text-red-500 pt-2">{error}</p>
            )}
            <div ref={bottom} />
          </div>

          <div className="border-t border-brand/5 p-4 bg-neutral/[0.03]">
            <form onSubmit={send} className="flex items-center gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask LLM anything..."
                className="flex-1 px-5 py-3 rounded-2xl border border-brand/10 bg-white text-sm text-neutral outline-none focus:border-accent/40 focus:ring-2 focus:ring-accent/10 transition-all duration-200 placeholder:text-neutral/30"
                disabled={typing}
              />
              <button
                type="submit"
                disabled={!input.trim() || typing}
                className="p-3 rounded-2xl bg-accent text-white hover:bg-accent/90 disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:shadow-accent/20 cursor-pointer"
              >
                {typing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
