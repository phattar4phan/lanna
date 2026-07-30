import { useState, useRef, useEffect, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Send } from "lucide-react";
import { Reveal } from "./utils";

const MOCK = [
  "That's an interesting question.",
  "I'm still under active development.",
  "Here's one possible explanation...",
  "My current architecture contains approximately 50 million parameters.",
  "I don't always know the answer, but here's my best guess.",
];

type Msg = { id: number; role: "user" | "assistant"; text: string };

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
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
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, typing]);

  function send(e: FormEvent) {
    e.preventDefault();
    const clean = input.trim();
    if (!clean || typing) return;

    setMsgs((p) => [...p, { id: Date.now(), role: "user", text: clean }]);
    setInput("");
    setTyping(true);

    setTimeout(() => {
      setMsgs((p) => [
        ...p,
        { id: Date.now() + 1, role: "assistant", text: pick(MOCK) },
      ]);
      setTyping(false);
    }, 1000 + Math.random() * 1500);
  }

  const bubble = (role: "user" | "assistant") =>
    role === "user"
      ? "bg-[#FF5722] text-[#2D2D2D] rounded rounded-br-none border-2 border-[#FF5722]"
      : "bg-[#3A3A3A] text-[#F1F1F1] rounded rounded-bl-none border-2 border-[#F1F1F1]/10";

  return (
    <section id="chat" className="py-24 px-4 border-t-2 border-[#F1F1F1]/5">
      <div className="max-w-2xl mx-auto">
        <Reveal>
          <div className="text-center mb-12">
            <h2 className="text-4xl sm:text-5xl font-black text-[#F1F1F1] tracking-tight mb-3">
              Try LLM
            </h2>
            <div className="w-12 h-1.5 bg-[#FF5722] mx-auto mb-4" />
            <p className="text-[#F1F1F1]/50 text-lg font-medium">
              A live demo interface — responses are simulated for now.
            </p>
          </div>
        </Reveal>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="rounded border-2 border-[#F1F1F1]/10 bg-[#333333] overflow-hidden"
        >
          <div className="h0125 overflow-y-auto p-6 space-y-4">
            <AnimatePresence>
              {msgs.map((m) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div className={`max-w-[80%] px-5 py-3 text-sm font-medium leading-relaxed ${bubble(m.role)}`}>
                    {m.text}
                  </div>
                </motion.div>
              ))}
              {typing && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="bg-[#3A3A3A] rounded rounded-bl-none border-2 border-[#F1F1F1]/10 px-5 py-3 flex gap-1.5">
                    {[0, 150, 300].map((d) => (
                      <span
                        key={d}
                        className="w-2 h-2 bg-[#FF5722] animate-bounce"
                        style={{ animationDelay: `${d}ms` }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={bottom} />
          </div>

          <div className="border-t-2 border-[#F1F1F1]/10 p-4 bg-[#2D2D2D]">
            <form onSubmit={send} className="flex items-center gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask LLM anything..."
                className="flex-1 px-5 py-3 rounded border-2 border-[#F1F1F1]/10 bg-[#2D2D2D] text-sm text-[#F1F1F1] font-medium outline-none focus:border-[#FF5722] transition-colors duration-150 placeholder:text-[#F1F1F1]/25"
                disabled={typing}
              />
              <button
                type="submit"
                disabled={!input.trim() || typing}
                className="p-3 rounded border-2 border-[#FF5722] bg-[#FF5722] text-[#2D2D2D] hover:bg-transparent hover:text-[#FF5722] disabled:opacity-30 disabled:cursor-not-allowed transition-colors duration-150 cursor-pointer"
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
