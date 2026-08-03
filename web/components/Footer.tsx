import { ExternalLink, FileText } from "lucide-react";
import { motion } from "framer-motion";

export default function Footer() {
  return (
    <footer className="py-16 px-4 border-t border-brand/10">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <div className="flex flex-col items-center sm:items-start gap-1">
            <span className="text-xl font-black text-brand tracking-tight">LLM</span>
            <span className="text-sm text-neutral/60 font-light">
              Built for learning, experimentation, and curiosity.
            </span>
          </div>

          <div className="flex items-center gap-4">
            <a
              href="#"
              className="p-2.5 rounded-2xl text-neutral/40 hover:text-accent hover:bg-accent/5 transition-all duration-200"
              aria-label="GitHub"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="p-2.5 rounded-2xl text-neutral/40 hover:text-accent hover:bg-accent/5 transition-all duration-200"
              aria-label="Documentation"
            >
              <FileText className="w-5 h-5" />
            </a>
          </div>
        </motion.div>

        <div className="mt-8 pt-8 border-t border-brand/5 text-center">
          <p className="text-xs text-neutral/40 font-light">
            An open-source research and learning project. Not a commercial product.
          </p>
        </div>
      </div>
    </footer>
  );
}
