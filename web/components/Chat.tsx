import { useState, useRef, useEffect, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Send } from "lucide-react";
import { Reveal } from "./utils";

const API = "https://llm-server-f6pp.onrender.com/chat";

const FALLBACKS = [
  "That's an interesting question — I'm still under active development.",
  "My current architecture contains approximately 50 million parameters.",
  "I don't always know the answer, but here's my best guess.",
  "I'm an experimental model, still learning from every interaction.",
];

type Msg = { id: number; role: "user" | "assistant"; text: string };

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
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  async function send(e: FormEvent) {
    e.preventDefault();
    const clean = input.trim();
    if (!clean || typing) return;

    const userMsg: Msg = { id: Date.now(), role: "user", text: clean };
    setMsgs((p) => [...p, userMsg]);
    setInput("");
    setTyping(true);

    try {
      const history = [...msgs, userMsg].map((m) => ({
        role: m.role,
        text: m.text,
      }));

      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history }),
      });

      const data = await res.json();
      const reply = data.response?.trim() || randomFallback();

      setMsgs((p) => [
        ...p,
        { id: Date.now() + 1, role: "assistant", text: reply },
      ]);
    } catch {
      setMsgs((p) => [
        ...p,
        { id: Date.now() + 1, role: "assistant", text: randomFallback() },
      ]);
    }

    setTyping(false);
  }

  function randomFallback() {
    return FALLBACKS[Math.floor(Math.random() * FALLBACKS.length)];
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
              A live interface connected to the real model behind the scenes.
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
                  <div className={`max-w-[80%] px-5 py-3 rounded-2xl text-sm leading-relaxed ${bubble(m.role)}`}>
                    {m.text}
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
